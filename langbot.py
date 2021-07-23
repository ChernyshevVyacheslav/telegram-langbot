from googletrans import Translator
import re
import logging
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, update
from state import State

languages=['en', 'ru', 'de', 'zh-cn', 'hi', 'fr', 'ar', 'es']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

translator = Translator()

class langbot:
    def __init__(self, token):
        self.state = State()
        self.updater = Updater(token=token)
        self.bot = Bot(token)
        dispatcher = self.updater.dispatcher
        dest_handler = CommandHandler('dest', self.dest)
        action_handler = CommandHandler('change_action', self.change_action)
        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(CallbackQueryHandler(self.button))
        dispatcher.add_handler(action_handler)
        dispatcher.add_handler(dest_handler)
        dispatcher.add_handler(help_handler)
        dispatcher.add_handler(MessageHandler((Filters.text | Filters.photo) & ~Filters.command, self.translate))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def is_photo(self, len):
        return bool(len)


    def has_cyrillic(self, text):
        return bool(re.search('[а-яА-Я]', text))
    
    def send_to_chat(self, message, translated_message, update: Update, context: CallbackContext):
        user_name = update.message.from_user.username
        if self.is_photo(len(message.photo)):
            context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=message.photo[0]["file_id"], caption=translated_message+'\n\n'+user_name)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=user_name + "\n\n" + translated_message)


    def translate(self, update: Update, context: CallbackContext):
        chat_id = self.state.check(chat_id = update.effective_chat.id)
        lang = self.state.get[chat_id][1]
        if self.is_photo(len(update.message.photo)):
            is_cyr = self.has_cyrillic(str(update.message.caption))
            mes = update.message.caption
        else:    
            is_cyr = self.has_cyrillic(update.message.text)
            mes = update.message.text
        if is_cyr:
            try:
                translated_message = translator.translate(mes, dest=lang).text
                if (self.state.get[chat_id][0] == "reply"):
                    update.message.reply_text(translated_message, quote=True)
                else:
                    self.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)
                    self.send_to_chat(message = update.message, translated_message = translated_message, update = update, context=context)
            except Exception as e:
                logger.error(f"Exception during translate: {e}")

    def change_action(self, update):
        chat_id = self.state.check(update.effective_chat.id)
        button_list = [
        [InlineKeyboardButton("Reply", callback_data='reply'), InlineKeyboardButton("Delete", callback_data='delete')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)
        update.message.reply_text('You can choose action with messages (delete initial message of reply it):', reply_markup=reply_markup)

    def help(self, update, context):
        text='**About bot**\n'\
            'This bot can automatically translate Russian-language messages in your chat.\n'\
            'To start working with it, add it to your chat.'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


    def dest(self, update, context):
        button_list = [
        [InlineKeyboardButton("English", callback_data='en'), InlineKeyboardButton("Russian", callback_data='ru')],
        [InlineKeyboardButton("German", callback_data='de'), InlineKeyboardButton("Chinnesse", callback_data='zh-cn')],
        [InlineKeyboardButton("Hindi", callback_data='hi'), InlineKeyboardButton("French", callback_data='fr')],
        [InlineKeyboardButton("Arabic", callback_data='ar'), InlineKeyboardButton("Spanish", callback_data='es')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)
        update.message.reply_text('You can choose destination language:', reply_markup=reply_markup)

    def button(self, update, context):
        chat_id = self.state.check(update.effective_chat.id)
        query = update.callback_query
        variant = query.data
        if variant in languages:
            self.state.set_dest(chat_id, variant)
            query.answer()
            query.edit_message_text(text=f"Choosen language : {variant}")
        else:
            self.state.set_action(chat_id, variant)
            query.answer()
            query.edit_message_text(text=f"Choosen action : {variant}")
        self.state.save(chat_id)