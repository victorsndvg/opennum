#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import os
import sys
import logging



class Process():



    def __init__(self, parent):
        self.parent = parent
        self.process = None
        self.process_pid = None
        self.process_out = None
        self.process_err = None
        self.process_in = None



    def is_running(self):
        return self.process is not None



    def start(self, command, stdin):
        if self.process is not None:
            #print u'process: busy' #code prior version 0.0.1
            logging.warning(u'process: busy')
            return False

        #print 'process: executing', command, #code prior version 0.0.1
        logging.debug(u'process: executing'+unicode(command))
        if stdin is not None:
            #print 'with', stdin #code prior version 0.0.1
            logging.debug(u'with: executing'+unicode(stdin))
        #else:
            #print #code prior version 0.0.1
            
        self.process = wx.Process(self.parent)
        self.process.Redirect()
        self.process_pid = wx.Execute(command, wx.EXEC_ASYNC, self.process)
        #print u'process: exec', self.process_pid #code prior version 0.0.1
        logging.debug(u'process: exec'+unicode(self.process_pid))
        if self.process_pid==0:
            #print u'process: error' #code prior version 0.0.1
            logging.error(u'process: error')
            #self.process_clear() # fallaba aqui
            self.ended() # parece ser buen reemplazo para lo anterior
            return None
        self.process_in = self.process.GetOutputStream()
        #print u'stream pread', stream
        if self.process_in is not None and stdin is not None:
            #print u'process: write', self.process_in.write(stdin), self.process_in.LastWrite() #code prior version 0.0.1
            logging.debug(u'process: write'+unicode(self.process_in.write(stdin))+unicode(self.process_in.LastWrite()))
        self.process.CloseOutput()
        self.process_out = self.process.GetInputStream()
        self.process_err = self.process.GetErrorStream()
        #print u'stream pwrite', self.process_out
        #print u'stream perror', self.process_err
        return True



    def ended(self):
        self.process_out = None
        self.process_err = None
        self.process_in = None
        self.process.Destroy()
        del self.process
        self.process = None
        self.process_pid = None



    def kill(self):
        if self.process is not None:
            #pid = self.process.GetPid()
            #print pid, self.process_pid
            if self.process_pid is not None and self.process_pid > 0:
                #print u'process: SIGTERM', wx.Process.Kill(self.process_pid, wx.SIGTERM) #code prior version 0.0.1
                logging.debug(u'process: SIGTERM'+unicode(wx.Process.Kill(self.process_pid, wx.SIGTERM)))
                if os.name == u'nt':
                    #print u'process: SIGKILL', wx.Process.Kill(self.process_pid, wx.SIGKILL) #code prior version 0.0.1
                    logging.debug(u'process: SIGKILL'+unicode(wx.Process.Kill(self.process_pid, wx.SIGKILL)))



    def read(self):
        txt = u''
        if self.process is not None:
            if self.process_out is not None:
                while self.process.IsInputAvailable():
                    txt += self.tryunicode(self.process_out.read())
                    #print u'process: read', self.process_out.LastRead() #code prior version 0.0.1
                    logging.debug(u'process: read'+unicode(self.process_out.LastRead()))
            if self.process_err is not None:
                while self.process.IsErrorAvailable():
                    txt += self.tryunicode(self.process_err.read())
                    #print u'process: error', self.process_err.LastRead() #code prior version 0.0.1
                    logging.debug(u'process: error'+unicode(self.process_err.LastRead()))
        return txt



    def readstdout(self):
        txt = ''
        if self.process is not None:
            if self.process_out is not None:
                while self.process.IsInputAvailable():
                    txt += self.process_out.read()
        return txt



    def readstderr(self):
        txt = ''
        if self.process is not None:
            if self.process_err is not None:
                while self.process.IsErrorAvailable():
                    txt += self.process_err.read()
        return txt



    @staticmethod
    def tryunicode(str):
        txt = u''
        try:
            txt += str
        except UnicodeDecodeError, u:
            #print 'process: UnicodeDecodeError1', u #code prior version 0.0.1
            logging.debug(u'process: UnicodeDecodeError1'+unicode(u))
            try:
                #txt += unicode(str,sys.getfilesystemencoding()) # o getdefaultencoding ?
                txt += unicode(str, errors='ignore')
                #txt += unicode(str, errors='replace') # non vai
            except UnicodeDecodeError, u:
                #print 'process: UnicodeDecodeError2', u #code prior version 0.0.1
                logging.debug(u'process: UnicodeDecodeError2'+unicode(u))
                txt += "unicode?"
        return txt
