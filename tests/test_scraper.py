#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src as paperless

import datetime
import re
from unittest import TestCase

class TestScraper(TestCase):
    def assertIsNotNoneOrEmpty(self, value):
        self.assertIsNotNone(value)
        self.assertNotEqual(value, '')

    def assertIsPersonName(self, value):
        self.assertIsNotNone(re.match('^[A-Z][a-z]+, [A-Z][a-z]+$', value))

    def test_my_schedules(self):
        schedules = paperless.Scraper().my_schedules()
        self.assertIsNotNone(schedules)
        self.assertIsNot(schedules, [])
        self.assertLess(len(schedules), 50)

        # Init
        prev_pilot = schedules[0].pilot

        # Let's check that each schedule has valid data in it

        for schedule in schedules:
            # String checks
            self.assertIsNotNoneOrEmpty(schedule.id)
            self.assertIsNotNoneOrEmpty(schedule.tail_number)
            assert schedule.tail_number.startswith('N') \
                   or schedule.tail_number == 'GROUND'

            # Person names
            self.assertIsPersonName(schedule.cfi)
            self.assertIsPersonName(schedule.pilot)

            # Check pilot is always the same
            self.assertEqual(schedule.pilot, prev_pilot)
            prev_pilot = schedule.pilot

            # Datetime checks
            # the flight is 4 hr or less
            four_hours = datetime.timedelta(hours = 4)
            schedule.end_dt <= schedule.start_dt + four_hours
            # Start is after 9 am
            start_hour = schedule.start_dt.hour
            self.assertGreaterEqual(start_hour, 9)
            # End is before 10 pm
            end_hour = schedule.end_dt.hour
            end_minute = schedule.end_dt.minute
            if end_hour == 22:
                self.assertEqual(end_minute, 0)
            self.assertLessEqual(end_hour, 22)

            # if schedule.note is defined, it shouldn't be ''
            self.assertIsNot(schedule.note, '')


#schedules = ["Schedule('337926','N12234',datetime.datetime(2020, 10, 21, 14, 0),datetime.datetime(2020, 10, 21, 16, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('332806','N12234',datetime.datetime(2020, 10, 24, 14, 0),datetime.datetime(2020, 10, 24, 16, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('332807','N12234',datetime.datetime(2020, 10, 25, 16, 0),datetime.datetime(2020, 10, 25, 18, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335986','N12234',datetime.datetime(2020, 10, 30, 14, 0),datetime.datetime(2020, 10, 30, 16, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335988','N6796H',datetime.datetime(2020, 11, 7, 11, 0),datetime.datetime(2020, 11, 7, 13, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335989','N12234',datetime.datetime(2020, 11, 11, 11, 0),datetime.datetime(2020, 11, 11, 13, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335991','N12234',datetime.datetime(2020, 11, 14, 11, 0),datetime.datetime(2020, 11, 14, 13, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335992','N12234',datetime.datetime(2020, 11, 21, 11, 0),datetime.datetime(2020, 11, 21, 13, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('335993','N12234',datetime.datetime(2020, 11, 22, 11, 0),datetime.datetime(2020, 11, 22, 13, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('337311','N12234',datetime.datetime(2020, 11, 28, 14, 0),datetime.datetime(2020, 11, 28, 16, 0),'Clement, Mathieu','Templeton, Mitchell',None)", "Schedule('337314','N12234',datetime.datetime(2020, 11, 29, 14, 0),datetime.datetime(2020, 11, 29, 16, 0),'Clement, Mathieu','Templeton, Mitchell',None)"]
