#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os.path
import FileTrack2
import FileManager2Trackers as FMT



Debug = True



# manages files to plot and convert

class FileManager2:
    def __init__(self):
        self.callback = None
        self.num = 0
        self.trackers = []

# to reuse
        self.buffer0 = {} # (string)
        self.buffer1 = {} # (string)
        self.buffer2 = {} # (string,number/string)
        self.buffer3 = {} # (string,string,number/string)
        self.buffer4 = {} # (string)
        self.buffer5 = {} # (string)
        self.buffer6 = {} # (Node)
        self.buffer7 = None # void
        self.buffer8 = {} # (Node)



# output messages
    def set_callback(self, callback=None):
        self.callback = callback



    def get_callback(self):
        return self.callback



# clears internal data
    def clear(self):
        self.num = 0
        del self.trackers[:]
        self.buffer0.clear()
        self.buffer1.clear()
        self.buffer2.clear()
        self.buffer3.clear()
        self.buffer4.clear()
        self.buffer5.clear()
        self.buffer6.clear()
        self.buffer7 = None
        self.buffer8.clear()



# for Trackers
    def get_num(self):
        num = self.num
        self.num = self.num + 1
        return num



# gets following object. vtk file
    def get_tracker_file(self, filename):
        if filename in self.buffer0:
            if Debug:
                print '0aproveitando', filename
            return self.buffer0[filename]
        else:
            if Debug:
                print '0creando', filename
            tracker = FMT.TrackerFile(self, filename)
            self.trackers.append(tracker)
            self.buffer0[filename] = tracker
            return tracker



# gets following object. vtk file
    def get_tracker_vtk_file(self, vtkfile):
        if vtkfile in self.buffer1:
            if Debug:
                print '1aproveitando', vtkfile
            return self.buffer1[vtkfile]
        else:
            if Debug:
                print '1creando', vtkfile
            tracker = FMT.TrackerVTKFile(self, vtkfile)
            self.trackers.append(tracker)
            self.buffer1[vtkfile] = tracker
            return tracker



# gets following object. mesh+ref,nsd
    def get_tracker_mfm_file(self, mesh, dim):
        if (mesh,dim) in self.buffer2:
            if Debug:
                print '2aproveitando', mesh, dim
            return self.buffer2[(mesh,dim)]
        else:
            if Debug:
                print '2creando', mesh, dim
            tracker = FMT.TrackerMFMFile(self, mesh, dim)
            self.trackers.append(tracker)
            self.buffer2[(mesh,dim)] = tracker
            return tracker



# gets following object. mesh+field
    def get_tracker_mfm_mff_files(self, mesh, field, params):
        dim = params.get('dim')
        if (mesh,field,dim) in self.buffer3:
            if Debug:
                print '3aproveitando', mesh, field, dim
            return self.buffer3[(mesh,field,dim)]
        else:
            if Debug:
                print '3creando', mesh, field, dim
            tracker = FMT.TrackerMFMMFFFiles(self, mesh, field, params)
            self.trackers.append(tracker)
            self.buffer3[(mesh,field,dim)] = tracker
            return tracker



    def get_tracker_unv_file(self, unvfile):
        if unvfile in self.buffer4:
            if Debug:
                print '4aproveitando', unvfile
            return self.buffer4[unvfile]
        else:
            if Debug:
                print '4creando', unvfile
            tracker = FMT.TrackerUNVFile(self, unvfile)
            self.trackers.append(tracker)
            self.buffer4[unvfile] = tracker
            return tracker



# gets following object. vtk file
    def get_tracker_pvd_file(self, pvdfile):
        if pvdfile in self.buffer5:
            if Debug:
                print '5aproveitando', pvdfile
            return self.buffer5[pvdfile]
        else:
            if Debug:
                print '5creando', pvdfile
            tracker = FMT.TrackerPVDFile(self, pvdfile)
            self.trackers.append(tracker)
            self.buffer5[pvdfile] = tracker
            return tracker



    def get_tracker_mesh_file(self, filename, dim=None):
        if filename.lower().endswith('.vtu'):
            return self.get_tracker_vtk_file(filename)
        elif filename.lower().endswith('.vtk'):
            return self.get_tracker_vtk_file(filename)
        elif filename.lower().endswith('.unv'):
            return self.get_tracker_unv_file(filename)
        elif filename.lower().endswith('.mfm'):
            return self.get_tracker_mfm_file(filename, dim)
        elif filename.lower().endswith('.pvd'): # is it a mesh file ? may work as a mesh file
            return self.get_tracker_pvd_file(filename)
        return None



    def get_tracker_node_files(self, node,is_nodepvd=False): #modificado
        if node in self.buffer6:
            if Debug:
                print '6aproveitando', node
            return self.buffer6[node]
        else:
            if Debug:
                print '6creando', node
            tracker = FMT.TrackerNodeFiles(self, node,is_nodepvd) #modificado
            self.trackers.append(tracker)
            self.buffer6[node] = tracker
            return tracker



    def get_tracker_void(self):
        if self.buffer7 is not None:
            if Debug:
                print '7aproveitando'
            return self.buffer7
        else:
            if Debug:
                print '7creando'
            tracker = FMT.TrackerVoid(self)
            self.trackers.append(tracker)
            self.buffer7 = tracker
            return tracker



    def get_tracker_formula(self, node, text, variables, data):
        if node in self.buffer8:
            if Debug:
                print '8aproveitando', node
            return self.buffer8[node]
        else:
            if Debug:
                print '8creando', node
#            tracker = FMT.TrackerFormula(self, node, text, variables, data)
            tracker = FMT.TrackerFormula2(self, node, text, variables, data)
            self.trackers.append(tracker)
            self.buffer8[node] = tracker
            return tracker

