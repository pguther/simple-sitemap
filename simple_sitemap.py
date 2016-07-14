from urlparse import urlparse
import os
from bs4 import BeautifulSoup
import requests
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer, AdaptiveETA, AbsoluteETA, AdaptiveTransferSpeed


def get_soup_from_url(page_url):
    """
    Takes the url of a web page and returns a BeautifulSoup Soup object representation
    :param page_url: the url of the page to be parsed
    :param article_url: the url of the web page
    :raises: r.raise_for_status: if the url doesn't return an HTTP 200 response
    :return: A Soup object representing the page html
    """
    r = requests.get(page_url)
    if r.status_code != requests.codes.ok:
        return None
    if r.headers['content-type'] != 'text/html; charset=UTF-8':
        return None
    return BeautifulSoup(r.content, 'html.parser')


def recursive_print_dictionary(site_map, level, name):
    print name + '/'
    print '|'
    recursive_print_dictionary_helper(site_map, level + 1)


def recursive_print_dictionary_helper(current_dict, level):

    pre_string = '|' + (' ' * ((level * 3) - 1)) + '|- '

    for key, value in current_dict.iteritems():

        entry_string = key
        post_string = ''

        if value is not None:
            if isinstance(value, dict):
                entry_string += '/'
            else:
                post_string = ' ' + ('_' * (60 - (len(pre_string) + len(entry_string) + 1))) + '# ' + value
        else:
            post_string = ' ' + ('_' * (60 - (len(pre_string) + len(entry_string) + 1))) + '#'

        print pre_string + entry_string + post_string

        if value is not None:
            if isinstance(value, dict):
                recursive_print_dictionary_helper(value, level + 1)
    print '|'

site_map = dict()

url_list = []

with open("sitemap.txt", "r") as infile:

    for line in infile:
        url_list.append(line.rstrip())

pbar = ProgressBar(widgets=[Percentage(), Bar()], max_value=len(url_list)).start()

url_num = 1

for url in url_list:

    pbar.update(url_num)
    url_num += 1

    parsed_url = urlparse(url)
    path = parsed_url.path

    if path[-1:] == '/':
        continue

    path = os.path.normpath(path)
    soup = get_soup_from_url(url)

    if soup is not None:
        title = soup.head.title.get_text()
    else:
        title = None

    # print parsed_url.path
    path_list = path.split(os.sep)[1:]

    folders = path_list[:-1]
    filename = path_list[-1:][0]

    # noinspection PyRedeclaration
    current_dict = site_map
    for folder in folders:
        # print folder
        if folder not in current_dict:
            current_dict[folder] = dict()

        current_dict = current_dict[folder]

    current_dict[filename] = title

pbar.finish()

recursive_print_dictionary(site_map, 0, 'www.ucsc.edu')
