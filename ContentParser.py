import os
import json
import gzip
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup


class ContentFinder:
    def __init__(self, config):
        self.config = config

    def get_source_page(self, url):
        res = urllib.request.urlopen(url)

        full_page = res.read()
        if res.headers.get('Content-Encoding', 'identity') == 'gzip':
            full_page = gzip.decompress(full_page)

        charset = res.headers.get_content_charset('utf-8')
        source_page = full_page.decode(charset)

        return source_page

    def find(self, config, raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')

        soup_content = soup.find(config['content']['tag'], config['content']['class'])
        soup_title = soup.find(config['title']['tag'], config['title']['class'])

        return soup_title.get_text(), soup_content

    def get_soup(self, url):
        source_page = self.get_source_page(url)
        domain = urllib.parse.urlparse(url)[1]

        return self.find(self.config[domain], source_page)


class ContentFormater:
    def format(self, title, soup_content):
        images = soup_content.find_all('img')
        links = soup_content.find_all('a')

        formated_content = title
        formated_content += str(soup_content)

        formated_content, img_list = self.format_images(formated_content, images)
        formated_content = self.format_link(formated_content, links)
        formated_content = self.remove_tags(formated_content)

        formated_content = re.sub(r'^[ \t]+', '', formated_content, flags=re.M)
        formated_content = re.sub('[\r]', '\n', formated_content, flags=re.M)
        formated_content = re.sub('[\n]{2,}', '\n', formated_content, flags=re.M)

        formated_content = self.format_string_limit(formated_content)

        return str(formated_content), img_list

    def format_images(self, content, images):
        img_list = []

        for image in images:
            content = re.sub(str(image), '[' + image['src'] + ']', content)
            img_list.append(image['src'])

        return content, img_list

    def format_link(self, content, links):
        for link in links:
            try:
                formated_link = '[' + link.get('href') + ']' + link.get_text()
            except:
                formated_link = ''

            content = re.sub(str(link), formated_link, content)

        return content

    def remove_tags(self, content):
        return BeautifulSoup(content, 'html.parser').get_text()

    def format_string_limit(self, content):
        paragraphs = content.split('\n')
        new_content = ''

        while paragraphs:
            paragraph = paragraphs.pop(0)
            words = paragraph.split(' ')

            if len(words) == 1:
                word = words.pop(0)
                new_content+= word

            count = 0
            while words:
                word = words.pop(0)
                count += len(word) + 1

                if len(word) > 79:
                    new_content += '\n' + word + '\n'
                    count = 0

                elif count > 79:
                    new_content += '\n' + word + ' '
                    count = len(word) + 1

                else:
                    new_content += word + ' '

            if len(paragraphs) != 1:
                new_content += '\n\n'

        return new_content


class ContentSaver:
    def save(self, title, content, img_list=None, base_dir=''):
        self.write(title, content, base_dir)

        if img_list:
            self.dowloand_images(img_list, os.path.join(base_dir, title))

    def dowloand_images(self, images, dir='.'):
        if dir:
            os.makedirs(dir, exist_ok=True)

        for image in images:
            name = image.split('/')[-1]
            with open(os.path.join(dir, '%s' % name), 'wb') as f:
                download_img = urllib.request.urlopen(image)
                f.write(download_img.read())

    def write(self, title, content, base_dir=''):
        if base_dir:
            os.makedirs(base_dir, exist_ok=True)

        with open(os.path.join(base_dir, title + '.txt'), 'w') as f:
            f.write(content)


def load_config():
    f = open(os.path.join(os.path.dirname(__file__), 'config'), 'r')
    config = f.read()
    config = json.loads(config)

    return config


if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    config = load_config()
    url = 'http://habrahabr.ru/post/257287/'

    ContentFinder = ContentFinder(config)
    ContentFormater = ContentFormater()
    ContentSaver = ContentSaver()

    title, soup_content = ContentFinder.get_soup(url)
    content, img_list = ContentFormater.format(title, soup_content)
    ContentSaver.save(title, content, img_list, base_dir)
