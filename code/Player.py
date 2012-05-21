#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Player.py
# PlayerConst.py


import wx_version
import wx



class Player():

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
        self.position = 0 # seguinte que toca



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

#        print 'times', times # todos

        self.counter.Start()
        self.started = True
        self.paused = False

        if timei < timef:
            self.direction = 1
            self.position = 0
            while self.position >= 0 and self.position < len(times) and \
                self.times[self.position].get('time') < self.timei:
                    self.position += 1
        elif timei > timef:
            self.direction = -1
            self.position = len(self.times) - 1
            while self.position >= 0 and self.position < len(times) and \
                self.times[self.position].get('time') > self.timei:
                    self.position -= 1
        else:
            self.direction = 0
            self.position = 0
            while self.position >= 0 and self.position < len(times) and \
                self.times[self.position].get('time') < self.timei:
                    self.position += 1
        print 'dir', self.direction, 'pos', self.position



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

        can_end = False

        if time >= self.duration * 1000.0:
            fraction = 1.0
        else:
            fraction = time / (self.duration * 1000.0)

        # value: valor que lle tocaria
        if self.direction == 0:
            value = self.timei # intervalo baleiro
        else:
            value = self.timei + fraction * (self.timef - self.timei)


        # facendo o bucle, vese ben o obxecto e a escala, pero non deixa interaccionar
        # (será porque o bucle de eventos non itera)
        #done = True
        #while done:
        if True:
            done = False
            new_position = None
            if self.direction == 1:
                if self.position < len(self.times) and value >= self.times[self.position].get('time'):
                    new_position = self.position + 1
                    done = True
                else:
                    can_end = True
            elif self.direction == -1:
                if self.position >= 0 and value <= self.times[self.position].get('time'):
                    new_position = self.position - 1
                    done = True
                else:
                    can_end = True
            elif self.direction == 0:
                if self.position < len(self.times) and value >= self.times[self.position].get('time'):
                    new_position = self.position + 1
                    done = True
                else:
                    can_end = True

            if done:
                print 'step ms', time
                self.plot.time_goto_step(self.position)
                self.position = new_position



        if time >= self.duration * 1000.0 and can_end:
            self.stop()
            return False

        # agora: só enteiros
        
        return True
