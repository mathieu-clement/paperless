#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src as paperless

import datetime
import pdb
import pprint
import pytz
from unittest import TestCase

pp = pprint.PrettyPrinter(indent=4)

class TestScraper(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = paperless.Scraper()

    def assertIsNotNoneOrEmpty(self, value):
        self.assertIsNotNone(value)
        self.assertNotEqual(value, '')

    def assertIsPersonName(self, value):
        self.assertRegex(value, '^.+?, .+?$')

    def test_my_schedules(self):
        schedules = self.scraper.my_schedules()
        self.assertIsNotNone(schedules)
        self.assertIsNot(schedules, [])
        self.assertLess(len(schedules), 50)

        # Init
        prev_pilot = schedules[0].pilot

        # Let's check that each schedule has valid data in it
        
        for schedule in schedules:
            pp.pprint(schedule)

            # ID and tail number
            self.assertIsNotNoneOrEmpty(schedule.id)
            self.assert_schedule_tail_number(schedule)

            # Person names
            self.assertIsPersonName(schedule.cfi)
            self.assertIsPersonName(schedule.pilot)

            # Check pilot is always the same
            self.assertEqual(schedule.pilot, prev_pilot)
            prev_pilot = schedule.pilot

            self.assert_schedule_times(self. schedule)

            # if schedule.note is defined, it shouldn't be ''
            self.assertIsNot(schedule.note, '')


    def test_aircraft_schedules(self):
        schedules = self.scraper.aircraft_schedules('12234')
        
        self.assertIsNotNone(schedules)
        self.assertIsNot(schedules, [])
        self.assertGreater(len(schedules), 10)

        prev_tail_number = schedules[0].tail_number

        for schedule in schedules:
            pp.pprint(schedule)

            self.assert_schedule_tail_number(schedule)
            
            self.assertEqual(schedule.tail_number, prev_tail_number)
            prev_tail_number = schedule.tail_number

            self.assertIsPersonName(schedule.pilot)
            
            self.assertIsNotNone(schedule.start_dt)
            self.assertIsNotNone(schedule.start_dt.tzinfo)
            self.assertIsNotNone(schedule.end_dt)
            self.assertIsNotNone(schedule.start_dt.tzinfo)
            self.assertEqual(schedule.start_dt.day, schedule.end_dt.day)
            self.assertEqual(schedule.start_dt.month, schedule.end_dt.month)
            self.assertEqual(schedule.start_dt.year, schedule.end_dt.year)
            self.assertEqual(schedule.start_dt.tzinfo, schedule.end_dt.tzinfo)


    def assert_schedule_tail_number(self, schedule):
        self.assertIsNotNoneOrEmpty(schedule.tail_number)
        self.assertGreater(len(schedule.tail_number), 1)
        assert schedule.tail_number.startswith('N') \
               or schedule.tail_number == 'GROUND'


    def assert_schedule_times(self, schedule, 
                              max_length=4,
                              min_start_hour=9, max_end_hour=19):
        # Datetime checks
        # Timezone is set
        self.assertIsNotNone(schedule.start_dt.tzinfo)
        self.assertIsNotNone(schedule.end_dt.tzinfo)
        # Check flight length
        four_hours = datetime.timedelta(hours = max_length)
        schedule.end_dt <= schedule.start_dt + four_hours
        # Check start time
        start_hour = schedule.start_dt.hour
        self.assertGreaterEqual(start_hour, min_start_hour)
        # Check end time
        end_hour = schedule.end_dt.hour
        end_minute = schedule.end_dt.minute
        if end_hour == max_end_hour:
            self.assertEqual(end_minute, 0)
        self.assertLessEqual(end_hour, max_end_hour)





