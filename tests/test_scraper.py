#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src as paperless

import datetime
import pdb
import pprint
import pytz
from unittest import TestCase, skip

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


    def test_next_flight_is_in_the_future(self):
        # Next flight must end in the future
        self.assertGreater(self.scraper.my_next_flight().end_dt, 
                           datetime.now())


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


class TestAircraftAvailable(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = paperless.Scraper()


    def available(self, pilot_schedules, aircraft_schedules):
        return self.scraper.is_aircraft_available_before_flight(
                pilot_schedules, aircraft_schedules)


    def test_next_flight_not_found_should_raise(self):
        acft_schedules = self.make_aircraft_schedules([
            # pilot       tail_num  d  hr  m  hr  m
            ['Smith, John', '9876', 6, 14, 0, 16, 0]
            ])[0]
        with self.assertRaises(Exception):
            self.available(None, acft_schedules)
    

    def test_aircraft_schedules_not_found_should_raise(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = []
        with self.assertRaises(Exception):
            self.available(pilot_schedules, acft_schedules)

    def test_next_flight_different_pilot_should_raise(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Attica, Mark', '9876', 5, 14, 0, 16, 0]])
        with self.assertRaises(Exception):
            self.available(pilot_schedules, acft_schedules)

    @skip
    def test_next_flight_different_time_same_pilot_should_raise(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', '9876', 5, 15, 0, 16, 0]])
        with self.assertRaises(Exception):
            self.available(pilot_schedules, acft_schedules)


    def test_next_flight_same_time_different_day_should_raise(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', '9876', 6, 14, 0, 16, 0]])
        with self.assertRaises(Exception):
            self.available(pilot_schedules, acft_schedules)
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', '9876', 4, 14, 0, 16, 0]])
        with self.assertRaises(Exception):
            self.available(pilot_schedules, acft_schedules)


    def test_airplane_free_less_than_15_minutes_before_is_not_available(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Karuak, Justine', '9876', 5, 10, 0, 13, 50],
            ['Smith, John',     '9876', 5, 14, 0, 16, 0]
            ])
        self.assertFalse(self.available(pilot_schedules, acft_schedules))


    def test_airplane_free_exactly_15_minutes_before_is_available(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Karuak, Justine', '9876', 5, 10, 0, 13, 45],
            ['Smith, John',     '9876', 5, 14, 0, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))
    

    def test_airplane_free_exactly_15_minutes_before_is_available_min_30(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 30, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Karuak, Justine', '9876', 5, 10, 0, 14, 0],
            ['Smith, John',     '9876', 5, 14, 30, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))
    

    def test_airplane_free_exactly_15_minutes_before_next_day_is_available(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 6, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Karuak, Justine', '9876', 5, 10, 0, 13, 45],
            ['Karuak, Justine', '9876', 6, 10, 0, 13, 45],
            ['Smith, John',     '9876', 6, 14, 0, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))
    

    def test_airplane_free_more_than_15_minutes_before_is_available(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Karuak, Justine', '9876', 5, 10, 0, 13, 44],
            ['Smith, John',     '9876', 5, 14, 0, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))
    

    def test_first_acft_flight_is_pilot_flight(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', '9876', 5, 14, 0, 16, 0],
            ['Smith, Kirk', '9876', 5, 16, 0, 19, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))
    

    def test_second_acft_flight_is_pilot_flight_at_same_time(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, Kirk', '9876', 4, 14, 0, 16, 0],
            ['Smith, Mark', '9876', 5, 13, 0, 13, 55],
            ['Smith, John', '9876', 5, 14, 0, 16, 0],
            ])
        self.assertFalse(self.available(pilot_schedules, acft_schedules))


    def test_tail_number_canonicalization1(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John', '1234')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', 'N1234', 5, 14, 0, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))

    
    def test_tail_number_canonicalization2(self):
        pilot_schedules = self.make_pilot_schedules([
        #    d  hr  m  hr  m
            ['9876', 5, 14, 0, 16, 0]
            ], 'Smith, John', 'N1234')[0]
        acft_schedules = self.make_aircraft_schedules([
            ['Smith, John', '1234', 5, 14, 0, 16, 0]
            ])
        self.assertTrue(self.available(pilot_schedules, acft_schedules))

    
    def make_aircraft_schedules(self, times):
        # times is [ [pilot, tail_number, day, 
        # start_hour, start_minute, end_hour, end_minute]... ]
        # see below
        schedules = []
        tz = pytz.timezone('America/Los_Angeles')

        counter = 1
        for t in times:
            pilot = t[0]
            tail_number = t[1]
            day = t[2]
            start_hour = t[3]
            start_minute = t[4]
            end_hour = t[5]
            end_minute = t[6]

            s = paperless.Schedule()
            s.id = str(counter)
            counter = counter + 1
            s.tail_number = tail_number
            s.start_dt = tz.localize(datetime.datetime(
                1991, 11, day, start_hour, start_minute))
            s.end_dt = tz.localize(datetime.datetime(
                1991, 11, day, end_hour, end_minute))
            s.pilot = pilot 
            s.cfi = 'Stewart, Michael'
            schedules.append(s)

        return schedules


    def make_pilot_schedules(self, times, pilot='Smith, John', 
                             tail_number='9876'):
        # times is [ [tail_number, day, 
        # start_hour, start_minute, end_hour, end_minute]... ]
        # see below
        schedules = []
        tz = pytz.timezone('America/Los_Angeles')

        counter = 1
        for t in times:
            tail_number = t[0]
            day = t[1]
            start_hour = t[2]
            start_minute = t[3]
            end_hour = t[4]
            end_minute = t[5]

            s = paperless.Schedule()
            s.id = str(counter)
            counter = counter + 1
            s.tail_number = tail_number
            s.start_dt = tz.localize(datetime.datetime(
                1991, 11, day, start_hour, start_minute))
            s.end_dt = tz.localize(datetime.datetime(
                1991, 11, day, end_hour, end_minute))
            s.pilot = pilot
            s.cfi = 'Stewart, Michael'
            schedules.append(s)

        return schedules


