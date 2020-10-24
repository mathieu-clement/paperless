#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Schedule:
    id = None
    tail_number = None
    start_dt = None
    end_dt = None
    pilot = None
    cfi = None
    note = None

    def __init__(self, id_=None, tail_number=None, start_dt=None, end_dt=None, 
                 pilot=None, cfi=None, note=None):
        self.id = id_
        self.tail_number = tail_number
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.pilot = pilot
        self.cfi = cfi
        self.note = note

    def __repr__(self):
        return repr('Schedule(%s,%s,%s,%s,%s,%s,%s)' % (
            repr(self.id),
            repr(self.tail_number), 
            repr(self.start_dt), 
            repr(self.end_dt), 
            repr(self.pilot),
            repr(self.cfi),
            repr(self.note)
            ))
