import ScroogeServer
import Bob
import Alice
from ScroogeMain import *


def run():
    print("Enter 1 to Start ScroogeServer. Enter 2 to Start Bob. Enter 3 to start Alice")
    userinput = input()
    try:
        if int(userinput) != 1 and int(userinput) != 2 and int(userinput) != 3 and int(userinput) != 4:
            print(userinput)
            print("Invalid Input")
    except Exception as E:
        print("Invalid Input, Try Again")

    userinput = int(userinput)
    if userinput == 1:
        newServer = ScroogeServer.ScroogeServer()
        newServer.startServer()
    elif userinput == 3:
        newAlice = Alice.Alice()
        newAlice.startClient()
    elif userinput == 2:
        newBob = Bob.Bob()
        newBob.startClient()


def testscroogetest():
    scroogeInstance = Scrooge()
    user1id = "1"
    user2id = "2"
    scroogeInstance.users.append(scroogeUser(user1id))
    scroogeInstance.users.append(scroogeUser(user2id))
    outputX = ""

    user1 = None
    user2 = None

    for u in scroogeInstance.users:
        if u.id == "1":
            user1 = u
        else:
            user2 = u
    for i in range(10):
        newCoin = Coin()
        newCoin.sign_coin(scroogeInstance.private_key)
        newTrans = Transaction(
            None, [newCoin], scroogeInstance.public_key, user1.public_key
        )
        printUP = newTrans.details()
        outputX += printUP + "\n\n"
        # 8- Scrooge will create and sign the 10 initial scrooge coins for each user.
        newTrans.sign_tx(scroogeInstance.private_key)
        printUP = scroogeInstance.add_trans_to_temp_block(newTrans)
        outputX += printUP + "\n"
    # Once Scrooge accumulates 10 transaction, he can form a block and attach it to the blockchain.
    printUP = scroogeInstance.create_new_block()
    outputX += printUP + "\n"
    # print(output)

    for i in range(10):
        newCoin = Coin()
        newCoin.sign_coin(scroogeInstance.private_key)
        newTrans = Transaction(
            None, [newCoin], scroogeInstance.public_key, user2.public_key
        )
        printUP = newTrans.details()
        outputX += printUP + "\n\n"
        # 8- Scrooge will create and sign the 10 initial scrooge coins for each user.
        newTrans.sign_tx(scroogeInstance.private_key)
        printUP = scroogeInstance.add_trans_to_temp_block(newTrans)
        outputX += printUP + "\n"
    # Once Scrooge accumulates 10 transaction, he can form a block and attach it to the blockchain.
    printUP = scroogeInstance.create_new_block()
    outputX += printUP + "\n"
    # print(output)

    for ux in range(len(scroogeInstance.users)):
        userX = scroogeInstance.users[ux]
        printUP = (
                "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nUser "
                + str(ux + 1)
                + "\n\nUser's public key : "
                + get_string_key(userX.public_key)
                + "\nPEM format :\n"
                + userX.public_key.to_pem().decode("utf-8")
        )
        outputX += printUP + "\n"
        if not args.dontprint:
            print(printUP)
        printUP = (
                "Amount of coins this user has : "
                + str(len(userX.coins))
                + " coins.\n"
                + "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"
        )
        outputX += printUP + "\n"
        if not args.dontprint:
            print(printUP)

    senderIndex = 0
    recvrIndex = 1
    # A != B
    while senderIndex == recvrIndex:
        recvrIndex = randint(0, len(scroogeInstance.users) - 1)
    sendr = scroogeInstance.users[senderIndex]
    recvr = scroogeInstance.users[recvrIndex]
    if len(sendr.coins) > 0:
        money = 5
        for t in range(money):
            coinX = sendr.coins[t]
            newTrans = Transaction(
                coinX.last_trans, [coinX], sendr.public_key, recvr.public_key
            )
            # The transaction is signed by the private-key of the sender.
            newTrans.sign_tx(sendr.private_key)

            # Scrooge get notified by every transaction.
            # Scrooge verifies the signature before accumulating the transaction.
            # ❖ Upon detecting any transaction, scrooge verifies it by making sure the coin
            # really belongs to the owner and it has not been spent before.
            # 5- Scrooge verifies that the transaction belongs to the owner.
            # 6- Scrooge verifies that the transaction is not a Double spending.
            validTransCode = scroogeInstance.check_transaction(newTrans)

            # ❖ If verified, Scrooge adds the transaction to the blockchain. Double spending
            # can only happen before the transaction is published.
            if validTransCode == 0:
                # 0 -> valid transaction
                printUP = newTrans.details()
                outputX += printUP + "\n\n"
                if not args.dontprint:
                    print(printUP + "\n")
                printUP = scroogeInstance.add_trans_to_temp_block(newTrans)
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
            elif validTransCode == 1:
                # 1 -> invalid signature
                printUP = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\nInvalid transaction due to invalid " \
                          "signature! "
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
                printUP = newTrans.details()
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
                printUP = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
            elif validTransCode == 2:
                # 2 -> double spending
                printUP = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\nInvalid transaction due to double " \
                          "spending problem! "
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
                printUP = newTrans.details()
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)
                printUP = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                outputX += printUP + "\n"
                if not args.dontprint:
                    print(printUP)

        if len(scroogeInstance.temp_block) > 0:
            printUP = scroogeInstance.create_new_block()
            outputX += printUP + "\n"
            if not args.dontprint:
                print(printUP)

        for ux in range(len(scroogeInstance.users)):
            userX = scroogeInstance.users[ux]
            printUP = (
                    "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nUser "
                    + str(ux + 1)
                    + "\n\nUser's public key : "
                    + get_string_key(userX.public_key)
                    + "\nPEM format :\n"
                    + userX.public_key.to_pem().decode("utf-8")
            )
            outputX += printUP + "\n"
            if not args.dontprint:
                print(printUP)
            printUP = (
                    "Amount of coins this user has : "
                    + str(len(userX.coins))
                    + " coins.\n"
                    + "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"
            )
            outputX += printUP + "\n"
            if not args.dontprint:
                print(printUP)


if __name__ == '__main__':
    run()
    # testscroogetest()
