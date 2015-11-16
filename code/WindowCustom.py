#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx
import config
import dialogs



# window/dialog to ask data for remote execution
class WindowCustom(wx.Dialog):

    def __init__(self, parent, action):
        self.parent = parent
        space = 5
	self.txtcontrols = []
	self.customaction = False
	title='Fill in execution parameters'
	customcommand=''
        
	if action is not None:
	    if action.get(u'title') is not None: title=action.get(u'title')
	    params = action.get('params')


        wx.Dialog.__init__(self, parent, wx.ID_ANY,
            title,
            style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

        panel = wx.Panel(self, wx.ID_ANY)
        pbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(pbox)
        
        stb = wx.StaticBox(panel, -1, '')
        sbox = wx.StaticBoxSizer(stb, wx.VERTICAL) # takes ownership of stb
        
        pbox.Add(sbox,1,wx.EXPAND|wx.ALL,space)
        
        leftfactor = 1
        rightfactor = 4
        text_style = 0 # wx.ALIGN_RIGHT
	textsize = (250,-1)
        leftflags = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        rightflags = wx.EXPAND

	if action.get(u'data') is not None:
            fgs = wx.FlexGridSizer(0, 2, 5, 5) #rows cols vgap hgap

       	    stt1 = wx.StaticText(panel, -1, 'Command: ', style=text_style)
       	    stt1.SetToolTip(wx.ToolTip(u'Enter the command'))
       	    stx1 = wx.TextCtrl(panel, -1, action.get(u'data'), size = textsize)

	    fgs.Add(stt1,leftfactor,leftflags)
       	    fgs.Add(stx1,2,rightflags)
	    self.txtcontrols.append({u'textcontrol1':stx1})
	    self.customaction = True

	else:
	    stb.SetLabel(u'Commands to run (in descending order):')
            fgs = wx.FlexGridSizer(0, 3, 5, 5) #rows cols vgap hgap
#       	    stt = wx.StaticText(panel, -1, '', style=text_style)
#       	    fgs.Add(stt,leftfactor,text_style)
######################################################################
       	    fgs.Add(wx.StaticText(panel, -1, ''),leftfactor,text_style)
       	    fgs.Add(wx.StaticText(panel, -1, ''),leftfactor,text_style)
       	    fgs.Add(wx.StaticText(panel, -1, ''),leftfactor,text_style)
######################################################################
       	    stt = wx.StaticText(panel, -1, 'Prefix command', style=wx.ALIGN_RIGHT)
       	    fgs.Add(stt,leftfactor,text_style)
       	    stt = wx.StaticText(panel, -1, 'Executable', style=wx.ALIGN_RIGHT)
       	    fgs.Add(stt,leftfactor,text_style)
       	    stt = wx.StaticText(panel, -1, 'Executable arguments', style=wx.ALIGN_RIGHT)
       	    fgs.Add(stt,leftfactor,text_style)
######################################################################

	    if params is not None:
		counter = 1
		for param in params:
		    attribs = param.get(u'attrib')
		    text = param.get(u'text') or ''
		    data = attribs.get(u'data') or ''
		    args = attribs.get(u'args') or ''
		    showvalues = (attribs.get(u'showvalues') == config.VALUE_TRUE) or False
        
#        	    stt2 = wx.StaticText(panel, -1, str(counter), style=text_style)
#       	    stt2.SetToolTip(wx.ToolTip(u'Enter the command '+str(counter)))
#		    fgs.Add(stt2,leftfactor,leftflags)
        	    stx1 = wx.TextCtrl(panel, -1, data, size = textsize)
        	    stx2 = wx.TextCtrl(panel, -1, text, size = textsize)
        	    stx3 = wx.TextCtrl(panel, -1, args, size = textsize)
		    if not showvalues:
			stx2.Enable(False)
			stx3.Enable(False)

        	    fgs.Add(stx1,2,rightflags)
        	    fgs.Add(stx2,3,rightflags)
        	    fgs.Add(stx3,4,rightflags)
		    self.txtcontrols.append({u'textcontrol1':stx1,u'textcontrol2':stx2,u'textcontrol3':stx3})
		    counter = counter + 1
        
        fgs.AddGrowableCol(2)
        
        sbox.Add(fgs, 1, wx.EXPAND)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(panel,1,wx.EXPAND)

        sizer  = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if sizer is not None:
            vbox.Add(sizer,0,wx.EXPAND|wx.ALL,space)

        self.SetSizerAndFit(vbox)

    def get_custom_command(self):
	commandlist = []
	if self.txtcontrols is not None and self.customaction:
	    return self.txtcontrols[0].get(u'textcontrol1').GetValue()
	else:
	    for ctrl in self.txtcontrols:
		commandlist.append( {u'text': ctrl.get(u'textcontrol2').GetValue(), 
                                     u'attrib': { \
                                         u'data': ctrl.get(u'textcontrol1').GetValue(), \
                                         u'args': ctrl.get(u'textcontrol3').GetValue(), \
                                         u'showvalues': str(ctrl.get(u'textcontrol2').Enabled).lower() \
                                                } \
                                    })
	    return commandlist
	return None

    def close_event(self, event):
        print 'close'
        event.Skip()
