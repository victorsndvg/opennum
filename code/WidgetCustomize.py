#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import Widget



class WidgetCustomize(wx.BoxSizer):
	def __init__(self, parent, method):
		wx.BoxSizer.__init__(self, wx.VERTICAL)
		self.method = method

		self.entry = wx.TextCtrl(parent, wx.ID_ANY)
		button1 = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_ADD, style=wx.BU_EXACTFIT)
		button2 = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_DEL, style=wx.BU_EXACTFIT)
		button1.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_ADD))
		button2.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_DEL))

		self.b1 = button1.GetId()
		self.b2 = button2.GetId()

		boxh = wx.BoxSizer(wx.HORIZONTAL)
		boxh.Add(self.entry, 1)
		boxh.Add(button1, 0, wx.LEFT, Widget.PIXELS_MARGIN)
		boxh.Add(button2, 0, wx.LEFT, Widget.PIXELS_MARGIN)

		self.Add(boxh, 0, wx.EXPAND, 0)

		button1.Bind(wx.EVT_BUTTON, self.event_button1)
		button2.Bind(wx.EVT_BUTTON, self.event_button2)



	def event_button1(self, event):
		if self.method is not None:
			result = self.method(u'+',self.entry.GetValue())
			if result is None: # se non hai erro
				self.entry.SetValue(u'') # changevalue => 2.7.1



	def event_button2(self, event):
		if self.method is not None:
			self.method(u'-',None)

	#Gestion del foco del widget
	def SetFocus(self):				#añadido
		self.entry.SetFocus()			#añadido

