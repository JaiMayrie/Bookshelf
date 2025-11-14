from structure import Chatlog
from structure import User
from structure import FAQ
import time
class chatPage:

    def __init__(self, user):
        #Initialize values
        self.user = user
        self.chatbot = Chatbot(user)
        self.chatbot.loadchatlog(user)

    def getChatlog(self):
        #Returns chatlog for display when not responding.
        return self.chatbot.getChatlog()
    def speak(self, text):
        #reads text and returns nothing
        self.chatbot.read(text)
        return
    def respond(self): 
        #Responds to most recent text in chatlog
        return self.chatbot.respond()
    def summarize(self):
        #Summarizes the chatlog (simulated)
        return self.chatbot.summarize()
    pass


class Chatbot:
    chatlog = []
    user = None
    def __init__(self, user):
        self.chatlog = []
        self.user = user
    def loadchatlog(self, user):
        #Loads chatlog from user
        self.chatlog = user.sendChatLog()
    def respond(self):
        #Generates response based on most recent text in chatlog
        respText = ""
        text = self.chatlog[-1].text
        checkFAQResult = self.checkFAQ(text)
        if checkFAQResult:
            respText = checkFAQResult
        elif "help" in text.lower():
            respText = "Have you tried turning it off and on again?"
        else:
            respText = self.contactEmployee()
        newRespLog = Chatlog(respText, "Chatbot", time.time())
        self.chatlog.append(newRespLog)
        self.user.updateChatlog(newRespLog)
        return self.chatlog
    def contactEmployee():
        #Returns simulated employee contact response
        return "Employee has been contacted. Please wait for their response."
    def read(self, text):
        # Reads text and appends to chatlog
        startTime = time.time()
        newLog = Chatlog(text, self.user.username, startTime)
        self.chatlog.append(newLog)
        self.user.updateChatlog(newLog)
        return
    def checkFAQ(text):
        # Checks FAQ for answer to text
        return FAQ.sendAnswers(text)
    def summarize():
        # Simulated summary of chatlog.
        return "Many topics were discussed in this chat. Some big, some small. But I hope I have been helpful to you in the process."
    def getChatlog(self):
        return self.chatlog
    #Sends responses to chatPage
    pass
