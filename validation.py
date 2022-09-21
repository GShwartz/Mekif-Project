import pwinput
import sys


def validation():
    users = ['g', 'r', 'i']
    phrase = ' '
    tries = 0
    while True:
        user = input("Username: ")
        validate = pwinput.pwinput(prompt="Password: ", mask='*')
        if str(validate) == str(phrase) and user in users:
            tries = 0
            return

        else:
            tries += 1
            print(f"Wrong password! [{tries} of 3]")
            if int(tries) >= 3:
                print("Exiting.")
                sys.exit()
