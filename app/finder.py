import re
import gzip
import logging
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


class Finder:
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

    def get_content(self):
        if self.content is None:
            raise RuntimeError("Find content before")

        return self.content

    def find_content(self):
        blocks = [
            self._find_block_with_most_used_el('p'),
            self._find_block_with_most_used_el('br')
        ]

        ratings = []
        for block in blocks:
            ratings.append(self.is_text_rating(block.get_text()))

        index = ratings.index(max(ratings))
        content = blocks[index]

        self.content = content

    def _find_block_with_most_used_el(self, tag):
        paragraphs = self._soup.find_all(tag)

        el_with_paragraph = []
        for paragraph in paragraphs:
            el_with_paragraph.append(paragraph.parent)

        count_paragraphs = []
        for el in el_with_paragraph:
            count_paragraphs.append(len(el.find_all(tag)))

        index = count_paragraphs.index(max(count_paragraphs))
        content = el_with_paragraph[index]

        return content

    def is_text_rating(self, text):
        # defind checks for text
        checks = [
            self._check_spaces_ratio
        ]

        # collect rating from checks
        rating = []
        for check in checks:
            rating.append(int(check(text)))

        # calc averge rating
        averge_rating = sum(rating) / len(rating)

        return averge_rating

    def _check_spaces_ratio(self, text):
        # unnecessary spaces
        text = re.sub('(\s){2,}', ' ', text)

        # calc ratio
        general_length = len(text)
        spaces_count = len(text) - len(re.sub('(\s)+', '', text))

        ratio = round(spaces_count / general_length, 2)

        # average ratio is between 0.10 - 0.16
        return 0.10 < ratio < 0.16

    def get_title(self):
        return self._soup.find('title').get_text()

    def get_images(self):
        if self.content is None:
            raise RuntimeError("At first you should find content")

        images = self.content.find_all('img')

        return images
