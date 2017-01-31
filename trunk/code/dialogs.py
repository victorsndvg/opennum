#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import os
import os.path
import config



def get_folder(parent, path_initial):
    #|wx.DD_NEW_DIR_BUTTON #segfault
    dialog = wx.DirDialog(parent, u"Select a folder", path_initial, wx.RESIZE_BORDER)
    result = dialog.ShowModal()
    path = None
    if (result == wx.ID_OK):
        path = dialog.GetPath()
    dialog.Destroy()
    dialog = None
    return path



def get_file(parent, path_initial, file_extensions=None):
    (dir_name,file_name) = os.path.split(path_initial)
#    "Estes Ficheiros(*.py;*.txt)|*.py;*.txt"
    if dir_name == "": # para que apareza no directorio actual se estaba nel
        dir_name = "."
    if file_extensions is None:
        dialog = wx.FileDialog(parent, u"Select a file", dir_name, file_name, style=wx.OPEN)
    else:
        dialog = wx.FileDialog(parent, u"Select a file", dir_name, file_name, file_extensions, style=wx.OPEN)
    result = dialog.ShowModal()
    file = None
    if (result == wx.ID_OK):
        file = dialog.GetPath()
    dialog.Destroy()
    dialog = None
    return file



def get_file_save(parent, dir_name, file_name, file_extensions=None, title=None):
#    "Estes Ficheiros(*.py;*.txt)|*.py;*.txt"
    if title == None:
        title = u"Select a file to save"
    if file_extensions is None:
        dialog = wx.FileDialog(parent, title, dir_name, file_name, style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
    else:
        dialog = wx.FileDialog(parent, title, dir_name, file_name, file_extensions, style=wx.SAVE|wx.FD_OVERWRITE_PROMPT)
    result = dialog.ShowModal()
    file = None
    ext_selected = None
    if (result == wx.ID_OK):
        file = dialog.GetPath()
        ext_selected = dialog.GetFilterIndex()
    dialog.Destroy()
    dialog = None
    return [file,ext_selected]



def show_info(parent, txt):
    dialog = wx.MessageDialog(parent, txt, u'Info', wx.OK | wx.ICON_INFORMATION)
    dialog.ShowModal()
    dialog.Destroy()
    dialog = None



def show_error(parent, txt):
    dialog = wx.MessageDialog(parent, txt, u'Error', wx.OK | wx.ICON_ERROR)
    dialog.ShowModal()
    dialog.Destroy()
    dialog = None



def ask_yes_no(parent, txt):
    dialog = wx.MessageDialog(parent, txt, u'Question', wx.YES_NO | wx.NO_DEFAULT)
    result = dialog.ShowModal()
    dialog.Destroy()
    dialog = None
    return result == wx.ID_YES



def ask_ok_cancel(parent, txt):
    dialog = wx.MessageDialog(parent, txt, u'Warning', wx.OK | wx.CANCEL)
    result = dialog.ShowModal()
    dialog.Destroy()
    dialog = None
    return result == wx.ID_OK



def about(name, path):

        if name.lower() == 'maxfem':
            description = name + """ is an interface for electromagnetic simulation"""
        elif name.lower() == 'menum':
            description = name + """ is a reconfigurable interface"""
        elif name.lower() == 'opennum':
            description = name + """ is a reconfigurable interface"""
        else:
            description = name + """ is a reconfigurable interface"""
            

        licence = name + """ is free software; you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the Free Software Foundation; 
either version 2 of the License, or (at your option) any later version.

""" + name + """ is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have received a copy of 
the GNU General Public License along with File Hunter; if not, write to 
the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"""

        info = wx.AboutDialogInfo()

#        info.SetIcon(wx.Icon(os.path.join(path , os.pardir, condig.DIR_IMAGES, u'chispa2_t.png'), wx.BITMAP_TYPE_PNG))
        info.SetName(name)
        info.SetVersion('0.5.9')
        info.SetDescription(description)
        info.SetCopyright('(C) 2009,2010 dma')
        info.SetWebSite('http://www.example.com')
        info.SetLicence(licence)
        info.AddDeveloper('someone')
        info.AddDocWriter('someone')
        info.AddArtist('another one')
        info.AddTranslator('another one')

        wx.AboutBox(info)
