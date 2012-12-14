#!/usr/bin/env python
# -*- coding: utf-8 -*-



# crea unha cabeceira con texto, tooltip, e posiblemente botóns Show e Help,
# para poñer no widget correspondente a un elemento.



import wx_version
import wx
import config
import Widget
import PanelWidgets



class WidgetHeader(wx.BoxSizer):

    # text: basestring
    # tooltip: None / basestring
    # tabular: T/F/None=auto; needs: window, struct
    # help: T/F/None=auto; needs: window, struct
    # struct: None/struct
    # window: None/window
    def __init__(self, parent, text, tooltip, show, help, struct, window):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
	tabular = None
	plot = None
	#default button size
	buttonsize = [45,29]											#añadido
	#size of buttons and margins
	spacesize = 2*(Widget.PIXELS_MARGIN + PanelWidgets.PIXELS_MARGIN)					#añadido
        if show is None:
            tabular = struct.get_attribs().get(config.AT_SHOW) == config.AT_TABULAR or struct.get_attribs().get(config.AT_SHOW) == config.AT_ALL
            plot = struct.get_attribs().get(config.AT_SHOW) == config.AT_PLOT or struct.get_attribs().get(config.AT_SHOW) == config.AT_ALL
	    if tabular or plot:
		spacesize = spacesize + buttonsize[0]
        if help is None:
            help = struct.get_attribs().get(config.AT_HELPWINDOWDATA) is not None
	    if help:
		spacesize = spacesize + buttonsize[0]
        self.tabular = tabular
        self.window = window
        self.struct = struct

        txt = wx.StaticText(parent, wx.ID_ANY, text)
	# Multiline: resizes the line.
	txt.Wrap(self.window.panelA.Size[0] - spacesize)								#añadido

        if tooltip is not None:
            txt.SetToolTip(wx.ToolTip(tooltip))

        self.Add(txt, 1)

	#Se crea el boton show y se asocia al evento segun la etiqueta sea tabular, plot o all
        if tabular and plot:											#añadido
            button_tabular = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_TABULAR, style=wx.BU_EXACTFIT,size=buttonsize)	#añadido
            button_tabular.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_TABULAR))				#añadido
            button_tabular.Bind(wx.EVT_BUTTON, self.event_all)							#añadido
            self.Add(button_tabular, 0, wx.LEFT, Widget.PIXELS_MARGIN) # revisar marxes				#añadido
	elif tabular:												#añadido
            button_tabular = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_TABULAR, style=wx.BU_EXACTFIT,size=buttonsize)	#añadido
            button_tabular.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_TABULAR))				#añadido
            button_tabular.Bind(wx.EVT_BUTTON, self.event_tabular)						#añadido
            self.Add(button_tabular, 0, wx.LEFT, Widget.PIXELS_MARGIN) # revisar marxes				#añadido
        elif plot:												#añadido
            button_tabular = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_TABULAR, style=wx.BU_EXACTFIT,size=buttonsize)	#añadido
            button_tabular.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_TABULAR))				#añadido
            button_tabular.Bind(wx.EVT_BUTTON, self.event_plot)							#añadido
            self.Add(button_tabular, 0, wx.LEFT, Widget.PIXELS_MARGIN) # revisar marxes				#añadido

        if help:
            button_help = wx.Button(parent, wx.ID_ANY, Widget.TXT_BUTTON_HELP, style=wx.BU_EXACTFIT,size=buttonsize)
            button_help.SetToolTip(wx.ToolTip(Widget.TXT_TOOLTIP_BUTTON_HELP))
            button_help.Bind(wx.EVT_BUTTON, self.event_help)
            self.Add(button_help, 0, wx.LEFT, Widget.PIXELS_MARGIN) # revisar marxes



    def event_tabular(self, event):										#añadido
        self.window.tabular_show(self.struct)									#añadido
	widgets = self.window.panelA.widgets									#añadido
	#Al mostrar la tabla oculta el widget con los valores							#añadido
	#for i in range(self.window.panelA.widgetcounter-1,-1,-1):						#añadido
	#    if widgets[i].get_struct() is self.struct:								#añadido
	#	if i == self.window.panelA.widgetcounter-1:							#añadido
	#	    break											#añadido
	#	self.window.panelA.display_add(self.struct,i)							#añadido
	#	break												#añadido




    def update_tabular(self):
        if self.tabular:
            self.window.tabular_update(self.struct)



    def event_help(self, event):
        self.window.htmlhelp_show(self.struct)



    def event_plot(self, event):										#añadido
    	self.window.graph2d_from_struct(self.struct)								#añadido



    def event_all(self, event):											#añadido
    	self.event_plot(event)											#añadido
	self.event_tabular(event)										#añadido


