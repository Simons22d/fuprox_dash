import logging
import sys

# setting the logger
logging.basicConfig(filename="logger.txt",level=logging.DEBUG)


class User:
    username = "killer"

    def name(self,username):
        pass

    def getUser(self):
        logging.info("Just Leanring logging Code in Python")


User().getUser()
