from termcolor import colored
import time
import socket


def vitals_input():
    while True:
        # Wait For User Input
        pick = input("CONTROL@> ")
        try:
            float(pick)

        # Restart Loop If Input Is Not a Number
        except ValueError:
            print(f"[{colored('*', 'yellow')}]Wrong choice.")
            continue

        # Start
        if int(pick) == 1:
            return True

        # Back
        elif int(pick) == 2:
            return False

        # Restart Loop If Input Number Is Incorrect
        else:
            print(f"[{colored('*', 'red')}]Wrong Number! "
                  f"[{colored('1', 'yellow')} - {colored('3', 'yellow')}]")


def vital_signs(targets, ips, clients, connections):
    """
        Create temp lists for current connected sockets.
        Send a Poke message to each socket connection and wait for answer.
        If the socket doesn't respond then shutdown the socket connection,
        close the socket connection and remove connection details from connection lists.
        Reset temp lists.

        :return: Process Completed.
    """

    # Capture Current Connected Sockets
    tmpconns = targets

    # Create Temp Lists For Socket Connections and IPs
    templist = []
    tempips = []

    # Set Response String To Compare To The Answer From The Client.
    callback = 'yes'
    i = 0

    # Return False If Socket Connection List is Empty
    if len(targets) == 0:
        print(f"[{colored('*', 'yellow')}]No connected stations.")
        print(f"[{colored('*', 'yellow')}]Terminating process.")
        return False

    # Iterate Through Temp Connected Sockets List
    for t in tmpconns:
        try:
            # Send a Poke Message To The Client
            t.send('alive'.encode())
            # Wait For Answer From The Client
            ans = t.recv(1024).decode()

            # Compare Client's Answer To Response String Set Above
            # Update Temp Lists if True
            if str(ans) == str(callback):
                print(f"[{colored('V', 'green')}]{ips[i]}")
                templist.append(targets[i])
                tempips.append(ips[i])
                i += 1
                time.sleep(1)

        except ConnectionResetError:
            print(f"[{colored('*', 'red')}]{ips[i]} does not respond.")
            tempIP = ips[i]
            # Iterate clients, Shutdown + Close Connection
            # Remove Connection Details From Lists
            try:
                for conKey, ipValue in clients.items():
                    for tmp in tmpconns:
                        # Compare Socket Connection From Clients Dict Against
                        # Socket Connection In Temp Connections List
                        if conKey == tmp and conKey in targets:
                            for ipKey, identValue in ipValue.items():
                                conKey.shutdown(socket.SHUT_RDWR)
                                conKey.close()

                                targets.remove(conKey)
                                ips.remove(tempIP)
                                if tmp in tmpconns:
                                    tmpconns.remove(tmp)

                                del connections[conKey]
                                del clients[conKey]
                                for identKey, userValue in identValue.items():
                                    print(f"[{colored('*', 'red')}]({colored(f'{tempIP}', 'red')} | "
                                          f"{colored(f'{identKey}', 'red')} | "
                                          f"{colored(f'{userValue}', 'red')}) "
                                          f"has been removed from the availables list.")

            except (ConnectionResetError, ConnectionError,
                    ConnectionAbortedError, ConnectionRefusedError, RuntimeError):
                print(f"[{colored('*', 'cyan')}]Runtime: Idents & Connections Dicts Changed Size.")
                pass

    # Reset Temp Lists
    tmpconns = []
    tempips = []
    templist = []

    print(f"\n[{colored('*', 'green')}]Vital Signs Process completed.\n")

    return
