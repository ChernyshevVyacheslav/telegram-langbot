import logging
import os
import re

import googletrans
from googletrans import Translator
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from dotenv import load_dotenv
import json
state=''
chat_id=''
bot=None
def save_json():
    json_data={}
    with open('state.json', 'r') as j:
            json_data = json.load(j)
    id=chat_id
    json_data[id]=[state[id][0], state[id][1]]
    with open('state.json', 'w') as file:
        json.dump(json_data, file)
    j.close()
    file.close
def new_dict(chat_id):
    global state
    chat_id=str(chat_id)
    state={chat_id:["reply", "en"]}
def load_state(chat_id):
    with open('state.json', 'r') as j:
            jsonstate = json.load(j)
            id=str(chat_id)
            if id in jsonstate:
                global state
                state={id: [jsonstate[id][0], jsonstate[id][1]]}
            else:
                new_dict(chat_id)
    j.close
def Default_delete(update, context):
    global state
    global chat_id
    chat_id=str(update.effective_chat.id)
    if state == '':
        load_state(update.effective_chat.id)
    state[chat_id][0]="delete"
    save_json()
def Default_reply(update, context):
    global state
    global chat_id
    chat_id=str(update.effective_chat.id)
    if state == '':
        load_state(update.effective_chat.id)
    state[chat_id][0]="reply"
    save_json()
def languages():
    text='English - en\nRussian - ru\nChinnesse - zh-cn\nHindi - hi\nFrench - fr\nSpanish - es\nGerman - de\nArabic - ar'
    return text
def Dest(update, context):
    global chat_id
    chat_id=str(update.effective_chat.id)
    if state == '':
        load_state(update.effective_chat.id)
    if context.args:
        state[chat_id][1]=''.join(context.args)
        save_json()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=languages())
def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def translate(update: Update, context: CallbackContext) -> None:
    if state == '':
        load_state(update.effective_chat.id)
    global chat_id
    chat_id=str(update.effective_chat.id)
    lang=state[chat_id][1]
    if has_cyrillic(update.message.text):
        user_name=update.message.from_user.username
        try:
            eng_message = translator.translate(update.message.text, dest=lang).text
            lang=state[chat_id][1]
            if (state[chat_id][0]=="reply"):
                update.message.reply_text(eng_message)
            else:
                bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
                context.bot.send_message(chat_id=update.effective_chat.id,  text=user_name+"\n\n"+eng_message)
        except Exception as e:
            logger.error(f"Exception during translate: {e}")


def main():
    load_dotenv()
    Token=os.getenv("TOKEN")
    updater = Updater(token=Token)
    global bot
    bot=Bot(Token)
    dispatcher = updater.dispatcher
    dest_handler = CommandHandler('dest', Dest)
    delete_handler = CommandHandler('default_delete', Default_delete)
    reply_handler = CommandHandler('default_reply', Default_reply)
    dispatcher.add_handler(delete_handler)
    dispatcher.add_handler(reply_handler)
    dispatcher.add_handler(dest_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, translate))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    translator = Translator()
    main()
