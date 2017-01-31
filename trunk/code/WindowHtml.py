#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import wx.html
import os.path



def add_pre(parent, data, configuration, instpath=None):

    modo = 'url'

    if configuration is None:
        return add(parent, data, modo)

    ancho = -1
    alto = -1
    titulo = 'Help'

    configparts = configuration.split(',',3) # maximo 4 partes

    if len(configparts) > 0:
        modo = configparts[0]
        if modo != 'code' and modo != 'frontcode' and modo != 'url' and modo != 'urlinst':
            return 'Invalid mode'
    if len(configparts) > 1 and len(configparts[1])>0:
        try:
            ancho = int(configparts[1])
        except ValueError:
            return 'Invalid width'
    if len(configparts) > 2 and len(configparts[2])>0:
        try:
            alto = int(configparts[2])
        except ValueError:
            return 'Invalid height'
    if len(configparts) > 3:
        titulo = configparts[3]

    # engade prefixo de directorio de instalacion para paths relativos a este
    if modo == 'urlinst':
        if instpath is not None:
            data = os.path.join(instpath, data)
        modo = 'url'

    return add(parent, data, modo, titulo, (ancho,alto))



#    size = (-1, -1)
#    size = (150, -1)
#    size = (-1, 100)
#    size = (200, 200)
def add(parent, data, mode, title='Help', size=(-1,-1)):
    lost = WindowHtml(parent, size, title, mode, data)
    if lost.error is not None:
        lost.Destroy()
    if lost.code == -1: # para evitar duplicacion de mensaxes de erro
        return None
    return lost.error



class WindowHtml(wx.Frame):
    def __init__(self, parent, Size, title, mode, data):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=Size)
        html = wx.html.HtmlWindow(self)
        self.error = None
        self.code = 0

#        if “gtk2″ in wx.PlatformInfo:
#            html.SetStandardFonts()

        ret = None

        if mode == 'code':
            ret = html.SetPage(data)
        elif mode == 'url':
            ret = html.LoadPage(data)
        elif mode == 'frontcode':
            html.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnURLClick)
            ret = html.SetPage(data)

        if ret is True:
            self.Show()
        elif ret is False:
            self.code = -1

        if ret == None:
            self.error = 'Invalid mode b'
        elif ret is False:
            self.error = 'Error loading page'

    def OnURLClick(self,event):
        url = event.GetLinkInfo().GetHref()
        print 'launching ' + url
        wx.LaunchDefaultBrowser(url.replace(' ', '%20')) 
