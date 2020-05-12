import socket
import sys
from typing import List
import subprocess
import threading as th


def init_clients(port: int):
    subprocess.call("bash ./bash_scripts/init.sh %d" % port, shell=True)


def start_server(port: int, cmd_list: List[str]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(1000)
    for cmd in cmd_list:
        if not cmd:
            continue
        conn, addr = s.accept()
        print("Assigning: " + cmd + " to IP " + str(addr))
        sys.stdout.flush()
        conn.sendall(cmd.encode())
        conn.close()

    # we have finished sending all commands, now we just accept connections and close them
    # this is a signal to clients that we have no more commands to distribute
    while True:
        conn, addr = s.accept()
        conn.close()


def get_cmd_list():
    result = subprocess.run("bash user_scripts/gen_cmds.sh", shell=True, stdout=subprocess.PIPE)
    return list(map(lambda cmd: cmd.strip(), result.stdout.decode().split("\n")))


def main():
    if len(sys.argv) != 2:
        print("Usage: dealer.py SERVER_PORT")
        exit(1)

    port = int(sys.argv[1])
    cmd_list = get_cmd_list()
    server_th = th.Thread(target=start_server, args=(port, cmd_list), daemon=True)
    server_th.start()

    init_clients(port)  # this function will return only once all the clients have finished executing all the commands
    print("Done with all our work!")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
