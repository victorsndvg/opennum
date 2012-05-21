#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os



# posible transformar a cadea de ..\files\0.unv a ../files/0.unv

class NameTransform:
    """This class transforms a set of File Names in several directories
    to an enumeration of file names like 0.unv, 1.mfm, ..."""
    def __init__(self, prefix='', dirs='.'):
        self.prefix = prefix
        self.dirs = dirs
        self.cache = {} # old name -> [new name, new path]



    def add_get_file(self, file):
        values = self.cache.get(file)
        if values is None:
            num = len(self.cache)
            base = os.path.basename(file)
            i = base.find('.')
            if i == -1:
                ext = ''
            else:
                ext = base[i:]
            
            values = []
            values.append(unicode(num) + ext)
            values.append(self.prefix + unicode(num) + ext)
                
            self.cache[file] = values

        # debug
        print values[1], '<-', file
            
        return values[1]



    def add_get_dir(self, dir):
        return self.dirs



    def get_cache(self):
        return self.cache
