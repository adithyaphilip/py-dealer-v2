import sys
import multiprocessing as mp
import threading as th
import subprocess
import socket
import time

_CON_FAIL_SLEEP_TIME_S = 30
_STDOUT_ERR_FOLDER = "pydealer-client-stdouterr"


def recvall(sock):
    buf_size = 4096  # 4 KiB
    data = b''
    while True:
        part = sock.recv(buf_size)
        data += part
        if len(part) < buf_size:
            # either 0 or end of data
            break
    return data.decode()


def fetch_new_cmd(dealer_ip: str, port: int):
    # connect to dealer server socket
    # if connection fails, wait for 30s and retry
    # as soon as we connect the dealer will write a command to the socket, send it to us, and close the socket
    while True:
        try:
            print("Connecting for command")
            conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn_sock.connect((dealer_ip, port))
            return recvall(conn_sock)
        except Exception as e:
            print(e, file=sys.stderr)
            time.sleep(_CON_FAIL_SLEEP_TIME_S)


def exec_cmd(cmd: str, semaphore: th.BoundedSemaphore):
    # execute the command, and release the semaphore when we are done
    with open(_STDOUT_ERR_FOLDER + "/" + cmd[cmd.index("--nodes"):] + ".out", "w") as stdout_f:
        with open(_STDOUT_ERR_FOLDER + '/' + cmd[cmd.index("--nodes"):] + ".err", "w") as stderr_f:
            print("Executing command " + cmd)
            subprocess.call(cmd, shell=True, stdout=stdout_f, stderr=stderr_f)
            semaphore.release()


def start_cmd_loop(dealer_ip: str, port: int):
    cores_allowed = mp.cpu_count() - 1
    # create the semaphore using all but two of the cores
    semaphore = th.BoundedSemaphore(cores_allowed)

    workers = []

    while True:
        semaphore.acquire()  # can we afford to spawn more processes?
        # yes we can!
        time.sleep(5) # by waiting five seconds before we fetch each command, we effectively implement a kind of round-robin amongst the client nodes
        cmd = fetch_new_cmd(dealer_ip, port)  # we have the next command!
        # Spawn a new thread to spawn a new process to execute that command. Once that processes finishes, the thread
        # will release the semaphore we acquire in the loop
        if cmd:
            worker_th = th.Thread(target=exec_cmd, args=(cmd, semaphore))
            workers.append(worker_th)
            worker_th.start()
        else:  # we will no longer receive any commands, just wait for all existing workers then break
            for worker in workers:
                worker.join()
            break


def main():
    # wakes up knowing which folder to use and who the dealer is
    if len(sys.argv) != 3:
        print("Usage: client.py DEALER_SERVER_IP DEALER_SERVER_PORT", file=sys.stderr)
        exit(1)

    dealer_ip = sys.argv[1]
    dealer_port = int(sys.argv[2])
    # requests the dealer for commands in a loop until it is full
    start_cmd_loop(dealer_ip, dealer_port)


if __name__ == '__main__':
    main()
