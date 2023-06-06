import sys
import multiprocessing as mp
import threading as th
import subprocess
import socket
import time
import json

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


def exec_cmd(cmd: str, semaphore: th.BoundedSemaphore, node_id, cmd_id):
    # execute the command, and release the semaphore when we are done
    exp_name = f"pydealer_{str(node_id)}_{str(cmd_id)}_{str(time.time()).replace('.', '_')}"
    with open(f"{_STDOUT_ERR_FOLDER}/{exp_name}.out", "w") as stdout_f:
        with open(f"{_STDOUT_ERR_FOLDER}/{exp_name}.err", "w") as stderr_f:
            print("Executing command " + cmd)
            exit_status = subprocess.call(cmd, shell=True, stdout=stdout_f, stderr=stderr_f)
            with open(f"{_STDOUT_ERR_FOLDER}/{exp_name}.json", "w") as info_f:
                json.dump({"cmd": cmd, "node_id": node_id, "cmd_id": cmd_id, "exit_status": exit_status,
                           "exp_name": exp_name}, info_f)
            semaphore.release()


def start_cmd_loop(dealer_ip: str, port: int, node_id: int, max_parallel: int):
    cores_allowed = min(mp.cpu_count() - 1, max_parallel)
    # create the semaphore using all but two of the cores
    semaphore = th.BoundedSemaphore(cores_allowed)
    # TODO: Is there a reason we didn't just use a ThreadPool here? Was it so we fetch only one command at a time and in round-robin? Is there a way to do that with a ThreadPool?
    #  E.g. If we have a queue of jobs lined up in a ThreadPool, and two of them start up simultaneously, they'll make concurrent requests for jobs
    workers = []
    cmd_id = 0
    while True:
        semaphore.acquire()  # can we afford to spawn more processes?
        # yes we can!
        # by waiting five seconds before we fetch each command,
        # we effectively implement a kind of round-robin amongst the client nodes
        time.sleep(5)
        cmd = fetch_new_cmd(dealer_ip, port)  # we have the next command!
        cmd_id += 1
        # Spawn a new thread to spawn a new process to execute that command. Once that processes finishes, the thread
        # will release the semaphore we acquire in the loop
        # NOTE: It's okay for us to use threads here because we create a new process within the thread, so we
        # don't suffer from the GIL
        if cmd:
            worker_th = th.Thread(target=exec_cmd, args=(cmd, semaphore, node_id, cmd_id))
            workers.append(worker_th)
            worker_th.start()
        else:  # we will no longer receive any commands, just wait for all existing workers then break
            for worker in workers:
                worker.join()
            break


def main():
    # wakes up knowing which folder to use and who the dealer is
    print("Arguments:", sys.argv)
    if len(sys.argv) != 5:
        print("Usage: client.py DEALER_SERVER_IP DEALER_SERVER_PORT NODE_ID MAX_PARALLEL", file=sys.stderr)
        exit(1)

    dealer_ip = sys.argv[1]
    dealer_port = int(sys.argv[2])
    node_id = int(sys.argv[3])
    max_parallel = int(sys.argv[4])
    # requests the dealer for commands in a loop until it is full
    start_cmd_loop(dealer_ip, dealer_port, node_id, max_parallel)


if __name__ == '__main__':
    main()
