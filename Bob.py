import socket
import time
import random
import settings
import pickle
from Email import email
from hashcash import verify_token
from hashcash import make_token


def makeNonce():
    a = random.getrandbits(64)
    b = '{0:64b}'.format(a)
    return b


class User:
    name = None
    id = None
    conn = None
    email = None
    wallet = None

    def __init__(self, id, givenname):
        self.id = id
        self.name = givenname
        self.email = givenname + "@email.com"

    def print(self):
        print(f" ID: {self.id}\n User Name: {self.name}\n Email: {self.email}\n")

    def setWallet(self, gwallet):
        self.wallet = gwallet


class Bob:
    def __init__(self):
        self.HEADERSIZE = settings.HEADERSIZE
        self.PORT = settings.PORT
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MSG = "!DISCONNECT"
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user = None

    def sendMessage(self, msg):
        msg = msg.encode(self.FORMAT)
        msglen = len(msg)
        sendlen = str(msglen).encode(self.FORMAT)
        sendlen += b' ' * (self.HEADERSIZE - len(sendlen))
        self.SOCKET.send(sendlen)
        self.SOCKET.send(msg)
        print(self.SOCKET.recv(2048).decode(self.FORMAT))

    def sendObject(self, sendObj=None):
        if sendObj is not None:
            msg = pickle.dumps(sendObj)
            msglen = len(msg)  # pickle
            sendlen = str(msglen).encode(self.FORMAT)
            sendlen += b' ' * (self.HEADERSIZE - len(sendlen))
            self.SOCKET.send(sendlen)
            self.SOCKET.send(msg)

    def startClient(self):
        print("Bob Started.")
        self.SOCKET.connect(self.ADDR)
        connection = self.SOCKET
        name = "bob"
        sendObj = {"type": "register", "name": name}
        self.sendObject(sendObj)
        msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
        if msglen:
            msglen = int(msglen)
            msg = connection.recv(msglen)  # pickle
            recvdobj = pickle.loads(msg)
            # print(recvdobj["type"])
            if recvdobj["type"] == "regdone":
                print("Registration Done")
                print("Your Details:")
                gname = recvdobj["name"]
                gid = recvdobj["id"]
                self.user = User(gid, gname)
                print(f" ID: {self.user.id}\n User Name: {self.user.name}\n Email: {self.user.email}")

        while True:
            # Get User Input
            print("\n\n[Bob] Options:")
            print("[Bob] Enter 'list' to see list of connected users")
            print("[Bob] Enter 'send' to send sample mail")
            print("[Bob] Enter 'disconnect' to disconnect")
            print("[Bob] Enter 'coins' to see amount each user has")

            message = input("\n>>>")
            # List of Users
            if message == "list":
                keyObj = {"type": "command", "command": "list"}
                self.sendObject(keyObj)
                msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
                if msglen:
                    msglen = int(msglen)
                    msg = connection.recv(msglen)
                    recvdobj = pickle.loads(msg)
                    if recvdobj["type"] == "cmdresponse":
                        enb = recvdobj["cmdresponse"]
                        print(enb)
            # To Disconnect
            if message == "disconnect":
                keyObj = {"type": "command", "command": "disconnect"}
                self.sendObject(keyObj)
                print("\n[Bob] Disconnected")
                break
            if message == "send":
                to = "alice@email.com"
                subject = "sample subject"
                body = "hi i am bob the muffin man and i like to make muffins"
                newemail = email()
                # newemail.setMail(self.user.email, to, subject, body)
                token = make_token(to + subject, 1)
                keyObj = {"type": "command", "command": "sendmail", "to": to, "subject": subject, "body": body,
                          "token": token}
                self.sendObject(keyObj)
            if message == "coins":
                keyObj = {"type": "command", "command": "coins"}
                self.sendObject(keyObj)
                msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
                if msglen:
                    msglen = int(msglen)
                    msg = connection.recv(msglen)
                    recvdobj = pickle.loads(msg)
                    if recvdobj["type"] == "coinoutput":
                        enb = recvdobj["output"]
                        print(enb)
        self.SOCKET.close()
