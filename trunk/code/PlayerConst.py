#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Player.py
# PlayerConst.py


import wx_version
import wx



class PlayerConst():

    def __init__(self, plot, timemanager):
        self.plot = plot
        self.timemanager = timemanager
        self.counter = wx.StopWatch()

        self.timei = None
        self.timef = None
        self.duration = None
        self.times = []

        self.started = False
        self.paused = False
        
        self.direction = 1 # 1 or -1
        self.position = None # actual
        self.positionI = 0 # primeiro
        self.positionF = 0 # ultimo



    def stop(self):
        self.timei = None
        self.timef = None
        self.duration = None
        self.started = False
        self.paused = False
        self.counter.Pause()



    def start(self, timei, timef, duration, times):
        self.timei = timei
        self.timef = timef
        self.duration = duration
        self.times = times

        self.counter.Start()
        self.started = True
        self.paused = False

        if timei < timef:
            self.direction = 1
            self.position = None
            self.positionI = 0
            self.positionF = len(self.times) - 1
            while self.positionI >= 0 and self.positionI < len(times) and \
                self.times[self.positionI].get('time') < self.timei:
                    self.positionI += 1
            while self.positionF >= 0 and self.positionF < len(times) and \
                self.times[self.positionF].get('time') > self.timef:
                    self.positionF -= 1
        elif timei > timef:
            self.direction = -1
            self.position = None
            self.positionI = len(self.times) - 1
            self.positionF = 0
            while self.positionI >= 0 and self.positionI < len(times) and \
                self.times[self.positionI].get('time') > self.timei:
                    self.positionI -= 1
            while self.positionF >= 0 and self.positionF < len(times) and \
                self.times[self.positionF].get('time') < self.timef:
                    self.positionF += 1
        else:
            self.direction = 0
            self.position = 0
            self.positionI = 0
            self.positionF = 0
            # tempo asociase a mesma ou seguinte posicion
            while self.position >= 0 and self.position < len(times) and \
                self.times[self.position].get('time') < self.timei:
                    self.position += 1
            self.positionI = self.position
            self.positionF = self.position
            self.position = None

        print 'dir', self.direction, 'pos', self.position, 'posI', self.positionI, 'posF', self.positionF



    def start_or_continue(self, timei, timef, duration, times):
        equals = timei == self.timei and timef == self.timef and self.duration == duration
        if self.paused and self.started and equals:
            self.continue_()
            return 1
        else:
            self.start(timei, timef, duration, times)
            return 0


    def pause(self):
        if self.paused or not self.started:
            return
        self.paused = True
        self.counter.Pause() # recursivo con resume


    def continue_(self):
        if not self.paused or not self.started:
            return
        self.paused = False
        self.counter.Resume() # recursivo con pause


    def reset(self):
        pass


    def step(self):
        time = self.counter.Time()
        #print 'step', time
        if self.duration is None: # innecesario
            return False

        if time >= self.duration * 1000.0:
            fraction = 1.0
        else:
            fraction = time / (self.duration * 1000.0)

        # value: valor que lle tocaria
        if self.direction == 0:
            value = self.positionI # intervalo baleiro
        elif self.direction == 1:
            value = self.positionI + long(fraction * (self.positionF - self.positionI))
        elif self.direction == -1:
            value = self.positionI - long(fraction * (self.positionI - self.positionF))

        done = False
        if self.position is None:
            self.position = self.positionI
            done = True
        else:
            if self.direction == 1:
                if self.position < value:
                    self.position += 1
                    done = True
            elif self.direction == -1:
                if self.position > value:
                    self.position -= 1
                    done = True
            elif self.direction == 0: # innecesario
                if self.position != value:
                    self.position = value
                    done = True

        can_end = self.position == self.positionF

        if done:
            print 'step ms', time
            self.plot.time_goto_step(self.position)

        if time >= self.duration * 1000.0 and can_end:
            self.stop()
            return False

        return True

