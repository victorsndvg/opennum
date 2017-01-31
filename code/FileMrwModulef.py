#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrw



class FileMrwModulef(FileMrw.FileMrw):

    def __init__(self, callback=None):
        FileMrw.FileMrw.__init__(self, callback)
        self.numElements = []
        self.numNodes = []
        self.numVertex = []

        self.dim = None
        self.lnn = None
        self.lnv = None
        self.lne = None
        self.lnf = None

        self.mm = []
        self.nrc = []
        self.nra = []
        self.nrv = []
        self.z = []
        self.nsd = []

    def GetValues(self):
        print 'self.numElements ' + unicode((self.numElements))
        print 'self.numNodes ' + unicode((self.numNodes))
        print 'self.numVertex ' + unicode((self.numVertex))
        print 'self.mm ' + unicode(len(self.mm))
        print 'self.nrc ' + unicode(len(self.nrc))
        print 'self.nra ' + unicode(len(self.nra))
        print 'self.nrv ' + unicode(len(self.nrv))
        print 'self.z ' + unicode(len(self.z))
        print 'self.nsd ' + unicode(len(self.nsd))
            
        
    def write1dArray(self,array,openfile):
        if (len(array) == 0):
            return -1
        for x in array:
            openfile.write(unicode(x) + ' ')
        openfile.write('\n')
        return 0

    
    def save2(self,openfile):

        info = [self.numElements,self.numNodes,self.numVertex,self.dim,self.lnn,self.lnv,self.lne,self.lnf]
        if self.write1dArray(info,openfile) == 0: pass#print 'escribe nel,nnod,nver,dim,lnn,lnv,lne,lnf'
        if self.write1dArray(self.mm,openfile) == 0: pass#print 'escribe mm'
        if self.write1dArray(self.nrc,openfile) == 0: pass#print 'escribe nrc'
        if self.write1dArray(self.nra,openfile) == 0: pass#print 'escribe nra'
        if self.write1dArray(self.nrv,openfile) == 0: pass#print 'escribe nrv'
        if self.write1dArray(self.z,openfile) == 0: pass#print 'escribe z'
        if self.write1dArray(self.nsd,openfile) == 0: pass#print 'escribe nsd'

        return True

