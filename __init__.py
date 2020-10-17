#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This package logs into the Paperless141 website (tested only with the version
the author's flight club is using), reads the flight schedules from the
user, and returns them in a structured form.

The other part of this package reads that structure and converts it to
calendar events, such that they can be used as an Apple Calendar subscription.


Copyright 2020 Mathieu Clement

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = 'Mathieu Clement'
__copyright__ = 'Copyright 2020, paperless'
__credits__ = []
__license__ = 'Apache License 2.0'
__version__ = '0.0.1'
__maintainer__ = 'Mathieu Clement'
__email__ = 'tiktaktok@users.noreply.github.com'
__status__ = ''

from .core import absolute_filename
from .schedule import Schedule
from .scraper import Scraper
