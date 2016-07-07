#!/usr/bin/env python
# -*- coding: utf-8 -*-



import datetime
import shutil
import logging


class Log():


    filename1 = u'log.txt'
    filename2 = u'log.old.txt'



    def __init__(self):
        self.loggers = []
        self.file = None



    def start(self, problem): # filename
        if self.file is not None:
            end()

        try:
            self.file = open( self.filename1 , "a") # a | w
        except IOError, x:
            print 'Log.py:', repr(x)
            pass

        text = u'LOG START: ' + Log.get_now()
        if isinstance(problem, basestring):
            text += u' ' + problem
        text += u'\n'
        #self.add_text(text) #code prior version 0.0.1
        logging.debug(text)
        return self.file is not None



    def end(self):
        self.add_text(u'LOG END:   '+Log.get_now()+u'\n')
        self.clear_text()
        if self.file is not None:
            self.file.close()
            self.file = None



    def change(self):
        try:
            shutil.move( self.filename1 , self.filename2 )
        except IOError:
            pass



    def add_logger(self, logger):
        self.loggers.append(logger)



    def clear_text(self):
        for logger in self.loggers:
            logger.clear_text()



    def add_text(self, txt):
# does print more that should print
#        txt = txt + '\n'
        # fallou algunha vez ao imprimir datos binarios u'\u2029' u'\u2013'

        # en Windows puede ser incorrecto uft-8, pero otras codificaciones no tienen hat{h} y otros
        txte = txt.encode('utf-8')
        
        if len(txte)>0: # creo que evita bug de imprimir espazos
            #print txte, #code prior version 0.0.1
            logging.debug(txte)
        if self.file is not None:
            self.file.write(txt.encode('utf-8')) # ?
            self.file.flush()
        for logger in self.loggers:
            logger.add_text('ll'+txt)



    @staticmethod
    def get_now():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

