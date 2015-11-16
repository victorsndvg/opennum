#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx



class MainBar(wx.ScrolledWindow):

    def __init__(self, parent, plot):
    
        #wx.Panel.__init__(self, parent, style=wx.HSCROLL)
	wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(1,0)

        self.myparent = parent
        self.plot = plot
        self.parent = self
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.widgets = []

        self.SetSizer(self.sizer)



    def add(self, widget):
        self.widgets.append(widget)



    def actual_add(self):
        """ add current queue and erase queue to allow multiple invocations """
        for w in self.widgets:
            self.sizer.Add(w, 0, wx.ALIGN_CENTER_VERTICAL)
	self.SetSize(self.GetBestSize())
        del self.widgets[:]



    def layout(self):
        self.sizer.Layout()
        self.Layout()
