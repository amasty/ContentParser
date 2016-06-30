import logging
import argparse

from app.saver import Saver
from app.finder import Finder
from app.formater import Formater


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=10)

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-u', '--url', help="url with content, example: http://example.com/page.html")
    arg_parser.add_argument('-d', '--dir', help="dir to save content")
    args = arg_parser.parse_args()

    if args.url is None:
        exit("Define an url. Example: -u http://example.com/ Use -h or --help for more options")

    finder = Finder.from_url(args.url)
    finder.find_content()
    content = finder.get_content()
    title = finder.get_title()

    formater = Formater(title, content)
    formater.format()
    formated_content = formater.get()

    images = finder.get_images()
    saver = Saver(title, formated_content, dir=args.dir, images=images)
    saver.save()
