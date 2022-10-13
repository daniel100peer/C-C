import socket
import threading
import dataclasses
from typing import List
import pickle
import typer
from Protocol import Command, unpack_data, pack_data, Disconnect

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello{name}")


HEADER = 64
PORT = 5055
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = ("0.0.0.0", PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
clients = []
client_number = 0
aliases = []  # nicknames

example_command = Command(
    command_payload="""
def upload_file(data, path):
    with open(path, "wb") as f:
        f.write(data.encode("utf-8"))""".encode('utf-8'),
    command_type="upload_file",
    command_identifier=1,
    command_payload_arguments=["Hello World11", r"C:\Users\דניאל\AppData\Local\Temp\hello.txt"])
example_command2 = Command(
    command_payload="""
import socket
import ipaddress
import re
#"Please enter the range of ports you want to scan in format: <int>-<int> (ex would be 60-120)"

def port_scanner(port_range,ip):
    port_range_pattern = re.compile("([0-9]+)-([0-9]+)")
    port_min = 0
    port_max = 65535
    open_ports = []
    while True:
        ip_add_entered = ip
        # If we enter an invalid ip address the try except block will go to the except block and say you entered an invalid ip address.
        try:
            ip_address_obj = ipaddress.ip_address(ip_add_entered)
            # The following line will only execute if the ip is valid.
            break
        except:
            print("You entered an invalid ip address")

    while True:
        # You can scan 0-65535 ports. This scanner is basic and doesn't use multithreading so scanning all
        # the ports is not advised.
        port_range = port_range
        port_range_valid = port_range_pattern.search(port_range.replace(" ", ""))
        if port_range_valid:
            port_min = int(port_range_valid.group(1))
            port_max = int(port_range_valid.group(2))
            break

    for port in range(port_min, port_max + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect((ip_add_entered, port))
                open_ports.append(port)

        except:
            # We don't need to do anything here. If we were interested in the closed ports we'd put something here.
            pass

    for port in open_ports:
        # We use an f string to easily format the string with variables so we don't have to do concatenation.
        print(f"Port {port} is open on {ip_add_entered}.")
        return open_ports
    if (len(open_ports)==0):
        return("all ports are closed")""".encode('utf-8'),
    command_type="port_scanner",
    command_identifier=2,
    command_payload_arguments=["60-62", "127.0.0.1"])


def broadcast(message):
    for client in clients:
        client.send(message)


def handle_client(client, addr):  # handle the individual connection
    ## this one is for each client.
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append((client, addr))
    global client_number
    client_number+=1
    connected = True
    data = b''
    client.send(pack_data(pickle.dumps(example_command)))
    while connected:
        data += client.recv(HEADER)
        msgs, data = unpack_data(data)
        for msg_data in msgs:
            msg = pickle.loads(msg_data)
            if isinstance(msg, Disconnect):
                connected = False
                client.close()
                print(f"[{addr}] disconnected!")
            else:
                print(f"[{addr}] {msg}")

    client.close()


def start():  # handle new connections and distribute them to where they need to go
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        client, addr = server.accept()  # Client is a socket object
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
