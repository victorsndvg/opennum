#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk



class PlotScalarDeformed(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()        
        
        choices = [u'Colored', u'Plain']
        self.cb2 = wx.Choice(self.plotbar, wx.ID_ANY, choices = choices)
        self.cb2.SetSelection(0) # in windows appears without selection
        self.plotbar.add(self.cb2)
        
        self.add_sw_1(selection=1)
        
        self.Bind(wx.EVT_CHOICE, self.c2, self.cb2)




    def get_options(self):
        return {u'title':'3D plot'}



    def c2(self, event):
        if not self.done:
            return

        sel = self.cb2.GetSelection()

        if sel == 0:
            self.wireM2.ScalarVisibilityOn()
        if sel == 1:
            self.wireM2.ScalarVisibilityOff()

        self.widget.Render()

        
        
    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('new'):
            if self.data1.get('fielddomain') == 'cell':
                self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            else:
                self.warpT.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())
        if changes.get('changed'):
            self.update_outline(self.warpT)
        if changes.get('changed'):
            self.copy_params(self.struct)
        return True



    def range_update3(self, range):
        self.wireM2.SetScalarRange(range)
        self.look.SetTableRange(range)



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

	self.bounds = self.src.GetOutput().GetBounds()                  #añadido

        # si es cell data, lo transforma a point data, porque vtkWarpScalar parece ser que no soporta cell data.
        if self.data1.get('fielddomain') == 'cell':
            self.cdtpd = vtk.vtkCellDataToPointData()
            self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            self.warpT = vtk.vtkWarpScalar()
            self.warpT.SetInputConnection(self.cdtpd.GetOutputPort())
        else:
            self.warpT = vtk.vtkWarpScalar()
            self.warpT.SetInputConnection(self.src.GetOutputPort())
        
        self.wireM2 = vtk.vtkDataSetMapper()
        self.wireM2.SetInputConnection(self.warpT.GetOutputPort())
        
        #self.wireM2.SetScalarRange(self.cdtpd.GetOutput().GetScalarRange())


# reverse rainbow [red->blue] -> [blue->red]
        self.look = self.wireM2.GetLookupTable()
    

#        self.wireM2.ScalarVisibilityOff()
        
        self.wireA2 = vtk.vtkActor()
        self.wireA2.SetMapper(self.wireM2)
        self.wireA2.GetProperty().SetRepresentationToSurface()
        self.wireA2.GetProperty().SetColor(Plot.edges_color)

        self.add_sw_2(self.wireA2)

        self.rens[0].AddActor(self.wireA2)

	self.maxrange = self.src.GetOutput().GetScalarRange()[1]
        
        self.copy_params(struct)

        self.warpT.Update()
#        self.add_outline_2(self.src)
        self.add_outline_2(self.warpT)

        self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())

        self.add_scalarbar_2(self.look)

        self.done = True



# fai falta
    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()



    def copy_params(self, struct):

        nums = struct.get_elements()
#        print 'nums', nums
        if len(nums) == 1:
            num = nums[0]
            numf = None
            try:
                numf = float(num)
            except ValueError:
                pass
            if numf is not None:
                self.warpT.SetScaleFactor(numf)
                self.update_outline(self.warpT)
            else:
                self.data_error('Error converting \'' + num + '\' to float')
        elif len(nums) == 0:					#añadido
	    scale = self.calc_best_scale()			#añadido
            self.warpT.SetScaleFactor(scale)			#añadido
            self.update_outline(self.warpT)			#añadido
	    nums = struct.set_elements([str(scale)])		#añadido
            self.panel_widgets.update_widget_struct(nums)	#añadido
	else:
            self.data_error('Incorrect number of elements (1 needed)')

    def calc_best_scale(self):                                  #añadido
	if self.maxrange is not None:				#añadido
            xdist = (self.bounds[1]-self.bounds[0])             #añadido
            ydist = (self.bounds[3]-self.bounds[2])             #añadido
            zdist = (self.bounds[5]-self.bounds[4])             #añadido
            maxdist = xdist					#añadido
            if maxdist<ydist:					#añadido
		maxdist = ydist					#añadido
            if maxdist<zdist:					#añadido
		maxdist = zdist 				#añadido
            if self.maxrange == 0:				#añadido
		return 0.0					#añadido
            else:						#añadido
		return self.round_to_1(maxdist/(self.maxrange*20))#añadido
	else:
            return 0.0

    def round_to_1(self,x):					#añadido
	from math import floor, log10				#añadido
	try:
		res = round(x, -int(floor(log10(x))))		#añadido
		return res
	except:
		return 0.0
