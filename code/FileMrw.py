#!/usr/bin/env python
# -*- coding: utf-8 -*-



class FileMrw():



    def __init__(self, callback=None):
        self.callback = callback
        self.filename = None
        self.attribs = {}



    def read(self, filename, attribs):
        self.filename = filename
        self.attribs = attribs



    def cc(self, txt):
        if self.callback is not None:
            self.callback(txt)



#    @staticmethod
#    def build(typename, callback=None):
#        if typename == u'scalars':
#            return FileMrwScalars.FileMrwScalars(callback)
#        elif typename == u'reconvxx':
#            return FileMrwReconvxx.FileMrwReconvxx(callback)
#        else:
#            return None


    # to-do: ponher o indice da palabra para cada linha

    @staticmethod
    def split(filename):
        tokens = []
        data = {}
        data[u'error'] = None
        data[u'data'] = tokens

        numl = 0
        numt = 0
        f = None
        try:
            f = open(filename, 'rt')
            for line in f:
                temp = line.split()
                tokens.extend(temp)
                numt += len(temp)
                numl += 1
        except IOError, x:
            data[u'error'] = repr(x)
        finally:
            if f is not None:
                f.close()
                f = None

        data[u'lines'] = numl
        data[u'words'] = numt

        return data


# file write open,close


    @staticmethod
    def read_ints(array, index, num):
        if len(array) < index + num: # adicional
            return False
        try:
            result = map(int,array[index:index+num])
            return result
        except ValueError, e:
            return False
        return False



    @staticmethod
    def read_ints_1(array, index, num):
        if len(array) < index + num: # adicional
            return False
        try:
            result = map(lambda x: int(x)-1, array[index:index+num])
            return result
        except ValueError, e:
            return False
        return False



    @staticmethod
    def read_floats(array, index, num):
        if len(array) < index + num: # adicional
            return False
        try:
            result = map(float,array[index:index+num])
            return result
        except ValueError, e:
            return False
        return False



    @staticmethod
    def filewriteopen(filename):
        try:
            f = open(filename, 'wt')
        except IOError, e:
            pass
        else:
            return f
        return False



    @staticmethod
    def fileclose(f):
        try:
            f.close()
        except IOError, e:
            pass
        else:
            return True
        return False



    def save(self, filename):
        f = FileMrw.filewriteopen(filename)
        if f is False:
            return False
        res = self.save2(f)
        FileMrw.fileclose(f)
        return res



    def save2(self, openfile):
        return False



#import FileMrwScalars
#import FileMrwReconvxx
