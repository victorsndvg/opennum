#!/usr/bin/env python
# -*- coding: utf-8 -*-



import wx_version
import wx



class ScaleBar(wx.PyPanel):

    def __init__(self, parent, plot):
    
        wx.PyPanel.__init__(self, parent)

        self.myparent = parent
        self.plot = plot
        self.data1 = plot.data1
        self.parent = self
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []

        self.progress = None

        self.is_temporal = False
        self.scale_visible = True
        self.abs_rel_pos = None

        self.scale_button = b = wx.ToggleButton(self.parent, wx.ID_ANY, 'Scale', style=wx.BU_EXACTFIT)
        b.Bind(wx.EVT_TOGGLEBUTTON, self.scale_event)
        b.SetToolTip(wx.ToolTip(u'Toogle visibility of scale'))
        self.buttons.append(b)

        self.color_pos = 0
        self.color_choices = [u'Blue to red', u'Red to Blue',u'Cool',u'Warm']
        self.color_widget = wx.Choice(self.parent, wx.ID_ANY, choices = self.color_choices)
        self.color_widget.SetSelection(self.color_pos) # in windows appears without selection
        self.color_widget.Bind(wx.EVT_CHOICE, self.color_event)
        self.color_widget.SetToolTip(wx.ToolTip(u'Change scalarbar color range'))
        self.buttons.append(self.color_widget)
        
        self.abs_rel_pos = 0
        self.abs_rel_choices = [u'Absolute scale', u'Relative scale']
        self.abs_rel_widget = wx.Button(self.parent, wx.ID_ANY, self.abs_rel_choices[self.abs_rel_pos], style=wx.BU_EXACTFIT)
        self.abs_rel_widget.Bind(wx.EVT_BUTTON, self.abs_rel_event)
        self.abs_rel_widget.Hide()
        self.abs_rel_widget.SetToolTip(wx.ToolTip(u'Toogle scale relative to visible part'))
        self.buttons.append(self.abs_rel_widget)

        self.mode_code = ''
        self.mode_choices = [u'Adjust manually', u'Adjust to the ' + self.data1.get('evolution_lower') + ' interval', u'Adjust to the current field', u'Adjust to every field']
        self.mode_choices_code = {self.mode_choices[0]:'m', self.mode_choices[1]:'t', self.mode_choices[2]:'c', self.mode_choices[3]:'f'}
        self.mode_choice = wx.Choice(self.parent, wx.ID_ANY, choices = self.mode_choices)
        #self.mode_choice.SetSelection(3) # in windows appears without selection
        self.mode_choice.Bind(wx.EVT_CHOICE, self.mode_event)
        self.mode_choice.SetToolTip(wx.ToolTip(u'Choose scale range'))
        self.buttons.append(self.mode_choice)
        
        for button in self.buttons:
            self.sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL)

        esize = (90,-1)

        self.txt_l0 = l = wx.StaticText(self.parent, wx.ID_ANY, '  From: ')
        self.sizer.Add(l, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        self.txt_r0 = e = wx.TextCtrl(self.parent, wx.ID_ANY, size=esize, style=wx.TE_PROCESS_ENTER)
        e.Bind(wx.EVT_TEXT_ENTER , self.r0_enter)
        #self.sizer.Add(e, 0, wx.FIXED_MINSIZE)
        self.sizer.Add(e, 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_l1 = l = wx.StaticText(self.parent, wx.ID_ANY, '  To: ')
        self.sizer.Add(l, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        self.txt_r1 = e = wx.TextCtrl(self.parent, wx.ID_ANY, size=esize, style=wx.TE_PROCESS_ENTER)
        e.Bind(wx.EVT_TEXT_ENTER , self.r1_enter)
        #self.sizer.Add(e, 0, wx.FIXED_MINSIZE)
        self.sizer.Add(e, 0, wx.ALIGN_CENTER_VERTICAL)

        #print self.scale_button.GetSize(), '~', self.mode_choice.GetSize(), '~', l.GetSize(), '~', self.txt_time.GetSize()

        self.SetSizer(self.sizer)
        
        self.sizer.Layout() # se non os 'e' quedan mal debuxados



    # public
    def set_scale_visible(self, opt):
        self.scale_visible = opt
#            self.scale_action()


    # public
    def set_scale_abs_rel(self, opt):
        self.abs_rel_pos = opt
#            self.plot.set_abs_rel_pos(self.abs_rel_pos)
#            self.plot.adjust_abs_rel()
#            self.plot.do_render()



    # public
    def set_is_temporal(self, opt):
        self.is_temporal = opt
#            self.mode_handler()



    # public # must be called
    def init(self):
        # scale_visible
        self.scale_button.SetValue(self.scale_visible)
        
        # abs_rel_pos
        if self.abs_rel_pos == 0 or self.abs_rel_pos == 1:
            self.abs_rel_widget.SetLabel(self.abs_rel_choices[self.abs_rel_pos])
            self.abs_rel_widget.Show()
        else: # none
            self.abs_rel_widget.Hide()

        # is_temporal
        temporal = self.is_temporal

        # is_inmutable
        local = self.plot.scalarrange.mode_get() == 0 and self.plot.scalarrange.mode_mutable_get() == False

        # combo
        self.mode_choice.Clear()

        if temporal and not local:
            self.mode_choice.Append(self.mode_choices[0]) # manual
            self.mode_choice.Append(self.mode_choices[1]) # time interval
            self.mode_choice.Append(self.mode_choices[2]) # current
            self.mode_choice.Append(self.mode_choices[3]) # free
        elif temporal and local:
            self.mode_choice.Append(self.mode_choices[3]) # free
        elif not temporal and not local:
            self.mode_choice.Append(self.mode_choices[0]) # manual
            self.mode_choice.Append(self.mode_choices[3]) # free
        elif not temporal and local:
            self.mode_choice.Append(self.mode_choices[3]) # free

        mode_value = self.mode_choice.GetCount() - 1 # ultimo

        self.mode_choice.SetSelection(mode_value) # in windows appears without selection

        self.mode_handler() # necesario (?)



    def scale_event(self, event):
        self.scale_action()



    def scale_action(self):
        self.plot.scalarbar_change(self.scale_button.GetValue())



    def abs_rel_event(self, event):
        if not self.plot.is_done() or self.abs_rel_pos is None:
            return    
        self.abs_rel_pos = (self.abs_rel_pos + 1) % 2
        self.abs_rel_widget.SetLabel(self.abs_rel_choices[self.abs_rel_pos])
        self.plot.set_abs_rel_pos(self.abs_rel_pos)
        self.plot.adjust_abs_rel()
        self.plot.do_render()
        # render must be called here because it is the proper place reached by control flow

    def color_event(self, event):   
        self.color_pos = self.color_widget.GetCurrentSelection()
        self.color_widget.SetLabel(self.color_choices[self.color_pos])
        if self.color_pos == 0: # blue->red
            self.plot.scalarbar_change_color((0.66667, 0.0), (1.0, 1.0), (1.0, 1.0), u'Curve')
        elif self.color_pos == 1: # red->blue
            self.plot.scalarbar_change_color((0.0, 0.66667), (1.0, 1.0), (1.0, 1.0), u'Curve')
        elif self.color_pos == 2: # cool
            self.plot.scalarbar_change_color((0.66667, 0.5), (1.0, 0.0), (0.7, 1.0), u'Sqrt')
        elif self.color_pos == 3: # warm
            self.plot.scalarbar_change_color((0.16667, 0.0), (0.0, 1.0), (1.0, 0.7), u'Sqrt')
#        self.plot.do_render()



    def mode_event(self, event):
        self.mode_handler()



    def mode_handler(self):
        ##print self.scale_button.GetSize(), '~', self.mode_choice.GetSize(), '~', self.txt_time.GetSize()
        #print self.mode_choice.GetSelection(), self.mode_choice.GetCurrentSelection()
        
        mode_value = self.mode_choice.GetSelection()
        
        self.mode_code = choice = self.get_choice(self.mode_choice.GetString(mode_value))
        
        self.abs_rel_widget.Enable(choice == 'f')

        self.txt_r0.Enable(choice == 'm')
        self.txt_r1.Enable(choice == 'm')
        self.txt_l0.Enable(choice == 'm')
        self.txt_l1.Enable(choice == 'm')
        #self.txt_r0.SetEditable(choice == 'm')
        #self.txt_r1.SetEditable(choice == 'm')

        # 1º rango 2º modo
        if choice == 'm': # manual
            rango = self.get_range()
            if rango[0] is not None and rango[1] is not None:
                self.plot.scalarrange.imposed_set(rango)
            self.plot.scalarrange.mode_set(1)
        elif choice == 't': # time
            time_range = self.plot.timebar.get_time_range()
            if time_range[0] is not None and time_range[1] is not None:
                self.time_range_step(None,None)
                if time_range[0] > time_range[1]: # swap
                    time_range = (time_range[1], time_range[0])
                rango = self.plot.timemanager.get_value_range(time_range, self.time_range_step)
                self.time_range_step(None,None)
                if rango is False:
                    pass # cancelled
                elif isinstance(rango, basestring):
                    self.plot.window.errormsg('Error calculating range for selected ' + self.data1.get('evolution_lower') + ': ' + rango)
                else:
                    self.update_range2(rango)
                    self.plot.scalarrange.imposed_set(rango)
            self.plot.scalarrange.mode_set(1)
        elif choice == 'c': # current
            rango = self.plot.scalarrange.local_get()
            self.update_range2(rango)
            self.plot.scalarrange.imposed_set(rango)
            self.plot.scalarrange.mode_set(1)
        elif choice == 'f': # free
            self.update_range2(self.plot.scalarrange.local_get()) # cuestionable necesidad de este
            self.plot.scalarrange.mode_set(0)

        self.plot.do_render() # necesario



    # chamado desde plot
    # para cando o plot actualiza or rango local e estamos en current field de non pvd
    def update_range(self, range):
        if self.mode_code == 'f':
            self.update_range2(range)



    def update_range2(self, range):
        if range is None:
            self.txt_r0.ChangeValue('')
            self.txt_r1.ChangeValue('')
        else:
            self.txt_r0.ChangeValue(unicode(range[0]))
            self.txt_r1.ChangeValue(unicode(range[1]))



    def get_choice(self, str):
        return self.mode_choices_code.get(str)



    def get_range(self):
        txt0 = self.txt_r0.GetValue()
        txt1 = self.txt_r1.GetValue()

        d0 = None
        try:
            d0 = float(txt0)
        except ValueError, v:
            self.plot.window.errormsg('First range value error: can not convert \''+txt0+'\' to a floating point number')

        d1 = None
        try:
            d1 = float(txt1)
        except ValueError, v:
            self.plot.window.errormsg('Second range value error: can not convert \''+txt1+'\' to a floating point number')

        return (d0,d1)



    def r0_enter(self, event):
        rango = self.get_range()
        if rango[0] is not None and rango[1] is not None:
            self.plot.scalarrange.imposed_set(rango)
            self.plot.do_render() # necesario
    

    
    def r1_enter(self, event):
        rango = self.get_range()
        if rango[0] is not None and rango[1] is not None:
            self.plot.scalarrange.imposed_set(rango)
            self.plot.do_render() # necesario




    def time_range_step(self, current, total):
        #print current, total
        ret = True
        if current is None and self.progress is not None:
            self.progress.Destroy()
            self.progress = None
        elif (current is None or current == 0) and total is not None:
            self.progress = wx.ProgressDialog('Reading files','Read 0 of '+unicode(total)+' files', total, \
                self.plot.window, wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        elif self.progress is not None:
            res = self.progress.Update(current,'Read '+unicode(current)+' of '+unicode(total)+' files')
            if res[0] is not True: # cancelled
                ret = False
            #self.plot.window.process_pending() # posto ao principio causa mala interacción
        return ret
