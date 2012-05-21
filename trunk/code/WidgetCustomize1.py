#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import Widget



class WidgetCustomize1(wx.BoxSizer):
	def __init__(self, parent, method):
		wx.BoxSizer.__init__(self, wx.HORIZONTAL)
		self.method = method

		self.entry = wx.TextCtrl(parent, wx.ID_ANY)
		button1 = wx.Button(parent, wx.ID_ANY, Widget.TXT_BURRON_ADD, style=wx.BU_EXACTFIT)
		button1.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_ADD))

		self.Add(self.entry, 1)
		self.Add(button1, 0, wx.LEFT, Widget.PIXELS_MARGIN)

		button1.Bind(wx.EVT_BUTTON, self.event_button)



	def event_button(self, event):
		if self.method is not None:
			result = self.method(u'+',self.entry.GetValue())
			if result is None: # se non hai erro
				self.entry.ChangeValue(u'') # changevalue => 2.7.1
