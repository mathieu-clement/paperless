#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src as paperless

schedules = paperless.Scraper().my_schedules()
calendar = paperless.Calendar(schedules)
calendar.write_filename('paperless.ics')
