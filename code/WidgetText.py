#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import Widget
import WidgetHeader
import Source


class WidgetText(Widget.Widget):



    def __init__(self, parent, window, struct, index):
        Widget.Widget.__init__(self, parent, window, struct, index)

#        self.vali = u" ".join(struct.get_elements())

        attribs = struct.get_attribs()

        self.text = u''
        showfile = attribs.get(u'showfile')
	newpath = self.parse_path_var(showfile, True, struct)
	if newpath is None:
            res = struct.parse_source_string_1(showfile)
	else:
	    res = struct.parse_source_string_1(newpath)

        if res[0] == 1 or res[0] == 2:
            self.filename = res[1]
        else:
            self.filename = None
            unused = self.check_error (u'Error parsing value of showfile attribute')
        if self.filename is not None:
            ben = True
            try:
                f = open(self.filename,'r')
                self.text = f.read()
                f.close()
            except IOError, x: # notificar o usuario
                ben = False
                print 'WidgetText:', repr(x)
            if not ben:
                unused = self.check_error (u'Error reading file: \'' + self.filename + '\'')
        elif res[0] == 1 or res[0] == 2:
            unused = self.check_error (u'No file found')

        title = attribs.get(u'title')
        if title is None:
            disp = Widget.TXT_VALUE + struct.get_name() + Widget.TXT_END_LINE
        else:
            disp = title

        # TE_RICH para que admita textos de más de 64 KB en Windows
        # posible también TE_RICH2
        self.textctrl = wx.TextCtrl(self, wx.ID_ANY, self.text, \
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.TE_RICH )
        self.textctrl.SetMinSize((-1,200))
        
        box = wx.BoxSizer(wx.VERTICAL)
        self.header = WidgetHeader.WidgetHeader(self, disp, attribs.get(u'tooltip'), False, None, struct, window)
        box.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        box.Add(self.textctrl, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        self.SetSizerAndFit(box)

#        self.Bind(wx.EVT_TEXT_ENTER, self.event_enter)

    def parse_path_var(self, path, is_menu, struct, objects=None):
	#No demasiado testeado.
	#Variables permitidas: texto desde leaf. Elemento (solo 1) seleccionado desde struct
        #para construir un nombre de fichero 
        parts = Source.Source.extract_var(path)		

        if isinstance(parts,list):
            if parts[1] is None: # no hay variables
		return None
            else: # hay una variable
                array = struct.get_from_path(parts[1], False, objects, False) #
                if isinstance(array, tuple):
                    txt = u''
		    if len(array) >= 3:
			#Solo permite un elemento seleccionado
			try:
			    sel = array[2][0].get_elements_selected()
                    	    for a in array[0]:
                                # escapar 'a' que proven dun nome e vai ser desescapada
			        if len(array[0])==1 or a == sel[0]:
                                    txt = Source.Source.desescape(parts[0]) + a + Source.Source.desescape(parts[2])
			except:
			    return None
                    return txt
                else:
                    return None
        else:
            return None



#    def save_mem(self):
#        val = self.entry.GetValue()
#        vals = val.split()
#        self.struct.set_elements_nosel(vals)
#        self.struct.apply_to_all_plots(self.window.panelB.update)
#        self.struct.call_influences(self.window.panelB.update_from_dependency) # 'punteiros inversos'



#    def save_log(self):
#        val = u' '.join(self.entry.GetValue().split())
#        if val != self.vali:
#            self.log(val)



#    def event_enter(self, event):
#        self.save_mem()

    #Gestion del foco del widget
    def SetFocus(self):				#añadido
	self.textctrl.SetFocus()		#añadido

