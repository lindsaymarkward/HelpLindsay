"""
Display a list of all images contained in all HTML files in a folder

"""
import os
from html.parser import HTMLParser

__author__ = 'Lindsay Ward'
PATH = '/Users/sci-lmw1/GoogleDrive/OffCampus/JCUS/CP1406/CP1406 2016 SP51/_Pracs'


class ImageFinderParser(HTMLParser):
    """
    Custom subclass of HTMLParser with one overridden method, to handle img elements
    """
    def handle_starttag(self, tag, attrs):
        """
        Print the src of all img elements
        :param tag: HTML element as str
        :param attrs: attributes as list of tuples (attribute, value)
        :return: None
        """
        if tag == 'img':
            # print("Images:")
            for attr in attrs:
                if attr[0] == 'src':
                    print('\t', attr[1])


def main():
    os.chdir(PATH)
    # create instance of custom parser to print images
    parser = ImageFinderParser()

    for filename in os.listdir('.'):
        if filename.endswith('.html'):
            print(filename)
            f = open(filename, encoding='utf8')
            text = f.read()
            parser.feed(text)
            # parser.reset()
            f.close()

main()