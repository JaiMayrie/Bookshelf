users=[]

class loginPage:
    @staticmethod
    def checkUserPass(username, password):
        from structure import users
        for u in users:
            if u.username == username and u.password == password:
                return True
        return False

    @staticmethod
    def login():
        print("\n LOGIN PAGE ")
        username = input("Enter username: ")
        password = input("Enter password: ")

        if loginPage.checkUserPass(username, password):
            print("Login successful!")
            for u in users:
                if u.username == username:
                    return u
        else:
            print("Incorrect username or password.\n")
            return None

    @staticmethod
    def resetPass():
        return resetPassPage.resetPassword()
    pass

class resetPassPage:
    @staticmethod
    def resetPassword():
        print("\n RESET PASSWORD PAGE ")

        username = input("Enter your username: ")

        for u in users:
            if u.username == username:
                new_pass = input("Enter your new password: ")
                u.password = new_pass
                print("Password reset successful!\n")
                return True

        print("User not found.\n")
        return False
    pass

class registrationPage:
    @staticmethod
    def register():
        
        print("\n REGISTRATION PAGE ")

        username = input("Enter new username: ")

        for u in users:
            if u.username == username:
                print("User already exists!\n")
                return False

        password = input("Enter new password: ")

        new_user = User(username, password)
        users.append(new_user)

        print("Registration successful!\n")
        return True
    pass

class employeePage:
    # Employee page representation with contact info property
    def __init__(self, employee="", notify=False, userPhoneNumber="", userEmail=""):
        self.employee = employee
        self.notify = notify
        self.userPhoneNumber = userPhoneNumber
        self.userEmail = userEmail
        self._userContactInfo = [self.userPhoneNumber, self.userEmail]

    @property
    def userContactInfo(self):
        """Return [phone, email] for the employee."""
        return list(self._userContactInfo)

    @userContactInfo.setter
    def userContactInfo(self, value):
        """Set the contact info; expects a list/tuple of two items: [phone, email].

        This also updates `userPhoneNumber` and `userEmail` fields.
        """
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("userContactInfo must be a list or tuple [phone, email]")
        self._userContactInfo = [value[0], value[1]]
        self.userPhoneNumber, self.userEmail = self._userContactInfo


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.chatlogs = []
    def updateChatlog(self, chatlog):
        #Appends a chatlog to the user's chatlogs
        self.chatlogs.append(chatlog)
    
    def sendChatlog(self):
        #Sends the user's chatlogs to other class.
        return self.chatlogs
    
    pass

class FAQ:
    """FAQ storage and lookup using a 2D list of [question, answer]."""
    def __init__(self, faqs=None):
        # Expect faqs to be an iterable of [question, answer] pairs.
        self.faqs = [list(pair) for pair in faqs] if faqs else []

    def compareQueryAnswer(self, query):
        """Return the index of a question that matches `query`, or -1 if none."""
        if not isinstance(query, str):
            return -1
        q_norm = query.strip().lower()
        for i, pair in enumerate(self.faqs):
            if not pair:
                continue
            stored_q = pair[0]
            if isinstance(stored_q, str) and stored_q.strip().lower() == q_norm:
                return i
        return -1

    def sendAnswer(self, query):
        """Return the answer corresponding to `query`, or `None` if not found."""
        idx = self.compareQueryAnswer(query)
        if idx != -1:
            return self.faqs[idx][1]
        return None

    def add_faq(self, question, answer):
        """Add a question/answer pair to the FAQ store."""
        self.faqs.append([question, answer])

class Chatlog:
    #information for use loading the chatbot
    text = ""
    identifier = ""
    DateTime = ""
    def __init__(self, text, identifier, DateTime):
        self.text = text
        self.identifier = identifier
        self.DateTime = DateTime
    def setText(self, text):
        self.text = text
        return
    def setIdentifier(self, identifier):
        self.identifier = identifier
        return
    def setDateTime(self, DateTime):
        self.DateTime = DateTime
        return
    def getText(self):
        return self.text
    def getIdentifier(self):
        return self.identifier
    def getDateTime(self):
        return self.DateTime
    
    pass