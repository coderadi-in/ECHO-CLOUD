"""
Run command file for the project.

Runs the project on ngrok server.
"""

# ? IMPORTS
from main import server
from plugins import socket
import ngrok
import os
import threading

# ! LOAD VENV
from dotenv import load_dotenv
load_dotenv('.venv/vars.env')

# * HANDLER FUNCTION
def connect_ngrok():
    # Set the authtoken programmatically
    NGROK_AUTH = os.getenv("NGROK_AUTHTOKEN")
    ngrok.set_auth_token(NGROK_AUTH)
    
    try:
        forwarder = ngrok.forward(
            "http://127.0.0.1:5000",
            domain="decade-grimacing-riverbank.ngrok-free.dev",
            verify_upstream_tls=False
        )
        print(f"Ngrok tunnel established at: {forwarder.url()}")
        return forwarder
    except Exception as e:
        print(f"Failed to connect ngrok: {e}")
        raise

# ! RUN
if (__name__ == "__main__"):
    ngrok_thread = threading.Thread(target=connect_ngrok, daemon=True)
    ngrok_thread.start()

    socket.run(server, debug=True, host='0.0.0.0')