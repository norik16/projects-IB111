from html.parser import HTMLParser
import time
import locale

locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
fb_home = 'facebook-ronaldluc'
me = 'Ronald Luc'


# print(time.strptime('%d. %B %Y v %H:%M', '08. prosinec 2016 v 22:05 '))
# print(time.strptime('%H', '22'))
# print(time.strptime(time.strftime('%d. %B %Y v %H:%M', time.gmtime()), '%d. %B %Y v %H:%M'))

# print(time.strptime("%a, %d %b %Y %H:%M:%S +0000", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))

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


def smiley_stats():
    pass


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


m_list = open(fb_home + '/html/messages.htm')

c_list_parser = ConversationListHTMLParser()
messages_parser = MessagesHTMLParser()

for line in m_list:
    c_list_parser.feed(line)

char_count()

# print(parser.get_messages())
