#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs
import logging
import sys
import ThreadRemoteQsub



# window/dialog to check status for remote execution
class WindowStatus(wx.Dialog):

    def __init__(self, parent, data):
        self.parent = parent
        space = 5

        self.data = {}
        if data is None:
            self.load_runstatus()
        elif data.get('queuing') == u'get':
            self.load_runstatus()
            self.data['queuing'] = u'get'
        else:
            self.data = data

        if self.data.get('host') is None:
            self.data['host'] = ''
        if self.data.get('user') is None:
            self.data['user'] = ''
        if self.data.get('pass') is None:
            self.data['pass'] = ''
        if self.data.get('key') is None:
            self.data['key'] = ''
        if self.data.get('queuing') is None:
            self.data['queuing'] = ''
        if self.data.get('state') is None:
            self.data['state'] = ''
        if self.data.get('exec_command') is None:
            self.data['exec_command'] = ''
        if self.data.get('local_dir') is None:
            self.data['local_dir'] = ''
        if self.data.get('remote_dir') is None:
            self.data['remote_dir'] = ''
        if self.data.get('job_id') is None:
            self.data['job_id'] = ''

        if self.data.get('queuing') == u'get':
            wx.Dialog.__init__(self, parent, wx.ID_ANY,
                'Get remote execution results',
                style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
        else:
            wx.Dialog.__init__(self, parent, wx.ID_ANY,
                'Check remote execution status',
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
        
        stt1 = wx.StaticText(panel, -1, 'Host: ', style=text_style)
        stt1.SetToolTip(wx.ToolTip(u'Enter the name or the IP address of the remote machine'))
        self.stx1 = wx.TextCtrl(panel, -1, self.data.get('host'), style = wx.TE_READONLY)
        self.stx1.SetBackgroundColour(stt1.GetBackgroundColour())
        fgs.Add(stt1,leftfactor,leftflags)
        fgs.Add(self.stx1,rightfactor,rightflags)
        
        stt2 = wx.StaticText(panel, -1, 'User: ', style=text_style)
        stt2.SetToolTip(wx.ToolTip(u'Enter your user name in the remote machine'))
        self.stx2 = wx.TextCtrl(panel, -1, self.data.get('user'), style = wx.TE_READONLY)
        self.stx2.SetBackgroundColour(stt2.GetBackgroundColour())
        fgs.Add(stt2,leftfactor,leftflags)
        fgs.Add(self.stx2,rightfactor,rightflags)

        stt3 = wx.StaticText(panel, -1, 'Password: ', style=text_style)
        stt3.SetToolTip(wx.ToolTip(u'Enter your password when not using keys'))
        self.stx3 = wx.TextCtrl(panel, -1, self.data.get('pass'), style=wx.TE_PASSWORD)
        fgs.Add(stt3,leftfactor,leftflags)
        fgs.Add(self.stx3,rightfactor,rightflags)
        
        stt4 = wx.StaticText(panel, -1, 'Key file: ', style=text_style)
        stt4.SetToolTip(wx.ToolTip(u'Enter or choose your private key file, if used and not automatically detected'))
        self.stx4 = wx.TextCtrl(panel, -1, self.data.get('key'))
        fgs.Add(stt4,leftfactor,leftflags)
        fgs.Add(self.stx4,rightfactor,rightflags)

        stt5 = wx.StaticText(panel, -1, '', style=text_style)
        self.stx5 = wx.Button(panel, -1, 'Choose private key file')
        self.stx5.SetToolTip(wx.ToolTip(u'Choose your private key file if not automatically detected'))
        fgs.Add(stt5,leftfactor,leftflags)
        fgs.Add(self.stx5,rightfactor,rightflags)

        #stt6 = wx.StaticText(panel, -1, 'Queuing command: ', style=text_style)
        #stt6.SetToolTip(wx.ToolTip(u'Enter a command that will be used to check the job status'))
        #self.stx6 = wx.TextCtrl(panel, -1, self.data.get('queuing'))
        #fgs.Add(stt6,leftfactor,leftflags)
        #fgs.Add(self.stx6,rightfactor,rightflags)

        fgs.AddGrowableCol(1)

        sbox.Add(fgs, 1, wx.EXPAND)

        stb2 = wx.StaticBox(panel, -1, 'Last checked status')
        sbox2 = wx.StaticBoxSizer(stb2, wx.VERTICAL) # takes ownership of stb
        
        pbox.Add(sbox2,1,wx.EXPAND|wx.ALL,space)
        
        fgs2 = wx.FlexGridSizer(0, 2, 5, 5) #rows cols vgap hgap

        stt7 = wx.StaticText(panel, -1, 'State: ', style=text_style)
        self.stx7 = wx.TextCtrl(panel, -1, self.data.get('state'), style = wx.TE_READONLY)
        self.stx7.SetBackgroundColour(stt7.GetBackgroundColour())
        fgs2.Add(stt7,leftfactor,leftflags)
        fgs2.Add(self.stx7,rightfactor,rightflags)

        stt8 = wx.StaticText(panel, -1, 'Executed: ', style=text_style)
        self.stx8 = wx.TextCtrl(panel, -1, self.data.get('exec_command'), style = wx.TE_READONLY)
        self.stx8.SetBackgroundColour(stt8.GetBackgroundColour())
        fgs2.Add(stt8,leftfactor,leftflags)
        fgs2.Add(self.stx8,rightfactor,rightflags)

        stt9 = wx.StaticText(panel, -1, 'Local dir: ', style=text_style)
        self.stx9 = wx.TextCtrl(panel, -1, self.data.get('local_dir'), style = wx.TE_READONLY)
        self.stx9.SetBackgroundColour(stt9.GetBackgroundColour())
        fgs2.Add(stt9,leftfactor,leftflags)
        fgs2.Add(self.stx9,rightfactor,rightflags)

        stt10 = wx.StaticText(panel, -1, 'Remote dir: ', style=text_style)
        self.stx10 = wx.TextCtrl(panel, -1, self.data.get('remote_dir'), style = wx.TE_READONLY)
        self.stx10.SetBackgroundColour(stt10.GetBackgroundColour())
        fgs2.Add(stt10,leftfactor,leftflags)
        fgs2.Add(self.stx10,rightfactor,rightflags)

        stt11 = wx.StaticText(panel, -1, 'Job ID: ', style=text_style)
        self.stx11 = wx.TextCtrl(panel, -1, self.data.get('job_id'), style = wx.TE_READONLY)
        self.stx11.SetBackgroundColour(stt11.GetBackgroundColour())
        fgs2.Add(stt11,leftfactor,leftflags)
        fgs2.Add(self.stx11,rightfactor,rightflags)

        fgs2.AddGrowableCol(1)
        
        sbox2.Add(fgs2, 1, wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel,1,wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        if self.data.get('queuing') == u'get':
            buttonCheck = wx.Button(self, wx.ID_OK, 'Get results')
        else:
            buttonCheck = wx.Button(self, wx.ID_OK, 'Check job status')
        buttonCancel = wx.Button(self, wx.ID_CANCEL)
        button_sizer.Add(buttonCheck, 0, wx.ALL, 0)
        button_sizer.Add(buttonCancel, 0, wx.ALL, 0)
        if self.data.get('queuing') == u'get':
            buttonCheck.Bind(wx.EVT_BUTTON, self.get_event)
        else:
            buttonCheck.Bind(wx.EVT_BUTTON, self.check_event)
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)
        if sizer is not None:
            vbox.Add(sizer,0,wx.EXPAND|wx.ALL,space)

        self.SetSizerAndFit(vbox)

        self.stx5.Bind(wx.EVT_BUTTON, self.button_event)
        self.Bind(wx.EVT_CLOSE, self.close_event)

        self.set_state(self.data.get('state'))
        


    def get_data(self):
        data = {}
        data['host'] = self.stx1.GetValue()
        data['user'] = self.stx2.GetValue()
        data['pass'] = self.stx3.GetValue()
        data['key'] = self.stx4.GetValue()
        data['queuing'] = self.data.get('queuing')
        data['state'] = self.data.get('state')
        data['exec_command'] = self.data.get('exec_command')
        data['local_dir'] =  self.data.get('local_dir')
        data['remote_dir'] =  self.data.get('remote_dir')
        data['job_id'] =  self.data.get('job_id')
        return data



    def button_event(self, event):
        file = dialogs.get_file(self, self.stx4.GetValue())
        if file is not None:
            self.stx4.ChangeValue(file)



    def close_event(self, event):
        print 'close'
        event.Skip()



    def check_event(self, event):
        options = {}
        options['host'] = self.stx1.GetValue()
        options['user'] = self.stx2.GetValue()
        options['passw'] = self.stx3.GetValue()
        options['keyfile'] = self.stx4.GetValue()
        options['queuing'] = u'qstat'
        options['state'] = self.data.get('state')
        options['exec_command'] = self.data.get('exec_command')
        options['local_dir'] = self.data.get('local_dir')
        options['remote_dir'] = self.data.get('remote_dir')
        options['job_id'] = self.data.get('job_id')

        self.stx7.SetBackgroundColour(u'WHITE')
        self.stx7.ChangeValue(u'')

        thread = ThreadRemoteQsub.ThreadRemoteQsub(self, self.parent, options)
        self.parent.add_thread(thread)
        thread.start()



    def get_event(self, event):
        options = {}
        options['host'] = self.stx1.GetValue()
        options['user'] = self.stx2.GetValue()
        options['passw'] = self.stx3.GetValue()
        options['keyfile'] = self.stx4.GetValue()
        options['queuing'] = u'get'
        options['state'] = self.data.get('state')
        options['exec_command'] = self.data.get('exec_command')
        options['local_dir'] = self.data.get('local_dir')
        options['remote_dir'] = self.data.get('remote_dir')
        options['job_id'] = self.data.get('job_id')
        event.Skip()
        if 'linux' not in sys.platform: #ultimo dia de Fran Prieto
            self.Close()



    def load_runstatus(self):
        if self.parent.path_local is None:
            return

        try:
            file = open(config.FILE_RUNSTATUS,'rb')
        except Exception, why:
            # default value
            if not 'queuing' in self.data:
                self.data['queuing'] = 'qstat'
            # Not really an error, occurs always the first time is executed
            logging.debug(u'Problem loading run status data: '+unicode(repr(why)))
            return

        for line in file:
            if line[-1] == '\n':
                line = line[:-1]
            parts = line.split(None,1)
            if len(parts) < 2:
                continue
            if parts[0] == 'state:':
                self.data['state'] = parts[1]
            elif parts[0] == 'host:':
                self.data['host'] = parts[1]
            elif parts[0] == 'user:':
                self.data['user'] = parts[1]
            elif parts[0] == 'key:':
                self.data['key'] = parts[1]
            elif parts[0] == 'exec_command:':
                self.data['exec_command'] = parts[1]
            elif parts[0] == 'local_dir:':
                self.data['local_dir'] = parts[1]
            elif parts[0] == 'remote_dir:':
                self.data['remote_dir'] = parts[1]
            elif parts[0] == 'job_id:':
                self.data['job_id'] = parts[1]
        file.close()



    def save_runstatus(self):
        if config.FILE_RUNSTATUS is None:
            return False

        try:
            file = open(config.FILE_RUNSTATUS,'wb')
        except Exception, why:
            self.errormsg('Error saving run status data: ' + repr(why))
            return False

        state = self.data.get('state')
        if state is None:
            state = ''
        host = self.data.get('host')
        if host is None:
            host = ''
        user = self.data.get('user')
        if user is None:
            user = ''
        exec_command = self.data.get('exec_command')
        if exec_command is None:
            exec_command = ''
        local_dir = self.data.get('local_dir')
        if local_dir is None:
            local_dir = ''
        remote_dir = self.data.get('remote_dir')
        if remote_dir is None:
            remote_dir = ''
        job_id = self.data.get('job_id')
        if job_id is None:
            job_id = ''

        file.write('state: ' + state + '\n')
        file.write('-------------------------------\n')
        file.write('host: ' + host + '\n')
        file.write('user: ' + user + '\n')
        file.write('exec_command: ' + exec_command + '\n')
        file.write('local_dir: ' + local_dir + '\n')
        file.write('remote_dir: ' + remote_dir + '\n')
        file.write('job_id: ' + job_id + '\n')
        file.close()
        return True



    def set_state(self, state=None):
        if state is None:
            self.load_runstatus()
            state = self.data.get('state')
        if state == 'Finished':
            self.stx7.SetBackgroundColour(u'GREEN')
        elif state == 'Finished (with error)':
            self.stx7.SetBackgroundColour(u'RED')
        else:
            self.stx7.SetBackgroundColour(u'YELLOW')
        self.stx7.ChangeValue(state)
        return True
