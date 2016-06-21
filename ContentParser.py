import re
import os
import gzip
import logging
import argparse
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


class ContentFinder:
    def __init__(self, source_page):
        self._source_page = source_page
        self._soup = BeautifulSoup(self._source_page, 'html.parser')
        self.content = None

    @classmethod
    def from_url(cls, url):
        logging.debug("opening page: {}".format(url))

        try:
            res = urllib.request.urlopen(url)

        except:
            raise RuntimeError("Its not a real url or website is unavailable")

        full_page = res.read()
        if res.headers.get('Content-Encoding', 'identity') == 'gzip':
            full_page = gzip.decompress(full_page)

        charset = res.headers.get_content_charset('utf-8')
        source_page = full_page.decode(charset)

        return cls(source_page)

    def find_content(self):
        divs = self._soup.find_all('div')

        only_text = []
        for div in divs:
            if div.find('div') is not None:
                only_text.append('')

            else:
                only_text.append(div.get_text())

        main_content = max(only_text, key=len)

        index = only_text.index(main_content)
        self.content = divs[index]

        return self.content

    def find_title(self):
        return self._soup.find('title').get_text()

    def find_images(self):
        if self.content is None:
            raise RuntimeError("At first you should find content")

        images = self.content.find_all('img')

        return images


class ContentFormater:
    def __init__(self, title, content):
        self._title = title
        self._content = content
        self.formated_content = str(content)

    def format_images(self):
        images = self._content.find_all('img')

        for image in images:
            self.formated_content = self.formated_content.replace(str(image), '[{}]'.format(image['src']))

    def format_links(self):
        links = self._content.find_all('a')

        for link in links:
            href = link.get('href', None)

            if href is not None:
                format_link = '[{}]{}'.format(link.get('href'), link.get_text())

            else:
                format_link = ''

            self.formated_content = self.formated_content.replace(str(link), format_link)

    def remove_html_tags(self):
        self.formated_content = BeautifulSoup(self.formated_content, 'html.parser').get_text()

    def format_string_limit(self):
        paragraphs = self.formated_content.split('\n')
        _content = str()

        while paragraphs:
            paragraph = paragraphs.pop(0)
            words = paragraph.split(' ')

            length = 0
            while words:
                word = words.pop(0)
                length += len(word) + 1

                if len(word) > 79:
                    _content += '\n {} \n'.format(word)
                    length = 0

                elif length > 79:
                    _content += '\n {} '.format(word)
                    length = len(word) + 1

                else:
                    _content += ' {}'.format(word)

            _content += '\n'

        self.formated_content = _content

    def remove_garbage(self):
        self.formated_content = re.sub(r'^[ \t]+', '', self.formated_content, flags=re.M)
        self.formated_content = re.sub('[\r]', '\n', self.formated_content, flags=re.M)
        self.formated_content = re.sub('[\n]{2,}', '\n', self.formated_content, flags=re.M)

    def format(self):
        self.format_images()
        self.format_links()
        self.remove_html_tags()
        self.remove_garbage()
        self.formated_content = '{}\n\n{}'.format(self._title, self.formated_content)
        self.format_string_limit()

        return self.formated_content


class ContentSaver:
    base_dir = os.path.dirname(__file__)

    def __init__(self, title, content,  dir=None, images=None):
        self._title = title
        self._content = content
        self._dir = dir
        self._images = images

    def save(self):
        self._check_title()

        if self._dir is None:
            self._dir = os.path.join(self.base_dir, 'output', self._title)

        logging.debug("saving content to: {}".format(self._dir))
        os.makedirs(self._dir, exist_ok=True)

        self._write()

        if self._images is not None:
            self._dowloand_images()

    def _check_title(self):
        # \/:*?"<>|
        self._title = re.sub('\\\|\/|:|\*|"|<|>\||\?', '', self._title)
        self._title = self._title[0:255]

    def _write(self):
        file_name = '{}.txt'.format(self._title)

        with open(os.path.join(self._dir, file_name), 'w') as f:
            f.write(self._content)

    def _dowloand_images(self):
        for image in self._images:
            name = image.get('src').split('/')[-1]

            with open(os.path.join(self._dir, name), 'wb') as f:
                logging.debug("dowloading image: {}".format(image.get('src')))
                image_content = urllib.request.urlopen(image.get('src'))
                f.write(image_content.read())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=10)

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-u', '--url', help="url with content, example: http://example.com/page.html")
    arg_parser.add_argument('-d', '--dir', help="dir to save content")
    args = arg_parser.parse_args()

    if args.url is None:
        exit("Define an url. Example: -u http://example.com/ Use -h or --help for more options")

    content_finder = ContentFinder.from_url(args.url)
    content = content_finder.find_content()
    title = content_finder.find_title()

    content_formater = ContentFormater(title, content)
    formated_content = content_formater.format()

    images = content_finder.find_images()
    content_saver = ContentSaver(title, formated_content, dir=args.dir, images=images)
    content_saver.save()
