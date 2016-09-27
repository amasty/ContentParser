import re

from bs4 import BeautifulSoup


class Formater:
    def __init__(self, title, content):
        self._title = title
        self._content = content
        self.formated_content = None

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
        self.formated_content = str(self._content)

        self.format_images()
        self.format_links()
        self.remove_html_tags()
        self.remove_garbage()
        self.formated_content = '{}\n\n{}'.format(self._title, self.formated_content)
        self.format_string_limit()

    def get(self):
        if self.formated_content is None:
            raise RuntimeError("Format content before")

        return self.formated_content
