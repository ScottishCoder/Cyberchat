# Developed by Chris Troy

import socket
import threading
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from art import *
from colorama import *
from sys import exit

init()  # init colorama for terminal color support


class Encryptor:

    def __init__(self, password):
        # User public key password. All clients need the same password for decryption
        if len(password) > 16:
            print(Fore.RED)
            print("Password must have a length of 16!")
            print(Fore.RESET)
        else:
            self.key = password.encode()
            # used to identify the encrypted message
            self.header = get_random_bytes(16)

    def encrypt(self, message):
        try:
            cipher = AES.new(self.key, AES.MODE_EAX)
            cipher.update(self.header)
            ciphertext, tag = cipher.encrypt_and_digest(message.encode())
            auth_structure = [b64encode(x).decode('utf-8') for x in (cipher.nonce, self.header, ciphertext, tag)]
            eo = json.dumps({"Nonce": auth_structure[0], "Header": auth_structure[1], "Ciphertext": auth_structure[2],
                             "Tag": auth_structure[3]})
            return eo
        except AttributeError as f:
            print(Fore.RED)
            print("Your password doesn't have a length ot 16, so encryption will not work!")
            print(Fore.RESET)
            print(f)

    def decrypt(self, encobject_in):
        try:
            encobject_out = json.loads(encobject_in)
            auth_attributes = ['Nonce', 'Header', 'Ciphertext', 'Tag']
            auth_structure_decoded = {k: b64decode(encobject_out[k]) for k in auth_attributes}
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=auth_structure_decoded['Nonce'])
            cipher.update(auth_structure_decoded['Header'])
            plaintext = cipher.decrypt_and_verify(auth_structure_decoded['Ciphertext'], auth_structure_decoded['Tag'])
            return plaintext.decode()
        except ValueError as KeyError:
            return "[ You don't share the secret to view this users message ]"


class Client:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.event_lock = threading.Lock()

        while True:
            print(Fore.YELLOW)
            self.username = input("What do you want your username to be. 4-15 chars: ")
            print(Fore.RESET)
            if len(self.username) <= 2 or len(self.username) >= 15:
                print(Fore.RED)
                print("Minimum username 4 chars. Maximum username: 15 chars")
                print(Fore.RESET)
                continue
            else:
                break

        self.enc = Encryptor(self.security_setup())
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4 / TCP
        self.__connect_to_server()


    def security_setup(self):

        while True:
            print("{}Please follow these instructions carefully:{}".format(Fore.RED, Fore.RESET))
            print("{}This client and the server utilise AES encryption and MAC for validation{}".
                  format(Fore.LIGHTMAGENTA_EX,Fore.RESET))
            print("{}Provide the shared secret below. It must be a {}{}fixed size password with a length of 16 "
                  "characters.{}".format(Fore.LIGHTMAGENTA_EX, Fore.RESET, Fore.RED, Fore.RESET))
            print(Fore.LIGHTMAGENTA_EX)
            print("Please input the shared secret below:")
            print(Fore.RESET)
            print(Fore.RED)
            shared_secret = input(": ")
            print(Fore.RESET)
            if len(shared_secret) != 16:
                print(Fore.RED)
                print("\tThis isn't 16 in length! Please re-do it")
                if input("\tProceed: y or n: ").lower() == "y":
                    continue
                else:
                    exit()
                print(Fore.RESET)
            else:
                print("{}==========[[[[Shared Secret has been set]]]]=========={}".format(Fore.GREEN, Fore.RESET))

            print("""
                   Commands: {}!quitserver{} (Exits the server properly)
                          
                   """.format(Fore.YELLOW, Fore.RESET, Fore.YELLOW, Fore.RESET))

            return shared_secret

    def __connect_to_server(self):

        try:
            self.client.settimeout(3)
            self.client.connect((self.host, self.port))
            self.client.settimeout(None)
            print("{}You have successfully connected to the CyberChat Server{}".format(Fore.BLUE, Fore.RESET))
            print("{}Start chatting below. You can type and hit enter to send a message to everyone connected!{}".
                  format(Fore.YELLOW, Fore.RESET))


            send_message_thread = threading.Thread(target=self.send_message, args=())
            send_message_thread.start()


            while True:

                try:

                    incoming_msgs = self.client.recv(1024)

                    if not incoming_msgs:
                        break

                    else:
                        unpacked_message = json.loads(incoming_msgs.decode())

                        if "Ciphertext" in unpacked_message['msg']:

                            print("{}{} said:{} {}{}{}".format(Fore.LIGHTCYAN_EX,unpacked_message['uname'],Fore.RESET,
                                                               Fore.LIGHTMAGENTA_EX,
                                                               self.enc.decrypt(unpacked_message['msg']), Fore.RESET))

                        else:
                            if unpacked_message['msg'] == "!quitserver":
                                break
                except:
                    pass

        except socket.error as e:
            print(e)

    # use a new thread to handle this!
    def send_message(self):

        while True:

        # encode for transmission

            msg = input("")
            msg = self.emoticon(msg)

            if msg == "!quitserver":

                msg_prep = json.dumps({"uname":self.username, "msg":msg})

                self.client.send(msg_prep.encode())
                break
                # exit()

            elif len(msg) <= 0 or len(msg) >= 150:

                print(Fore.RED)
                print("[[[ WARNING! EMPTY OR EXCEEDED CHARACTER LIMIT ]]]")
                print(Fore.RESET)

            else:

                new_msg = self.enc.encrypt(msg)
                msg_prep = json.dumps({"uname": self.username, "msg": new_msg})
                assert self.client.send(msg_prep.encode())


    def emoticon(self, msg):

        x = msg.replace(":)", "(^V^)").replace(":(", "(┬_┬)").replace(":|", "(-_-)").replace(":evil:","ψ(^w´)ψ").\
            replace(":facepalm:","(－‸\)").replace(":gimmie:","(/3°o°)/3").replace(":love:","(^-^)<3").\
            replace(":omg:","(`o`)").\
            replace(":shrug:","\_(0_o)_/").replace(":tired:","(x_x)zzz").\
            replace(";)","(^_-)").replace(":s","(?_?)").replace(":cute:","OwO").replace(":D","(＾v＾)").\
            replace(":music:","d[-_-]b").replace(":cheers:", "(^_^)=b[][]d=(^_^)").\
            replace(":angry:","└(>o< )┘").replace(":o", "(0o0)").replace(":creep:","┬┴┬┴┤° -°) ├┬┴┬┴").\
            replace(":bow:","__|```|O").replace(":finger:",".!.(--_--).!.")

        return x


print(Fore.LIGHTMAGENTA_EX)
tprint("CyberChat", font="sub-sero")
tprint("Client", font="cybermedium")
print(Fore.RESET)
print(Fore.RED)
print("Developed by CyberChris")
print(Fore.RESET)
print(Fore.LIGHTMAGENTA_EX)
print("This is the client component of CyberChat. You have to provide the IP address of the CyberChat Server.")
print("The port number is also required. You must use the same port number the server is listening on.")
print(Fore.RESET)
print(Fore.YELLOW)

fail_count = 0
while True:
    if fail_count > 3:

        print(Fore.RED)
        print("You seem to be having a little bit of an issue. Do you want to quit? ")
        print(Fore.RESET)

        conf = input("y or n: ")
        if conf.lower() == "y":
            exit()
        else:
            fail_count = 0
    print(Fore.YELLOW)
    try:
        host = input("Enter address to connect to: ")
        if len(host) <= 0:
            print("You cannot have an empty address!")
            fail_count += 1
            continue
        else:
            pass
    except:
        pass
    try:
        port = int(input("Enter port number: "))
        if port > 65555 or port < 0:
            print(Fore.Red)
            print("Enter the correct port number")
            print(Fore.RESET)
        else:
            break
    except ValueError:
        print(Fore.RED)
        print("You cannot have an empty port number")
        print(Fore.RESET)
        fail_count += 1
        continue



print(Fore.RESET)

Client(host, port)





