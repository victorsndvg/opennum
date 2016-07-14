#!/usr/bin/env python
# -*- coding: utf-8 -*-



# Choice -> Combo



import wx_version
import wx
import copy
import config
import Widget
import WidgetCustomize0
import WidgetCustomize1
import WidgetHeader
import logging



class WidgetChoice(Widget.Widget):



    def __init__(self, parent, window, struct, index):
        Widget.Widget.__init__(self, parent, window, struct, index)

        self.names = []
        self.selected = wx.NOT_FOUND
        attribs = struct.get_attribs()
        self.has_source = struct.has_source()
        self.is_leaf = struct.get_tag() == u'leaf'
        self.is_customize = attribs.get(config.AT_CUSTOMIZE) == config.VALUE_TRUE and not self.has_source

        if self.has_source:
            elements = self.check_error ( struct.get_elements_with_source(self.menus) )
            for element in elements:
                if element[1]:
                    self.selected = len(self.names)
                self.names.append(element[0])
        else:
            children = struct.get_children()
            for child in children:
                attribsch = child.get_attribs()
                if attribsch.get(u"selected") == u"true":
                    self.selected = len(self.names)
                self.names.append(child.get_name())

        if self.is_customize:
            text = Widget.TXT_CHOOSE_CUSTOMIZE
        else:
            text = Widget.TXT_CHOOSE
        title = attribs.get(u'title')
        if title is None:
            disp = text + struct.get_name() + Widget.TXT_END_LINE
        else:
            disp = title

        self.combobox = wx.Choice( self, choices = names )

        if self.selected != wx.NOT_FOUND:
            self.combobox.SetSelection(self.selected)
# do not auto select 1st (!)
#        elif (len(self.names)>0):
#            self.combobox.SetSelection(0)
        self.subselect(False)

        box = wx.BoxSizer(wx.VERTICAL)
        self.header = WidgetHeader.WidgetHeader(self, disp, attribs.get(u'tooltip'), False, None, struct, window)
        box.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)

        if (self.is_customize and not self.is_leaf):
            customizer0 = WidgetCustomize0.WidgetCustomize0(self, self.event_customize) # -
            customizer1 = WidgetCustomize1.WidgetCustomize1(self, self.event_customize) # +
            boxh = wx.BoxSizer(wx.HORIZONTAL)
            boxh.Add(self.combobox, 1)
            boxh.Add(customizer0, 0, wx.LEFT, Widget.PIXELS_MARGIN)
            box.Add(boxh, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
            box.Add(customizer1, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        else:
            box.Add(self.combobox, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)

        self.SetSizerAndFit(box)

        self.Bind(wx.EVT_CHOICE, self.event_list)



    def subselect(self, changes=True):
        self.save_mem() # maybe 'can' modify children ...

        # poñer dentro de changes ?
        self.struct.apply_to_all_plots(self.window.panelB.update)
        if changes:
            self.struct.call_influences(self.window.panelB.update_from_dependency) # 'punteiros inversos'

        offset = self.combobox.GetSelection()
        children = self.struct.get_children()

        # event
        if not self.is_leaf:
            if (offset != wx.NOT_FOUND and offset>=0 and offset<len(children)):
                evt = Widget.EventStructChange(self.GetId(), index=self.index+1, struct=children[offset])
                wx.PostEvent(self,evt)
            else:
                evt = Widget.EventStructChange(self.GetId(), index=self.index+1, struct=None)
                wx.PostEvent(self,evt)



    def event_list(self, event):
        self.subselect()



    def save_log(self):
        offset = self.combobox.GetSelection()
        if offset != self.selected:
            if self.has_source:
                if offset >= 0 and offset < len(self.names):
                    #self.log(self.names[offset]) #code prior version 0.0.1
                    logging.debug(self.names[offset])
                else:
                    #self.log(u'') #code prior version 0.0.1
                    logging.debug(u'')
            else:
                children = self.struct.get_children()
                if offset >= 0 and offset < len(children):
                    #self.log(children[offset].get_name()) #code prior version 0.0.1
                    logging.debug(children[offset].get_name())
                else:
                    #self.log(u'') #code prior version 0.0.1
                    logging.debug(u'')



    def save_mem(self):
        if self.has_source:
            elements = []
            offset = self.combobox.GetSelection()
            if offset>=0 and offset<len(self.names):
                elements.append(self.names[offset])
#            self.struct.set_elements_with_source(self.menus, elements)
#            now does not reread sources
            self.struct.set_elements(elements)
        else:
            children = self.struct.get_children()
            offset = self.combobox.GetSelection()
            i = 0
            for child in children:
                attribs = child.get_attribs()
                if (u"selected" in attribs):
                    del attribs[u"selected"]
                if (offset == i):
                    attribs[u"selected"] = u"true"
                i = i + 1



    def event_customize(self, action, name=None):

        if (action == u'-'):
            children = self.struct.get_children()
            offset = self.combobox.GetSelection()
            if (offset != wx.NOT_FOUND and offset>=0 and offset<len(children)):
                self.log(u'- '+children[offset].get_name())
                self.combobox.Delete(offset)
                self.struct.del_child(offset)
                if (offset >= len(children)):
                    offset = len(children) - 1
                if (offset >= 0):
                    self.combobox.SetSelection(offset)
                self.subselect()
                    
        elif (action == u'+'):
            name = name.strip()
            if len(name)>0:

                # comprobación se repetido
                repeated = self.check_repeated(name, self.struct)
                if repeated:
                    return False
            
                children = self.struct.get_children()
                defaults = self.struct.create_defaults(name)
                for default in defaults:
                    self.combobox.Append(default.get_name())
                    self.struct.add_child(default)
                if len(defaults)>0:
                    self.log(u'+ '+name)
                    self.combobox.SetSelection(len(children)-1)
                    self.subselect()

        return None

    #Gestion del foco del widget
    def SetFocus(self):				#añadido
        self.combobox.SetFocus()		#añadido
