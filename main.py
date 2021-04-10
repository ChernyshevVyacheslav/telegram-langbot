import logging
import os
import re

import googletrans
from googletrans import Translator
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import json

state = ''
bot = None

languages=['en', 'ru', 'de', 'zh-cn', 'hi', 'fr', 'ar', 'es']

def build_menu(buttons):
    menu = [buttons[i] for i in range(3)]
    return menu

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def check_state(chat_id):
    global state
    chat_id = str(chat_id)
    if state == '':
        state=load_state(chat_id)
    if chat_id not in state:
        state[chat_id]=["reply", "en"]
    return chat_id


def save_json(chat_id):
    json_data = {}
    with open('state.json', 'r') as j:
        json_data = json.load(j)
    if isinstance(json_data, str):
        json_data = dict(eval(json_data))
    json_data[chat_id] = [state[chat_id][0], state[chat_id][1]]
    with open('state.json', 'w') as file:
        json.dump(json_data, file)
    j.close()
    file.close()


def new_dict(chat_id):
    new_state = {chat_id: ["reply", "en"]}
    return new_state


def load_state(chat_id):
    if os.path.exists('state.json'):
        with open('state.json', 'r') as j:
            jsonstate = json.load(j)
            if chat_id in jsonstate:
                state_loaded = {chat_id: [jsonstate[chat_id][0], jsonstate[chat_id][1]]}
            else:
                state_loaded=new_dict(chat_id)
    else:
        state_loaded=new_dict(chat_id)
        with open('state.json', 'w+') as j:
            json.dump(state_loaded, j)
    j.close
    return state_loaded

def change_action(update, context):
    chat_id = check_state(update.effective_chat.id)
    button_list = [
    [InlineKeyboardButton("Reply", callback_data='reply'), InlineKeyboardButton("Delete", callback_data='delete')]
    ]
    reply_markup = InlineKeyboardMarkup(button_list)
    update.message.reply_text('You can choose action with messages (delete initial message of reply it):', reply_markup=reply_markup)

def Help(update, context):
    text='**About bot**\n'\
        'This bot can automatically translate Russian-language messages in your chat.\n'\
        'To start working with it, add it to your chat.'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def Dest(update, context):
    chat_id = check_state(update.effective_chat.id)
    button_list = [
    [InlineKeyboardButton("English", callback_data='en'), InlineKeyboardButton("Russian", callback_data='ru')],
    [InlineKeyboardButton("German", callback_data='de'), InlineKeyboardButton("Chinnesse", callback_data='zh-cn')],
    [InlineKeyboardButton("Hindi", callback_data='hi'), InlineKeyboardButton("French", callback_data='fr')],
    [InlineKeyboardButton("Arabic", callback_data='ar'), InlineKeyboardButton("Spanish", callback_data='es')]
]
    reply_markup = InlineKeyboardMarkup(button_list)
    update.message.reply_text('You can choose destination language:', reply_markup=reply_markup)

def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def button(update, context):
    chat_id = check_state(update.effective_chat.id)
    query = update.callback_query
    variant = query.data
    if variant in languages:
        state[chat_id][1]=variant
        query.answer()
        query.edit_message_text(text=f"Choosen language : {variant}")
    else:
        state[chat_id][0]=variant
        query.answer()
        query.edit_message_text(text=f"Choosen action : {variant}")
    save_json(chat_id)


def is_photo(len):
    if len !=0:
        return True
    else:
        return False

def translate(update: Update, context: CallbackContext) -> None:
    chat_id = check_state(update.effective_chat.id)
    lang = state[chat_id][1]
    is_ph=is_photo(len(update.message.photo))
    if is_ph:
        is_cyr=has_cyrillic(str(update.message.caption))
        mes=update.message.caption
    else:
        is_cyr=has_cyrillic(update.message.text)
        mes=update.message.text
    if is_cyr:
        user_name = update.message.from_user.username
        try:
            eng_message = translator.translate(mes, dest=lang).text
            if (state[chat_id][0] == "reply"):
                update.message.reply_text(eng_message)
            else:
                if is_ph:
                    bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
                    context.bot.sendPhoto(chat_id=chat_id, photo=update.message.photo[0]["file_id"], caption=eng_message+'\n\n'+user_name)
                else:
                    bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
                    context.bot.send_message(chat_id=update.effective_chat.id, text=user_name + "\n\n" + eng_message)
        except Exception as e:
            logger.error(f"Exception during translate: {e}")



def main():
    load_dotenv()
    Token = os.getenv("TOKEN")
    updater = Updater(token=Token)
    global bot
    global state
    bot = Bot(Token)
    dispatcher = updater.dispatcher
    dest_handler = CommandHandler('dest', Dest)
    action_handler = CommandHandler('change_action', change_action)
    help_handler = CommandHandler('help', Help)
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(action_handler)
    dispatcher.add_handler(dest_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(MessageHandler((Filters.text | Filters.photo) & ~Filters.command, translate))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    translator = Translator()
    main()
