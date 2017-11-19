from html.parser import HTMLParser
import time
import locale

locale.setlocale(locale.LC_ALL,'cs_CZ.utf8')

# print(time.strptime('%d. %B %Y v %H:%M', '08. prosinec 2016 v 22:05 '))
# print(time.strptime('%H', '22'))
# print(time.strptime(time.strftime('%d. %B %Y v %H:%M', time.gmtime()), '%d. %B %Y v %H:%M'))

# print(time.strptime("%a, %d %b %Y %H:%M:%S +0000", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))


class MyHTMLParser(HTMLParser):
    __indent = 0
    __last_tag = ''
    __messages = []
    __to_set = ''

    def handle_starttag(self, tag, attrs):
        # print('\t'*self.__indent, tag, attrs)
        self.__indent += 1

        if self.__last_tag == 'div' and tag == 'span':
            self.__to_set = 'name'
            self.__messages.append({'name': None, 'datetime': None, 'text': None})
        elif self.__last_tag == 'span' and tag == 'span':
            self.__to_set = 'datetime'
        elif tag == 'p':
            self.__to_set = 'text'

        self.__last_tag = tag

    def handle_endtag(self, tag):
        self.__indent -= 1
        # print('\t'*self.__indent, tag)

    def handle_data(self, data):
        # print('\t'*self.__indent, data)

        if self.__to_set == 'datetime':
            self.__messages[-1][self.__to_set] = time.strptime( data +'00', '%d. %B %Y v %H:%M %Z%z')
        elif self.__to_set in ['name', 'text']:
            self.__messages[-1][self.__to_set] = data

    def get_messages(self):
        return self.__messages


m_list = open('facebook-ronaldluc/html/messages.htm')

parser = MyHTMLParser()



for line in inpt:
    parser.feed(line)

print(parser.get_messages())
