# developed by Chris Troy

import socket
import threading
import json
from art import *
from colorama import *
import random
import hashlib
from sys import exit

init()


class Server:
    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.connected_count = 0
        self.connected_clients = set()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4 / TCP
        self.server.bind((self.host, self.port))
        self.ids = list(range(1, 500))
        random.shuffle(self.ids)
        self.event_lock = threading.Lock()
        self.listen_for_client()

    def listen_for_client(self):
        self.server.listen(5)
        # print('{}{} Hello World !!! {}{}'.format(fg(2), bg(8), attr(4), attr(0)))
        print("{}SERVER IS UP AND RUNNING...{}".format(Fore.BLUE, Fore.RESET))
        print("""CyberChat Server is active and listening on {}[{}]{} using port {}[{}]{}""".format(Fore.RED,
                                                                                                    self.host,
                                                                                                    Fore.RESET,
                                                                                                    Fore.RED, self.port,
                                                                                                    Fore.RESET))

        while True:
            try:
                conn, addr = self.server.accept()
                # lock event until connection added. Stops disconnect when adding to set
                with self.event_lock:
                    self.connected_clients.add(conn)
                    self.connected_count += 1
                    print("{}[!!!A client connected!!!]{}".format(Fore.YELLOW, Fore.RESET))
                # new thread to handle new client. Stops the blocking of other clients.
                new_client = threading.Thread(target=self.new_client_connection, args=(conn, addr))
                new_client.start()
            except socket.error as e:
                print("INTO 1")


    def new_client_connection(self, conn, add):

        discon = False
        users_id = self.ids.pop()
        while True:
            try:
                incoming_message = conn.recv(1024)
                if not incoming_message:
                    break
                else:
                    unpacked_message = json.loads(incoming_message.decode())

                    if unpacked_message['msg'] == "!quitserver":

                        # once client leaves deduct from connection count
                        self.connected_count -= 1
                        self.ids.append(users_id)
                        for client in self.connected_clients:
                            if client == conn:
                                with self.event_lock:
                                    self.connected_clients.remove(client)
                                    client.close()
                                    discon = True
                                    print("{}[!!!A Client Disconnected!!!]{}".format(Fore.CYAN, Fore.RESET))
                                break


                    else:
                        with self.event_lock:
                            # send message back to all connected clients
                            if not discon:
                                for client in self.connected_clients:
                                    try:
                                        msg_prep = json.dumps(
                                            {"uname": unpacked_message['uname'] + str(users_id),
                                             "msg": unpacked_message['msg']})
                                        client.send(msg_prep.encode())
                                    except ConnectionError as e:
                                        pass
                            else:
                                break
            except:
                continue


print(Fore.BLUE)
tprint("CyberChat", font="sub-sero")
tprint("Server", font="cybermedium")

print(Fore.RESET)
print(Fore.RED + "Developed by CyberChris" + Fore.RESET)

print(Fore.BLUE)
print("This is the server component of CyberChat. Your system will act as a server for clients to connect to.")
print(Fore.RESET)

print(
    "This works well for LAN chat, but can also be used for online chat purposes. {}WARNING: IF USING AT HOME:".format(
        Fore.RED))
print("Please ensure your network security is setup, and you use the DMZ. It would be better to use a VPS.")
print("A (Virtual Private Cloud) allows you to run applications on a virtual LAN. AWS, DigitalOcean, are")
print("""vendors offering this virtualization and security (Not-Promoting). They do cost money, but some do 
offer free tiers.""")

print("""{}Example:{} {}You can spin up an EC2 instance in AWS. Your private IPV4 will be what you insert here.
You must create a new security group and allow TCP connections on the port of your choice. Users must
connect to the public IPV4 address from the client which can be found on the EC2 section on your AWS 
dashboard.{}""".
      format(Fore.GREEN, Fore.RESET, Fore.LIGHTBLUE_EX, Fore.RESET))
fail_count = 0
while True:
    print(Fore.YELLOW)
    try:
        if fail_count > 3:
            print(Fore.RED)
            print("You seem to be having some issues, would you like to quit? ")
            print(Fore.RESET)
            conf = input("y or n: ")
            if conf.lower() == "y":
                exit()
            else:
                fail_count = 0
        print(Fore.YELLOW)
        host = input("Enter servers IP address: ")
        print(Fore.RESET)
        if len(host) <= 0:
            print(Fore.RED)
            print("You cannot have an empty address!")
            print(Fore.RESET)
            fail_count += 1
            continue

        a = hashlib.sha3_256(host.encode())
        con = a.hexdigest()
        if str(con) == str("3a6da0f8c2f47bb1356d9524260010a6751a2d61442759c2d6e699b2e0918790"):
            print(Fore.LIGHTRED_EX)
            print("""\


                                                          88                         
                                          ""                                                                                              
88,dPYba,,adPYba,   ,adPPYba, 8b,     ,d8 88  ,adPPYba,  ,adPPYba,   
88P'   "88"    "8a a8P_____88  `Y8, ,8P'  88 a8"     "" a8"     "8a  
88      88      88 8PP"""""""    )888(    88 8b         8b       d8  
88      88      88 "8b,   ,aa  ,d8" "8b,  88 "8a,   ,aa "8a,   ,a8"  
88      88      88  `"Ybbd8"' 8P'     `Y8 88  `"Ybbd8"'  `"YbbdP"' 


                 ******       ******
               **********   **********
             ************* *************
            *****************************
            *****************************
            *****************************
             ***************************
               ***********************
                 *******************
                   ***************
                     ***********
                       *******
                         ***
                          *
          

            """)
            continue
    except:
        exit()

    try:
        print(Fore.YELLOW)
        port = int(input("Enter servers port number: "))
        print(Fore.RESET)
        print("\n")
        if port > 65535:
            print(Fore.RED)
            print("Port numbers only go up to 65,535. Please choose carefully")
            print(Fore.RESET)
            continue
    except ValueError:
        print(Fore.RED)
        print("You cannot have an empty port number!")
        print(Fore.RESET)
        continue

    print("You have chosen IP: {} [{}] {} and PORT {} [{}] {}. Are these the correct settings? ".format(Fore.RED, host,
                                                                                                        Fore.RESET,
                                                                                                        Fore.RED, port,
                                                                                                        Fore.RESET))
    print(Fore.RED)
    confirm = input("y or n: ")
    if confirm.lower() == "y":
        break
    else:
        continue

print(Fore.RESET)

Server(host, port)

