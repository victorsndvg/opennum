#!/usr/bin/env python
# -*- coding: utf-8 -*-



import config
import Plot
import wx_version
import wx
import vtk
import ClickLabel3 as ClickLabel



# mostrar etiquetas con el valor del campo en los puntos donde se hace 'doble click'
interactive = True



class PlotPicture(Plot.Plot):

    def __init__(self, parent):
        Plot.Plot.__init__(self, parent)

#        self.add_scalarbar_1()
#        self.add_outline_1()
        
#        self.add_swe_1(selection=1) # wireframe/surface/surface+edges

#        self.add_opacity_1(selection=0) # Opacity: 100%/75%/50%/25%/0%
        
        self.clicker = None

#        self.add_time_1()



    def get_options(self):
        ops = {u'title':'Image'}
        if interactive:
            ops[u'interactor']=True
        return ops



    # para cuando cambia el tiempo y por tanto, self.src
    def src_update1(self, changes):
#        if changes.get('changed'):
#            self.update_outline(self.src)
        if changes.get('new'):
            self.src.Update()
            if vtk.vtkVersion.GetVTKMajorVersion() < 6:
                self.imageActor.SetInput(self.src.GetOutput())
            else:
                self.imageActor.SetInputData(self.src.GetOutput())
            self.src.SetDataScalarTypeToDouble()
#        self.src_update_clicker(self.clicker, self.src, changes)
        return True




    def plot(self, struct):

        # creates self. data1, legend, filename, fieldname, dim, has_field, tracker, revision
        if not self.call_config(struct):
            return

        # creates self.src
        if not self.call_src():
            return

        print self.src
        self.src.Update()
#        self.add_outline_2(self.src)
        self.src.SetDataScalarTypeToDouble()


        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(256)
#        lut.SetTableRange(minIntensity, maxIntensity)
        lut.SetRampToLinear()
        lut.SetScaleToLinear()
        lut.Build() 

        table = vtk.vtkLookupTable()
        table.SetRange(0, 2000) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()

#        imageMapper = vtk.vtkImageMapper()
#        imageMapper.SetInputConnection(self.src.GetOutputPort())
#        imageMapper.SetColorWindow(255)
#        imageMapper.SetColorLevel(127.5)
#        self.Actor2D = vtk.vtkActor2D()
#        self.Actor2D.SetMapper(imageMapper)


        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(self.src.GetOutputPort())

        self.imageActor = vtk.vtkImageActor()
        if vtk.vtkVersion.GetVTKMajorVersion() < 6:
            self.imageActor.SetInput(self.src.GetOutput())
        else:
            self.imageActor.SetInputData(self.src.GetOutput())
#        self.imageActor.GetMapper().SetInputData(self.src.GetOutput());

#        self.imageActor.PickableOn();
#        imageActor.SetDisplayExtent(0, im_width, 0, in_height, 0, 0);
#        self.imageActor.SetInterpolate(True)
#        bounds = self.imageActor.GetBounds()
#        self.imageActor.SetDisplayExtent([b for b in bounds])
#        print '############################################3'
#        self.imageActor.SetScale(bounds[1], bounds[3], bounds[5])
#        print self.imageActor
#        self.imageActor.SetScale(bounds[1],bounds[3],bounds[5])




#        viewer = vtk.vtkImageViewer()
#        viewer.SetInputConnection(self.src.GetOutputPort())
#        viewer.SetColorWindow(256)
#        viewer.SetColorLevel(127.5)

        self.rens[0].AddActor2D(self.imageActor) # malla con cores

        self.do_render()
        self.done = True



# non fai falta
#    def update(self, struct):
#        self.widget.Render()
