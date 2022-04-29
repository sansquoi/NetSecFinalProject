import socket
import threading
import settings
import pickle
from hashcash import verify_token
from ScroogeMain import *
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Email import email

amount = 10
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


class mailUser:
    name = None
    id = None
    conn = None
    email = None
    wallet = None
    index = None
    coins = None

    def __init__(self, id, conn):
        self.id = id
        self.conn = conn
        self.coins = 0

    def setName(self, givenname):
        self.name = givenname
        self.email = givenname + "@email.com"

    def setWallet(self, gwallet):
        self.wallet = gwallet

    def print(self):
        print(f" ID: {self.id}\n User Name: {self.name}\n Email: {self.email}\n Connection: {self.conn}")

    def setIndex(self, ind):
        self.index = ind

    def updateCoins(self, c):
        self.coins = c


class ScroogeServer:
    def __init__(self):
        self.HEADERSIZE = settings.HEADERSIZE
        self.PORT = settings.PORT
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MSG = "!DISCONNECT"
        self.CONN = None
        self.CLIENTKEYS = dict()
        self.CONNECTIONS = dict()
        self.NUMBEROFUSERS = 0
        self.user1 = None
        self.user2 = None
        self.user3 = None
        self.user4 = None
        self.count = 0
        seed(23)
        self.scrooge = Scrooge()
        self.mails = []

    def sendToAlice(self, sendobj):
        sendconn = None
        for conn in self.CONNECTIONS:
            useriter = self.CONNECTIONS[conn]
            if useriter.name == "alice":
                sendconn = useriter.conn
                print(sendconn)
                print(useriter.id)
        self.sendObject(sendconn, sendobj)

    def sendToBob(self, sendobj):
        sendconn = None
        for conn in self.CONNECTIONS:
            useriter = self.CONNECTIONS[conn]
            if useriter.name == "bob":
                sendconn = useriter.conn
        self.sendObject(sendconn, sendobj)

    def sendObject(self, sendObj=None):
        if sendObj is not None:
            msg = pickle.dumps(sendObj)
            msglen = len(msg)  # pickle
            sendlen = str(msglen).encode(self.FORMAT)
            sendlen += b' ' * (self.HEADERSIZE - len(sendlen))
            self.CONN.send(sendlen)
            self.CONN.send(msg)

    def sendObject(self, connection, sendObj=None):
        if sendObj is not None:
            msg = pickle.dumps(sendObj)
            msglen = len(msg)  # pickle
            sendlen = str(msglen).encode(self.FORMAT)
            sendlen += b' ' * (self.HEADERSIZE - len(sendlen))
            connection.send(sendlen)
            connection.send(msg)

    def handleClient(self, connection, addr, ):
        mailid = 0
        print(f"[Scrooge]: User: {self.CONNECTIONS[connection.getpeername()].id} connected on {addr}")
        currentUser = self.CONNECTIONS[connection.getpeername()]
        connected = True
        newMessage = True
        while connected:
            msglen = connection.recv(self.HEADERSIZE).decode(self.FORMAT)
            if msglen:
                msglen = int(msglen)
                msg = connection.recv(msglen)  # pickle
                recvdobj = pickle.loads(msg)
                if newMessage:
                    if recvdobj["type"] == "register":
                        getname = recvdobj["name"]
                        currentUser.setName(getname)
                        currentUser.print()
                        sendobj = {"type": "regdone", "id": currentUser.id, "name": currentUser.name}
                        self.sendObject(connection, sendobj)
                    newMessage = False
                else:
                    if recvdobj["type"] == "command":
                        command = recvdobj["command"]
                        print(command)
                        if command == "list":
                            outputX = ""
                            for conn in self.CONNECTIONS:
                                useriter = self.CONNECTIONS[conn]
                                print(useriter.id)
                                outputX += "User " + str(useriter.id) + ": "
                                outputX += str(conn) + "\n"
                            print(outputX)
                            if len(self.CONNECTIONS) == 1:
                                sendobj = {"type": "cmdresponse", "cmdresponse": "[KDC] You are the only user"}
                                self.sendObject(connection, sendobj)
                            else:
                                print("output: ", outputX)
                                sendobj = {"type": "cmdresponse", "cmdresponse": outputX}
                                self.sendObject(connection, sendobj)
                        if command == "disconnect":
                            connected = False
                            print(f"\nUser {scrUser.id} disconnected.")
                            print(f"[SERVER]: Server is listening on {str(self.SERVER)}...")
                            self.CONNECTIONS[connection.getpeername()] = None
                        if command == "sendmail":
                            mailid += 1
                            mailfrom = currentUser.email
                            mailto = recvdobj["to"]
                            mailsubject = recvdobj["subject"]
                            mailbody = recvdobj["body"]
                            token = recvdobj["token"]
                            newemail = email()
                            newemail.setMail(mailid, mailfrom, mailto, mailsubject, mailbody)
                            self.mails.append(newemail)

                            if verify_token(mailto + mailsubject, token):
                                print("Hashcash Token Verified")

                            # Send Money
                            senderIndex = currentUser.index
                            recvrIndex = 0
                            sendr = self.scrooge.users[senderIndex]
                            recvr = self.scrooge.users[recvrIndex]

                            outputX = ""
                            for money in range(amount):
                                coinX = sendr.coins[money]
                                newTrans = Transaction(
                                    coinX.last_trans, [coinX], sendr.public_key, recvr.public_key
                                )
                                newTrans.sign_tx(sendr.private_key)
                                validTransCode = self.scrooge.check_transaction(newTrans)
                                if validTransCode == 0:
                                    # 0 -> valid transaction
                                    printUP = newTrans.details()
                                    outputX += printUP + "\n\n"
                                    printUP = self.scrooge.add_trans_to_temp_block(newTrans)
                                    outputX += printUP + "\n"
                                elif validTransCode == 1:
                                    # 1 -> invalid signature
                                    printUP = "\nInvalid transaction due to invalid " \
                                              "signature! "
                                    outputX += printUP + "\n"
                                    printUP = newTrans.details()
                                    outputX += printUP + "\n"
                                    outputX += printUP + "\n"
                                elif validTransCode == 2:
                                    # 2 -> double spending
                                    printUP = "\nInvalid transaction due to double " \
                                              "spending problem! "
                                    outputX += printUP + "\n"
                                    printUP = newTrans.details()
                                    outputX += printUP + "\n"
                                    outputX += printUP + "\n"

                            if len(self.scrooge.temp_block) > 0:
                                printUP = self.scrooge.create_new_block()
                                outputX += printUP + "\n"

                            # Get New Key
                            while True:
                                try:
                                    key = DES3.adjust_key_parity(get_random_bytes(16))
                                    break
                                except ValueError:
                                    pass

                            newemail.setKey(key)

                            encryptedBody = getEncryptedMessagePad(mailbody.encode(settings.FORMAT), key)
                            print(encryptedBody)

                            newemail.setEncryptedBody(encryptedBody)
                            newemail.setFromIndex(currentUser.index)

                            self.mails.append(newemail)

                            # decryptedBody = getDecryptedMessagePad(encryptedBody, key).decode(settings.FORMAT)
                            # print(decryptedBody)

                            sendobj = {"type": "mailfrombob", "id": mailid, "from": mailfrom, "to": mailto, "subject":
                                mailsubject, "encryptedBody": encryptedBody}
                            self.sendToAlice(sendobj)
                        if command == "coins":
                            outputX = ""
                            for index in range(len(self.scrooge.users)):
                                username = ""
                                if index == 0:
                                    username = "ScroogeServer"
                                elif index == 1:
                                    username = "Bob"
                                elif index == 2:
                                    username = "Alice"
                                scrUser = self.scrooge.users[index]
                                printUP = (
                                        f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n{username}: "
                                        + str(index + 1)
                                        + "\n\nUser's public key : "
                                        + get_string_key(scrUser.public_key)
                                        + "\nPEM format :\n"
                                        + scrUser.public_key.to_pem().decode("utf-8")
                                )
                                outputX += printUP + "\n"
                                printUP = (
                                        "Amount of coins this user has : "
                                        + str(len(scrUser.coins))
                                        + " coins.\n"
                                        + "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"
                                )
                                outputX += printUP + "\n"
                            sendobj = {"type": "coinoutput", "output": outputX}
                            self.sendToBob(sendobj)
                    if recvdobj["type"] == "readmail":
                        mailid = recvdobj["id"]
                        mailobject = None
                        for item in self.mails:
                            if item.id == mailid:
                                print(f"Mailkey Found: {item.key}")
                                mailobject = item
                                break
                        sendObj = {"type": "mailkey", "id": mailid, "key": mailobject.key}
                        self.sendToAlice(sendObj)

                        print(f"Refunding ScroogeCoins to User {mailobject.fro}...")

                        senderIndex = 0
                        recvrIndex = mailobject.fromindex

                        sendr = self.scrooge.users[senderIndex]
                        recvr = self.scrooge.users[recvrIndex]

                        outputX = ""
                        for money in range(amount):
                            coinX = sendr.coins[money]
                            newTrans = Transaction(
                                coinX.last_trans, [coinX], sendr.public_key, recvr.public_key
                            )
                            newTrans.sign_tx(sendr.private_key)
                            validTransCode = self.scrooge.check_transaction(newTrans)
                            if validTransCode == 0:
                                # 0 -> valid transaction
                                printUP = newTrans.details()
                                outputX += printUP + "\n\n"
                                printUP = self.scrooge.add_trans_to_temp_block(newTrans)
                                outputX += printUP + "\n"
                            elif validTransCode == 1:
                                # 1 -> invalid signature
                                printUP = "\nInvalid transaction due to invalid " \
                                          "signature! "
                                outputX += printUP + "\n"
                                printUP = newTrans.details()
                                outputX += printUP + "\n"
                                outputX += printUP + "\n"
                            elif validTransCode == 2:
                                # 2 -> double spending
                                printUP = "\nInvalid transaction due to double " \
                                          "spending problem! "
                                outputX += printUP + "\n"
                                printUP = newTrans.details()
                                outputX += printUP + "\n"
                                outputX += printUP + "\n"

                        if len(self.scrooge.temp_block) > 0:
                            printUP = self.scrooge.create_new_block()
                            outputX += printUP + "\n"
        connection.close()

    def startServer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.ADDR)
        server.listen()
        print("[Scrooge]: Server is listening on " + str(self.SERVER))
        self.scrooge.users.append(scroogeUser("0"))
        while True:
            conn, addr = server.accept()
            self.CONN = conn
            if conn not in self.CONNECTIONS.keys():
                self.NUMBEROFUSERS += 1
                currentUser = self.CONNECTIONS[conn.getpeername()] = mailUser(id=str(self.NUMBEROFUSERS).zfill(8),
                                                                              conn=conn)
                self.scrooge.users.append(scroogeUser(currentUser.id))
                currentUser.setIndex(len(self.scrooge.users) - 1)
                print(f"ScroogeIndex for User {currentUser.id}: {currentUser.index}")
                outputX = "\n"
                sUser = None
                for u in self.scrooge.users:
                    if u.id == currentUser.id:
                        sUser = u
                for index in range(100):
                    newCoin = Coin()
                    newCoin.sign_coin(self.scrooge.private_key)
                    newTrans = Transaction(
                        None, [newCoin], self.scrooge.public_key, sUser.public_key
                    )
                    printUP = newTrans.details()
                    outputX += printUP + "\n\n"
                    # 8- Scrooge will create and sign the 10 initial scrooge coins for each user.
                    newTrans.sign_tx(self.scrooge.private_key)
                    printUP = self.scrooge.add_trans_to_temp_block(newTrans)
                    outputX += printUP + "\n"
                # Once Scrooge accumulates 10 transaction, he can form a block and attach it to the blockchain.
                printUP = self.scrooge.create_new_block()
                outputX += printUP + "\n"
                # print(output)

            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
            print(f"[Scrooge]: Active Connections: {str(threading.active_count() - 1)}")
