#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pathlib


DATA_DIR = os.path.join(str(pathlib.Path.home()), '.paperless')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def absolute_filename(filename):
    return os.path.join(DATA_DIR, filename)
