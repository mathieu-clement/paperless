#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import src as paperless

if paperless.Scraper().is_aircraft_available_before_my_next_flight():
    print('Aircraft AVAILABLE before next flight')
else:
    print('Aircraft BUSY before next flight')
