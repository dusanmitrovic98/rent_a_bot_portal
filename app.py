import os
import platform
import subprocess
import threading
import uuid
import logging
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

# Get the current directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['SECRET_KEY'] = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure SocketIO with correct async mode
async_mode = 'threading' if platform.system() == 'Windows' else 'eventlet'
socketio = SocketIO(app, async_mode=async_mode, logger=True, engineio_logger=True)

# Session management
active_sessions = {}

def get_system_shell():
    """Detect OS and return appropriate shell"""
    return 'cmd.exe' if platform.system() == 'Windows' else '/bin/bash'

def create_shell_session(session_id):
    """Create persistent shell process for a session"""
    try:
        shell = get_system_shell()
        creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
        
        # Start the shell with a clean configuration
        if platform.system() == 'Windows':
            args = [shell, '/Q', '/K', 'prompt $S$G']
        else:
            args = [shell, '--norc', '-i']
        
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=False,
            creationflags=creationflags
        )
        
        # Start output reader thread
        def output_reader():
            try:
                # Skip initial output until we see the prompt
                prompt_detected = False
                command_echo_mode = False
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Skip initial Windows messages
                        if not prompt_detected:
                            if 'Microsoft Windows' in output or 'Copyright' in output:
                                continue
                            if any(char in output for char in ['>', '$', '#']):
                                prompt_detected = True
                                continue
                        
                        # Skip command echo
                        if command_echo_mode:
                            command_echo_mode = False
                            continue
                            
                        # Skip prompt lines
                        if any(char in output for char in ['>', '$', '#']):
                            continue
                            
                        # Send cleaned output
                        if output.strip():
                            socketio.emit('output', {'data': output, 'session_id': session_id})
            except Exception as e:
                logger.error(f"Output reader error: {str(e)}")
        
        thread = threading.Thread(target=output_reader)
        thread.daemon = True
        thread.start()
        
        return process, thread
    except Exception as e:
        logger.exception("Failed to create shell session")
        return None, None

@app.route('/')
def index():
    """Serve terminal interface"""
    return render_template('term.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify(status="ok", platform=platform.system())

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on('create_session')
def handle_create_session():
    """Create new terminal session"""
    try:
        session_id = str(uuid.uuid4())
        process, thread = create_shell_session(session_id)
        if process and thread:
            active_sessions[session_id] = {
                'process': process,
                'thread': thread
            }
            logger.info(f"Created new session: {session_id}")
            emit('session_created', {'session_id': session_id})
        else:
            emit('session_error', {'message': 'Failed to create shell process'})
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        emit('session_error', {'message': str(e)})

@socketio.on('execute')
def handle_command(data):
    """Execute command in existing session"""
    session_id = data.get('session_id')
    command = data.get('command', '')
    
    if not session_id or not command:
        return
    
    if session_id in active_sessions:
        try:
            proc = active_sessions[session_id]['process']
            # Windows needs \r\n line endings
            if platform.system() == 'Windows' and not command.endswith('\r'):
                command = command.replace('\n', '\r\n')
            proc.stdin.write(command)
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            emit('output', {'data': '\r\nSession terminated\r\n', 'session_id': session_id})
    else:
        emit('session_error', {'message': f"Invalid session ID: {session_id}"})

@socketio.on('close_session')
def handle_close_session(data):
    """Terminate shell session"""
    session_id = data.get('session_id')
    if session_id and session_id in active_sessions:
        proc = active_sessions[session_id]['process']
        try:
            # Try graceful exit
            proc.stdin.write('exit\n')
            proc.stdin.flush()
        except:
            pass
        
        # Force terminate if needed
        try:
            if proc.poll() is None:
                proc.terminate()
        except:
            pass
        
        del active_sessions[session_id]
        logger.info(f"Closed session: {session_id}")

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Platform: {platform.system()}")
    
    if platform.system() == 'Windows':
        print(f"Server running at http://{host}:{port}")
        print("Press Ctrl+C to stop")
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
    else:
        socketio.run(app, host=host, port=port)