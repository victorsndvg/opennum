#!/usr/bin/env python
# -*- coding: utf-8 -*-


class FileParse():



    def __init__(self):
        self.f = None
        self.line = None
        self.index = None
        self.tokens = None
        self.error = ''



    def get_error(self):
        return self.error



    def open(self, filename):
        try:
            self.f = open(filename, 'rt') # con t o sin nada, abre en modo texto (\r\n -> \n)
        except IOError, x:
            self.error = unicode(x)
            return self.error
        return True



    def close(self):
        if self.f is not None:
            try:
                self.f.close()
                self.f = None
            except IOError, x:
                self.error = unicode(x)
                return self.error
        return True



    # false: error ; none: eof
    def getword(self):
        while self.tokens is None or self.index is None or self.index >= len(self.tokens):
            err = self.readline()
            if err is True:
                pass
            elif err is None: 
                return None
            else:
                return False
        if self.index < len(self.tokens):
            i = self.index
            self.index += 1
            return self.tokens[i]



    # descarta lineas leidas parcialmente
    # false: error ; none: eof
    def getline(self):
        #if self.line is None: # no
        if True: #así descarta lineas ya (semi) procesadas
            err = self.readline()
            if err is True:
                pass
            elif err is None: 
                return None
            else:
                return False
        line = self.line
        self.line = None
        self.index = None
        self.tokens = None
        return line



    # internal
    # true: ok
    # none: eof
    # str: error
    def readline(self):
        try:
            self.line = self.f.readline()
            if len(self.line) == 0:
                return None # eof
            self.tokens = self.line.split()
            self.index = 0
        except IOError, x:
            self.error = unicode(x)
            return self.error
        return True



    @staticmethod
    def to_int(str):
        try:
            result = int(str)
            return result
        except ValueError, e:
            return False



    @staticmethod
    def to_float(str):
        try:
            result = float(str)
            return result
        except ValueError, e:
            return False

