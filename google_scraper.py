from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from bs4.element import Tag
from mechanize import Browser
import requests
import justext
from threading import Thread
import functools

#timeout decorator to stop trying to open a link after 2 minutes of running
def timeout(seconds_before_timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, seconds_before_timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(seconds_before_timeout)
            except Exception as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

# google scraper
# scrapes the front page of google whenever you search an article for their titles, bodies, and links
class GoogleScraper:
    def __init__(self, n_searches = 5):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1920x1080')
        self.options.add_argument("disable-gpu")
        self.s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.s, options=self.options)

        self.br = Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent',
                               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36')]
        self.n_searches = n_searches

    def _get_site_body(self, link):
        response = requests.get(link)
        paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
        full_text = []

        for paragraph in paragraphs:
            if not paragraph.is_boilerplate:
                full_text.append(paragraph.text)

        #print("got text body")
        return ' '.join(full_text)

    @timeout(120)
    def _browser_helper(self, r):
        #print('finding link')
        link = r.find('a', href=True)
        print('scraping link')
        self.br.open(link['href'])
        title = self.br.title()
        body = self._get_site_body(link['href'])

        return link, title, body

    def get_results(self, query):

        print(f'searching google the first {self.n_searches} results of google')

        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}" + "&num=" + f'{self.n_searches}'
        self.driver.get(google_url)
        time.sleep(3)

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        result_div = soup.find_all('div', attrs={'class': 'g'})

        titles_bodies_links = []

        for r in result_div:
            # Checks if each element is present, else, raise exception
            try:
                link, title, body = self._browser_helper(r)
                # Check to make sure everything is present before appending
                if link != '' and title != '':
                    if title != 'Images' and title != 'Description' and title != None:
                        self.br.open(link['href'])
                        titles_bodies_links.append((title, body, link['href']))
                        #print(link['href'], 'Appended')


            # Next loop if one element is not present
            except Exception as e:
                #print(e)
                continue

        return titles_bodies_links
