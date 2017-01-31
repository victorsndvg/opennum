#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk



class PlotVectorDeformed(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()        
        
        #choices = [u'Colored', u'Plain']
        #self.cb2 = wx.Choice(self.plotbar, wx.ID_ANY, choices = choices)
        #self.cb2.SetSelection(0) # in windows appears without selection
        #self.plotbar.add(self.cb2)
        
        self.add_sw_1(selection=1)
        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
        #self.Bind(wx.EVT_CHOICE, self.c2, self.cb2)




    def get_options(self):
        return {u'title':'Vector deformed'}



#    def c2(self, event):
#        if not self.done:
#            return
#
#        sel = self.cb2.GetSelection()
#
#        if sel == 0:
#            self.wireM2.ScalarVisibilityOn()
#        if sel == 1:
#            self.wireM2.ScalarVisibilityOff()
#
#        self.widget.Render()

        
        
    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('new'):
            if self.data1.get('fielddomain') == 'cell':
                self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            else:
                self.warpT.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            if self.data1.get('fielddomain') == 'cell':
                self.vectors = self.src.GetOutput().GetCellData().GetVectors()
            elif self.data1.get('fielddomain') == 'point':
                self.vectors = self.src.GetOutput().GetPointData().GetVectors()
            sr = self.vectors.GetRange(-1)
            self.scalarrange.local_set(sr)
            #self.wireM2.SetScalarRange(sr)
        if changes.get('changed'):
            self.update_outline(self.warpT)
        if changes.get('changed'):
            self.copy_params(self.struct)
        return True



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        self.update_field_type('vector', True)
        self.update_legend_data()

        # creates self.src
        if not self.call_src():
            return
        self.ini_data(self.src)

        # si es cell data, lo transforma a point data, porque vtkWarpScalar parece ser que no soporta cell data.
        if self.data1.get('fielddomain') == 'cell':
            self.cdtpd = vtk.vtkCellDataToPointData()
            self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            self.warpT = vtk.vtkWarpVector()
            self.warpT.SetInputConnection(self.cdtpd.GetOutputPort())
        else:
            self.warpT = vtk.vtkWarpVector()
            self.warpT.SetInputConnection(self.src.GetOutputPort())

        self.warpT.GetOutput().GetPointData().SetVectors(self.vectors)
#        print self.warpT

        
        #Creacion de una tabla de color
        lut = vtk.vtkLookupTable()
        lut.SetRampToLinear()
        lut.SetScaleToLinear()
        # When using vector magnitude for coloring
        lut.SetVectorModeToMagnitude()
        if self.vectors is not None:
            lutrange = self.vectors.GetRange(-1)
            lut.SetTableRange(lutrange)
        lut.Build()


        self.wireM2 = vtk.vtkDataSetMapper()
        self.wireM2.SetInputConnection(self.warpT.GetOutputPort())
        #Definicion del campo y el rango para colorear
        if self.vectors is not None:
             self.wireM2.SelectColorArray(self.vectors.GetName())
             self.wireM2.SetScalarRange(lutrange)
        if self.data1.get('fielddomain') == 'cell':
            self.wireM2.SetScalarModeToUseCellFieldData()
        else:
            self.wireM2.SetScalarModeToUsePointFieldData()
        self.wireM2.ScalarVisibilityOn()
        self.wireM2.SetLookupTable(lut)
        self.wireM2.Update()

#        print self.wireM2 

        self.wireA2 = vtk.vtkActor()
        self.wireA2.SetMapper(self.wireM2)
        self.wireA2.GetProperty().SetRepresentationToSurface()
        self.wireA2.GetProperty().SetColor(Plot.edges_color)

        self.add_sw_2(self.wireA2)
        self.add_opacity_2([self.wireA2]) # Opacity: 100%/75%/50%/25%/0%
#Para pintar el wireframe original(sin desplazamiento)
#        self.wireM = vtk.vtkDataSetMapper()
#        self.wireM.SetInputConnection(self.src.GetOutputPort())
#        self.wireM.ScalarVisibilityOff()

#        self.wireA3 = vtk.vtkActor()
#        self.wireA3.SetMapper(self.wireM)
#        self.wireA3.GetProperty().SetRepresentationToWireframe()
#        self.wireA3.GetProperty().SetColor(Plot.mesh_color)
#        self.wireA3.GetProperty().SetEdgeColor(Plot.unselected_color)

#        self.rens[0].AddActor(self.wireA3)
        self.rens[0].AddActor(self.wireA2)
        
        self.copy_params(struct)

        self.warpT.Update()
#        self.add_outline_2(self.src)
        self.add_outline_2(self.warpT)

# reverse rainbow [red->blue] -> [blue->red]
        if self.vectors is not None:
            self.scalarrange.local_set(lutrange)
            self.add_scalarbar_2(lut)

        self.done = True



# fai falta
    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()


    def range_update3(self,range):
        #self.warpT.SetScaleFactor(self.scale)
        self.wireM2.SetScalarRange(range)
        self.wireM2.GetLookupTable().SetTableRange(range)

    def copy_params(self, struct):

        nums = struct.get_elements()
#        print 'nums', nums
        if len(nums) == 1:
            num = nums[0]
            self.scale = None
            try:
                self.scale = float(num)
            except ValueError:
                pass
            if self.scale is not None:
                self.warpT.SetScaleFactor(self.scale)
                self.update_outline(self.warpT)
            else:
                self.data_error('Error converting \'' + num + '\' to float')
        else:
            #self.data_error('Incorrect number of elements (1 needed)')
            self.scale = self.calc_best_scale()
            self.warpT.SetScaleFactor(self.scale)
            self.update_outline(self.warpT)
            nums = struct.set_elements([str(self.scale)])
            #self.panel_widgets.update_widget_struct(nums[0])


    def ini_data(self, src):
        o = src.GetOutput()
        
        if self.data1.get('fielddomain') == 'cell':
            self.vectors = o.GetCellData().GetVectors()
            pc = 1
        elif self.data1.get('fielddomain') == 'point':
            self.vectors = o.GetPointData().GetVectors()
            pc = 0
        else:
            self.vectors = None

        self.bounds = self.src.GetOutput().GetBounds()
        self.maxNorm = None
        if self.vectors is not None:
        #Maximo valor da norma dos vectores
            self.maxNorm = self.vectors.GetMaxNorm()
        self.scale = self.calc_best_scale()



    def calc_best_scale(self):
        if self.maxNorm is not None:
            xdist = (self.bounds[1]-self.bounds[0])
            ydist = (self.bounds[3]-self.bounds[2])
            zdist = (self.bounds[5]-self.bounds[4])

            maxdist = xdist
            if maxdist<ydist:
                maxdist = ydist
            if maxdist<zdist:
                maxdist = zdist
            meddist = (xdist+ydist+zdist)/3
            #maxdist = ((xdist*xdist)+(ydist*ydist)+(zdist*zdist))
            if self.maxNorm == 0:
                return 1.0
            else:
                return self.round_to_1(maxdist/(self.maxNorm*20))
        else:
            return 1.0

#redondea al primer digito significativo
    def round_to_1(self,x):
        from math import log10, floor
        return round(x, -int(floor(log10(x))))

