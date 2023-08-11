import joblib
from tqdm import tqdm
import pandas as pd

import requests
import whois
import virustotal_python
from requests_html import HTMLSession
from collections import Counter
from urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import time
import datetime
from threading import Thread
import functools

disable_warnings(InsecureRequestWarning)

options = Options()
options.headless = True

from collections import defaultdict


# from urllib.request import urlopen, URLError
# import socket

# class TimeoutException(Exception):
#     def __init__(self, message="Data gathering took too long"):
#         self.message = message
#         super().__init__(self.message)


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


class SitePredictor:
    def __init__(self, timeout_secs=200):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1920x1080')
        self.options.add_argument("disable-gpu")

        self.s = Service(ChromeDriverManager().install())

        self.pr_headers = {'API-OPR': '4ok88wgckg8o0cgcswo4gc4kkc0sgocw0woww4o0'}
        self.checker_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

        self.session = HTMLSession()
        self.clf = joblib.load('classifiers/XGBoostClassifierNO-VT.joblib')
        self.timeout_sec = datetime.timedelta(seconds=timeout_secs)

    def get_pagerank(self, domain):
        print('pagerank')
        # headers = {'API-OPR':'4ok88wgckg8o0cgcswo4gc4kkc0sgocw0woww4o0'}
        url = 'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=' + domain
        request = requests.get(url, headers=self.pr_headers)
        if request.status_code == 200:
            result = request.json()
            if result['status_code'] == 200:
                pr_dec = result['response'][0]['page_rank_decimal']
                rank = result['response'][0]['rank']

                return pr_dec, rank

    def whois_checker(self, domain):
        print('whois')
        w = whois.whois(domain)
        if type(w.get('registrar')) == list:
            domain_registrar = w.get('registrar')[0]
        else:
            domain_registrar = w.get('registrar')

        if type(w.get('registrant_postal_code')) == list:
            postal_code = w.get('registrant_postal_code')[0]
        else:
            postal_code = w.get('registrant_postal_code')

        if type(w.get('country')) == list:
            country = w.get('country')[0]
        else:
            country = w.get('country')
        return domain_registrar, postal_code, country

    # def virus_scan(self, domain):
    #     print('virus')
    #     virus_data = None
    #     while True:
    #         try:
    #             with self.vt_apikey as vtotal:
    #                 resp = vtotal.request(f"domains/{domain}")
    #                 virus_data = resp.json()['data']['attributes']['last_analysis_stats']
    #                 #return virus_data['malicious']
    #         except Exception:
    #             print('restarting in 1 minute-virustotal')
    #             time.sleep(100)
    #             print('time up')
    #         else:
    #             return virus_data['malicious']

    @timeout(60)
    def link_checker(self, domain):
        print('linkcheck')
        # time.sleep(5)
        r = self.session.get("https://" + domain, verify=False)
        unique_netlocs = Counter(urlparse(link).netloc for link in r.html.absolute_links)
        outbound_n = 0
        local_n = 0

        for link in unique_netlocs:
            # print(link, unique_netlocs[link])
            if domain.lower() in link:
                local_n += unique_netlocs[link]
            else:
                outbound_n += unique_netlocs[link]

        return local_n, local_n + outbound_n

    def check_login(self, driver):

        wp_xpath = "//a[starts-with(@href, 'https://wordpress.org')]"
        try:
            displayed = driver.find_element('xpath', wp_xpath).is_displayed()

            return displayed
        except:
            return False

    def check_page_source(self, domain, driver):
        try:
            driver.get(f"https://{domain}/wp-admin")
            wp_pg = "wp-content" in driver.page_source
            return wp_pg
        except:

            return False

    def check_wp(self, domain):
        print('wordpress')
        # service_obj = Service(executable_path="C:/Users/cvaal/chromedriver.exe")
        # driver = webdriver.Chrome(options=options, service=service_obj)
        driver = webdriver.Chrome(service=self.s, options=self.options)

        driver.implicitly_wait(1)
        driver.get(f"https://{domain}/wp-admin")
        login = self.check_login(driver)
        pg_source = self.check_page_source(domain, driver)
        wp = None
        if login == False and pg_source == False:
            wp = False
        else:
            wp = True

        driver.close()
        return wp

    def check_url(self, url):
        print('url check')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        response = requests.get('https://' + url, timeout=5, headers=self.checker_headers)

        return response.status_code

    def get_site_data(self, domain):
        # try:
        # print(check_url(domain))
        # if check_url(domain) == True:
        # try:
        print('gathering data from', domain)
        # print('PLEASE WORK IM BEGGING')

        pr_dec, rank = self.get_pagerank(domain)
        domain_registrar, postal_code, country = self.whois_checker(domain)
        # malicious = self.virus_scan(domain)
        local_n, total_links = self.link_checker(domain)
        wp_check = self.check_wp(domain)
        return domain, pr_dec, rank, domain_registrar, postal_code, country, local_n, total_links, wp_check

    def get_and_organize_data(self, domain_list):
        columns = ['Domain', 'Page rank decimal', 'Site Rank', 'Domain registrar', 'Postal code', 'Country of origin',
                   'No. of Local links', 'Total links', 'Wordpress?']
        site_df_dict = defaultdict(list)
        time_start = datetime.datetime.now()
        for domain in domain_list:

            if 'http' in domain:
                domain = urlparse(domain).netloc.strip("www.")
            # print(domain)
            try:
                site_data = self.get_site_data(domain.lower())
                # time_elapsed = datetime.datetime.now() - time_start
                # if time_elapsed > self.timeout_sec:
                # raise TimeoutException()
                if type(site_data) == tuple:
                    print(site_data)
                    for column, data in zip(columns, site_data):
                        site_df_dict[column].append(data)

                else:
                    print('no data gathered')
                    continue

            except Exception as e:
                # print('EXCEPTION')
                print(e)
                continue

                # print(e)
                # rint('site down')

        print(site_df_dict)
        return pd.DataFrame(site_df_dict)

    def predict(self, domain_list):
        if domain_list:
            print('scanning sites:', domain_list)
            data = self.get_and_organize_data(domain_list)  # dataframe obj
            # domains = data['Domain'].values
            if isinstance(data, pd.DataFrame) and 'Domain' in data.columns:
                print('got thru')
                print('columns:', data.columns)
                features_df = data.drop('Domain', axis=1)
                print(type(features_df))
                print(features_df)

                preds = self.clf.predict(features_df)
                predictions = [round(value) for value in preds]
                print('RETURNING PREDICTIONS:', predictions)
                return predictions
            else:
                print('aint got thru')
                return None
        else:
            return None