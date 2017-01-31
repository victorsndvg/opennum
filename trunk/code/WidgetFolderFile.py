#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs
import Widget
import WidgetHeader
import paths



FOLDER = 1
FILE = 2



class WidgetFolderFile(Widget.Widget):
    def __init__(self, ff, parent, window, struct, index):
        Widget.Widget.__init__(self, parent, window, struct, index)
        self.ff = ff

        self.changed = False
        self.val = u''
        elements = struct.get_elements()
        if len(elements)>0:
            self.val = elements[0]

        self.vali = self.val

        attribs = struct.get_attribs()
        title = attribs.get(u'title')
        if title is None:
            disp = Widget.TXT_CHOOSE + struct.get_name() + Widget.TXT_END_LINE
        else:
            disp = title

        self.entry = wx.TextCtrl(self, wx.ID_ANY, self.val, style=wx.TE_READONLY)
        self.button = wx.Button(self, wx.ID_ANY, Widget.TXT_BUTTON_DOTS, style=wx.BU_EXACTFIT)

        boxh = wx.BoxSizer(wx.HORIZONTAL)
        boxh.Add(self.entry, 1)
        boxh.Add(self.button, 0, wx.LEFT, Widget.PIXELS_MARGIN)

        boxv = wx.BoxSizer(wx.VERTICAL)
        self.header = WidgetHeader.WidgetHeader(self, disp, attribs.get(u'tooltip'), False, None, struct, window)
        boxv.Add(self.header, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        boxv.Add(boxh, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, Widget.PIXELS_MARGIN)
        self.SetSizerAndFit(boxv)

        self.Bind(wx.EVT_BUTTON, self.event_button)



    def save_mem(self):
        pass



    def save_log(self):
        if self.changed:
            self.log(self.val)



    def event_button(self, event):
        val = None
        
        file_extensions = None
        
        attribs = self.struct.get_attribs()

        subtype = attribs.get(config.AT_SUBTYPE)

        attribmeshfield = self.parse_mesh_field_string(subtype)

        if attribmeshfield is not None:
            if len(attribmeshfield) == 1:
                if attribs.get(config.AT_SUBTYPE) == u'mesh':
        #            file_extensions = u'All supported (*.mfm;*.unv;*.bdf)|*.mfm;*.unv;*.bdf|Modulef Formatted Meshes (*.mfm)|*.mfm|Universal Files (*.unv)|*.unv|Nastran Input Data File (*.bdf)|*.bdf'
        #            file_extensions = u'All supported (*.mfm;*.unv)|*.mfm;*.unv|Modulef Formatted Meshes (*.mfm)|*.mfm|Universal Files (*.unv)|*.unv'
        #            file_extensions = u'All supported (*.mfm)|*.mfm|Modulef Formatted Meshes (*.mfm)|*.mfm'
                    file_extensions = u'All supported (*.mfm;*.unv;*.vtk;*.vtu;*.pvd)|*.mfm;*.unv;*.vtk;*.vtu;*.pvd|' +\
                        'Modulef Formatted Meshes (*.mfm)|*.mfm|' +\
                        'Universal Files (*.unv)|*.unv|' +\
                        'VTK Unstructured Grid Files (+) (*.vtk)|*.vtk|' +\
                        'VTK XML Unstructured Grid Files (+) (*.vtu)|*.vtu|' +\
                        'PVD Files (*.pvd)|*.pvd|' +\
                        'All Files (*)|*'
                
                if attribs.get(config.AT_SUBTYPE) == u'field':
        #            file_extensions = u'All supported (*.mff;*.vtu)|*.mff;*.vtu|Modulef Formatted Fields (*.mff)|*.mff|VTK XML Point Data Fields on Unstructured Grid (*.vtu)|*.vtu'
                    file_extensions = u'All supported (*.mff;*.vtk;*.vtu)|*.mff;*.vtk;*.vtu|' +\
                        'Modulef Formatted Fields (*.mff)|*.mff|' +\
                        'VTK Unstructured Grid Fields (*.vtk)|*.vtk|' +\
                        'VTK XML Unstructured Grid Fields (*.vtu)|*.vtu|' +\
                        'All Files (*)|*'

                if attribs.get(config.AT_SUBTYPE) == u'data':
                    file_extensions = u'All Files (*)|*'

            if len(attribmeshfield) == 2:
                if attribmeshfield[0] == u'mesh' or attribmeshfield[0] == u'field' or attribmeshfield[0] == u'data':
                    file_extensions = attribmeshfield[1]
        
        if self.ff == FOLDER:
            val = dialogs.get_folder(self.window, self.val)
        elif self.ff == FILE:
            val = dialogs.get_file(self.window, self.val, file_extensions)
        if val is not None:
            self.changed = True

            # para tratar de forma diferente a las rutas de los ficheros dentro del menu materials
            is_materials = False
            a = self.struct
            while a is not None:
                if a.get_data().get(config.IS_MATERIALS):
                    is_materials = True
                    break
                a = a.get_parent()

            relative = (is_materials and config.PATHS_RELATIVE_MATERIALS) or\
                (not is_materials and config.PATHS_RELATIVE)
                
            print 'is_materials', is_materials, 'relative', relative
            
            if relative:
                self.val = paths.relative(val)
            else:
                self.val = val

            self.entry.ChangeValue(self.val) # version >= 2.7.1

            self.struct.set_elements_nosel([self.val])

            self.struct.apply_to_all_plots(self.window.panelB.update)
            
            if self.struct.has_influences():
                dialogs.show_info(self.window, 'Graphics that are associated to this mesh will be updated')

            self.struct.call_influences(self.window.panelB.update_from_dependency) # 'punteiros inversos'

    @staticmethod
    def parse_mesh_field_string(string):
        ret = None
        if string is None:
            return ret
        i = string.find(':')
        if i < 0:
            return [string]
        pre = string[:i]
        post = string[i+1:]
        if pre == u'mesh' or pre == u'field' or pre == u'data':
            return [pre, post]
        else:
            return [string]

    #Gestion del foco del widget
    def SetFocus(self):
        self.button.SetFocus()
        
