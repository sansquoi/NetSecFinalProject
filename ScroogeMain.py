from argparse import ArgumentParser
from hashlib import sha256
from random import randint, seed

from ecdsa import SigningKey, VerifyingKey
from keyboard import is_pressed

parser = ArgumentParser(description="ScroogeCoin")
parser.add_argument(
    "--name", "-n", type=str, default="output"
)
parser.add_argument(
    "--dontprint",
    "-d",
    dest="dontprint",
    action="store_true",
)
parser.add_argument(
    "--initial",
    "-i",
    dest="initial",
    action="store_true",
)
args = parser.parse_args()


def generate_keys():
    private_key = SigningKey.generate()
    public_key = private_key.verifying_key
    return private_key, public_key


def sign(private_key, message):
    message = bytes(message, encoding="ascii")
    signature = private_key.sign(message, hashfunc=sha256)
    return signature


def verify_signature(public_key, message, signature):
    message = bytes(message, encoding="ascii")
    try:
        return public_key.verify(signature, message, hashfunc=sha256)
    except:
        return False


def get_string_key(key):
    return str(key.to_string().hex())


class Coin:
    coin_counter = 0

    def __init__(self):
        # 1- Each coin should have a coin ID.
        self.ID = sha256(
            bytes(("coin" + str(Coin.coin_counter)), encoding="ascii")
        ).hexdigest()

        Coin.coin_counter += 1

    def sign_coin(self, private_key):
        self.signature = sign(private_key, str(self.__hash__()))

    def set_coin_last_trans(self, trans_hash, trans_block):
        self.last_trans = Hash_Pointer(trans_hash, trans_block)


class scroogeUser:
    def __init__(self, id):
        self.id = id
        self.private_key, self.public_key = generate_keys()
        self.coins = []

    def confirm_transaction(self, coins, consume):
        for coin in coins:
            if consume:
                self.coins.remove(coin)
            else:
                self.coins.append(coin)


class Transaction:
    trans_counter = 0

    def __init__(self, prev_hash, coins, sender_puk, receiver_puk):
        self.transcount = Transaction.trans_counter
        Transaction.trans_counter += 1
        self.prev_hash = prev_hash
        self.coins = coins
        self.sender_puk = sender_puk
        self.receiver_puk = receiver_puk
        self.hash = sha256(
            bytes(
                (
                        "tx"
                        + str(self.transcount)
                        + str(self.coins)
                        + str(sender_puk)
                        + str(receiver_puk)
                ),
                encoding="ascii",
            )
        ).hexdigest()
        self.ID = self.hash

    def sign_tx(self, private_key):
        self.signature = sign(private_key, str(self.hash))

    def set_tx_block(self, pointer):
        self.block = pointer

    def details(self):
        return (
                "------------------------------------------------"
                + "\n"
                + "Trans ID\t: "
                + str(self.ID)
                + "\n"
                + (
                    ("Prev Trans\t: " + str(self.prev_hash.thash) + "\n")
                    if self.prev_hash
                    else ""
                )
                + (
                    ("Sender\t\t: " + get_string_key(self.sender_puk))
                    if self.prev_hash
                    else "Sender\t\t: Scrooge *COINBASE (Newly Generated Coins)*"
                )
                + "\n"
                + "Receiver\t: "
                + get_string_key(self.receiver_puk)
                + "\n"
                + "Amount\t\t: "
                + str(len(self.coins))
                + " SC"
                + "\n"
                + "CoinsIDs\t: [ "
                + str(self.coins[0].ID)
                + " ]\n"
                + "------------------------------------------------"
        )


class Hash_Pointer:
    def __init__(self, thash, pointer):
        self.thash = thash
        self.pointer = pointer

    def sign_hp(self, private_key):
        self.signature = sign(private_key, str(self.__hash__()))


class Block:
    block_counter = 0

    def __init__(self, transactions, prev_hash):
        self.blockcount = Block.block_counter
        Block.block_counter += 1
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = sha256(
            bytes(
                (str(self.blockcount) + str(self.transactions) + str(prev_hash)),
                encoding="ascii",
            )
        ).hexdigest()
        self.ID = self.hash

    def sign_bk(self, private_key):
        self.signature = sign(private_key, str(self.hash))


class Scrooge:

    def __init__(self):
        self.private_key, self.public_key = generate_keys()
        self.ledger = []
        self.block_chain = self.ledger
        self.final_hp = None
        self.temp_block = []
        self.users = []

    def sign_final_hp(self):
        self.final_hp.sign_hp(self.private_key)

    def create_new_block(self):
        new_block = Block(self.temp_block, self.final_hp)
        self.temp_block = []
        new_block.sign_bk(self.private_key)
        self.ledger.append(new_block)
        self.final_hp = Hash_Pointer(new_block.hash, (len(self.ledger) - 1))
        # The final hash pointer is signed by Scrooge.
        # 4- The final hash pointer should be signed by Scrooge.
        self.sign_final_hp()
        # 9- A user cannot confirm a transaction unless it is published on the blockchain.
        self.confirm_new_transactions()
        outret = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        outret += "A new block appended !\n"
        outret += "The current blockchain :\n"
        for block in self.ledger:
            tids = ""
            for tr in block.transactions:
                tids += str(tr.ID) + ", "
            outret += (
                    "<--"
                    + (
                        ("(Previous block : " + str(block.prev_hash.thash))
                        if block.prev_hash
                        else "("
                    )
                    + " BlockID : "
                    + str(block.ID)
                    + " || Block Transactions' IDs : [ "
                    + tids[:-2]
                    + " ] )\n"
            )
        outret += (
                "<-- ( Final H() : "
                + str(self.final_hp.thash)
                + " , signature : "
                + str(self.final_hp.signature.hex())
                + "\n"
        )
        outret += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        return outret

    def confirm_new_transactions(self):
        senders = []
        receivers = []
        coins = []
        for trans in self.ledger[-1].transactions:
            trans.set_tx_block(len(self.ledger) - 1)
            senders.append(trans.sender_puk)
            receivers.append(trans.receiver_puk)
            coins.append((trans.coins, trans.hash, trans.block))
        for user in self.users:
            if user.public_key in senders:
                for i in range(len(senders)):
                    if user.public_key == senders[i]:
                        user.confirm_transaction(coins[i][0], True)
            if user.public_key in receivers:
                for i in range(len(receivers)):
                    if user.public_key == receivers[i]:
                        coins[i][0][0].set_coin_last_trans(coins[i][1], coins[i][2])
                        user.confirm_transaction(coins[i][0], False)

    def check_transaction(self, transaction):
        valid_transaction = verify_signature(
            transaction.sender_puk, str(transaction.hash), transaction.signature
        )
        if not valid_transaction:
            return 1
        for user in self.users:
            if transaction.sender_puk == user.public_key:
                _sender = user
                break
        for coin in transaction.coins:
            if not (coin in _sender.coins):
                return 2
        for trans in self.temp_block:
            if trans.prev_hash == transaction.prev_hash:
                return 2

        return 0

    def add_trans_to_temp_block(self, new_trans):
        self.temp_block.append(new_trans)
        # ❖ Scoorge should print the block under construction for each new transaction
        # added (include the transaction details)
        outret2 = "################################################\n"
        outret2 += "A new transaction added !\n"
        outret2 += "Block under construction :\n"
        for i in range(len(self.temp_block)):
            outret2 += "Transaction_" + str(i) + " : " + self.temp_block[i].ID + "\n"
        outret2 += "################################################\n"
        return outret2
