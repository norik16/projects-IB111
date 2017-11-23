#!/usr/bin/python
# -*- coding: UTF-8 -*-

from html.parser import HTMLParser
import time
import locale
import emoji
import operator
import numpy as np
import matplotlib.pyplot as plt
import re

locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
fb_home = '../../2/facebook-ronaldluc'
me = 'Ronald Luc'

sm_minimum = 100


# plt.rc('font', family='Arial')


class ConversationListHTMLParser(HTMLParser):
    __indent = 0
    __last_tag = ''
    __conversations = []
    __to_set = ''

    def handle_starttag(self, tag, attrs):
        print('\t' * self.__indent, tag, attrs)
        self.__indent += 1

        if self.__last_tag == 'p' and tag == 'a':
            self.__to_set = ('conversation', attrs[0][1])
        else:
            self.__to_set = ('nothing', None)

        self.__last_tag = tag

    def handle_endtag(self, tag):
        self.__indent -= 1
        # print('\t' * self.__indent, tag)

    def handle_data(self, data):
        print('\t' * self.__indent, data)

        # if self.__to_set[0] == 'conversation' and self.__to_set[1] is not None and data == 'Markéta Doležalová':
        if self.__to_set[0] == 'conversation' and self.__to_set[1] is not None:
            conversation = open(fb_home + '/' + self.__to_set[1])
            messages_parser.rst()

            for m_line in conversation:
                messages_parser.feed(m_line)

            self.__conversations.append({'users': [user.strip() for user in data.split(',')],
                                         'messages': messages_parser.get_messages()})

            conversation.close()

    def get_conversations(self):
        return self.__conversations

    def error(self, message):
        pass


class MessagesHTMLParser(HTMLParser):
    __indent = 0
    __last_tag = ''
    __messages = []
    __to_set = ''

    def handle_starttag(self, tag, attrs):
        # print('\t' * self.__indent, tag, attrs)
        self.__indent += 1

        if self.__last_tag == 'div' and tag == 'span':
            self.__to_set = 'name'
            self.__messages.append({'name': '', 'datetime': None, 'text': ''})
        elif self.__last_tag == 'span' and tag == 'span':
            self.__to_set = 'datetime'
        elif tag == 'p':
            self.__to_set = 'text'
        else:
            self.__to_set = 'nothing'

        self.__last_tag = tag

    def handle_endtag(self, tag):
        self.__indent -= 1
        # print('\t' * self.__indent, tag)

    def handle_data(self, data):
        # print('\t' * self.__indent, data)

        if self.__to_set == 'datetime':
            self.__messages[-1][self.__to_set] = time.strptime(data + '00', '%d. %B %Y v %H:%M %Z%z')
        elif self.__to_set in ['name', 'text']:
            self.__messages[-1][self.__to_set] = data

    def get_messages(self):
        return self.__messages

    def rst(self):
        self.__indent = 0
        self.__last_tag = ''
        self.__messages = []
        self.__to_set = ''

    def error(self, message):
        pass


smiley_regex = re.compile(r'( |^)((?!(http:/|https:/))([3]?[>:;=][-oO]?[)(\[\]DPpd{}*oO/])|(\^_?\^))')


# smiley_regex = re.compile(r'( |^)(([3]?[>:;=][-oO]?[)(\[\]DPpd{}/])|(\^_?\^))')


def extract_smiles(str):
    smiles = [a[1] for a in smiley_regex.findall(str)]  # classic smiles
    smiles += ''.join(c for c in str if c in emoji.UNICODE_EMOJI)  # emojis

    return smiles


def smiley_stats():
    others_count = 0
    my_count = 0

    my_dictionary = {}
    others_dictionary = {}

    for conversation in c_list_parser.get_conversations():
        if len(conversation['users']) <= 2:
            for message in conversation['messages']:
                smileys = extract_smiles(message['text'])
                if message['name'] == me:
                    my_count += len(smileys)
                    for smiley in smileys:
                        if smiley in my_dictionary:
                            my_dictionary[smiley] += 1
                        else:
                            my_dictionary[smiley] = 1
                else:
                    others_count += len(smileys)
                    for smiley in smileys:
                        if smiley in others_dictionary:
                            others_dictionary[smiley] += 1
                        else:
                            others_dictionary[smiley] = 1

    print('I used ', my_count, ' smileys')
    print('They used ', others_count, ' smileys')

    to_show = [[], [], [], []]

    for x in reversed(sorted(my_dictionary.items(), key=operator.itemgetter(1))):
        if x[1] >= sm_minimum:
            if x[0] in others_dictionary:
                to_show[0].append((x[0], x[1], others_dictionary[x[0]]))
            else:
                to_show[0].append((x[0], x[1], 0))

    for x in reversed(sorted(others_dictionary.items(), key=operator.itemgetter(1))):
        if x[1] >= sm_minimum:
            if x[0] not in to_show:
                if x[0] in my_dictionary:
                    to_show[1].append((x[0], my_dictionary[x[0]], x[1]))
                else:
                    to_show[1].append((x[0], 0, x[1]))

    for x in reversed(sorted(my_dictionary.items(), key=operator.itemgetter(1))):
        if x[1] >= sm_minimum:
            if x[0] in others_dictionary:
                to_show[2].append((x[0], x[1] / my_count * 100, others_dictionary[x[0]] / others_count * 100))
            else:
                to_show[2].append((x[0], x[1] / my_count * 100, 0))

    for x in reversed(sorted(others_dictionary.items(), key=operator.itemgetter(1))):
        if x[1] >= sm_minimum:
            if x[0] not in to_show:
                if x[0] in my_dictionary:
                    to_show[3].append((x[0], my_dictionary[x[0]] / my_count * 100, x[1] / others_count * 100))
                else:
                    to_show[3].append((x[0], 0, x[1] / others_count * 100))

    for show in to_show[:2]:
        n = len(show)
        my_sm = [x[1] for x in show]
        others_sm = [x[2] for x in show]

        print(show)

        ind = np.arange(n)  # the x locations for the groups
        width = 0.42  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, my_sm, width, color='r')
        rects2 = ax.bar(ind + width, others_sm, width, color='y')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Počet použití')
        ax.set_title('Míra používání smajlíků')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels([x[0] for x in show])

        ax.legend((rects1[0], rects2[0]), ('Já', 'Ostatní'))

        plt.show()

    for show in to_show[2:]:
        n = len(show)
        my_sm = [x[1] for x in show]
        others_sm = [x[2] for x in show]

        print(show)

        ind = np.arange(n)  # the x locations for the groups
        width = 0.42  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, my_sm, width, color='r')
        rects2 = ax.bar(ind + width, others_sm, width, color='y')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Procento z celkového počtu použití')
        ax.set_title('Míra používání smajlíků')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels([x[0] for x in show])

        ax.legend((rects1[0], rects2[0]), ('Já', 'Ostatní'))

        plt.show()


def char_count():
    others_count = 0
    my_count = 0

    for conversation in c_list_parser.get_conversations():
        if len(conversation['users']) <= 2:
            for message in conversation['messages']:
                if message['name'] == me:
                    my_count += len(message['text'])
                else:
                    others_count += len(message['text'])

    print('I wrote ', my_count, ' chars')
    print('They wrote ', others_count, ' chars')


def messages_count():
    others_count = 0
    my_count = 0

    for conversation in c_list_parser.get_conversations():
        if len(conversation['users']) <= 2:
            for message in conversation['messages']:
                if message['name'] == me:
                    my_count += 1
                else:
                    others_count += 1

    print('I send ', my_count, ' messages')
    print('They send ', others_count, ' messages')


def who_starts_hours():
    new_conv_limit = [x * 60 * 60 for x in range(1, 24)]

    others_starts = []
    my_starts = []

    others_ends = []
    my_ends = []

    for time_off in new_conv_limit:
        others_starts.append(0)
        my_starts.append(0)

        others_ends.append(0)
        my_ends.append(0)

        for conversation in c_list_parser.get_conversations():
            if len(conversation['users']) <= 2:
                last_msg = conversation['messages'][-1]
                for message in reversed(conversation['messages']):
                    if time.mktime(message['datetime']) - time.mktime(last_msg['datetime']) > time_off:
                        # print('Da', time.mktime(message['datetime']) - time.mktime(last_msg['datetime']))
                        if message['name'] == me:
                            my_starts[-1] += 1
                        else:
                            others_starts[-1] += 1

                        if last_msg['name'] == me:
                            my_ends[-1] += 1
                        else:
                            others_ends[-1] += 1

                    last_msg = message

    fig, ax = plt.subplots()
    dashes = [4, 4, 4, 4]  # 10 points on, 5 off, 10 on, 5 off

    a = [None for x in range(4)]

    a[1], = ax.plot([i / 60 / 60 for i in new_conv_limit], my_starts, color='r', label='Já začátek k.')
    a[0], = ax.plot([i / 60 / 60 for i in new_conv_limit], others_starts, color='y', label='Ostatní začátek k.')
    a[3], = ax.plot([i / 60 / 60 for i in new_conv_limit], my_ends, color='r', label='Já konec k.')
    a[2], = ax.plot([i / 60 / 60 for i in new_conv_limit], others_ends, color='y', label='Ostatní konec k.')

    a[2].set_dashes(dashes)
    a[3].set_dashes(dashes)

    ax.set_ylabel('Počet konverzací')
    ax.set_xlabel('Počet hodin bez interakce')
    ax.legend(loc='center right')
    plt.show()

    for i in range(len(my_starts)):
        my_starts[i] = my_starts[i] / (my_starts[i] + others_starts[i]) * 100
        others_starts[i] = 100 - my_starts[i]
        my_ends[i] = my_ends[i] / (my_ends[i] + others_ends[i]) * 100
        others_ends[i] = 100 - my_ends[i]

    fig, ax = plt.subplots()
    dashes = [4, 4, 4, 4]  # 10 points on, 5 off, 10 on, 5 off

    a = [None for x in range(4)]

    a[1], = ax.plot([i / 60 / 60 for i in new_conv_limit], my_starts, color='r', label='Já začátek k.')
    a[0], = ax.plot([i / 60 / 60 for i in new_conv_limit], others_starts, color='y', label='Ostatní začátek k.')
    a[3], = ax.plot([i / 60 / 60 for i in new_conv_limit], my_ends, color='r', label='Já konec k.')
    a[2], = ax.plot([i / 60 / 60 for i in new_conv_limit], others_ends, color='y', label='Ostatní konec k.')

    a[2].set_dashes(dashes)
    a[3].set_dashes(dashes)
    ax.set_ylim((0, 100))
    ax.set_ylabel('Procento konverzací')
    ax.set_xlabel('Počet hodin bez interakce')
    ax.legend(loc='lower right')
    plt.show()


def who_starts_days():
    new_conv_limit = [x * 60 * 60 * 24 for x in [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 7*5, 7*6, 7*7, 7*8]]

    others_starts = []
    my_starts = []

    others_ends = []
    my_ends = []

    for time_off in new_conv_limit:
        others_starts.append(0)
        my_starts.append(0)

        others_ends.append(0)
        my_ends.append(0)

        for conversation in c_list_parser.get_conversations():
            if len(conversation['users']) <= 2:
                last_msg = conversation['messages'][-1]
                for message in reversed(conversation['messages']):
                    if time.mktime(message['datetime']) - time.mktime(last_msg['datetime']) > time_off:
                        # print('Da', time.mktime(message['datetime']) - time.mktime(last_msg['datetime']))
                        if message['name'] == me:
                            my_starts[-1] += 1
                        else:
                            others_starts[-1] += 1

                        if last_msg['name'] == me:
                            my_ends[-1] += 1
                        else:
                            others_ends[-1] += 1

                    last_msg = message

    fig, ax = plt.subplots()
    dashes = [4, 4, 4, 4]  # 10 points on, 5 off, 10 on, 5 off

    a = [None for x in range(4)]

    a[1], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], my_starts, color='r', label='Já začátek k.')
    a[0], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], others_starts, color='y', label='Ostatní začátek k.')
    a[3], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], my_ends, color='r', label='Já konec k.')
    a[2], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], others_ends, color='y', label='Ostatní konec k.')

    a[2].set_dashes(dashes)
    a[3].set_dashes(dashes)

    ax.set_ylabel('Počet začatých / skončených konverzací')
    ax.set_xlabel('Počet dní bez interakce')
    ax.legend(loc='upper right')
    plt.show()

    for i in range(len(my_starts)):
        my_starts[i] = my_starts[i] / (my_starts[i] + others_starts[i]) * 100
        others_starts[i] = 100 - my_starts[i]
        my_ends[i] = my_ends[i] / (my_ends[i] + others_ends[i]) * 100
        others_ends[i] = 100 - my_ends[i]

    fig, ax = plt.subplots()
    dashes = [4, 4, 4, 4]  # 10 points on, 5 off, 10 on, 5 off

    a = [None for x in range(4)]

    a[1], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], my_starts, color='r', label='Já začátek k.')
    a[0], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], others_starts, color='y', label='Ostatní začátek k.')
    a[3], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], my_ends, color='r', label='Já konec k.')
    a[2], = ax.plot([i / 60 / 60 / 24 for i in new_conv_limit], others_ends, color='y', label='Ostatní konec k.')

    a[2].set_dashes(dashes)
    a[3].set_dashes(dashes)
    ax.set_ylim((0, 100))
    ax.set_ylabel('Počet začatých / skončených konverzací')
    ax.set_xlabel('Počet dní bez interakce')
    ax.legend(loc='upper right')
    plt.show()


m_list = open(fb_home + '/html/messages.htm')

c_list_parser = ConversationListHTMLParser()
messages_parser = MessagesHTMLParser()

for line in m_list:
    c_list_parser.feed(line)

# smiley_stats()
# char_count()
# messages_count()

# who_starts_hours()
who_starts_days()

# print(extract_smiles('>D :D 😀'))

# print(parser.get_messages())
