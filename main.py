import telebot;
import random
import logging
import sys
import signal
import argparse
import sched
import time
import gettext
import time

YES=0

parser = argparse.ArgumentParser("Thursday telegram bot")
parser.add_argument("--token",
                    dest="token",
                    help="Your telegram bot token.",
                    type=str)
parser.add_argument("--quota",
                    dest="quota",
                    help="Minimum amount of persons willing to participate.",
                    type=int)
parser.add_argument("--chat_id",
                    dest="chat_id",
                    help="Chat id to serve.",
                    type=int)
parser.add_argument("--active-for",
                    dest="active_for",
                    help="Time in second a poll will be active.",
                    default=86400,
                    type=int)
parser.add_argument("--roll-dice",
                    action=argparse.BooleanOptionalAction,
                    dest="is_roll_dice",
                    help="Ask to roll dices, when selecting a person to book a place.",
                    default=True,
                    type=bool)
parser.add_argument("--locale",
                    dest="locale",
                    help="Locale is used for bot language.",
                    default="en",
                    type=str)


args = parser.parse_args()
bot = telebot.TeleBot(args.token);
s = sched.scheduler(time.time, time.sleep)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('thursday')

poll_id=0
user_answer_map = {}

en_i18n = gettext.translation('msg', 'locale', languages=[args.locale])
en_i18n.install()

def create_poll(chat_id):
    global poll_id
    global user_answer_map
    log.debug("creating poll")
    user_answer_map = {}
    poll_msg = bot.send_poll(chat_id = chat_id,
                  question = _("Coming?"),
                  is_anonymous = False,
                  options = [_("Yes"), _("View results")])
    poll_id = poll_msg.poll.id
    bot.pin_chat_message(chat_id = chat_id, message_id = poll_msg.id)

def process_poll(chat_id, should_assign):
    yes_count = 0
    yes_answers = {}
    for k, v in user_answer_map.items():
        log.debug("v: {}\n".format(v))
        if (len(v) > 0):
            if (v[0] == YES):
                yes_count += 1
                yes_answers[telebot.types.User.de_json(k)] = v
                log.debug('{} said yes'.format(telebot.types.User.de_json(k).first_name))

    if (len(yes_answers) >= args.quota):
        bot.send_message(chat_id=chat_id,
                         text = _("Event will take place! We're expecting {} participants")
                         .format(yes_count)
                         )
        if should_assign:
            assignPerson(chat_id, yes_answers)
    else:
        bot.send_message(chat_id=chat_id,
                         text = "{} - ".format(len(yes_answers)) + _("too few people, cancel for today"))

def play_dice(chat_id, users):
    min = 100

    for user in users:
        user_id = user.id
        user_name = user.first_name
        bot.send_message(chat_id=chat_id,
                         text="{}:".format(user_name),
                         parse_mode='MarkdownV2')
        dice = bot.send_dice(chat_id=chat_id, emoji="🎲").dice

        if min == dice.value:
            losers.append(user)

        if min > dice.value:
            min = dice.value
            losers = []
            losers.append(user)

    if len(losers) > 1:
        return play_dice(chat_id, losers)
    else:
        return losers[0]


def assignPerson(chat_id, yes_answers):
    users = list(yes_answers.keys())
    if args.is_roll_dice:
        user = play_dice(chat_id, users)
    else:
        random.seed()
        user_index = random.randrange(len(users))
        user = users[user_index]

    send_assigned_user_msg(chat_id, user)

def send_assigned_user_msg(chat_id, user):
    user_name = user.first_name
    user_id = user.id
    bot.send_message(chat_id=chat_id,
                     text="[{}](tg://user?id={}), ".format(user_name, user_id) + _("I don't know how to organize cocial events, could you please, help me?"),
                     parse_mode='MarkdownV2')

@bot.message_handler(commands=['2beer'])
def handle_replies(p):
    log.debug("got 2beer cmd")
    if poll_id == 0:
        create_poll(args.chat_id)
    else:
        process_poll(args.chat_id, False)

@bot.poll_answer_handler()
def handle_poll_answer(p):
    log.debug("got poll answer")
    if p.poll_id == poll_id:
        user_answer_map[p.user.to_json()] = p.option_ids
        log.debug("saving {} answer".format(p.user.id))

def process_start_sighandler(num, fr):
    user_answer_map = {}
    poll_id = 0
    create_poll(args.chat_id)

def process_poll_sighandler(num, fr):
    process_poll(args.chat_id, True)

def process_poll_sigcleanup(num, fr):
    user_answer_map = {}
    poll_id = 0

signal.signal(signal.SIGUSR2, process_poll_sighandler)
signal.signal(signal.SIGUSR1, process_start_sighandler)

bot.infinity_polling()

