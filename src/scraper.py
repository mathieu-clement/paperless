#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import datetime
import pdb
import pickle
import pytz
import requests

from . import absolute_filename, Schedule


BS_PARSER='lxml'


class CookieManager: 
    def __init__(self, filename):
        self.filename = filename

    def save(self, session):
        with open(self.filename, 'wb') as f:
            pickle.dump(session.cookies, f)

    def load(self, session):
        with open(self.filename, 'rb') as f:
            session.cookies.update(pickle.load(f))


class Scraper:
    class Urls:
        def __init__(self, domain):
            self.BASE_URL = 'https://' + domain
            self.LOGIN_PAGE = self.BASE_URL + '/fcms1.aspx'
            self.MY_SCHEDULES = self.BASE_URL + '/mstr8.aspx'


    is_logged_in = False
    DT_FORMAT = '%m/%d/%Y %I:%M:%S %p'


    def __init__(self, base_url=None, username=None, password=None, 
                       timezone=None):
        if not base_url or not username or not password:
            assert not base_url and not username and not password, \
                'if one credential missing then all should be missing'
            settings = self.Settings()
            base_url = settings.base_url
            username = settings.username
            password = settings.password
            if settings.timezone:
                timezone = settings.timezone
        self.username = username
        self.password = password
        if timezone:
            self.timezone = pytz.timezone(timezone) 
        self.urls = self.Urls(base_url)
        self.cookie_manager = CookieManager(absolute_filename('cookies.bin'))


    def log_in(self):
        """Starts a new session, and performs login, whether the user is already
        connected or not.
        
        Returns True if login was successful, False otherwise 
        (maybe incorrect credentials)"""
        self.session = requests.Session()
        # Load an empty login page before login
        # to fetch hidden inputs to use in the form data
        get_request = self.session.get(self.urls.LOGIN_PAGE)
        form_data = {
            'TextBox1': 'Please Log In',
            'ButtLogin': 'Log In',
            'txtUserName': self.username,
            'txtPassword': self.password
            }
        # Add hidden input fields from earlier
        form_data.update(self.extract_viewstate_from_login_page(get_request))
        post_request = self.session.post(self.urls.LOGIN_PAGE, 
                                         data = form_data,
                                         allow_redirects=False)
        self.is_logged_in = 'Location' in post_request.headers \
                       and post_request.headers['Location'] == '/mstr7.aspx'
        #if self.is_logged_in:
            #self.cookie_manager.save(self.session)
        return self.is_logged_in

    def extract_viewstate_from_login_page(self, request):
        soup = BeautifulSoup(request.text, BS_PARSER)
        inputs = soup.select('input[type=hidden]')
        d = {}
        for input_ in inputs:
            d[input_['name']] = input_['value']
        return d


    def my_schedules(self):
        """Returns future schedules for logged in user in chronological order 
        (near future to distant future)"""
        if not self.is_logged_in:
            self.log_in()
        assert self.is_logged_in, "Could not log in"
        # Fetch page "My Schedules"
        request = self.session.get(self.urls.MY_SCHEDULES)
        soup = BeautifulSoup(request.text, BS_PARSER)

        schedules = []
        for tr in soup.select('#ctl00_ContentPlaceHolder1_GridView1')[0]\
                      .contents[2:-1]:
            s = Schedule()
            c = lambda i : tr.contents[i].text
            s.id = c(2)
            s.tail_number = 'N' + c(3)
            s.start_dt = self.parse_dt(c(4)) 
            s.end_dt = self.parse_dt(c(5)) 
            s.pilot = c(6)
            s.cfi = c(7)
            note = c(8)
            if note != '\xa0':
                s.note = note
            schedules.append(s)
        return schedules


    def parse_dt(self, text):
        naive = datetime.datetime.strptime(text, self.DT_FORMAT)
        if self.timezone:
            return self.timezone.localize(naive)
        else:
            return naive



    class Settings:

        def __init__(self):
            config = configparser.ConfigParser()
            settings_file_path = absolute_filename('settings.ini')
            config.read(settings_file_path)
            self.base_url = config['scraper']['url']
            self.username = config['scraper']['username']
            self.password = config['scraper']['password']
            self.timezone = config['scraper']['timezone']
            if not self.base_url or not self.username or not self.password:
                raise ValueError('Mandatory scraper settings missing'
                                 ' or unredable')

