#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import absolute_filename

import configparser
import icalendar

class Calendar:

    def __init__(self, schedules):
        if schedules is None or schedules == []:
            raise ValueError('Calendar cannot be empty')

        self.settings = self.Settings()
        self.principal_cfi = self.settings.principal_cfi
        self.fbo_url = self.settings.fbo_url
        self.fbo_address = self.settings.fbo_address

        self.schedules = schedules
        self.cal = icalendar.Calendar()
        self.cal['version'] = '2.0'
        self.cal['prodid'] = '-//TIKTAKTOK//PAPERLESS-ICAL//EN'

        for schedule in schedules:
            self.add_schedule(schedule)


    def write_filename(self, path=absolute_filename('calendar.ics')):
        with open(path, 'wb') as f:
            self.write_file(f)


    def write_file(self, f):
        f.write(self.cal.to_ical())


    def add_schedule(self, schedule):
        self.cal.add_component(self.event(schedule))


    def event(self, schedule):
        event = icalendar.Event()
        event.add('uid', 'PAPERLESS-ICAL-EVENT-' + schedule.id)
        event.add('dtstart', schedule.start_dt)
        event.add('dtend', schedule.end_dt)
        event.add('summary', self.summary(schedule))
        event.add('categories', self.categories(schedule), encode=0)
        # TODO consider using 'uri' property or whatever ends up in iCal in
        # the URL field
        event.add('description','PaperlessFBO: https://{}/'
                                .format(self.fbo_url))
        event.add('location', self.fbo_address)
        event.add('status', 'CONFIRMED')

        return event


    def summary(self, schedule):
        if self.is_flight(schedule):
            summary = 'Flight {}'.format(schedule.tail_number)
            if schedule.cfi != self.principal_cfi:
                summary = summary + ' ({})'.format(schedule.cfi)
        else:
            summary = schedule.tail_number
        return summary


    def categories(self, schedule):
        if self.is_flight(schedule):
            return 'FLIGHT'
        else:
            return schedule.tail_number
        


    def is_flight(self, schedule):
        return schedule.tail_number.startswith('N')


    class Settings:
        def __init__(self):
            config = configparser.ConfigParser()
            settings_file_path = absolute_filename('settings.ini')
            config.read(settings_file_path)
            self.principal_cfi = config['calendar']['principal_cfi']
            self.fbo_url = config['calendar']['fbo_url']
            self.fbo_address = config['calendar']['fbo_address']
