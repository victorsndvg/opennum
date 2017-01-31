#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import Widget



class WidgetCustomize0(wx.Button):
    def __init__(self, parent, method):
        wx.Button.__init__(self, parent, wx.ID_ANY, Widget.TXT_BUTTON_DEL, style=wx.BU_EXACTFIT)
        self.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_DEL))
        self.method = method
        self.Bind(wx.EVT_BUTTON, self.event_button)



    def event_button(self, event):
        if self.method is not None:
            self.method(u'-',None)
