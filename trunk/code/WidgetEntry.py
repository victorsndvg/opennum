#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import Widget
import WidgetHeader
import config



# para leafs de tipo float, reemplaza estos caracteres por espacios
replace = '[](),'



class WidgetEntry(Widget.Widget):



    def __init__(self, mode, parent, window, struct, index):
        Widget.Widget.__init__(self, parent, window, struct, index)
        self.mode = mode

        #self.password = self.struct.get_attribs().get(config.AT_SUBTYPE) == 'password'
        
        self.replace_set = set()
        for a in replace:
            self.replace_set.add(a)

        self.vali = u" ".join(struct.get_elements())

        attribs = struct.get_attribs()
        title = attribs.get(u'title')
        if title is None:
            disp = Widget.TXT_VALUE + struct.get_name() + Widget.TXT_END_LINE
        else:
            disp = title

        the_style = wx.TE_PROCESS_ENTER
        #if self.password:
        #    the_style |= wx.TE_PASSWORD
        self.entry = wx.TextCtrl(self, wx.ID_ANY, self.vali, style=the_style)

        box = wx.BoxSizer(wx.VERTICAL)
        self.header = WidgetHeader.WidgetHeader(self, disp, attribs.get(u'tooltip'), False, None, struct, window)
        box.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        box.Add(self.entry, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        self.SetSizerAndFit(box)

        self.entry.Bind(wx.EVT_TEXT_ENTER, self.event_enter)
        self.entry.Bind(wx.EVT_KILL_FOCUS, self.event_focus_out)


    def parse_complex(self, string,startchar,endchar,lista):
	"""
	Parse a list of complex and check the syntax. Recursive function.

	string: type String.
	startchar: type Character.
	endchar: type Character.
	list: type List.
	"""

	start = string.find(startchar)
	end = string.find(endchar)

	if start<end and start != -1 and end != -1:
	    complexstr = string[start:end+1]
	    try:
		if complexstr.find(',') == -1 or not len(map(float, complexstr[1:-1].replace(',', ' ').split())) == 2:
		    return -1
		lista.append(complexstr)
		return self.parse_complex(string[end+1:],startchar,endchar,lista)
	    except:
		return -1
	    return 1
	elif (start == -1 and end != -1) or (start != -1 and end == -1):
	    return -1
	else:
	    return 0

    def func(self,string,char):
	index = 0
	lista = []
        while index < len( string ):
	    index = string.find( char, index )
	    if index == -1:
		break
	    lista.append(index)
	    index += 1
	return lista

    def save_mem(self):
        print 'widget entry save mem'
        val = self.entry.GetValue()
        if self.mode == 0: # float
            val2 = self.preprocess_val(val)
            vals = val2.split()
	elif self.mode == 2: #complex
	    vals = []
	    if self.parse_complex(val,'(',')',vals) == -1:
		vals = [val]

        else: # string
            if val == '':
                #vals = []
                vals = [val]
            else:
                vals = [val]

        self.struct.set_elements_nosel(vals)
        self.struct.apply_to_all_plots(self.window.panelB.update)
        self.struct.call_influences(self.window.panelB.update_from_dependency) # 'punteiros inversos'

        # TEMPORARY FIX put here to notify tabular that data may be changed
        parent = self.struct.get_parent()
        if parent is not None:
	    #modificado para el nuevo atributo show (en lugar de tabular)
            if parent.get_attribs().get(config.AT_SHOW) == config.AT_TABULAR: # non imprescindible
                self.window.tabular_update(parent)


    def save_log(self):
        if self.mode == 0: # float
            val1 = self.entry.GetValue()
            val2 = self.preprocess_val(val1)
            val = u' '.join(val2.split())
        else: # string
            val = self.entry.GetValue()
        if val != self.vali:
            #if not self.password:
            self.log(val)



    def event_enter(self, event):
        print 'Entry enter'
        self.save_mem()
        #event.Skip() # non fai nada



    def event_focus_out(self, event):
        print 'Entry focus out'
        self.save_mem()
        #event.Skip() # non fai nada



    # actualiza o contido do widget a partir do struct
    def update_from_struct(self):
        print 'Update widget entry'
        val = u" ".join(self.struct.get_elements())
        self.entry.ChangeValue(val)



    def preprocess_val(self, val):
        out = []
        for char in val:
            if char in self.replace_set:
                out.append(' ')
            else:
                out.append(char)
        return ''.join(out)

    #Gestion del foco del widget
    def SetFocus(self):				#añadido
	self.entry.SetFocus()			#añadido

