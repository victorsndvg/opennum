#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os



class FileTrack2():
    def __init__(self, filename):
        self.filename = filename
        self.time = None
        self.next = None



    def get_name(self):
        return self.filename



# mark as unmodified up to is_changed self.next value
    def unchange(self):
        if self.next is not None:
            self.time = self.next



# mark as changed
    def change(self):
        self.time = None



    # file changed:  None:inaccesible True:yes False:no
    def is_changed(self):

        # 0/1
        try:
            s = os.stat(self.filename)
        except OSError:
            return None

        self.next = s.st_mtime

        #print u'FILETIME:',self.filename,'old:',self.time,u'new',s.st_mtime

        if self.time is None:
            return True

#        return self.time < s.st_mtime
        return self.time != s.st_mtime
