import logging
import tensorflow as tf
from model import Model
import cPickle
from utils import get_paths
from bot import BotApp
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

TOKEN = '266207277:AAFhKUqN_69eNka53ltHP1NT0CJVGXG3xo0'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN)

logger = logging.getLogger(__name__)


class BotApplication(object):
    def __init__(self, dispatcher, sess):

        model_path, config_path, vocab_path = get_paths('models/reddit')

        with open(config_path) as f:
            saved_args = cPickle.load(f)

        with open(vocab_path) as f:
            self.chars, self.vocab = cPickle.load(f)

        net = Model(saved_args, True)

        saver = tf.train.Saver(net.save_variables_list())
        saver.restore(sess, model_path)

        self.sess = sess
        self.net = net
        self.g = tf.get_default_graph()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                0: [MessageHandler(Filters.text, self.message, pass_user_data=True)],
            },
            fallbacks=[RegexHandler('^Done$', self.message, pass_user_data=True)]
        )
        dispatcher.add_handler(conv_handler)
        self.chat_rooms = {}

    def message(self, bot, update):
        with self.g.as_default():
            print(update.message.text)
            chat_app = self.chat_rooms[update.message.chat_id]
            msg = update.message.text
            ans = chat_app.chatbot(self.net, self.sess, self.chars, self.vocab, msg)
            self.response(bot, update, ans)

    def start(self, bot, update):
        with self.g.as_default():
            logger.debug("chat_id: {}".format(update.message.chat_id))
            self.chat_rooms[update.message.chat_id] = BotApp(self.net, self.sess)
            msg = "chat_id: {}".format(update.message.chat_id)
            self.response(bot, update, msg)

    def end(self, bot, update, args):
        self.chat_rooms.pop(update.message.chat_id)

    @staticmethod
    def response(bot, update, msg):
        bot.sendMessage(update.message.chat_id, text=msg)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

if __name__ == '__main__':
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    with tf.Session(config=config) as sess:
        tf.initialize_all_variables().run()
        updater = Updater(TOKEN)
        dp = updater.dispatcher
        bot_app = BotApplication(dp, sess)
        updater.start_polling()
        updater.idle()