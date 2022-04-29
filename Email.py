class email:
    def setMail(self, id ,fromx, tox, subjectx, bodyx):
        self.id = id
        self.fro = fromx
        self.to = tox
        self.subject = subjectx
        self.body = bodyx

    def setKey(self, key):
        self.key = key

    def setEncryptedBody(self, ebody):
        self.encryptedBody = ebody

    def setDecryptedBody(self, body):
        self.body = body

    def __init__(self):
        self.fro = None
        self.to = None
        self.subject = None
        self.body = None

    def print(self):
        print(f"\nFrom: {self.fro}")
        print(f"To: {self.to}")
        print(f"Subject: {self.subject}")
        print(f"Body: {self.body}")

    def setFromIndex(self, fi):
        self.fromindex = fi

    fromindex = None
    id = None
    fro = None
    to = None
    body = None
    subject = None
    key = None
    encryptedBody = None
