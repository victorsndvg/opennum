#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk
#import FileMrw
import FileParse

palette = [ \
                    (1.0,0.0,0.0), \
                    (0.0,1.0,0.0), \
                    (0.0,0.0,1.0), \

                    (1.0,1.0,0.0), \
                    (1.0,0.0,1.0), \
                    (0.0,1.0,1.0), \

                    (0.5,0.0,0.0), \
                    (0.0,0.5,0.0), \
                    (0.0,0.0,0.5), \

                    (0.5,0.5,0.0), \
                    (0.5,0.0,0.5), \
                    (0.0,0.5,0.5), \

                    (0.5,1.0,0.0), \
                    (0.5,0.0,1.0), \
                    (0.0,0.5,1.0), \
                    
                    (1.0,0.5,0.0), \
                    (1.0,0.0,0.5), \
                    (0.0,1.0,0.5), \
                    ]


class Plot2DGraph(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)
	self.parent = parent

        self.label_tbutton = wx.ToggleButton(self.plotbar, wx.ID_ANY, 'Labels', style=wx.BU_EXACTFIT)
        self.label_tbutton.SetValue(False)
        self.plotbar.add(self.label_tbutton)
        self.label_tbutton.Bind(wx.EVT_TOGGLEBUTTON, self.label_event)
        
        self.pospi0 = (0.0,0.05,0.0)
        self.pospt0 = (1.0,0.9,0.0)
        self.posli0 = (2.0,0.0)
        self.poslt0 = (2.0,1.0)
        self.pospi1 = (0.0,0.05,0.0)
        self.pospt1 = (0.85,0.9,0.0)
        self.posli1 = (1.0,0.0)
        self.poslt1 = (0.18,1.0)

        # hides 'center' buttons. not needed here
        # also mesh_names
        self.hide_center_1()
        self.hide_mesh_names_1()



    def label_event(self, event):
        if not self.done:
            return
        if not self.label_tbutton.GetValue():
            self.xyplot.GetPositionCoordinate().SetValue(self.pospi0)
            self.xyplot.GetPosition2Coordinate().SetValue(self.pospt0)
            self.xyplot.SetLegendPosition(self.posli0)
            self.xyplot.SetLegendPosition2(self.poslt0)
        else:
            self.xyplot.GetPositionCoordinate().SetValue(self.pospi1)
            self.xyplot.GetPosition2Coordinate().SetValue(self.pospt1)
            self.xyplot.SetLegendPosition(self.posli1)
            self.xyplot.SetLegendPosition2(self.poslt1)

        self.widget.Render()



    def get_options(self):
        return {u'title':'2D graph','interactor':True}



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
#        if changes.get('changed'):
#        if changes.get('new'):
        return True



    # responde a la pregunta: se puede actualizar a partir del tracker o de uno nuevo ?
    # si retorna False, no se actualiza el grafico, se crea nuevo ante cualquier cambio
#    def updatable_tracker(self):
#        return False

    def Gr2_File_to_Polydata(self,dataname):

        f = FileParse.FileParse()
        err = f.open(dataname)
        if err is not True:
            self.window.errormsg (u'Error opening file: ' + unicode(err))
            return False

        temp = f.getword()
        if temp is None:
            self.window.errormsg (u'Premature EOF')
            return False
        if temp is False:
            self.window.errormsg (u'I/O Error: ' + f.get_error())
            return False
        series_num = FileParse.FileParse.to_int(temp)
        if series_num is False:
            self.window.errormsg (u'Error converting \'' + unicode(temp) + '\' to integer')
            return False

	polydata = []

        for s in range(series_num):
            temp = f.getword()
            if temp is None:
                self.window.errormsg (u'Premature EOF')
                return False
            if temp is False:
                self.window.errormsg (u'I/O Error: ' + f.get_error())
                return False
            series_size = FileParse.FileParse.to_int(temp)
            if series_size is False:
                self.window.errormsg (u'Error converting \'' + unicode(temp) + '\' to integer')
                return False

            points = vtk.vtkPoints()

            for r in range(series_size):
                temp = f.getword()
                if temp is None:
                    self.window.errormsg (u'Premature EOF')
                    return False
                if temp is False:
                    self.window.errormsg (u'I/O Error: ' + f.get_error())
                    return False
                x = FileParse.FileParse.to_float(temp)
                if x is False:
                    self.window.errormsg (u'Error converting \'' + unicode(temp) + '\' to float')
                    return False
                points.InsertNextPoint( x , 0.0, 0.0 )

            ds = vtk.vtkPolyData()
            ds.SetPoints(points)
            pd = ds.GetPointData()
            sca = vtk.vtkDoubleArray()

            for r in range(series_size):
                temp = f.getword()
                if temp is None:
                    self.window.errormsg (u'Premature EOF')
                    return False
                if temp is False:
                    self.window.errormsg (u'I/O Error: ' + f.get_error())
                    return False
                y = FileParse.FileParse.to_float(temp)
                if y is False:
                    self.window.errormsg (u'Error converting \'' + unicode(temp) + '\' to float')
                    return False
                sca.InsertNextValue( y )
                
            pd.SetScalars(sca)
	    polydata.append(ds)

        labels = [] # string o None
        for t in range(3+series_num):
            temp = f.getline()
            if temp is False:
                self.window.errormsg (u'I/O Error: ' + f.get_error())
                return False
            elif temp is None:
                pass
            else:
                temp = temp.rstrip() # quita \n e espazos
            labels.append(temp)


        err = f.close()
        if err is not True:
            self.window.errormsg (u'Error closing file: ' + unicode(err))
            return False
        f = None

	return {'labels':labels, 'polydata':polydata, 'series_num':series_num}


    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return
        
        # creates self.src
        #if not self.call_src():
        #    return

        self.rens[0].SetBackground((1.0,1.0,1.0))
        self.xyplot = vtk.vtkXYPlotActor()

	if self.tracker.is_void:
	    return False
	elif self.tracker.type == "node_files":
            series_num = 0
	    labels = []

	    trackers = self.tracker.trackers
	    self.dataname = []
	    for tracker in trackers:
		self.dataname.append(tracker.get_vtkfile())

	    for name in self.dataname:
	        res = self.Gr2_File_to_Polydata(name)
		polydata = res.get('polydata')
		labels.extend(res.get('labels')[min(len(labels),3):])
		series_num = series_num + res.get('series_num')
		
		for pd in polydata:
        	    self.xyplot.AddInput(pd)
#	    return False
	else:
            self.dataname = self.tracker.get_vtkfile()
	    #returns 'labels', 'series_num' and 'polydata' keys
	    res = self.Gr2_File_to_Polydata(self.dataname)

	    polydata = res.get('polydata')
	    labels = res.get('labels')
	    series_num = res.get('series_num')

	    for pd in polydata:
        	self.xyplot.AddInput(pd)


        self.xyplot.GetPositionCoordinate().SetValue(self.pospi0)
        self.xyplot.GetPosition2Coordinate().SetValue(self.pospt0) # rel
        # relative to the ones avobe
        self.xyplot.SetLegendPosition(self.posli0)
        self.xyplot.SetLegendPosition2(self.poslt0) # rel

#        self.xyplot.SetXValuesToArcLength()
        self.xyplot.SetXValuesToValue()

        temp = labels[0]
        if temp is None:
            temp = '2D graph'
        self.xyplot.SetTitle(temp)
        temp = labels[1]
        if temp is None:
            temp = 'X axis'
        self.xyplot.SetXTitle(temp)
        temp = labels[2]
        if temp is None:
            temp = 'Y axis'
        self.xyplot.SetYTitle(temp)
        
        for t in range(series_num):
            temp = labels[3+t]
            if temp is None:
                temp = 'Series ' + unicode(t)
            self.xyplot.SetPlotLabel(t,temp)
            self.xyplot.SetPlotColor(t,palette[t%len(palette)])

        self.xyplot.LegendOn()
        
        self.xyplot.PlotPointsOn()

        self.xyplot.GetProperty().SetColor(0.0, 0.0, 0.0)
        self.xyplot.GetProperty().SetPointSize(3)
        # Set text prop color (same color for backward compat with test)
        # Assign same object to all text props
        tprop = self.xyplot.GetTitleTextProperty()
        tprop.SetColor(self.xyplot.GetProperty().GetColor())
        self.xyplot.SetAxisTitleTextProperty(tprop)
        self.xyplot.SetAxisLabelTextProperty(tprop)
        
        self.copy_params(struct)
        
        self.set_iren()
        self.inter = vtk.vtkInteractorStyleRubberBand2D()
        #self.inter = vtk.vtkInteractorStyleRubberBandZoom()
        self.inter.SetInteractor(self.iren)
        self.widget.SetInteractorStyle(self.inter)

        self.rens[0].AddActor(self.xyplot)

        self.last = None
        self.inter.AddObserver("SelectionChangedEvent", self.selection)
        # meanwhile not enough with the above:
        self.inter.AddObserver("StartInteractionEvent", self.selectioni)
        self.inter.AddObserver("EndInteractionEvent", self.selectionf)

        self.done = True


    def old_update(self, struct):

        self.copy_params(struct)
        self.widget.Render()

    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()
	self.update_from_dependency(struct)



    def update_from_dependency(self, struct):

        self.rens[0].RemoveActor(self.xyplot)
        self.xyplot.RemoveAllInputs()
        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return
        
        # creates self.src
        #if not self.call_src():
        #    return

        self.rens[0].SetBackground((1.0,1.0,1.0))

	if self.tracker.is_void:
	    return False
	elif self.tracker.type == "node_files":
            series_num = 0
	    labels = []

	    trackers = self.tracker.trackers
	    self.dataname = []
	    for tracker in trackers:
		self.dataname.append(tracker.get_vtkfile())

	    for name in self.dataname:
	        res = self.Gr2_File_to_Polydata(name)
		polydata = res.get('polydata')
		labels.extend(res.get('labels')[min(len(labels),3):])
		series_num = series_num + res.get('series_num')

		for pd in polydata:
        	    self.xyplot.AddInput(pd)

#	    return False
	else:
            self.dataname = self.tracker.get_vtkfile()
	    #returns 'labels', 'series_num' and 'polydata' keys
	    res = self.Gr2_File_to_Polydata(self.dataname)

	    polydata = res.get('polydata')
	    labels = res.get('labels')
	    series_num = res.get('series_num')

	    for pd in polydata:
        	self.xyplot.AddInput(pd)


        temp = labels[0]
        if temp is None:
            temp = '2D graph'
        self.xyplot.SetTitle(temp)
        temp = labels[1]
        if temp is None:
            temp = 'X axis'
        self.xyplot.SetXTitle(temp)
        temp = labels[2]
        if temp is None:
            temp = 'Y axis'
        self.xyplot.SetYTitle(temp)
        
        for t in range(series_num):
            temp = labels[3+t]
            if temp is None:
                temp = 'Series ' + unicode(t)
            self.xyplot.SetPlotLabel(t,temp)
            self.xyplot.SetPlotColor(t,palette[t%len(palette)])


######

        self.xyplot.GetPositionCoordinate().SetValue(self.pospi0)
        self.xyplot.GetPosition2Coordinate().SetValue(self.pospt0) # rel
        # relative to the ones avobe
        self.xyplot.SetLegendPosition(self.posli0)
        self.xyplot.SetLegendPosition2(self.poslt0) # rel


#        self.xyplot.SetXValuesToArcLength()
        self.xyplot.SetXValuesToValue()


        self.xyplot.LegendOn()
        
        self.xyplot.PlotPointsOn()

        self.xyplot.GetProperty().SetColor(0.0, 0.0, 0.0)
        self.xyplot.GetProperty().SetPointSize(3)
        # Set text prop color (same color for backward compat with test)
        # Assign same object to all text props
        tprop = self.xyplot.GetTitleTextProperty()
        tprop.SetColor(self.xyplot.GetProperty().GetColor())
        self.xyplot.SetAxisTitleTextProperty(tprop)
        self.xyplot.SetAxisLabelTextProperty(tprop)
        


        self.rens[0].AddActor(self.xyplot)

        self.last = None
        self.inter.AddObserver("SelectionChangedEvent", self.selection)
        # meanwhile not enough with the above:
        self.inter.AddObserver("StartInteractionEvent", self.selectioni)
        self.inter.AddObserver("EndInteractionEvent", self.selectionf)

        self.done = True

        if self.label_tbutton.GetValue():
	    self.label_event(None)


    def copy_params(self, struct):
	#Se hace esta comprobación por si la representacion viene del boton show en lugar de la propiedad plot
	if struct.get_attribs().get(u'plot') is not None:					#añadido
		ch = struct.get_children()
		if len(ch) != 2:
		    self.data_error('Incorrect number of childs in Plot2DGraph (2 needed)')
		    return None
		
		nums0 = ch[0].get_elements()
		nums1 = ch[1].get_elements()
		
		if len(nums0) != 0 and len(nums0) != 2:
		    self.data_error('Incorrect number of elements for X range (0 or 2 needed)')
		    return None

		if len(nums1) != 0 and len(nums1) != 2:
		    self.data_error('Incorrect number of elements for Y range (0 or 2 needed)')
		    return None
		
		numsf0 = []
		for num in nums0:
		    try:
		        numsf0.append(float(num))
		    except ValueError:
		        self.data_error('Error converting \'' + num + '\' to float in X range')
		        return None

		numsf1 = []
		for num in nums1:
		    try:
		        numsf1.append(float(num))
		    except ValueError:
		        self.data_error('Error converting \'' + num + '\' to float in Y range')
		        return None


		if len(numsf0) != 2:
		    self.xyplot.SetXRange((0.0,0.0))
		else:
		    self.xyplot.SetXRange(numsf0)
		if len(numsf1) != 2:
		    self.xyplot.SetYRange((0.0,0.0))
		else:
		    self.xyplot.SetYRange(numsf1)




    def selection(self, obj, evt):
        #print "sel", obj, evt, repr(obj), repr(evt), dir(obj), dir(evt)
        #print evt, self.iren.GetLastEventPosition(), self.iren.GetEventPosition()
        self.current = self.iren.GetEventPosition()
        if self.last is not None:
            self.rectangle(self.last, self.current)


    def selectioni(self, obj, evt):
        #print evt, self.iren.GetLastEventPosition(), self.iren.GetEventPosition()
        self.last = self.iren.GetEventPosition()
 
    def selectionf(self, obj, evt):
        #print evt, self.iren.GetLastEventPosition(), self.iren.GetEventPosition()
        pass
 
 
 
    def rectangle(self, xyfrom, xyto):
        self.xyplot.SetViewportCoordinate(xyfrom)
        self.xyplot.ViewportToPlotCoordinate(self.rens[0])
        plotfrom = self.xyplot.GetViewportCoordinate()

        self.xyplot.SetViewportCoordinate(xyto)
        self.xyplot.ViewportToPlotCoordinate(self.rens[0])
        plotto = self.xyplot.GetViewportCoordinate()
        
        x = [plotfrom[0], plotto[0]]
        if plotfrom[0] < plotto[0]:
            x = [plotfrom[0], plotto[0]]
        else:
            x = [plotto[0], plotfrom[0]]
 
        y = [plotfrom[1], plotto[1]]
        if plotfrom[1] < plotto[1]:
            y = [plotfrom[1], plotto[1]]
        else:
            y = [plotto[1], plotfrom[1]]
 
        self.xyplot.SetXRange(x)
        self.xyplot.SetYRange(y)

        # iguales se iguales
        #print self.xyplot.GetXRange(), self.xyplot.GetYRange()

	#si la visualización se realiza desde el boton 'show'
	#no se actualizan los structs con el rango de la 
	if self.struct.get_attribs().get(u'plot') is not None:
            self.set_params(self.struct, x, y, True)

        self.widget.Render()



    # write params to menu xml structure
    def set_params(self, struct, x, y, force=False):
        ch = struct.get_children()

        if len(ch) < 2:
            print 'Error: incorrect number of childs in Plot2dGraph'
            return
        
        nums = ch[0].get_elements()
        if len(nums) == 0 or force:
            if x[0] == x[1]:
                nums = []
            else:
                nums = [ unicode(x[0]), unicode(x[1])]
            ch[0].set_elements_nosel(nums)
            self.panel_widgets.update_widget_struct(ch[0])

        nums = ch[1].get_elements()
        if len(nums) == 0 or force:
            if y[0] == y[1]:
                nums = []
            else:
                nums = [ unicode(y[0]), unicode(y[1])]
            ch[1].set_elements_nosel(nums)
            self.panel_widgets.update_widget_struct(ch[1])

