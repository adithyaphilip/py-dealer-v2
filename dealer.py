import socket
import sys
from typing import List
import subprocess
import threading as th

_CLIENT_INPUT_FILE = "input_files/clients"


def gen_client_list(gen_clients_script: str):
    with open(_CLIENT_INPUT_FILE, "w") as f:
        result = subprocess.run([f"{gen_clients_script}"], stdout=f)
        print(f"Generated worker list with return code: {result.returncode}")


def init_clients(public_dealer_ip: str, port: int, max_parallel_per_node: int):
    subprocess.call(f"bash ./bash_scripts/init.sh {public_dealer_ip} {port} {max_parallel_per_node}", shell=True)


def start_server(ip: str, port: int, cmd_list: List[str]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(1000)
    for cmd in cmd_list:
        if not cmd:
            continue
        conn, addr = s.accept()
        print("Assigning: " + cmd + " to IP " + str(addr))
        sys.stdout.flush()
        conn.sendall(cmd.encode())
        conn.close()

    print("We've finished assigning all the commands we have to machines! Now we just need to wait for the results")
    # we have finished sending all commands, now we just accept connections and close them
    # this is a signal to clients that we have no more commands to distribute
    while True:
        conn, addr = s.accept()
        conn.close()


def get_cmd_list(gen_cmds_script: str):
    result = subprocess.run(gen_cmds_script, shell=True, stdout=subprocess.PIPE)
    return list(map(lambda cmd: cmd.strip(), result.stdout.decode().split("\n")))


def main():
    if len(sys.argv) != 7:
        print("Usage: dealer.py SERVER_LISTEN_IP SERVER_PORT PUBLIC_IP GEN_WORKERS_SCRIPT GEN_CMDS_SCRIPT MAX_PARALLELISM_PER_NODE")
        exit(1)

    listen_ip = sys.argv[1]
    port = int(sys.argv[2])
    public_ip = sys.argv[3]
    gen_client_script = sys.argv[4]
    gen_cmds_script = sys.argv[5]
    max_parallel_per_node = int(sys.argv[6])

    cmd_list = get_cmd_list(gen_cmds_script)
    server_th = th.Thread(target=start_server, args=(listen_ip, port, cmd_list), daemon=True)
    server_th.start()

    gen_client_list(gen_client_script)
    init_clients(public_ip, port, max_parallel_per_node)  # this function will return only once all the clients have finished executing all the commands
    print("Done with all our work!")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
