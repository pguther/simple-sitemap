from urlparse import urlparse, urljoin
import os
import sys
from bs4 import BeautifulSoup
import requests
from progressbar import Bar, Percentage, ProgressBar, UnknownLength, FormatLabel, RotatingMarker
import pprint
from unidecode import unidecode
import re
import argparse

pp = pprint.PrettyPrinter(indent=4)


def get_soup_from_url(page_url):
    """
    Takes the url of a web page and returns a BeautifulSoup Soup object representation
    :param page_url: the url of the page to be parsed
    :param article_url: the url of the web page
    :raises: r.raise_for_status: if the url doesn't return an HTTP 200 response
    :return: A Soup object representing the page html
    """
    r = requests.get(page_url)
    final_url = r.url
    if r.status_code != requests.codes.ok:
        raise requests.exceptions.RequestException
    if r.headers['content-type'] != 'text/html; charset=UTF-8':
        return None, final_url
    return BeautifulSoup(r.content, 'html.parser'), final_url


def convert_urls(body, page_url):
        """
        converts all urls in the body from relative to full urls
        :param page_url:
        :param body:
        :return:
        """
        a_tags = body.find_all("a")
        if a_tags is not None:
            for a_tag in a_tags:
                if 'href' in a_tag.attrs:
                    a_tag_relative_src = a_tag.attrs['href']
                    a_tag_src = urljoin(page_url, a_tag_relative_src)
                    a_tag.attrs['href'] = a_tag_src


def url_dict_from_file(root_url, max, pretty, filename):

    index_page_regex = re.compile(r"(http:\/\/.+\/)index.html")

    url_dict = dict()
    root_title = None

    if pretty:
        soup, final_url = get_soup_from_url(root_url)

        if soup is not None:
            title_tag = soup.find('title')
            if title_tag is not None:
                root_title = unidecode(title_tag.get_text())

    num_urls = 0

    with open(filename, 'r') as infile:
        for line in infile:

            matches = index_page_regex.findall(line)

            if matches:
                line = matches[0]

            line = line.rstrip()

            if line != root_url:
                url_dict[line.rstrip()] = None

            num_urls += 1
            if num_urls > max:
                break

    if pretty:
        num_scanned = 0
        print "Getting Page titles..."
        bar = ProgressBar(max_value=len(url_dict.keys()))
        bar.start()

        for key, value in url_dict.iteritems():
            num_scanned += 1
            bar.update(num_scanned)

            soup, final_url = get_soup_from_url(key)

            if soup is not None:
                title_tag = soup.find('title')
                if title_tag is not None:
                    url_dict[key] = unidecode(title_tag.get_text())

        bar.finish()

    return url_dict, root_title


def get_links_from_page(page_url):

    index_page_regex = re.compile(r"(http:\/\/.+\/)index.html")

    matches = index_page_regex.findall(page_url)

    if matches:
        page_url = matches[0]

    soup, final_url = get_soup_from_url(page_url)

    links_list = []

    if soup is None:
        return links_list, final_url, None
    else:
        title_tag = soup.find('title')
        if title_tag is not None:
            title = unidecode(title_tag.get_text())
        else:
            title = None

    body = soup.find('body')
    if body is not None:

        convert_urls(body, final_url)

        link_tags = body.find_all('a')

        if link_tags is not None:
            for link_tag in link_tags:
                if 'href' in link_tag.attrs:
                    href = link_tag['href']
                    links_list.append(href)

    return links_list, final_url, title


def spider(root_url, max_urls, pretty):
    num_visited = 0

    domain = urlparse(root_url).netloc
    root_title = ''

    site_dict = dict()

    pages_to_visit_dict = dict()
    pages_to_visit = [root_url, root_url + 'index.html']

    print "Mapping Site..."
    bar = ProgressBar(max_value=UnknownLength)
    bar.start()

    while num_visited < max_urls and pages_to_visit != []:
        num_visited += 1

        page_url = pages_to_visit[0]
        pages_to_visit = pages_to_visit[1:]

        bar.update(num_visited)

        try:
            links, final_url, title = get_links_from_page(page_url)
            pages_to_visit_dict[page_url] = None
            pages_to_visit_dict[final_url] = None

            if urlparse(final_url).netloc == domain:
                for link in links:
                    parsed_key_obj = urlparse(link)
                    parsed_key = parsed_key_obj.scheme + '://' + parsed_key_obj.netloc + parsed_key_obj.path

                    if parsed_key_obj.netloc == domain:
                        if parsed_key not in pages_to_visit_dict:
                            pages_to_visit.append(parsed_key)
                            pages_to_visit_dict[parsed_key] = None

                if final_url == root_url or final_url == root_url + 'index.html':
                    root_title = title
                elif final_url not in site_dict:
                    if pretty:
                        site_dict[final_url] = title
                    else:
                        site_dict[final_url] = None

        except requests.exceptions.RequestException as e:
            num_visited = num_visited
            # print(" **Failed!**")

    bar.finish()

    return site_dict, root_title


def recursive_print_pretty_dictionary(the_site_map, level, root_url, root_title, width, handle):

    if root_url[-1:] != '/':
        root_url += '/'

    post_string = root_url + ('_' * (width - len(root_url))) + '# ' + root_title

    handle.write(post_string + '\n')
    recursive_print_pretty_dictionary_helper(the_site_map, level + 1, width, handle)


def recursive_print_pretty_dictionary_helper(current_dict, level, width, handle):

    pre_string = '|' + (' ' * ((level * 3) - 1)) + '|- '

    for key, value in current_dict.iteritems():

        entry_string = key
        post_string = ''

        entry_title = value[0]

        entry_subfolder = value[1]

        if value is not None:
            if entry_subfolder is not None:
                entry_string += '/'
                if entry_title is not None:
                    post_string = ' ' + ('_' * (width - (len(pre_string) + len(entry_string) + 1))) + '# ' + entry_title
                else:
                    post_string = ' ' + ('_' * (width - (len(pre_string) + len(entry_string) + 1))) + '#'
            else:
                if entry_title is not None:
                    post_string = ' ' + ('_' * (width - (len(pre_string) + len(entry_string) + 1))) + '# ' + entry_title
                else:
                    post_string = ' ' + ('_' * (width - (len(pre_string) + len(entry_string) + 1))) + '#'

        handle.write(pre_string + entry_string + post_string + '\n')

        if value is not None and entry_subfolder is not None:
            recursive_print_pretty_dictionary_helper(entry_subfolder, level + 1, width, handle)
    handle.write('|\n')


def recursive_print_simple_dictionary(the_site_map, level, root_url, root_title, width, handle):

    if root_url[-1:] == '/':
        root_url = root_url[:-1] + ':'
    else:
        root_url += ':'

    handle.write(root_url + '\n')
    recursive_print_simple_dictionary_helper(the_site_map, level + 1, width, handle)


def recursive_print_simple_dictionary_helper(current_dict, level, width, handle):

    pre_string = (' ' * (level * 4)) + '- '

    for key, value in current_dict.iteritems():

        entry_string = key

        entry_subfolder = value[1]

        if value is not None:
            if entry_subfolder is not None:
                entry_string += ':'

        handle.write(pre_string + entry_string + '\n')

        if value is not None and entry_subfolder is not None:
            recursive_print_simple_dictionary_helper(entry_subfolder, level + 1, width, handle)


def create_site_map(root_url, url_title_dict):

    url_list = url_title_dict.keys()

    url_num = 1

    site_dict = dict()

    for url in url_list:
        url_num += 1

        parsed_url = urlparse(url)
        path = parsed_url.path

        path = os.path.normpath(path)

        title = url_title_dict[url]

        # print parsed_url.path
        path_list = path.split(os.sep)[1:]

        if url[-1:] == '/':
            folders = path_list
            filename = None
        else:
            folders = path_list[:-1]
            filename = path_list[-1:][0]

        current_dict = site_dict

        current_folder_path = root_url

        for folder in folders:

            current_folder_path += folder + '/'

            if current_dict is not None:
                if folder not in current_dict:
                    if current_folder_path in url_title_dict:
                        folder_title = url_title_dict[current_folder_path]
                    else:
                        folder_title = None
                    current_dict[folder] = (folder_title, dict())

                current_dict = current_dict[folder][1]
        if filename is not None:
            current_dict[filename] = (title, None)

    return site_dict


parser = argparse.ArgumentParser()

parser.add_argument('--base_url', help='The URL of a website to crawl and map', dest='base_url', required=True)
parser.add_argument('--input', help='A file containing a list of URLs to generate a sitemap from. '
                                    'Takes precedence over --base_url', dest='input')
parser.add_argument('--max', help='The maximum number of URLs to use in the site map, default is 500', default=500,
                    type=int, dest='max')
parser.add_argument('--output', help='A file to print the sitemap to, default is stdout', dest='output')
parser.add_argument('--pretty', help='Changes output format to pretty', dest='pretty', action='store_true')
parser.add_argument('--width', help='Width of output (without page descriptions), default is 60', dest='width',
                    type=int, default=60)

try:
    results = parser.parse_args()

    if results.input:
        url_desc_dict, base_title = url_dict_from_file(results.base_url, results.max, results.pretty, results.input)
    else:
        url_desc_dict, base_title = spider(results.base_url, results.max, results.pretty)

    site_map = create_site_map(results.base_url, url_desc_dict)

    fhandle = open(results.output, 'w') if results.output else sys.stdout

    if results.pretty:
        recursive_print_pretty_dictionary(site_map, 0, results.base_url, base_title, results.width, fhandle)
    else:
        recursive_print_simple_dictionary(site_map, 0, results.base_url, base_title, results.width, fhandle)

    if fhandle is not sys.stdout:
        fhandle.close()

except IOError, msg:
    parser.error(str(msg))
