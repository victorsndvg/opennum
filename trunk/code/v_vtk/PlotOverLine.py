#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk


# caso especial: dividida con 2 wxVTKRenderWindowInteractor


class PlotOverLine(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

        self.add_scalarbar_1(False)
        self.add_outline_1()
        self.set_iren() # RenderWindowInteractor
        
        self.add_swe_1(selection=1) # wireframe/surface/surface+edges



    def get_options(self):
        return {u'split':True,u'title':'Plot over line'}



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
        if changes.get('changed'):
            if self.data1.get('fielddomain') == 'cell':
                probe.SetSource(self.cdtpd.GetOutput())
            else:
                self.probe.SetSource(self.src.GetOutput())
        if changes.get('new'):
            self.wireM.SetInputConnection(self.src.GetOutputPort())
        if changes.get('changed'):
            self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())
            self.update_outline(self.src)
            #
            #self.sbA.SetLookupTable(self.look) # no actualiza
            #self.sbA.SetLookupTable(self.wireM.GetLookupTable()) # no actualiza

        if changes.get('changed'):
            self.lineI.SetInput(self.src.GetOutput())
#        if changes.get('changed'):
#            self.copy_params(self.struct) # not neccesary ?
        return True



    def range_update3(self, range):
        self.wireM.SetScalarRange(range)
        self.look.SetTableRange(range)
        #self.do_render() # extra sin o anterior


    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

# linha start
        # => src_update1
        self.range_in = self.src.GetOutput().GetScalarRange()
        b = self.range_bo = self.src.GetOutput().GetBounds()
        print 'reader scalars', self.range_in
        print 'reader bounds', self.range_bo

        # Create three the line source to use for the probe lines.
#        p1 = ((b[0]+b[1])/2.0, b[2], (b[4]+b[5])/2.0)
#        p2 = ((b[0]+b[1])/2.0, b[3], (b[4]+b[5])/2.0)
        p1 = (b[0], b[2], b[4])
        p2 = (b[1], b[3], b[5])
        self.line = vtk.vtkLineSource()
        self.line.SetResolution(100)
        #self.line.SetPoint1(p1)
        #self.line.SetPoint2(p2)
        self.line.SetPoint1((0,0,0))
        self.line.SetPoint2((1,1,1))

        self.probe = probe = vtk.vtkProbeFilter()
        probe.SetInputConnection(self.line.GetOutputPort())
        
        # si es cell data, lo transforma a point data, porque vtkProbeFilter parece ser que no soporta cell data.
        if self.data1.get('fielddomain') == 'cell':
            self.cdtpd = vtk.vtkCellDataToPointData()
            self.cdtpd.SetInputConnection(self.src.GetOutputPort())
            probe.SetSource(self.cdtpd.GetOutput())
        else:
            probe.SetSource(self.src.GetOutput())

#        lineMapper = vtk.vtkPolyDataMapper()
#        lineMapper.SetInputConnection(probe.GetOutputPort())
#        lineMapper.ScalarVisibilityOff()
#        self.lineActor = vtk.vtkActor()
#        self.lineActor.SetMapper(lineMapper)
#        self.lineActor.GetProperty().SetColor(Plot.probe_line_color)
# linha end

        self.wireM = vtk.vtkDataSetMapper()
        self.wireM.SetInputConnection(self.src.GetOutputPort())

# reverse rainbow [red->blue] -> [blue->red]
        self.look = look = self.wireM.GetLookupTable()

        self.scalarrange.local_set(self.src.GetOutput().GetScalarRange())

        self.add_scalarbar_2(look)

        self.add_outline_2(self.src)

        self.wireA = vtk.vtkActor()
        self.wireA.SetMapper(self.wireM)
        self.wireA.GetProperty().SetRepresentationToSurface()
        self.wireA.GetProperty().SetColor(Plot.edges_color)
        self.wireA.GetProperty().SetEdgeColor(Plot.edges_color)
        
        self.add_swe_2(self.wireA) # wireframe/surface/surface+edges
        
# test mover liña interactivamente 2 INICIO
        self.lineI = vtk.vtkLineWidget()
        self.lineI.GetLineProperty().SetColor(Plot.probe_line_color)
        seeds = vtk.vtkPolyData()
        self.lineI.SetInput(self.src.GetOutput())
        self.lineI.PlaceWidget()
        self.lineI.GetPolyData(seeds)

        iren = self.widget.GetRenderWindow().GetInteractor()
        self.lineI.SetInteractor(iren)
        self.lineI.On()

        self.lineI.AddObserver("StartInteractionEvent", self.event_start)
#        self.lineI.AddObserver("InteractionEvent", self.event)
        self.lineI.AddObserver("EndInteractionEvent", self.event_end)

# test mover liña interactivamente 2 FIN
        p1 = self.lineI.GetPoint1()
        p2 = self.lineI.GetPoint2()
        self.line.SetPoint1(p1)
        self.line.SetPoint2(p2)


        self.rens[0].AddActor(self.wireA)
#        self.rens[0].AddActor(self.lineActor)
        #self.rens[0].SetViewport(0, 0, 0.5, 1)

# end


        
# xy start

        # The x-values we are plotting are the underlying point data values.
        self.xyplot3 = xyplot3 = vtk.vtkXYPlotActor()
        xyplot3.AddInput(probe.GetOutput())
        xyplot3.GetPositionCoordinate().SetValue(0.0, 0.0, 0)
        xyplot3.GetPosition2Coordinate().SetValue(1.0, 0.95, 0) #relative to Position
#        xyplot3.SetXValuesToIndex()
#        SetXValuesToNormalizedArcLength()
        xyplot3.SetXValuesToArcLength()
#        xyplot3.SetXValuesToValue()
        xyplot3.SetPointComponent(0,1)
        xyplot3.SetNumberOfXLabels(6)
        xyplot3.SetTitle(" ")
        xyplot3.SetXTitle(" ")
        xyplot3.SetYTitle(" ")
        xyplot3.PlotPointsOn()
        xyplot3.GetProperty().SetColor(1, 1, 1)
        xyplot3.GetProperty().SetPointSize(3)
        # Set text prop color (same color for backward compat with test)
        # Assign same object to all text props
        tprop = xyplot3.GetTitleTextProperty()
        tprop.SetColor(xyplot3.GetProperty().GetColor())
        xyplot3.SetAxisTitleTextProperty(tprop)
        xyplot3.SetAxisLabelTextProperty(tprop)

#        self.ren2 = self.add_ren()
        ren = vtk.vtkRenderer()
        self.widget2.GetRenderWindow().AddRenderer(ren)
        #ren.SetViewport(0.5, 0, 1, 1)
        ren.AddActor(xyplot3)

# xy end

        # se é esta en branco o leaf float, encheo de valores extremos
        if self.is_empty(struct):
            self.fill(struct, p1, p2)
            
        # le os datos do leaf float
        self.copy_params(struct)

        self.done = True



    def event_start(self, obj, event):
        print 'start'

    def event(self, obj, event):
        pass

    def event_end(self, obj, event):
        p1 = self.lineI.GetPoint1()
        p2 = self.lineI.GetPoint2()
        print 'end', p1, p2
        self.line.SetPoint1(p1)
        self.line.SetPoint2(p2)
        self.fill(self.struct, p1, p2)
        #self.probe.Update()
        #self.ren2.Render()
        #self.xyplot3.Update()
        #self.widget.Render() # test
        self.widget2.Render()


# fai falta
    def update(self, struct):
        #print 'iren2.enabled:', self.iren2.GetEnabled()
        self.copy_params(struct)
        self.widget.Render() # necesario # comentado este, center non falla
        self.widget2.Render()



    def is_empty(self, struct):    
        ch = struct.get_children()
        if len(ch) < 2:
            return None
        nums1 = ch[0].get_elements()
        nums2 = ch[1].get_elements()
        return len(nums1) == 0 and len(nums2) == 0



    def fill(self, struct, pA, pB):
        ch = struct.get_children()
        if len(ch) < 2:
            return None
            
        p1 = []
        for a in pA:
            p1.append(unicode(a))
        p2 = []
        for a in pB:
            p2.append(unicode(a))

        ch[0].set_elements_nosel(p1)
        ch[1].set_elements_nosel(p2)
        self.panel_widgets.update_widget_struct(ch[0])
        self.panel_widgets.update_widget_struct(ch[1])



    def copy_params(self, struct):

        result = self.read_2_vectors(struct, [' in PlotOverLine',' in first point',' in second point'])

        if result is not None:
            self.lineI.SetPoint1(result[0])
            self.lineI.SetPoint2(result[1])
            self.line.SetPoint1(result[0])
            self.line.SetPoint2(result[1])
