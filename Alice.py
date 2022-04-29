import socket
import random
import settings
import pickle
from Email import email
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

blocksize = 24


def getDecryptedMessagePad(msg, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    msg = cipher.decrypt(msg)
    msg = unpad(msg, blocksize)
    return msg


def getEncryptedMessagePad(msg, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    msg = cipher.encrypt(pad(msg, blocksize))
    return msg


def makeNonce():
    a = random.getrandbits(64)
    b = '{0:64b}'.format(a)
    return b


class Alice:
    def __init__(self):
        self.HEADERSIZE = settings.HEADERSIZE
        self.PORT = settings.PORT
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MSG = "!DISCONNECT"
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mails = []

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

    def listmails(self):
        print("\n-------------------------------------------------------")
        for item in self.mails:
            print(f"{item.fro} | {item.subject} | {item.id}")


    def startClient(self):
        print("Bob Started.")
        self.SOCKET.connect(self.ADDR)
        connection = self.SOCKET
        name = "alice"
        sendObj = {"type": "register", "name": name}
        self.sendObject(sendObj)
        msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
        if msglen:
            msglen = int(msglen)
            msg = connection.recv(msglen)  # pickle
            recvdobj = pickle.loads(msg)
            if recvdobj["type"] == "regdone":
                print("\nRegistration Done")

        while True:
            # self.listmails()
            msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
            if msglen:
                msglen = int(msglen)
                msg = connection.recv(msglen)
                recvdobj = pickle.loads(msg)

                # Receive Mail
                if recvdobj["type"] == "mailfrombob":
                    print("Mail Recieved From Bob!")
                    mailid = recvdobj["id"]
                    mailfrom = recvdobj["from"]
                    mailto = recvdobj["to"]
                    mailsubject = recvdobj["subject"]
                    mailbody = "<ENCRYPTED>"
                    newemail = email()
                    newemail.setMail(mailid, mailfrom, mailto, mailsubject, mailbody)
                    encrmailbody = recvdobj["encryptedBody"]
                    newemail.setEncryptedBody(encrmailbody)
                    self.mails.append(newemail)
                    newemail.print()

                    print("Do you want to read the Email? Y/N")
                    userinput = input("Enter Y/N:")
                    if userinput.lower() == "y":
                        print("Requesting Key...")
                        sendObj = {"type": "readmail", "id": mailid}
                        self.sendObject(sendObj)

                if recvdobj["type"] == "mailkey":
                    mailid = recvdobj["id"]
                    mailx = None
                    for item in self.mails:
                        if item.id == mailid:
                            mailx = item
                            break
                    key = recvdobj["key"]
                    print("Received Key, Decrypting")
                    decryptedBody = getDecryptedMessagePad(mailx.encryptedBody, key).decode(settings.FORMAT)
                    mailx.setDecryptedBody(decryptedBody)
                    mailx.print()





        self.SOCKET.close()
