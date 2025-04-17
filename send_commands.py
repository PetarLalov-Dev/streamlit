import socket
import sys
import time
import argparse
import streamlit as st

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

def main(message):
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
    #use command_name to find the command in the commands list and send it to the serial port tunnel
    print (command['name'])
    main(command['command'])
    
# Input field and send button for random multiline command
input_col, button_col = st.columns([4, 1])
with input_col:
    random_command = st.text_area("Enter random command", height=80, key="random_command_input")
with button_col:
    if st.button("Send", type="primary", key="send_random_command"):
        if random_command.strip():
            # Replace each newline with \r\n
            command_with_crlf = random_command.replace("\n", "\r\n")
            command_with_crlf = command_with_crlf + "\r\n\r\n"
            cmd_dict = {"name": random_command[:15] + ("…" if len(random_command) > 15 else ""), "command": command_with_crlf.encode('utf-8')}
            send_command(cmd_dict)

# Arrange buttons in two columns
cols = st.columns(2)
for idx, command in enumerate(commands):
    col = cols[idx % 2]
    if command["name"] == "":
        name = command['command']
        # remove trailing \r\n, \r, \n from name
        name = name.decode('utf-8').replace("\r\n", "").replace("\r", "").replace("\n", "")
        display_name = name[:15] + ("…" if len(name) > 15 else "")
        col.button(display_name, type="primary", on_click=send_command, args=(command,))
    else:
        display_name = command['name'][:15] + ("…" if len(command['name']) > 15 else "")
        col.button(display_name, type="primary", on_click=send_command, args=(command,))





