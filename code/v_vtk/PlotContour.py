#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk



class PlotContour(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1()
        self.add_outline_1()
        
        self.edges_button = wx.ToggleButton(self.plotbar, wx.ID_ANY, u'Edges', style=wx.BU_EXACTFIT)
        self.edges_button.Bind(wx.EVT_TOGGLEBUTTON, self.edges_event)
        self.plotbar.add(self.edges_button)
        
        #self.scalarrange.mode_set(0) # tiña rango nulo => non actualiza rango
        #self.scalarrange.mode_mutable_set(False) # always local scalar range



    def get_options(self):
        return {u'title':'Contour'}



    def edges_event(self, event):
        if not self.done:
            return
        
        sel = self.edges_button.GetValue()

        if sel:
            self.wireA2.SetVisibility(1)
        else:
            self.wireA2.SetVisibility(0)

        self.widget.Render()



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('new'):
            self.wireM2.SetInputConnection(self.src.GetOutputPort())
            # self.wireM3.SetInputConnection(self.src.GetOutputPort())
        # if changed: - wireM2 - range
        if changes.get('changed'):
            self.update_outline(self.src)
        if changes.get('new'):
            if self.data1.get('fielddomain') == 'cell':
                self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            else:
                self.contours.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())
        if changes.get('changed'):
            self.copy_params(self.struct)
        return True



    def range_update3(self, range):
        self.wireM2.SetScalarRange(range)
        self.contM.SetScalarRange(range)
        #self.wireM3.SetScalarRange(range)



    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

        self.wireM2 = vtk.vtkDataSetMapper()
        self.wireM2.SetInputConnection(self.src.GetOutputPort())
        self.wireM2.ScalarVisibilityOff() # hurts: scalar bar does not work for range (0.0, 0.0)

        self.wireA2 = vtk.vtkActor()
        self.wireA2.SetMapper(self.wireM2)
        self.wireA2.GetProperty().SetRepresentationToWireframe()
        self.wireA2.GetProperty().SetColor(Plot.edges_color)
        self.wireA2.SetVisibility(0)        

#        # reverse rainbow [red->blue] -> [blue->red]
#        look = self.wireM2.GetLookupTable()
#        self.add_scalarbar_2(look) # does not work for range (0.0, 0.0) [shows (0.0, 1.0)]

        self.add_outline_2(self.src)


        # vtkCellDataToPointData() ? <-
        # vtkImplicitModeller

        # si es cell data, lo transforma a point data, porque vtkContourFilter no soporta cell data.
        if self.data1.get('fielddomain') == 'cell':
            self.cdtpd = vtk.vtkCellDataToPointData()
            self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            self.contours = vtk.vtkContourFilter()
            self.contours.SetInputConnection(self.cdtpd.GetOutputPort())
            self.contours.GenerateValues(10, self.cdtpd.GetOutput().GetScalarRange())
        else:
            self.contours = vtk.vtkContourFilter()
            self.contours.SetInputConnection(self.src.GetOutputPort())
            self.contours.GenerateValues(10, self.src.GetOutput().GetScalarRange())
        
# The contour lines are mapped to the graphics library.
        self.contM = vtk.vtkPolyDataMapper()
        self.contM.SetInputConnection(self.contours.GetOutputPort())
        
        #self.wireM3 = vtk.vtkDataSetMapper() # solo para scalarbar # non funcionou
        #self.wireM3.SetInputConnection(self.src.GetOutputPort())

        self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())

#        # reverse rainbow [red->blue] -> [blue->red]
        look = self.contM.GetLookupTable()
        #look = self.wireM2.GetLookupTable()
        #look = self.wireM3.GetLookupTable()

# Actor
        self.contA = vtk.vtkActor()
        self.contA.SetMapper(self.contM)

        self.rens[0].AddActor(self.contA)
        self.rens[0].AddActor(self.wireA2)
        
        self.add_scalarbar_2(look)

        self.copy_params(struct)

        self.done = True



# fai falta
    def update(self, struct):
        self.copy_params(struct)
        self.widget.Render()



    def copy_params(self, struct):

        ch = struct.get_children()

        if len(ch) != 2:
            self.data_error('Incorrect number of childs in PlotContour (2 needed)')
            return

        selected = None
        if ch[0].get_attribs().get(config.AT_SELECTED) == config.VALUE_TRUE:
            selected = 0
        elif ch[1].get_attribs().get(config.AT_SELECTED) == config.VALUE_TRUE:
            selected = 1
            
        if selected == None:
            self.data_error('No selected child (1 needed)')    
            return
    
    # especificado numero de contornos
        if selected == 0:
            nums = ch[0].get_elements()
            if len(nums) == 1:
                num = nums[0]
                numi = None
                try:
                    numi = int(num) + 2 #añadido +2 para no tener en cuenta los límites de la escala
                except ValueError:
                    pass
                if numi is not None:
                    self.contours.GenerateValues(numi, self.src.GetOutput().GetScalarRange())
                    # reforma
                    # update range to min and max contour
                    self.scalarrange.local_set( self.src.GetOutput().GetScalarRange() )
                else:
                    self.data_error('Error converting \'' + num + '\' to integer')
            else:
                self.data_error('Incorrect number of elements (1 needed)')
            

    # valor dos contornos especificado
        if selected == 1:
            nums = ch[1].get_elements()
            nums2 = []
            good = True
            numi = None
            for num in nums:
                numf = None
                try:
                    numf = float(num)
                except ValueError:
                    good = False
                    numi = num
                    break
                if numf is not None:
                    nums2.append(numf)
            if good:
                self.contours.SetNumberOfContours(len(nums2))
                i = 0
                while i < len(nums2):
                    self.contours.SetValue(i,nums2[i])
                    i += 1
                # reforma
                # update range to min and max contour
                self.scalarrange.local_set( (min(nums2),max(nums2)) )
            else:
                self.data_error('Error converting \'' + numi + '\' to float')
