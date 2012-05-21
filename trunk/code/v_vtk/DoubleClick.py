#!/usr/bin/env python
# -*- coding: utf-8 -*-



import time



# double click
# http://vtk.org/Wiki/VTK/Examples/Interaction/DoubleClick
# http://www.vtk.org/Wiki/VTK_Mouse_Picking


"""Determines whether a click is a double click, based on elapsed time"""



class DoubleClick():
    def __init__(self):
        self.lastT = None
        self.lastX = None
        self.lastY = None

    def is_double(self, x, y):
        result = False
        t = time.time()
        if self.lastX is not None and self.lastY is not None and self.lastT is not None:
            if self.lastX == x and self.lastY == y and self.lastT + 0.5 >= t:
                result = True
        self.lastT = t
        self.lastX = x
        self.lastY = y
        return result



import vtk



class MeuInteractorStyleTC(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        #vtk.vtkInteractorStyleTrackballCamera.__init__(self)
        pass

    def OnLeftButtonDown(self):
        print 'olbd'
        vtk.vtkInteractorStyleTrackballCamera.OnLeftButtonDown(self)
