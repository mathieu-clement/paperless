#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import configparser
import datetime
import pickle
import pdb
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


    def __init__(self, base_url=None, username=None, password=None):
        if not base_url or not username or not password:
            assert not base_url and not username and not password, \
                'if one credential missing then all should be missing'
            base_url, username, password = self.settings()
        self.username = username
        self.password = password
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
            s.id = tr.contents[2].text
            s.tail_number = 'N' + tr.contents[3].text
            s.start_dt = datetime.datetime.strptime(
                    tr.contents[4].text, self.DT_FORMAT) 
            s.end_dt   = datetime.datetime.strptime(
                    tr.contents[5].text, self.DT_FORMAT)
            s.pilot = tr.contents[6].text
            s.cfi = tr.contents[7].text
            note = tr.contents[8].text
            if note != '\xa0':
                s.note = note
            schedules.append(s)
        return schedules


    def settings(self):
        config = configparser.ConfigParser()
        settings_file_path = absolute_filename('settings.ini')
        config.read(settings_file_path)
        base_url = config['scraper']['url']
        username = config['scraper']['username']
        password = config['scraper']['password']
        if not base_url or not username or not password:
            raise ValueError('scraper settings not readable')
        return base_url, username, password

