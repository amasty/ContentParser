import re
import os
import codecs
import logging
import urllib.parse
import urllib.request


class Saver:
    base_dir = os.getcwd()

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
        # remove unallowed chars \/:*?"<>|
        self._title = re.sub('[\\|\/|:|\*|"|<|>\||\?]', '', self._title)
        self._title = self._title[0:255]

    def _write(self):
        file_name = '{}.txt'.format(self._title)

        with codecs.open(os.path.join(self._dir, file_name), 'w', 'utf-8-sig') as f:
            f.write(self._content)

    def _dowloand_images(self):
        for image in self._images:
            name = image.get('src').split('/')[-1]

            with open(os.path.join(self._dir, name), 'wb') as f:
                logging.debug("dowloading image: {}".format(image.get('src')))
                image_content = urllib.request.urlopen(image.get('src'))
                f.write(image_content.read())
