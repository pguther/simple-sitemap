from urlparse import urlparse, urljoin
import os
from bs4 import BeautifulSoup
import requests
from progressbar import Bar, Percentage, ProgressBar
import pprint
from unidecode import unidecode

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
    print 'page url:' + page_url
    print "final url: " + final_url
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


def get_links_from_page(page_url):
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


def spider(base_url):
    num_visited = 0
    domain = urlparse(base_url).netloc

    site_dict = dict()

    pages_to_visit_dict = dict()
    pages_to_visit = [base_url]

    print 'base url: ' + base_url
    print 'domain: ' + domain

    while num_visited < 500 and pages_to_visit != []:
        num_visited += 1

        page_url = pages_to_visit[0]
        pages_to_visit = pages_to_visit[1:]

        try:
            print(num_visited, "Visiting:", page_url)

            links, final_url, title = get_links_from_page(page_url)
            pages_to_visit_dict[page_url] = None

            if urlparse(final_url).netloc == domain:
                for link in links:
                    parsed_key_obj = urlparse(link)
                    parsed_key = parsed_key_obj.scheme + '://' + parsed_key_obj.netloc + parsed_key_obj.path
                    if parsed_key_obj.netloc == domain:
                        # print 'found page: ' + parsed_key
                        if parsed_key not in pages_to_visit_dict:
                            pages_to_visit.append(parsed_key)
                            pages_to_visit_dict[parsed_key] = None

                if final_url not in site_dict:
                    site_dict[final_url] = title

        except requests.exceptions.RequestException as e:
            print(" **Failed!**")
    return site_dict


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

"""
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
"""

the_site_dict = spider('http://www.ucsc.edu/')

pp.pprint(the_site_dict)
print len(the_site_dict.keys())
