# coding: utf-8
"""
created by artemkorkhov at 2017/07/26
"""

import argparse
import json
import os
import requests
import random
import time
import pprint

import re

import logging
import tensorflow as tf
from model import Model
from utils import get_paths
from bot import BotApp

try:
    import cPickle as pickle
except ImportError:
    import pickle


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN)

logger = logging.getLogger(__name__)


NIPS_URL = 'https://ipavlov.mipt.ru/nipsrouter-alt/'
NIPS_ID = '1686e6ee-71e2-11e7-bdb8-5f3547bb4fc8'

TELEGRAM_URL = 'https://api.telegram.org/bot'
TELEGRAM_ID = '424428369:AAF9kDFicflhVsErIJMjn0N7nrhMHkzYIPU'


class BotApplication(object):
    def __init__(self, sess, bot_url):

        self.bot_url = bot_url

        model_path, config_path, vocab_path = get_paths('bot/reddit')

        with open(config_path) as f:
            saved_args = pickle.load(f)

        with open(vocab_path) as f:
            self.chars, self.vocab = pickle.load(f)

        net = Model(saved_args, True)

        saver = tf.train.Saver(net.save_variables_list())
        saver.restore(sess, model_path)

        self.sess = sess
        self.net = net
        self.g = tf.get_default_graph()

        self.chat_rooms = {}

    def handle(self, msg):
        """ Handles new incoming message """
        if msg is None:
            logger.error("Incoming msg is None!")
            return
        if not msg:
            logger.error("Incoming msg is probably(?) incorrect: {}!".format(msg))

        chat_id = msg.get('message', {}).get('chat', {}).get('id')
        msg_id = msg.get('message', {}).get('message_id')
        if chat_id is None or msg_id is None:
            logger.error(
                "Incoming message doesn't contain chat_id or msg_id! msg: {}".format(msg)
            )
            return

        text = msg.get("message", {}).get("text")
        if text is None:
            logger.error("Msg without text!")
            return

        if chat_id not in self.chat_rooms:
            if not text.startswith("/start"):
                logger.info("Invalid start attempt")
                return
            else:
                self.chat_rooms[chat_id] = BotApp(self.net, self.sess)
                text = text.replace("/start ", "")
                time.sleep(random.choice(range(10)))

        if text.startswith("/end"):
            self.chat_rooms.pop(chat_id)
            logger.info("End of chat {} with msg: {}".format(chat_id, text))
            return self.compose_response(chat_id=chat_id, response=text)
        else:
            app = self.chat_rooms[chat_id]
            with self.g.as_default():
                response = app.chatbot(self.net, self.sess, self.chars, self.vocab, text)
                response = clean_response(response)
                logger.info("bot response: ".format(response))

            return self.compose_response(chat_id=chat_id, response=response)

    def compose_response(self, chat_id, response):
        """ Composes chatbot response """
        message = {
            'chat_id': chat_id
        }

        data = {}
        if response == '':
            logger.info("\tDecide to do not respond and wait for new message")
            return
        elif response == '/end':
            logger.info("\tDecide to finish chat %s" % chat_id)
            data['text'] = '/end'
            data['evaluation'] = {
                'quality': 0,
                'breadth': 0,
                'engagement': 0
            }
        else:
            logger.info("\tDecide to respond with text: %s" % response)
            data = {
                'text': response,
                'evaluation': 0
            }

        message['text'] = json.dumps(data)
        return message

    def send_msg(self, msg):
        """ Sends msg back to ConvAI router """
        if msg is None:
            logger.error("trying to send an empty msg, abort!")
            return

        response = requests.post(
            os.path.join(self.bot_url, 'sendMessage'),
            json=msg,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            logger.error("CONVAI RESPONSE ERROR: {}!".format(response.text))
            response.raise_for_status()


def clean_response(response):
    """ Cleans response from possible shit """

    response = re.sub(">", " ", response)
    response = re.sub("\s+", " ", response)
    response = response.strip()

    response.replace(
        "faggot",
        random.choice(["kiddo", "evaluator", "bot", "fag", "dude", "robot", "AI"])
    )
    response.replace(
        "asshole",
        random.choice(["nyasha", "arsehole", "hacker", "kek", "robot", "AI"])
    )

    response.replace(
        "fuck",
        random.choice(["kek", "Alisa"])
    )

    response.replace(
        "dick",
        random.choice(["robot", "Elisa"])
    )

    return response


def main(test=False):
    if test:
        bot_url = TELEGRAM_URL + TELEGRAM_ID
    else:
        bot_url = os.path.join(NIPS_URL, NIPS_ID)

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    with tf.Session(config=config) as sess:
        tf.initialize_all_variables().run()
        bot_app = BotApplication(sess=sess, bot_url=bot_url)

        while True:
            try:
                time.sleep(1)
                res = requests.get(os.path.join(bot_url, 'getUpdates'))
                if res.status_code != 200:
                    res.raise_for_status()

                data = res.json()

                if test:
                    messages = data["result"]
                else:
                    messages = data

                for m in messages:
                    response = bot_app.handle(msg=m)
                    if response is not None:
                        bot_app.send_msg(msg=response)

            except Exception as e:
                logger.exception("Error: ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', default=False, type=bool)
    parser.add_argument('-l', '--log', default='WARN', type=str)

    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log))
    main(test=args.test)
