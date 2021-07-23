import os
from dotenv import load_dotenv
from langbot import langbot
    


if __name__ == '__main__':
    load_dotenv()
    Token = os.getenv("TOKEN")
    langbot = langbot(Token)
    langbot.start()