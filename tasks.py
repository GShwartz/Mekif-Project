import socket
from datetime import datetime
from termcolor import colored
import time
import ntpath


class Tasks:
    def __init__(self, con, ip, ttl, clients, connections, targets, ips):
        self.con = con
        self.ip = ip
        self.ttl = ttl
        self.clients = clients
        self.connections = connections
        self.targets = targets
        self.ips = ips

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def tasks(self):
        d = datetime.now().replace(microsecond=0)
        dt = str(d.strftime("%b %d %Y | %I-%M-%S"))
        print(f"[{colored('*', 'cyan')}]Retrieving remote station's task list\n"
              f"[{colored('*', 'cyan')}]Please wait...")
        try:
            self.con.send('tasks'.encode())
            filenameRecv = self.con.recv(1024).decode()
            time.sleep(self.ttl)
            size = self.con.recv(4)
            size = self.bytes_to_number(size)
            current_size = 0
            buffer = b""

            with open(filenameRecv, 'wb') as tsk_file:
                while current_size < size:
                    data = self.con.recv(1024)
                    if not data:
                        break

                    if len(data) + current_size > size:
                        data = data[:size - current_size]

                    buffer += data
                    current_size += len(data)
                    tsk_file.write(data)

            with open(filenameRecv, 'r') as file:
                data = file.read()
                print(data)

            name = ntpath.basename(str(filenameRecv))
            self.con.send(f"Received file: {name}\n".encode())
            msg = self.con.recv(1024).decode()
            # print(f"[{colored('@', 'green')}]{msg}")

            return True

        except ConnectionResetError:
            print(f"[{colored('!', 'red')}]Client lost connection.")
            self.remove_lost_connection()

    def kill_tasks(self):
        while True:
            try:
                choose_task = input(f"[?]Kill a task [Y/n]? ")

            except ValueError:
                print(f"[{colored('*', 'red')}]Choose [Y] or [N].")

            if choose_task.lower() == 'y':
                self.task_to_kill()
                break

            elif choose_task.lower() == 'n':
                try:
                    self.con.send('pass'.encode())
                    break

                except ConnectionResetError:
                    self.remove_lost_connection()
                    break

            else:
                print(f"[{colored('*', 'red')}]Choose [Y] or [N].\n")

        return

    def task_to_kill(self):
        while True:
            task_to_kill = input(f"Task filename [Q Back]: ")
            if str(task_to_kill).lower() == 'q':
                break

            if str(task_to_kill).endswith('exe'):
                if self.confirm_kill(task_to_kill).lower() == "y":
                    try:
                        self.con.send('kill'.encode())
                        self.con.send(task_to_kill.encode())
                        msg = self.con.recv(1024).decode()
                        print(f"[{colored('*', 'green')}]{msg}\n")
                        break

                    except socket.error:
                        print(f"[{colored('!', 'red')}]Client lost connection.")
                        self.remove_lost_connection()

                else:
                    break

            else:
                print(f"[{colored('*', 'red')}]{task_to_kill} not found.")

        return task_to_kill

    def confirm_kill(self, task_to_kill):
        while True:
            confirm_kill = input(f"Are you sure you want to kill {task_to_kill} [Y/n]? ")
            if confirm_kill.lower() == "y":
                break

            elif confirm_kill.lower() == "n":
                break

            else:
                print(f"[{colored('*', 'red')}]Choose [Y] or [N].")

        return confirm_kill

    def remove_lost_connection(self):
        try:
            for conKey, ipValue in self.clients.items():
                if conKey == con:
                    for ipKey, identValue in ipValue.items():
                        if ipKey == ip:
                            for identKey, userValue in identValue.items():
                                self.targets.remove(con)
                                self.ips.remove(ip)

                                del self.connections[con]
                                del self.clients[con]
                                print(f"[{colored('*', 'red')}]{colored(f'{ip}', 'yellow')} | "
                                      f"{colored(f'{identKey}', 'yellow')} | "
                                      f"{colored(f'{userValue}', 'yellow')} "
                                      f"Removed from Availables list.\n")
            return False

        except RuntimeError:
            return False
