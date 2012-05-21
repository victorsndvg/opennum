#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs



# window/dialog to ask data for searching node or cell
class WindowSearch(wx.Dialog):

    def __init__(self, parent, data):
        self.parent = parent
        space = 5
        
        datax = data.get('x')
        if datax is None:
            datax = '0.0'
        datay = data.get('y')
        if datay is None:
            datay = '0.0'
        dataz = data.get('z')
        if dataz is None:
            dataz = '0.0'

        wx.Dialog.__init__(self, parent, wx.ID_ANY,
            'Choose coordinates to search',
            style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

        panel = wx.Panel(self, wx.ID_ANY)
        pbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(pbox)
        
        stb = wx.StaticBox(panel, -1, 'Coordinates')
        sbox = wx.StaticBoxSizer(stb, wx.VERTICAL) # takes ownership of stb
        
        pbox.Add(sbox,1,wx.EXPAND|wx.ALL,space)
        
        leftfactor = 1
        rightfactor = 3
        text_style = 0 # wx.ALIGN_RIGHT
        leftflags = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        rightflags = wx.EXPAND
        
        
        fgs = wx.FlexGridSizer(0, 2, 5, 5) #rows cols vgap hgap
        
        
        stt1 = wx.StaticText(panel, -1, 'X: ', style=text_style)
        stt1.SetToolTip(wx.ToolTip(u'X coordinate'))
        self.stx1 = wx.TextCtrl(panel, -1, datax)
        fgs.Add(stt1,leftfactor,leftflags)
        fgs.Add(self.stx1,rightfactor,rightflags)

        stt2 = wx.StaticText(panel, -1, 'Y: ', style=text_style)
        stt2.SetToolTip(wx.ToolTip(u'Y coordinate'))
        self.stx2 = wx.TextCtrl(panel, -1, datay)
        fgs.Add(stt2,leftfactor,leftflags)
        fgs.Add(self.stx2,rightfactor,rightflags)
        
        stt3 = wx.StaticText(panel, -1, 'Z: ', style=text_style)
        stt3.SetToolTip(wx.ToolTip(u'Z coordinate'))
        self.stx3 = wx.TextCtrl(panel, -1, dataz)
        fgs.Add(stt3,leftfactor,leftflags)
        fgs.Add(self.stx3,rightfactor,rightflags)
        
        fgs.AddGrowableCol(1)
        
        sbox.Add(fgs, 1, wx.EXPAND)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel,1,wx.EXPAND)

        sizer  = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if sizer is not None:
            vbox.Add(sizer,0,wx.EXPAND|wx.ALL,space)

        self.SetSizerAndFit(vbox)

        self.Bind(wx.EVT_CLOSE, self.close_event) # so cancelar



    def get_data(self):
        data = {}
        data['x'] = self.stx1.GetValue()
        data['y'] = self.stx2.GetValue()
        data['z'] = self.stx3.GetValue()
        return data



    def close_event(self, event):
        print 'close'
        event.Skip()

