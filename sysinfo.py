from datetime import datetime
import time
from termcolor import colored
import socket
import ntpath


def bytes_to_number(b):
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def system_information(con, ttl):
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%b %d %Y | %I-%M-%S"))
    print(f"[{colored('*', 'magenta')}]Retrieving remote station's system information\n"
          f"[{colored('*', 'magenta')}]Please wait...")

    # Send Systeminfo command to client
    con.send('si'.encode())

    # Get systeminfo filename
    filenameRecv = con.recv(1024)
    time.sleep(ttl)

    # Get file size in bytes
    size = con.recv(4)

    # Convert size to number
    size = bytes_to_number(size)

    # Init current size & buffer
    current_size = 0
    buffer = b""

    try:
        with open(filenameRecv, 'wb') as file:
            while current_size < size:
                data = con.recv(1024)
                if not data:
                    break

                if len(data) + current_size > size:
                    data = data[:size - current_size]

                buffer += data
                current_size += len(data)
                file.write(data)

    except socket.error as e:
        print(f"[{colored('*', 'red')}]{e}\n")
        return False

    except (ConnectionResetError, ConnectionError,
            ConnectionRefusedError, ConnectionAbortedError) as c:
        print(f"[{colored('*', 'red')}]{c}\n")
        return False

    name = ntpath.basename(str(filenameRecv))

    with open(filenameRecv, 'r') as file:
        data = file.read()
        print(data)

    print(f"[{colored('V', 'green')}]Received: {name} \n")
    con.send(f"Received file: {name}\n".encode())
    msg = con.recv(1024).decode()

    return
