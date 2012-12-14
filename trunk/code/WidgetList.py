#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import copy
import config
import Widget
import WidgetCustomize
import WidgetHeader



class WidgetList(Widget.Widget):
    def __init__(self, selection, parent, window, struct, index):
        Widget.Widget.__init__(self, parent, window, struct, index)
        self.selection = selection
	self.parent = parent
        self.names = []
        selected = []
        self.selectedset = set()
        attribs = struct.get_attribs()
        self.has_source = struct.has_source()
        self.is_leaf = struct.get_tag() == u'leaf'
        self.is_customize = attribs.get(config.AT_CUSTOMIZE) == config.VALUE_TRUE and not self.has_source

        if self.has_source:
            elements = self.check_error ( struct.get_elements_with_source(self.menus) )
	    index = 0
	    if len(elements) == 1:						#añadido
		float_range = self.float_range(elements[0][0])			#añadido
		# Si es un rango modificar totalnum
		if float_range[1] != -1:					#añadido
		    self.names += float_range[0].split()			#añadido
		    index += float_range[1]					#añadido
		else:								#añadido
		    self.names.append(elements[0][0])				#añadido
		    index += 1							#añadido
		
	    else:
		for element in elements:
		    if element[1]:
                        selected.append(len(self.names))
                        self.selectedset.add(index)
		    self.names.append(element[0])

        else:
            children = struct.get_children()
            index = 0
            for child in children:
                attribsch = child.get_attribs()
                if attribsch.get(u"selected") == u"true":
                    selected.append(len(self.names))
                    self.selectedset.add(index)
                self.names.append(child.get_name())
                index += 1

        if self.is_customize:
            text = Widget.TXT_CHOOSE_CUSTOMIZE
        else:
            text = Widget.TXT_CHOOSE
        if self.selection == 2:
            text += Widget.TXT_MULTIPLE_SEL
        title = attribs.get(u'title')
        if title is None:
            disp = text + struct.get_name() + Widget.TXT_END_LINE
        else:
            disp = title

        if self.selection == 2:
            style = wx.LB_MULTIPLE
        else:
            style = wx.LB_SINGLE
        self.listbox = wx.ListBox( self, wx.ID_ANY, style=style )

        size1 = 25
        sizet = 100
        test_size = 20 + len(self.names) * size1
        if test_size<=0:
            test_size = size1
        if test_size>sizet:
            test_size = sizet
        if self.is_customize:
            test_size = sizet

        self.listbox.SetMaxSize((-1,test_size)) # FIX
        self.listbox.SetMinSize((-1,test_size)) # FIX
        self.listbox.InsertItems(self.names, 0)

        if self.selection == 2: #multiple
            self.listbox.DeselectAll()
        else:
            self.listbox.SetSelection(wx.NOT_FOUND)

#        if self.selection != 0:
#            for item in selected:
#                self.listbox.Select(item)

        # para que aparezca seleccionado el elemento al crear el widget tambien cuando selection = None
        # tal como está, no aparece debajo el widget que aparecería al pulsar en el elemento
        for item in selected:
            self.listbox.Select(item)

        # para que aparezcan los widgets correspondientes a la seleccion actual
        self.subselect(False)

        self.box = wx.BoxSizer(wx.VERTICAL)

        self.header = WidgetHeader.WidgetHeader(self, disp, attribs.get(u'tooltip'), None, None, struct, window)

        self.box.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)

        if self.is_customize and not self.is_leaf: # names... "porque is_leaf?!!" # leaf non ten defaults
            self.customizer = WidgetCustomize.WidgetCustomize(self, self.event_customize)
            self.box.Add(self.listbox, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
            self.box.Add(self.customizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        else:
            self.box.Add(self.listbox, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)

        self.SetSizerAndFit(self.box)

        self.Bind(wx.EVT_LISTBOX, self.event_list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.event_list)

        self.poputmenu = None
        self.saveditem = None
        if self.is_customize and not self.is_leaf: # por que is leaf e non has_source ???
            self.popupmenu = wx.Menu()
            item = self.popupmenu.Append(-1, 'Delete')
            self.Bind(wx.EVT_MENU, self.rightdelete, item)        
            self.listbox.Bind(wx.EVT_CONTEXT_MENU, self.right)



    def right(self, event):
        pos = event.GetPosition()
        pos = self.listbox.ScreenToClient(pos)
        item = self.listbox.HitTest(pos)
        if item != wx.NOT_FOUND and self.popupmenu is not None:
            self.saveditem = item
            self.listbox.PopupMenu(self.popupmenu) #, pos)
            self.saveditem = None



    def rightdelete(self, event):
        print 'del', self.saveditem
        if self.saveditem is not None:
            self.event_customize(u'-', self.saveditem)



    def save(self):
        pass



    def save_log(self):
        if self.selection != 0:
            offsets = self.listbox.GetSelections()
            offsetsset = set(offsets)
            if offsetsset != self.selectedset:
                names = []
                for offset in offsets:
                    if offset>=0 and offset<len(self.names):
                        names.append(self.names[offset])
                txt = u' '.join(names)
                self.log(txt)



    def save_mem(self):
        if self.has_source: # => not customize
            elements = []
            offsets = self.listbox.GetSelections()
            for offset in offsets:
                if offset>=0 and offset<len(self.names):
                    elements.append(self.names[offset])
#            self.struct.set_elements_with_source(self.menus, elements)
#            now does not reread sources
            self.struct.set_elements(elements)
        else:
            if self.selection != 0:
                children = self.struct.get_children()
                offsets = self.listbox.GetSelections()
                offsetsset = set(offsets)
                i = 0
                for child in children:
                    attribs = child.get_attribs()
                    if u"selected" in attribs:
                        del attribs[u"selected"]
                    if i in offsetsset:
                        attribs[u"selected"] = u"true"
                    i += 1

        # updates tabular data, if any
        self.header.update_tabular()



    def subselect(self, savemem=True):
        if savemem:
            self.save_mem() # maybe 'can' modify children ...

        self.struct.apply_to_all_plots(self.window.panelB.update)
        self.struct.call_influences(self.window.panelB.update_from_dependency) # 'punteiros inversos'

        children = self.struct.get_children()
        offsets = self.listbox.GetSelections()
        
        if len(offsets)==1:
            offset = offsets[0]
        else:
            offset = wx.NOT_FOUND

        # event
        if not self.is_leaf:
            if offset != wx.NOT_FOUND and offset>=0 and offset<len(children):
                evt = Widget.EventStructChange(self.GetId(), index=self.index+1, struct=children[offset])
                wx.PostEvent(self, evt)
            else:
                evt = Widget.EventStructChange(self.GetId(), index=self.index+1, struct=None)
                wx.PostEvent(self, evt)



    def event_list(self, event):
        self.subselect()



    def event_customize(self, action, name=None):
        # name é o índice a borrar, se aparece, se non, borrase o seleccionado
        result = None
        if (action == u'-'):
            children = self.struct.get_children()
            if name is None:
                offsets = list(self.listbox.GetSelections())
            else:
                offsets = [name]
            offsets.sort() # important
            offsets.reverse() # important
            last = None
            for offset in offsets:
                if (offset != wx.NOT_FOUND and offset>=0 and offset<len(children)):
                    self.log(u'- '+children[offset].get_name())
                    self.listbox.Delete(offset)
                    self.struct.del_child(offset)
                    last = offset
            if last is not None:
                self.subselect() # important [update plots]
                    
        elif (action == u'+'):
            name = name.strip()
            if (len(name)>0):

                flag = False
                if (flag):
                    print 'ini1s', self.listbox.GetSize(), self.box.GetSize(), self.GetSize()
                    print 'ini1m', self.listbox.GetMinSize(), self.box.GetMinSize(), self.GetMinSize()
                    print 'fin1b', self.listbox.GetBestSize(), '~', self.GetBestSize()

                # comprobación se repetido
                repeated = self.check_repeated(name, self.struct)
                if repeated:
                    return False

                children = self.struct.get_children()
                defaults = self.struct.create_defaults(name)
                for default in defaults:
                    self.listbox.Append(default.get_name())
                    self.struct.add_child(default)
                if len(defaults)>0:
                
                    self.log(u'+ '+name)
    
                    self.listbox.Layout()
                    self.box.Layout()
                    self.Layout()
    
                    self.subselect() # important [update plots]

        return result



    # toogle item == param
    # chamado desde os plots para notificar selección co rato
    def update_from_param(self, param):
        print 'WidgetList:', param
        strs = self.listbox.GetStrings()
        changes = False
        index = 0
        while index < len(strs):
            str = strs[index]
            if str == param:
                if self.listbox.IsSelected(index):
                    self.listbox.Deselect(index)
                else:
                    self.listbox.Select(index)
                changes = True
            index += 1

        if changes:
            self.subselect()

    #Gestion del foco del widget
    def SetFocus(self):							#añadido
        if self.is_customize and self.listbox.GetCount() == 0:		#añadido
            self.customizer.SetFocus()					#añadido
        else:								#añadido
            self.listbox.SetFocus()					#añadido
