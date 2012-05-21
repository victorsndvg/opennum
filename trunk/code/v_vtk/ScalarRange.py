#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx



# para evitar actualizacións múltiples
# 1º cambiar rango
# 2º cambiar modo se é necesario



class ScalarRange():

    def __init__(self, obj):

        self.handler = obj[0]
        self.plot = obj[1] # not necessary
        
        self.mode = 0 # 0 local 1 imposed
        self.mode_mutable = True # True: mutable mode ; False: inmutable mode
        # ben a 'None' porque asi, ainda que se cambie de modo antes de plot.is_done(), non se actualiza
        self.local = None
        self.imposed = None



    def local_get(self):
        return self.local



    def mode_get(self):
        return self.mode



    def mode_mutable_get(self):
        return self.mode_mutable



    def mode_mutable_set(self, value):
        self.mode_mutable = value



    # public
    def local_set(self, range):
        self.local = range
        if self.mode == 0:
            self.handler(self.local)



    # public
    def imposed_set(self, range):
        self.imposed = range
        if self.mode == 1:
            self.handler(self.imposed)



    # public
    def mode_set(self, mode):
        if not self.mode_mutable:
            return
        if self.mode == mode:
            return
        self.mode = mode
        self.update1()



    def update1(self):
        if self.mode == 0:
            self.handler(self.local)
        elif self.mode == 1:
            self.handler(self.imposed)
