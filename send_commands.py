import socket
import sys
import time
import argparse
import streamlit as st
import textwrap

# Initialize cache and index in session_state
if 'command_history' not in st.session_state:
    st.session_state['command_history'] = []
if 'history_index' not in st.session_state:
    st.session_state['history_index'] = -1  # -1 means new input

commands = [
    {"name": "Restart", "command": b"#restart\r\n\r\n"},
    {"name": "SimICC", "command": b"#simicc\r\n\r\n"},
    {"name": "SimICC2", "command": b"#simicc2\r\n\r\n"},
    {"name": "DTMF Bootload", "command": b"#DTMFBOOTLOAD\r\n\r\n"},
    {"name": "SOT Status", "command": b"#sot?\r\n\r\n"},
    {"name": "Firmware", "command": b"#firmware\r\n\r\n"},
    {"name": "Version", "command": b"#version\r\n\r\n"},
    {"name": "RCONTR?", "command": b"#RCONTR?\r\n\r\n"},
    {
        "name": "Set RURL",
        "command": b"#RCONTR\r\nRURL=185.201.83.33:9000\r\n\r\nRURL2=212.116.138.114:9000\r\n\r\n",
    },
    {"name": "Set SIM 1", "command": b"#RCONTR\r\nDEFAULTSIM=1\r\n\r\n"},
    {"name": "Set SIM 2", "command": b"#RCONTR\r\nDEFAULTSIM=2\r\n\r\n"},
    {"name": "#Dir", "command": b'#dir,RControlConfigs/*\r\n\r\n'},
    {"name": "#at+csq", "command": b'#at+csq\r\n'},
    {"name": "at+csq", "command": b'at+csq\r\n'},
    {"name": "#dir,*", "command": b'#dir,*\r\n\r\n'},
    {"name": "", "command": b'#delfile,NOCONNRESTARTS.txt\r\n\r\n'},
    {"name": "", "command": b'#BYPASSEXT,520,EMPTY,1,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,STATUS\r\n\r\n'},
    {"name": "", "command": b'#RCARMED,1,ALL\r\n\r\n'},
    {"name": "", "command": b'#DEVICECHECK\r\n\r\n'},
]

# --- Preprocess commands for display ---
commands_display = []
for idx, cmd in enumerate(commands):
    # Determine raw name
    if cmd.get("name"):
        raw = cmd['name']
    else:
        raw = cmd['command'].decode('utf-8').strip()
    # Truncate with word-boundary
    display = textwrap.shorten(raw, width=15, placeholder="…")
    commands_display.append({
        'display': display,
        'command': cmd['command'],
        'key': f"predef_{idx}"
    })

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Socket client to send data to the serial port tunnel"
)
parser.add_argument(
    "-H",
    "--host",
    type=str,
    default="127.0.0.1",
    help="Server host (default: 127.0.0.1)",
)
parser.add_argument(
    "-p", "--port", type=int, default=8888, help="Server port (default: 8888)"
)
parser.add_argument(
    "-r",
    "--repeat",
    type=int,
    default=1,
    help="Number of times to send the message (default: 1)",
)
parser.add_argument(
    "-d",
    "--delay",
    type=float,
    default=1.0,
    help="Delay between repeated messages in seconds (default: 1.0)",
)
args = parser.parse_args()

def send_predefined_command(message):

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server
    server_address = (args.host, args.port)
    print(f"Connecting to {args.host}:{args.port}")

    try:
        sock.connect(server_address)
        print(f"Connected to {args.host}:{args.port}")

        # Convert the message to bytes and send it
        print(f"Sending: {message}")
        sock.sendall(message)

        print("Message(s) sent successfully")


    except ConnectionRefusedError:
        print(
            f"Connection refused. Make sure the server is running at {args.host}:{args.port}"
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing socket")
        sock.close()

def send_command(command):
    """
    Send the given command dict via the socket tunnel.
    """
    # Log in UI and console
    st.info(f"Sending: {command['name']}")
    print(command['name'])
    # Route through the predefined command sender
    send_predefined_command(command['command'])

# --- Custom Command Cache Implementation ---
# Helper to update history index and rerun
def update_input_from_history(offset):
    history = st.session_state['command_history']
    idx = st.session_state['history_index'] + offset
    if 0 <= idx < len(history):
        st.session_state['history_index'] = idx
        st.experimental_rerun()

# Determine value for text_area based on history index
if st.session_state['history_index'] >= 0 and st.session_state['history_index'] < len(st.session_state['command_history']):
    random_command_value = st.session_state['command_history'][st.session_state['history_index']]
else:
    random_command_value = ""

# Input field and send button for random multiline command with Prev/Next
input_col, button_col, prev_col, next_col = st.columns([4, 1, 0.7, 0.7])
def on_command_input_change():
    # Reset history index when editing
    st.session_state['history_index'] = -1

with input_col:
    random_command = st.text_area(
        "Enter random command",
        height=80,
        key="random_command_input",
        value=random_command_value,
        on_change=on_command_input_change
    )
with button_col:
    if st.button("Send", type="primary", key="send_random_command"):
        if random_command.strip():
            # Add to cache if not duplicate of last
            if not st.session_state['command_history'] or st.session_state['command_history'][-1] != random_command:
                st.session_state['command_history'].append(random_command)
            st.session_state['history_index'] = -1  # Reset index after send
            # Replace each newline with \r\n
            command_with_crlf = random_command.replace("\n", "\r\n")
            command_with_crlf = command_with_crlf + "\r\n\r\n"
            cmd_dict = {"name": random_command[:15] + ("…" if len(random_command) > 15 else ""), "command": command_with_crlf.encode('utf-8')}
            send_command(cmd_dict)
with prev_col:
    if st.button("Prev", key="prev_command"):
        update_input_from_history(-1)
with next_col:
    if st.button("Next", key="next_command"):
        update_input_from_history(1)

# Arrange predefined buttons in two columns
cols = st.columns(2)
for idx, cmd in enumerate(commands_display):
    col = cols[idx % 2]
    col.button(cmd['display'], type="primary", on_click=send_command,
               args=({'name': cmd['display'], 'command': cmd['command']},), key=cmd['key'])
