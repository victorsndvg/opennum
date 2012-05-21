#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs



# window/dialog to ask data for remote execution
class WindowRemote(wx.Dialog):

    def __init__(self, parent, data):
        self.parent = parent
        space = 5
        
        datauser = data.get('user')
        if datauser is None:
            datauser = ''
        datahost = data.get('host')
        if datahost is None:
            datahost = ''
        datapass = data.get('pass')
        if datapass is None:
            datapass = ''
        datakey = data.get('key')
        if datakey is None:
            datakey = ''
        dataqueuing = data.get('queuing')
        if dataqueuing is None:
            dataqueuing = ''

        wx.Dialog.__init__(self, parent, wx.ID_ANY,
            'Choose remote execution parameters',
            style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

        panel = wx.Panel(self, wx.ID_ANY)
        pbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(pbox)
        
        stb = wx.StaticBox(panel, -1, 'SSH Data')
        sbox = wx.StaticBoxSizer(stb, wx.VERTICAL) # takes ownership of stb
        
        pbox.Add(sbox,1,wx.EXPAND|wx.ALL,space)
        
        leftfactor = 1
        rightfactor = 3
        text_style = 0 # wx.ALIGN_RIGHT
        leftflags = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        rightflags = wx.EXPAND
        
        
        fgs = wx.FlexGridSizer(0, 2, 5, 5) #rows cols vgap hgap
        
        
        stt2 = wx.StaticText(panel, -1, 'Host: ', style=text_style)
        stt2.SetToolTip(wx.ToolTip(u'Enter the name or the IP address of the remote machine'))
        self.stx2 = wx.TextCtrl(panel, -1, datahost)
        fgs.Add(stt2,leftfactor,leftflags)
        fgs.Add(self.stx2,rightfactor,rightflags)
        
        stt1 = wx.StaticText(panel, -1, 'User: ', style=text_style)
        stt1.SetToolTip(wx.ToolTip(u'Enter your user name in the remote machine'))
        self.stx1 = wx.TextCtrl(panel, -1, datauser)
        fgs.Add(stt1,leftfactor,leftflags)
        fgs.Add(self.stx1,rightfactor,rightflags)

        stt3 = wx.StaticText(panel, -1, 'Password: ', style=text_style)
        stt3.SetToolTip(wx.ToolTip(u'Enter your password when not using keys'))
        self.stx3 = wx.TextCtrl(panel, -1, datapass, style=wx.TE_PASSWORD)
        fgs.Add(stt3,leftfactor,leftflags)
        fgs.Add(self.stx3,rightfactor,rightflags)
        
        stt4 = wx.StaticText(panel, -1, 'Key file: ', style=text_style)
        stt4.SetToolTip(wx.ToolTip(u'Enter or choose your private key file, if used and not automatically detected'))
        self.stx4 = wx.TextCtrl(panel, -1, datakey)
        fgs.Add(stt4,leftfactor,leftflags)
        fgs.Add(self.stx4,rightfactor,rightflags)

        stt5 = wx.StaticText(panel, -1, '', style=text_style)
        self.stx5 = wx.Button(panel, -1, 'Choose private key file')
        self.stx5.SetToolTip(wx.ToolTip(u'Choose your private key file if not automatically detected'))
        fgs.Add(stt5,leftfactor,leftflags)
        fgs.Add(self.stx5,rightfactor,rightflags)

        stt6 = wx.StaticText(panel, -1, 'Queuing command: ', style=text_style)
        stt6.SetToolTip(wx.ToolTip(u'Enter a command that will be used as the prefix of the solver executable name'))
        self.stx6 = wx.TextCtrl(panel, -1, dataqueuing)
        fgs.Add(stt6,leftfactor,leftflags)
        fgs.Add(self.stx6,rightfactor,rightflags)
        
        fgs.AddGrowableCol(1)
        
        sbox.Add(fgs, 1, wx.EXPAND)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel,1,wx.EXPAND)

        sizer  = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if sizer is not None:
            vbox.Add(sizer,0,wx.EXPAND|wx.ALL,space)

        self.SetSizerAndFit(vbox)

        self.stx5.Bind(wx.EVT_BUTTON, self.button_event)
        self.Bind(wx.EVT_CLOSE, self.close_event)



    def get_data(self):
        data = {}
        data['user'] = self.stx1.GetValue()
        data['host'] = self.stx2.GetValue()
        data['pass'] = self.stx3.GetValue()
        data['key'] = self.stx4.GetValue()
        data['queuing'] = self.stx6.GetValue()
        return data



    def button_event(self, event):
        file = dialogs.get_file(self, self.stx4.GetValue())
        if file is not None:
            self.stx4.ChangeValue(file)



    def close_event(self, event):
        print 'close'
        event.Skip()
