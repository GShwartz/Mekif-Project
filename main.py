from datetime import datetime
from termcolor import colored
from threading import Thread
from colorama import init
import subprocess
import pwinput
import os.path
import ntpath
import socket
import psutil
import time
import sys
import io
import validation
import screenshot
import connectedstations
from tasks import Tasks
import sysinfo
from freestyle import freestyle


# TODO: Break to modules.

init()


class Server:
    clients = {}
    connections = {}
    connHistory = []
    ips = []
    targets = []
    threads = []
    tmp_availables = []

    def __init__(self, serverIP, serverPort, ttl, path):
        self.serverIp = serverIP
        self.serverPort = serverPort
        self.ttl = ttl
        self.path = path
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.serverIp, self.serverPort))
        self.server.listen(5)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def run(self):
        self.connectThread = Thread(target=self.connect, daemon=True, name=f"Connect Thread").start()
        self.threads.append(self.connectThread)

    def connect(self):
        while True:
            # Capture Date & Time with AM PM
            self.d = datetime.now().replace(microsecond=0)
            self.dt = str(self.d.strftime("%b %d %Y %I:%M:%S %p"))

            self.conn, (self.ip, self.port) = self.server.accept()

            try:
                # Get Remote Computer's Name
                self.ident = self.conn.recv(1024).decode()

                # Get Current User:
                self.user = self.conn.recv(1024).decode()

            except (ConnectionResetError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError):
                print("Lost Connection")
                return  # Restart The Loop

            # Update Thread Dict and Connection Lists
            if self.conn not in self.targets and self.ip not in self.ips:
                # Add Socket Connection To Targets list
                self.targets.append(self.conn)
                # Add IP Address Connection To Targets list
                self.ips.append(self.ip)
                # Set Temp Dict To Update Connections List
                self.temp_connection = {self.conn: self.ip}
                # Add Temp Dict To Connections List
                self.connections.update(self.temp_connection)
                # Set Temp Idents Dict For Idents
                self.temp_ident = {self.conn: {self.ip: {self.ident: self.user}}}
                # Add Temp Idents Dict To Idents Dict
                self.clients.update(self.temp_ident)

            self.d = datetime.now().replace(microsecond=0)
            self.dt = str(self.d.strftime("%b %d %Y %I:%M:%S %p"))

            # Create a Dict of Connection, IP, Computer Name, Date & Time
            self.temp_connection_record = {self.conn: {self.ip: {self.ident: {self.user: self.dt}}}}
            # Add Connection to Connection History
            self.connHistory.append(self.temp_connection_record)

            if self.welcome_message():
                continue

    def welcome_message(self):
        # Send Welcome Message
        try:
            self.welcome = "Connection Established!"
            self.conn.send(f"@Server: {self.welcome}".encode())

            return True

        except (socket.error, ConnectionResetError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError):
            print(f"[{colored('*', 'red')}]Check client's connection.")
            if self.conn in self.targets and self.ip in self.ips:
                self.targets.remove(self.conn)
                self.ips.remove(self.ip)
                del self.connections[self.conn]
                del self.clients[self.conn]

                return False

    def connection_history(self):
        print(f"{colored('=', 'blue')}=>{colored('Connection History', 'red')}<={colored('=', 'blue')}")

        # Capture Current Date & Time
        self.d = datetime.now().replace(microsecond=0)
        self.dt = str(self.d.strftime("%b %d %Y %I:%M:%S %p"))

        # Break If Connection History List Is Empty
        if len(self.connHistory) == 0:
            print(f"[{colored('*', 'cyan')}]List is empty.")
            return

        c = 1  # Initiate Counter for Connection Number
        try:
            # Iterate Through Connection History List Items
            for connection in self.connHistory:
                for conKey, ipValue in connection.items():
                    for ipKey, identValue in ipValue.items():
                        for identKey, userValue in identValue.items():
                            for userKey, timeValue in userValue.items():
                                print(
                                    f"[{colored(str(c), 'green')}]{colored('IP', 'cyan')}: {ipKey} | "
                                    f"{colored('Station Name', 'cyan')}: {identKey} | "
                                    f"{colored('User', 'cyan')}: {userKey} | "
                                    f"{colored('Time', 'cyan')}: {timeValue}")
                    c += 1
            return

        # Break If Client Lost Connection
        except (KeyError, socket.error, ConnectionResetError):
            return

    def vital_signs(self):
        # Return False If Socket Connection List is Empty
        if len(self.targets) == 0:
            print(f"[{colored('*', 'yellow')}]No connected stations.")
            print(f"[{colored('*', 'yellow')}]Terminating process.")
            return False

        if connectedstations.vitals_input():
            connectedstations.vital_signs(self.targets, self.ips, self.clients, self.connections)
            return True

        else:
            return False

    def show_available_connections(self):
        if len(self.ips) == 0:
            print(f"[{colored('*', 'cyan')}]No connected stations.\n")
            return

        try:
            print(f"[{colored('*', 'cyan')}] {colored('Available Connections', 'green')} [{colored('*', 'cyan')}]")
            print(f"{colored('=', 'yellow') * 29}")
            count = 0
            for conKey, ipValue in self.clients.items():
                for ipKey, identValue in ipValue.items():
                    for con, ip in self.connections.items():
                        if ip == ipKey:
                            for identKey, userValue in identValue.items():
                                if (count, ipKey, identKey, userValue) in self.tmp_availables:
                                    continue

                                self.tmp_availables.append((count, ipKey, identKey, userValue))
                count += 1

            for item in self.tmp_availables:
                for conKey, ipValue in self.clients.items():
                    for ipKey in ipValue.keys():
                        if item[1] == ipKey:
                            print(f"Session [{colored(f'{item[0]}', 'cyan')}] | "
                                  f"Station IP: {colored(f'{item[1]}', 'green')} | "
                                  f"Station Name: {colored(f'{item[2]}', 'green')} | "
                                  f"Logged User: {colored(f'{item[3]}', 'green')}")

            print(f"\n[{colored('[Q/q]', 'cyan')}]Back")

            return True

        except ConnectionResetError:
            print(f"[{colored('*', 'red')}]Connection terminated by the client.")
            self.remove_lost_connection(con, ip)

    def get_station_number(self):
        if len(self.tmp_availables) == 0:
            return

        tries = 1
        while True:
            station_num = input(f"\n@Session #>> ")
            if str(station_num).lower() == 'q':
                return False

            try:
                val = int(station_num)
                if int(station_num) <= 0 or int(station_num) <= (len(self.tmp_availables)):
                    tarnum = self.targets[int(station_num)]
                    ipnum = self.ips[int(station_num)]
                    # self.shell(tarnum, ipnum)
                    return int(station_num), tarnum, ipnum
                    # break

                else:
                    print(f"[{colored('*', 'red')}]Wrong Number. Choose between [1 - {len(self.tmp_availables)}].\n"
                          f"[Try {colored(f'{tries}', 'yellow')}/{colored('3', 'yellow')}]")

                    if tries == 3:
                        print("U obviously don't know what you're doing. goodbye.")
                        if len(server.targets) > 0:
                            for t in server.targets:
                                t.send('exit'.encode())
                                t.shutdown(socket.SHUT_RDWR)
                                t.close()

                        sys.exit()

                    tries += 1

            except (TypeError, ValueError, IndexError):
                print(f"[{colored('*', 'red')}]Numbers only. Choose between [1 - {len(self.tmp_availables)}].\n"
                      f"[Try {colored(f'{tries}', 'yellow')}/{colored('3', 'yellow')}]")
                if tries == 3:
                    if len(server.targets) > 0:
                        for t in server.targets:
                            t.send('exit'.encode())
                            t.shutdown(socket.SHUT_RDWR)
                            t.close()

                    print("U obviously don't know what you're doing. goodbye.")
                    sys.exit()

                tries += 1

    def show_shell_commands(self, ip):
        print("\t\t" + f"{colored('=', 'blue')}" * 20, f"=> {colored('REMOTE CONTROL', 'red')} <=",
              f"{colored('=', 'blue')}" * 20)
        for conKey, ipValue in self.clients.items():
            for ipKey, userValue in ipValue.items():
                if ipKey == ip:
                    for identKey, timeValue in userValue.items():
                        print("\t\t" + f"Station IP: {colored(f'{ipKey}', 'green')} | "
                                       f"Station Name: {colored(f'{identKey}', 'green')} | "
                                       f"Logged User: {colored(f'{timeValue}', 'green')}")

        print("\t\t" + f"{colored('=', 'yellow')}" * 62 + "\n")

        print(f"\t\t[{colored('1', 'cyan')}]Screenshot          \t\t---------------> "
              f"Capture screenshot.")
        print(f"\t\t[{colored('2', 'cyan')}]System Info         \t\t---------------> "
              f"Show Station's System Information")
        print(f"\t\t[{colored('3', 'cyan')}]Last Restart Time   \t\t---------------> "
              f"Show remote station's last restart time")
        print(f"\t\t[{colored('4', 'cyan')}]Anydesk             \t\t---------------> "
              f"Start Anydesk")
        print(f"\t\t[{colored('5', 'cyan')}]Tasks               \t\t---------------> "
              f"Show remote station's running tasks")
        print(f"\t\t[{colored('6', 'cyan')}]Restart             \t\t---------------> "
              f"Restart remote station")
        print(f"\t\t[{colored('7', 'cyan')}]CLS                 \t\t---------------> "
              f"Clear Screen")
        print(f"\t\t[{colored('8', 'cyan')}]Back                \t\t---------------> "
              f"Back to Control Center \n")

    def confirm_restart(self):
        tries = 0
        while True:
            try:
                str(self.sure)

            except TypeError:
                print(f"[{colored('*', 'red')}]Wrong Input. [({colored('Y/y', 'yellow')}) | "
                      f"({colored('N/n', 'yellow')})]")

                if tries == 3:
                    print("U obviously don't know what you're doing. goodbye.")
                    if len(server.targets) > 0:
                        for t in server.targets:
                            t.send('exit'.encode())
                            t.shutdown(socket.SHUT_RDWR)
                            t.close()

                    sys.exit()
                tries += 1

            if str(self.sure).lower() == "y":
                return True

            elif str(self.sure).lower() == "n":
                return False

            else:
                print(f"[{colored('*', 'red')}]Wrong Input. [({colored('Y/y', 'yellow')}) | "
                      f"({colored('N/n', 'yellow')})]")

                if tries == 3:
                    print("U obviously don't know what you're doing. goodbye.")
                    if len(server.targets) > 0:
                        for t in server.targets:
                            t.send('exit'.encode())
                            t.shutdown(socket.SHUT_RDWR)
                            t.close()

                    sys.exit()
                tries += 1

    def restart(self, con, ip):
        errCount = 3
        self.d = datetime.now().replace(microsecond=0)
        self.dt = str(self.d.strftime("%b %d %Y | %I-%M-%S"))
        self.sure = input("Are you sure you want to restart [Y/n]?")
        if self.confirm_restart():
            try:
                con.send('restart'.encode())
                try:
                    self.remove_lost_connection(con, ip)
                    return False

                except RuntimeError:
                    return False

            except ConnectionResetError:
                print(f"[{colored('!', 'red')}]Client lost connection.")
                self.remove_lost_connection(con, ip)

        return

    def bytes_to_number(self, b):
        res = 0
        for i in range(4):
            res += b[i] << (i * 8)
        return res

    def shell(self, con, ip):
        errCount = 0
        while True:
            self.show_shell_commands(ip)

            # Wait for User Input
            cmd = input(f"COMMAND@{ip}> ")

            # Input Validation
            try:
                val = int(cmd)

            except (TypeError, ValueError):
                print(f"[{colored('*', 'red')}]Numbers Only [{colored('1', 'yellow')} - {colored('8', 'yellow')}]!")
                errCount += 1
                if errCount == 3:
                    print("U obviously don't know what you're doing. goodbye.")
                    con.send("exit".encode())
                    con.shutdown(socket.SHUT_RDWR)
                    con.close()
                    sys.exit()

                continue

            # Run Custom Command
            if int(cmd) == 100:
                con.send("freestyle".encode())
                freestyle(con)
                continue

            # Create INT Zone Condition
            if int(cmd) <= 0 or int(cmd) > 8:
                errCount += 1
                if errCount == 3:
                    print("U obviously don't know what you're doing. goodbye.")
                    con.send("exit".encode())
                    con.shutdown(socket.SHUT_RDWR)
                    con.close()
                    sys.exit()

                print(f"[{colored('*', 'red')}]{cmd} not in the menu."
                      f"[try {colored(errCount, 'yellow')} of {colored('3', 'yellow')}]\n")

            # Screenshot
            if int(cmd) == 1:
                errCount = 0
                if len(self.targets) == 0:
                    print(f"[{colored('*', 'red')}]No connected stations.")
                    break

                try:
                    screenshot.screenshot(con, path, self.tmp_availables, self.clients)

                except ConnectionResetError:
                    print(f"[{colored('!', 'red')}]Client lost connection.")
                    self.remove_lost_connection(con, ip)
                    break

            # System Information
            elif int(cmd) == 2:
                errCount = 0
                if len(self.targets) == 0:
                    print(f"[{colored('*', 'red')}]No connected stations.")
                    break

                try:
                    sysinfo.system_information(con, self.ttl)

                except ConnectionResetError:
                    print(f"[{colored('!', 'red')}]Client lost connection.")
                    try:
                        self.remove_lost_connection(con, ip)
                        return

                    except RuntimeError:
                        return

            # Last Restart Time
            elif int(cmd) == 3:
                errCount = 0
                if len(self.targets) == 0:
                    print(f"[{colored('*', 'red')}]No connected stations.")
                    break

                self.d = datetime.now().replace(microsecond=0)
                self.dt = str(self.d.strftime("%b %d %Y | %I-%M-%S"))

                try:
                    con.send('lr'.encode())
                    msg = con.recv(4096)
                    print(f"[{colored('@', 'green')}]{msg.decode()}")

                except ConnectionResetError:
                    print(f"[{colored('!', 'red')}]Client lost connection.")
                    try:
                        self.remove_lost_connection(con, ip)
                        break

                    except RuntimeError:
                        return

            # Anydesk
            elif int(cmd) == 4:
                errCount = 0
                print(f"[{colored('*', 'magenta')}]Starting AnyDesk...\n")
                if len(self.targets) == 0:
                    print(f"[{colored('*', 'red')}]No connected stations.")
                    break

                self.d = datetime.now().replace(microsecond=0)
                self.dt = str(self.d.strftime("%b %d %Y | %I-%M-%S"))

                try:
                    con.send('anydesk'.encode())
                    msg = con.recv(1024).decode()

                    if "OK" not in msg:
                        print(msg)

                except (ConnectionResetError, ConnectionError, socket.error,
                        ConnectionAbortedError, ConnectionRefusedError):
                    print(f"[{colored('!', 'red')}]Client lost connection.")
                    try:
                        self.remove_lost_connection(con, ip)
                        break

                    except RuntimeError:
                        return

            # Tasks
            elif int(cmd) == 5:
                errCount = 0
                if len(self.targets) == 0:
                    print(f"[{colored('*', 'red')}]No connected stations.")
                    break

                tasks = Tasks(con, ip, ttl, self.clients, self.connections, self.targets, self.ips)
                if not tasks.tasks():
                    return False

                task = tasks.kill_tasks()
                if task is None:
                    continue

                try:
                    tasks.task_to_kill()
                    return True

                except ConnectionResetError:
                    print(f"[{colored('!', 'red')}]Client lost connection.")
                    try:
                        self.remove_lost_connection(con, ip)

                    except RuntimeError:
                        return False

            # Restart
            elif int(cmd) == 6:
                self.restart(con, ip)
                return

            # Clear Screen
            elif int(cmd) == 7:
                os.system('cls')
                continue

            # Back
            elif int(cmd) == 8:
                d = datetime.now().replace(microsecond=0)
                dt = str(d.strftime("%b %d %Y | %I-%M-%S"))
                break

        return

    def remove_lost_connection(self, con, ip):
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


def headline():
    print(f"\t\t\t\t{colored('==+-+-+-+-+-+-++-0-+-+-0++-+-+-+-+-+-+-+-+-++', 'red')}\n"
          f"\t\t\t\t{colored('|W|e|l|c|o|m|e', 'yellow')} {colored('|0|T|o|0|', 'green')} "
          f"{colored('M|e|k|i|f|A|d|m|i|n', 'yellow')}\n"
          f"\t\t\t\t{colored('==+-+-+-+-+-+-++-0-+-+-0++-+-+-+-+-+-+-+-+-++', 'red')}")
    print(f""
          f"\t\t\t\t{colored('By Gil Shwartz', 'green')} {colored('@2022', 'yellow')}\n")
    print(f"\t\t({colored('1', 'yellow')})Remote Control          ---------------> "
          f"Show Remote Commands")
    print(f"\t\t({colored('2', 'yellow')})Connection History      ---------------> "
          f"Show connection history.")
    print(f"\t\t({colored('3', 'yellow')})Show Connected Stations ---------------> "
          f"Display Current connected stations")
    print(f"\t\t({colored('4', 'yellow')})CLS                     ---------------> "
          f"Clear Local Screen")
    print(f"\t\t({colored('5', 'yellow')})Server Info             ---------------> "
          f"Show Server Information")
    print(f"\n\t\t({colored('6', 'red')})Exit                    ---------------> "
          f"Close connections and exit program.\n")


def main():
    headline()

    # Wait For User Commands
    command = input("CONTROL@> ")

    # Input Validation
    try:
        int(command)

    except ValueError:
        print(
            f"[{colored('*', 'red')}]Numbers only. Choose between "
            f"[{colored('1', 'yellow')} - {colored('5', 'yellow')}].\n")

        return False

    if int(command) <= 0 or int(command) > 6:  # Validate input is in the menu
        print(f"[{colored('*', 'red')}]Wrong Number. [{colored('1', 'yellow')} - {colored('5', 'yellow')}]!")
        return False

    # Remote Shell Commands
    if int(command) == 1:
        if len(server.clients) != 0:
            print(f"{colored('=', 'blue')}=>{colored('Remote Shell', 'red')}<={colored('=', 'blue')}")
            # Show Available Connections
            server.show_available_connections()

            # Get Number from User and start Remote Shell
            station = server.get_station_number()
            if station:
                server.shell(station[1], station[2])
                return

        else:
            print(f"[{colored('*', 'cyan')}]No available connections.")

        return

    # Connection History
    elif int(command) == 2:
        server.connection_history()
        return

    # Vital Signs - Show Connected Stations
    elif int(command) == 3:
        if len(server.ips) == 0:
            print(f"[{colored('*', 'yellow')}]No connected stations.")
            return

        print(f"{colored('=', 'blue')}=>{colored('Vital Signs', 'red')}<={colored('=', 'blue')}")
        print(f"[{colored('1', 'green')}]Start | "
              f"[{colored('2', 'cyan')}]Back\n")

        server.vital_signs()

    # Clear Screen
    elif int(command) == 4:
        os.system('cls')

    # Show Server's Information
    elif int(command) == 5:
        last_reboot = psutil.boot_time()
        print(f"\n[{colored('*', 'cyan')}]Server running on IP: {server.serverIp} | Port: {server.serverPort}")
        print(f"[{colored('*', 'cyan')}]Server's last restart: "
              f"{datetime.fromtimestamp(last_reboot).replace(microsecond=0)}")
        print(f"[{colored('*', 'cyan')}]Connected Stations: {len(server.clients)}\n")

    # Exit Program
    elif int(command) == 6:
        server.d = datetime.now().replace(microsecond=0)
        server.dt = str(server.d.strftime("%b %d %Y %I:%M:%S %p"))
        if len(server.targets) > 0:
            try:
                for t in server.targets:
                    t.send('exit'.encode())
                    t.close()

            except ConnectionResetError:
                print("Connection Reset")
                pass

        sys.exit()

    return


if __name__ == '__main__':
    port = 55400
    ttl = 5
    hostname = socket.gethostname()
    serverIP = str(socket.gethostbyname(hostname))
    path = r'c:\MekifRemoteAdmin'

    # Run User Validation
    # validation.validation()

    # Initialize Server Class
    server = Server(serverIP, port, ttl, path)
    server.run()

    while True:
        main()
