#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os.path
import FileTrack2
import FileMrwReconvxx as R
import FileMrwScalars as S
import FileMrwUNV as U
import FileMrwVTK
import FilePVD
import Formulas as psps # para postproceso
from v_vtk import sourceVTK2

Debug = False

# Tracker used in other classes

class Tracker:
    def __init__(self, fm):
        self.type = "generic"
        self.fm = fm
        self.cb = fm.get_callback()
        self.num = -1
        self.needs_vtkfiles = True
        self.vtkfile = ''
        self.filetracks = []
        self.dim = None
        self.revision = 0
        self.revision_src = 0
        self.revision_in_src = -1 # revision a la que corresponde revision_src
        self.refs = None # dictionary of { string -> list of strings }
        self.src = None
        self.size1 = 1 # size of first group (1). 0 => main 0 additional 1 ; 1 => main 1 additional 0
        self.name = '-'
        self.center = None
        self.has_series_ = False
	self.is_nodepvd = False			#añadido. identificacion de trackernode
	self.is_void = False			#añadido. identificacion de trackervoid



    # to avoid tests
    def cbc(self, str):
        if self.cb is not None:
            self.cb(str)



# before update does not give value
    def get_vtkfile(self):
        return self.vtkfile



    def get_revision(self):
        return self.revision


    def get_revision_src(self):
        return self.revision_src


# + update ?
    def get_refs(self):
        return self.refs

        
        
    def get_type(self):
        return self.type



# devolve se o tracker ten gardadas series de mallas por tempo, frecuencia, ...
    def has_series(self):
        return self.has_series_



    def get_dim(self):
        return self.dim



# Null / False / True
    def is_changed(self, write=True):
        changed = False
        for a in self.filetracks:
            state = a.is_changed()
            if state is None:
                if write:
                    self.cbc(u'Error: file \'' + a.get_name() + '\' is not accesible\n')
            if state is True and changed is not None:
                changed = True
            if state is None:
                changed = None
        return changed


# Devielve una lista de trackers a partir de una lista de mallas individuales
    def get_additional_trackers(self,filesmesh):				#añadido
	trackerlist = []							#añadido
	for fn in filesmesh:							#añadido	
	    trackerlist.append(self.fm.get_tracker_mesh_file(fn))		#añadido
	return trackerlist


# public
# rereads files if necesary
# ref N/t/f - fail/changed/not_changed
    def update(self):

        changed = self.is_changed()

        if changed:

            if self.needs_vtkfiles:
                self.num = self.fm.get_num()
                self.vtkfile = u'tempfile_' + unicode(self.num) + '.vtk'
            result = self.recalculate()
            self.revision = self.revision + 1 # also on fail
            if result:
                for a in self.filetracks:
                    a.unchange() # marks as unchanged
            else:
                return None

        return changed



    def recalculate(self):
# vtkname and num already defined
        return True




    def get_src(self, labels=None,index=None): # posible informar de se recalculou/rexerou
        recalc = self.src is None
        recalc = recalc or self.revision_in_src != self.revision # outros fóra poden chamar a update()

        res = self.update() # necesario ter chamado, antes de get_vtkfile()
        if res is None: #fail
            return 'Error updating source file data'
        elif res is True: #changed
            recalc = recalc or True
        elif res is False: #unchanged
            recalc = recalc or False

        if recalc:
            src = sourceVTK2.get_source(self.get_vtkfile())
            if isinstance(src, basestring):
                return src
            self.revision_in_src = self.revision
            self.revision_src += 1
            self.src = src
            self.center = None

        if labels is not None:
            if self.center is None:
                self.center = self.src.GetOutput().GetCenter()
            labels.append([self.center, self.get_name()])

        return self.src



    # redefinido en subclase
    def forget_src(self):
        self.src = None



    def set_size1(self, value):
        self.size1 = value



    # para que TrackerNodeFiles lo sobreescriba
    # 0 todos
    # 1 principales
    # 2 secundarios
    # aquí: todos principales
    def get_src_group(self, group, labels=None):
        if group == 0:
            return self.get_src(labels)
        elif group == 1:
            if self.size1 > 0:
                return self.get_src(labels)
            else:
                return self.fm.get_tracker_void().get_src(labels)
        elif group == 2:
            if self.size1 < 1:
                return self.get_src(labels)
            else:
                return self.fm.get_tracker_void().get_src(labels) # was None
        else:
            return 'Incorrect group number'



    # os do grupo 1 que non teñan o campo van para o grupo 2
    def get_src_group_f(self, group, field=None, labels=None,index=None):
        if group == 0:
            return self.get_src(labels)
        elif group == 1:
            if self.size1 <= 0:
                return self.fm.get_tracker_void().get_src(labels)
            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            src = self.get_src(labels_aux)
            if isinstance(src, basestring):
                return src
            has = sourceVTK2.has_field(src, field)
            if not has:
                return self.fm.get_tracker_void().get_src(labels)
            if labels is not None:
                labels.extend(labels_aux)
            return src
        elif group == 2:
            if self.size1 < 1:
                return self.get_src(labels)
            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            src = self.get_src(labels_aux)
            if isinstance(src, basestring):
                return src
            has = sourceVTK2.has_field(src, field)
            if not has:
                if labels is not None:
                    labels.extend(labels_aux)
                return src
            return self.fm.get_tracker_void().get_src(labels) # was None
        else:
            return 'Incorrect group number'



    def get_original_files(self):
        files = []
        for f in self.filetracks:
            files.append(f.get_name())
        return files



    def set_name(self, name):
        self.name = name



    def get_name(self):
        return self.name



# tracker for no file:



class TrackerVoid(Tracker):

    def __init__(self, fm):
        Tracker.__init__(self, fm)
        self.needs_vtkfiles = False
	self.is_void = True

    def get_src(self, labels=None):
        # non se engaden labels para o obxecto baleiro
        if self.src is None:
            self.src = sourceVTK2.get_void()
        return self.src



# tracker for 'files'. trivial

class TrackerFile(Tracker):
    def __init__(self, fm, filename):
        Tracker.__init__(self, fm)
        self.needs_vtkfiles = False
        self.filetracks.append(FileTrack2.FileTrack2(filename))
#        self.set_name(os.path.basename(filename))



#overwrite method to reuse 'file' name
    def get_vtkfile(self):
        return self.filetracks[0].get_name()





# tracker for vtk/vtu files. trivial

class TrackerVTKFile(Tracker):
    def __init__(self, fm, vtkfile):
        Tracker.__init__(self,fm)
        self.needs_vtkfiles = False
        self.filetracks.append(FileTrack2.FileTrack2(vtkfile))
#        self.set_name(os.path.basename(vtkfile))



#overwrite method to reuse vtk file name
    def get_vtkfile(self):
        return self.filetracks[0].get_name()





# tracker for mesh files mfm

class TrackerMFMFile(Tracker):
    def __init__(self, fm, mesh, dim):
        Tracker.__init__(self,fm)
        self.dim = dim
        self.filetracks.append(FileTrack2.FileTrack2(mesh))
#        self.set_name(os.path.basename(mesh))



# private
    def recalculate(self):
        the_file = self.filetracks[0].get_name()
        rr = R.FileMrwReconvxx(self.cb)
        res = rr.read(the_file, {'dim':self.dim})
        
        if res is not True:
            self.cbc(u'Error loading file \''+the_file+'\': '+ unicode(res) +'\n')
            return False
        else:
            self.dim = rr.get_dim()

            # some file may not have every reference
                     
            # nsd nrc nra nrv -> element_ref face_ref edge_ref vertex_ref
            self.refs = {}
            for k, v in rr.get_refs().items():
                if v is not None:
                    temps = v.copy()
                    temps.discard(0)
                    templ = list(temps)
                    templ.sort()
                    self.refs[k] = map(str, templ)

            self.cbc(u'Calculating submesh ... ')

            res = rr.calculate_submesh()

            if not res:
                self.cbc(u'Error calculating submesh: \''+the_file+'\'\n')
                return False

            self.cbc('\n')

            self.cbc(u'Converting to .vtk ... ')
    
            k = rr.to_vtk()

            self.cbc('\n')

            # o: meter dentro de to_vtk, controlado por un bool, o recuperar numero de subceldas
            
            # array de puntos .. id [0..n-1] -> [1..n]
            # para ter os números dispoñibles para as etiquetas
            k.add_point_data_sequential()
            array = range(1, rr.nel + 1) # elementos originales numerados
            array.extend([0] * rr.nsm) # la submalla no se numera
            k.add_cell_data_sequential(array)

            # optional
            res = k.check()
            if res is not True:
                self.cbc(u'Error checking .vtk: k.check(): ' + res + u'\n')
                return False

            self.cbc(u'Saving \'' + self.vtkfile + '\' ... ')

            res = k.save(self.vtkfile)

            if not res:
                self.cbc(u'Error saving file: \''+the_file+'\'\n')
                return False
                
            self.cbc('saved!\n')
                
            return True



# 'tracker' for mesh + field files

class TrackerMFMMFFFiles(Tracker):
    def __init__(self, fm, mesh, field, params):
        Tracker.__init__(self, fm)
        self.params = params
        self.dim = params.get('dim')
        self.filetracks.append(FileTrack2.FileTrack2(mesh))
        self.filetracks.append(FileTrack2.FileTrack2(field))
#        self.set_name(os.path.basename(mesh)+'+'+os.path.basename(field))



# private
# does not work with .vtk mesh
    def recalculate(self):
        the_mesh = self.filetracks[0].get_name()
        the_field = self.filetracks[1].get_name()
        rr = R.FileMrwReconvxx(self.cb)
        res = rr.read(the_mesh, {'dim':self.dim})
        
        if res is not True:
            self.cbc(u'Error loading file \''+the_mesh+'\': '+ unicode(res) +'\n')
            return False
        else:

            self.dim = rr.get_dim()

            # element_ref face_ref edge_ref vertex_ref
            # submesh not calculated

            # self.refs not calculated -> calculated
            # some file may not have every reference
            # nsd nrc nra nrv -> element_ref face_ref edge_ref vertex_ref
            self.refs = {}
            for k, v in rr.get_refs().items():
                if v is not None:
                    temps = v.copy()
                    temps.discard(0)
                    templ = list(temps)
                    templ.sort()
                    self.refs[k] = map(str, templ)


            self.cbc(u'Converting to .vtk ... ')
    
            k = rr.to_vtk()
            
            self.cbc('\n')

            ss = S.FileMrwScalars(self.cb)
            res = ss.read(the_field,{})

            if res is not True:
                self.cbc(u'Error reading field: \''+the_field+'\': '+unicode(res)+'\n')
                return False
                
            field_data = ss.gets()

            # more tests
            # self.params.get('fieldtype')
            pnum = k.get_point_num()
            cnum = k.get_cell_num()
            fnum = len(field_data)

            anum = None
            if self.params.get('fielddomain') == 'point':
                anum = pnum
            elif self.params.get('fielddomain') == 'cell':
                anum = cnum

            if Debug: print 'point', pnum, 'cell', cnum, 'field', fnum, 'point_or_cell', anum
                
            if anum == fnum:
                if self.params.get('fielddomain') == 'point':
                    k.add_point_data('SCALARS',self.params.get('fieldname'),'double',None,field_data)
                elif self.params.get('fielddomain') == 'cell':
                    k.add_cell_data('SCALARS',self.params.get('fieldname'),'double',None,field_data)
            elif anum * 2 == fnum:
                # insertar ceros para tener 3 componentes
                datanew = []
                for i in range(anum):
                    datanew.append(field_data[i*2])
                    datanew.append(field_data[i*2+1])
                    datanew.append(0.0)
                if self.params.get('fielddomain') == 'point':
                    k.add_point_data('VECTORS',self.params.get('fieldname'),'double',None,datanew)
                elif self.params.get('fielddomain') == 'cell':
                    k.add_cell_data('VECTORS',self.params.get('fieldname'),'double',None,datanew)
            elif anum * 3 == fnum:
                if self.params.get('fielddomain') == 'point':
                    k.add_point_data('VECTORS',self.params.get('fieldname'),'double',None,field_data)
                elif self.params.get('fielddomain') == 'cell':
                    k.add_cell_data('VECTORS',self.params.get('fieldname'),'double',None,field_data)
            elif anum is None:
                print 'FileManager2Trackers.py: not cell not point'
                pass
            else:
                self.cbc(u'Error: number of items of field file \''+the_field+'\' does not match number of items of mesh file \''+the_mesh+'\'\n')
                return False

            # optional
            res = k.check()
            if res is not True:
                self.cbc(u'Error checking .vtk: k.check(): ' + res + u'\n')
                return False

            self.cbc(u'Saving \'' + self.vtkfile + '\' ... ')

            res = k.save(self.vtkfile)

            if not res:
                self.cbc(u'Error saving file: \''+the_mesh+'\' + \''+the_field+'\'\n')
                return False

            self.cbc('saved!\n')

            return True




# tracker for UNV files .unv

class TrackerUNVFile(Tracker):
    def __init__(self, fm, mesh):
        Tracker.__init__(self,fm)
        #self.dim = dim
        self.filetracks.append(FileTrack2.FileTrack2(mesh))
#        self.set_name(os.path.basename(mesh))



    # private
    def recalculate(self):
        the_file = self.filetracks[0].get_name()
        unv = U.UNV()
        error = unv.read(the_file)
        if error is not None:
            self.cbc(u'Error loading file: \''+the_file+':'+error+u'\n')
            return False
        
        vtk = unv.to_vtk()
        
        if not isinstance(vtk, FileMrwVTK.FileMrwVTK):
            self.cbc("Error converting to .vtk: " + vtk + u'\n')
            return False
        
        # optional
        res = vtk.check()
        if res is not True:
            self.cbc(u'Error checking .vtk: vtk.check(): ' + res + u'\n')
            return False

        # nsd nrc nra nrv -> element_ref face_ref edge_ref vertex_ref
        self.refs = {}
        for k, v in unv.get_refs().items():
            if v is not None:
                self.refs[k] = map(str, v)
    
        self.cbc(u'Saving \'' + self.vtkfile + '\' ... ')

        result = vtk.save(self.vtkfile)
    
        if result is not True:
            self.cbc("Error saving .vtk file\n")
            return False

        self.cbc('saved!\n')
        
        return True



class TrackerPVDFile(Tracker):
    """Tracker for .pvd files"""



    def __init__(self, fm, file):
        Tracker.__init__(self,fm)
        self.type = 'pvd'
        self.needs_vtkfiles = False
        self.filetracks.append(FileTrack2.FileTrack2(file))
        self.times = []
        self.trackers = []
        self.has_series_ = True



    def recalculate(self):
        the_file = self.filetracks[0].get_name()
        res = FilePVD.read(the_file)
        if isinstance(res, list):
            self.times = res
            self.trackers = [None] * len(res)
            return True
        else:
            self.times = []
            self.trackers = []
            self.cbc(res+"\n")
            return False



    def get_vtkfile(self):
        return self.filetracks[0].get_name()



    def get_times(self):
        return self.times



    # before update does not give value
    def get_tracker(self, index):
        if len(self.trackers) <= 0:
            return ".pvd file with 0 entries"
        if not (index >= 0 and index < len(self.trackers)):
            return ".pvd: index out of range"
        if self.trackers[index] is not None:
            return self.trackers[index]

        rel = self.times[index].get('file')
        
        filename = os.path.join(os.path.dirname(self.get_vtkfile()), rel)

        tracker = self.fm.get_tracker_mesh_file(filename)

        if tracker is None:
            return 'Unable to open file from .pvd: \''+ filename +'\''
        
        tracker.set_name(os.path.basename(rel))
        
        self.trackers[index] = tracker
        
        return tracker

    def search_time_pos(self, time,evolution=None):
	auxtimedic = None
	for timedic in self.times:
	    #Si encuentra el tiempo devuelve la posición
	    if timedic.get(u'time') == time:
		return self.times.index(timedic)
	    elif auxtimedic is not None:
		#Si no encuentra el tiempo, devuelve el comienzo del intervalo
		if auxtimedic.get(u'time')<time and timedic.get(u'time')>time:
		    return self.times.index(auxtimedic)
	    auxtimedic = timedic
	return None





class TrackerNodeFiles(Tracker):
    """Tracker for joining several files"""
    
    def __init__(self, fm, node,is_nodepvd=False):
        Tracker.__init__(self, fm)
        self.needs_vtkfiles = False
        self.type = "node_files"
        
        self.node = node
        self.trackers = []
        self.sources = []
        self.labels = [] # array [[[]]]
        # index of first additional mesh == size of main meshes
        self.size1 = 0
        
        self.src1 = None
        self.src2 = None
        self.rev1 = -1
        self.rev2 = -1
        self.modified = True # non 'standard'

	self.is_nodepvd = is_nodepvd					#añadido
	self.has_series_ = is_nodepvd					#añadido



#    def has_series(self):
#	return True

    def get_times(self):
	times = []
	for tr in self.trackers:
	    res =  FilePVD.read(tr.filetracks[0].get_name())
	    tr.times = res
	    times.append(res)
	return times
	    

    # before update does not give value
    def get_tracker(self, index):
	trackers = []
        if len(self.trackers) <= 0:
            return ".pvd node file with 0 entries"
        if not (index >= 0):
            return ".pvd: index out of range"

	for tr in self.trackers:
	    if len(tr.trackers)>0:
	    	if tr.trackers[index] is not None:
		    tracker =  tr.trackers[index]
	    	    trackers.append(tracker)
	    else:
		rel  = tr.get_times()[index].get('file')
		filename = os.path.join(os.path.dirname(tr.get_vtkfile()), rel)
		tracker = self.fm.get_tracker_mesh_file(filename)
		if tracker is None:
		    return 'Unable to open file from .pvd: \''+ filename +'\''
		tracker.set_name(os.path.basename(rel))
		try:
		    tr.trackers[index] = tracker
		except IndexError:
		    pass
		trackers.append(tracker)

	return trackers

    def get_original_files(self):


        files = []
        for f in self.filetracks:
            files.append(f.get_name())
        return files

########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################


        # posto aqui para evitar que cree o plot e dea erro despois: que o dea antes
    # Null / False / True
    def is_changed(self, write=True):
        if self.modified:
            return True
        for t in self.trackers:
            res = t.is_changed(write)
            if res is None:
                return None
            if res is True:
                return True
        return False



    def set_trackers(self, trackers, first_group=-1):

        if len(self.trackers) != len(trackers):
            self.modified = True
        else:
            for i in xrange(len(trackers)):
                if self.trackers[i] is not trackers[i]:
                    self.modified = True
        self.trackers = trackers[:]
        if first_group < 0:
            self.size1 = len(trackers)
        else:
            self.size1 = first_group

    # before update does not give value
    def get_tracker(self, index):						#añadido
        if len(self.trackers) <= 0:						#añadido
            return "node tracker file with 0 entries"				#añadido
        if not (index >= 0):							#añadido
            return "node tracker file: index out of range"			#añadido
        if self.trackers is not None:						#añadido
	    t = []
	    for tr in self.trackers:
		# Captura del error. Necesario en mallas adicionales
		try:								#añadido
		    t.append(tr.get_tracker(index))
		except:								#añadido
		    pass							#añadido
            return t 								#añadido
				
        rel = self.times[index].get('file')					#añadido
        
        filename = os.path.join(os.path.dirname(self.get_vtkfile()), rel)	#añadido

        tracker = self.fm.get_tracker_mesh_file(filename)			#añadido

        if tracker is None:							#añadido
            return 'Unable to open file from .pvd: \''+ filename +'\''		#añadido
        
        tracker.set_name(os.path.basename(rel))					#añadido
        
        self.trackers[index] = tracker						#añadido
        
        return tracker								#añadido


    # Devuelve la lista de tiempos 
    def get_times(self):							#añadido
	times = []								#añadido
	for tr in self.trackers:						#añadido
	    # Captura del error. Necesario en mallas adicionales
	    try:								#añadido
		lasttime = tr.get_times()					#añadido
		times.append(tr.get_times())					#añadido
	    except:								#añadido
		pass								#añadido
	return lasttime								#añadido



    # private
    def get_sources(self, trackers,index=None):

        srcs = []
        labels = []

	if self.is_nodepvd:							#añadido
	    if index is not None:						#añadido
		for tr in trackers:						#añadido
		    # Captura del error. Necesario en la actualización de mallas adicionales
		    try:							#añadido
			t = tr.get_tracker(index)				#añadido
			labels1 = []						#añadido
			src = t.get_src(labels1,index)				#añadido	
			if isinstance(src, basestring):				#añadido
			    return (src, [])					#añadido
			srcs.append(src)					#añadido
			labels.append(labels1) # append non extend. habilitar varias/ningunha label por src#añadido
		    except:							#añadido
                	labels1 = []
                	src = tr.get_src(labels1,index)
                	if isinstance(src, basestring):
                    	    return (src, [])
                	srcs.append(src)
                	labels.append(labels1) # append non extend. habilitar varias/ningunha label por src
	    else:
		return ['Error','Index in multiple PVD trackerNodeFiles is None']

	else:
            for tr in trackers:
                labels1 = []
                src = tr.get_src(labels1)
                if isinstance(src, basestring):
                    return (src, [])
                srcs.append(src)
                labels.append(labels1) # append non extend. habilitar varias/ningunha label por src
        self.modified = False
        return (srcs, labels)



    # private
    def compare_sources(self, srcs1, srcs2):
        if len(srcs1) != len(srcs2):
            return False
        for i in range(len(srcs1)):
            if srcs1[i] is not srcs2[i]:
                return False
        return True



    def forget_src(self):
        self.src = None # pode non ser vtkAppendFilter
        self.src1 = None
        self.src2 = None



    # self.src pode non ser vtkAppendFilter
    def get_src(self, labels=None,index=None):				#modificado

        (newsrcs,newlabels) = self.get_sources(self.trackers,index)

        if isinstance(newsrcs, basestring):
            return newsrcs
        res = self.compare_sources(self.sources, newsrcs)

        recalc = False
        if not res:
            recalc = True
        if self.src is None:
            recalc = True

        if recalc:
            self.sources = newsrcs
            self.labels = newlabels
            
            # ou ben actualizar o que habia

            
            # self.src pode non ser vtkAppendFilter
            # evita update con tamanho 0. vtkAppendFilter ten que ter >0 entradas
            if len(self.sources) == 0:
                self.src = self.fm.get_tracker_void().get_src(labels)
            else:
                self.src = sourceVTK2.get_append(self.sources)

            self.src.Update() # para poder obtener números de referencia en sourceVTK2. (o llamarlo allí)
            #self.revision_in_src = self.revision # aqui pareceme que non fai falta
            self.revision_src += 1

        if labels is not None:
            for ls in self.labels:
                labels.extend(ls)

        return self.src



    # TrackerNodeFiles lo sobreescribe
    # 0 todos
    # 1 principales
    # 2 secundarios
    def get_src_group(self, group, labels=None, index=None):

        if group == 1:
            if self.size1 == 0: # baleiro
                return self.fm.get_tracker_void().get_src(labels)
            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            res = self.get_src(labels_aux, index)
            if isinstance(res, basestring):
                return res
            if self.size1 == len(self.sources): # todos
                if labels is not None:
                    labels.extend(labels_aux)
                return res
            if self.src1 is None or self.rev1 != self.revision_src:
                if self.src1 is None:
                    self.src1 = sourceVTK2.get_append(self.sources[:self.size1])
                else:
                    self.src1 = sourceVTK2.config_append(self.src1, self.sources[:self.size1])
                self.src1.Update() # para poder obtener números de referencia en sourceVTK2. (o llamarlo allí)
                self.rev1 = self.revision_src
            if labels is not None:
                for ls in self.labels[:self.size1]:
                    labels.extend(ls)
            return self.src1
        elif group == 2:
            if self.size1 == len(self.sources): # baleiro
                return self.fm.get_tracker_void().get_src(labels) # was None
            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            res = self.get_src(labels_aux)
            if isinstance(res, basestring):
                return res
            if self.size1 == 0: # todos
                if labels is not None:
                    labels.extend(labels_aux)
                return res
            if self.src2 is None or self.rev2 != self.revision_src:
                if self.src2 is None:
                    self.src2 = sourceVTK2.get_append(self.sources[self.size1:])
                else:
                    self.src2 = sourceVTK2.config_append(self.src2, self.sources[self.size1:])
                self.src2.Update() # para poder obtener números de referencia en sourceVTK2. (o llamarlo allí)
                self.rev2 = self.revision_src
            if labels is not None:
                for ls in self.labels[self.size1:]:
                    labels.extend(ls)
            return self.src2
        elif group == 0:
            return self.get_src(labels)
        else:
            return 'Incorrect group number'



    # os do grupo 1 que non teñan o campo van para o grupo 2
    def get_src_group_f(self, group, field=None, labels=None,index=None):		#modificado

        if group == 1:
            if self.size1 == 0: # baleiro
                return self.fm.get_tracker_void().get_src(labels)
            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            res = self.get_src(labels_aux,index)					#modificado
            if isinstance(res, basestring):
                return res

            # mirar cada un que vale
            labels_aux2 = []
            total = []
            i = 0
            for s in self.sources:
                if i >= self.size1:
                    break
                has = sourceVTK2.has_field(s, field)
                if has:
                    total.append(s)
                    if labels is not None:
                        labels_aux2.extend(self.labels[i])
                i += 1

            if len(total) == len(self.sources): # todos
                if labels is not None:
                    labels.extend(labels_aux)
                return res
            if len(total) == 0:
                return self.fm.get_tracker_void().get_src(labels)
            if self.src1 is None or self.rev1 != self.revision_src:
                if self.src1 is None:
                    self.src1 = sourceVTK2.get_append(total)
                else:
                    self.src1 = sourceVTK2.config_append(self.src1, total)
                self.src1.Update() # para poder obtener números de referencia en sourceVTK2. (o llamarlo allí)
                self.rev1 = self.revision_src
            if labels is not None:
                labels.extend(labels_aux2)
            return self.src1
        elif group == 2:

            if labels is None:
                labels_aux = None
            else:
                labels_aux = []
            res = self.get_src(labels_aux,index)

            if isinstance(res, basestring):
                return res
            if self.size1 == 0: # todos
                if labels is not None:
                    labels.extend(labels_aux)
                return res

            # mirar cada un que vale
            labels_aux2 = []
            total = []
            i = 0
            for s in self.sources:
                if i >= self.size1:
                    break
                has = sourceVTK2.has_field(s, field)
                if not has:
                    total.append(s)
                    if labels is not None:
                        labels_aux2.extend(self.labels[i])
                i += 1

            if self.size1 - len(total) == len(self.sources): # baleiro
                return self.fm.get_tracker_void().get_src(labels) # was None
            
            for l in self.labels[self.size1:]:
                labels_aux2.extend(l)

            todos = total + self.sources[self.size1:]
	    #Es necesario forzar para ver las mallas secundarias????
	    #self.src2 = None
            if self.src2 is None or self.rev2 != self.revision_src:
                if self.src2 is None:
                    self.src2 = sourceVTK2.get_append(todos)
                else:
                    self.src2 = sourceVTK2.config_append(self.src2, todos)
                self.src2.Update() # para poder obtener números de referencia en sourceVTK2. (o llamarlo allí)
                self.rev2 = self.revision_src

            if labels is not None:
                labels.extend(labels_aux2)

            return self.src2

        elif group == 0:
            return self.get_src(labels)
        else:
            return 'Incorrect group number'



# BORRABLE
# crear como o pvd: recalculate
# é pvd: devolver se ten fillos pvds [se ten varios queda pendente comprobar/que facer se son incompatibles]
class TrackerFormula(Tracker):
    """Tracker for formulas"""



    def __init__(self, fm, node, text, variables, data):
        Tracker.__init__(self,fm)
        self.type = 'formula'
        self.needs_vtkfiles = False
        self.trackers = []
        self.sources = []
        self.varias = []

        self.node = node
        self.text = text
        self.variables = variables
        self.data = data

        self.set_name('formula')
        self.revision_varias = 0
        self.revision_varias_src = -1



    def fill(self):
        # get data, campos...
        # engadir dependencias ou xa computadas noutro lado: PanelVisual? si, xa noutro lado
        for var,data in zip(self.variables, self.data['formula_data']):
            if var[4] == 'menu-field':
                tracker = var[3].get_tracker5(self.fm, data)
                if isinstance(tracker, basestring):
                    return 'Error filling formula:' + tracker
                self.trackers.append(tracker)
            else:
                self.trackers.append(None)

        ret = self.combinate()

        return ret # True



    def combinate(self):
        # averiguar point/cell !
        # averiguar scalar/vector !
        # averiguar nomes de campos !
        # averiguar numero de items
        # comprobar que coincidan
        # crear src
        # encher src
        srcs = []
        srcsnames = []
        srcsfieldnames = []
        varnames = set()
        varias = []
        for var,data,tracker in zip(self.variables, self.data['formula_data'], self.trackers):
            name = var[0]
            if name in varnames:
                return "Error: repeated variable name: " + name
            varnames.add(name)
            type2 = var[4]
            if type2 == 'menu-field':
                # non válido para os pvd
                src = tracker.get_src_group(1) # ou tracker.get_src_group_f(1, self.fielddata, mnames) "ou sin f"
                if isinstance(src, basestring):
                    return "Error getting source object: " + src
                srcs.append(src)
                srcsnames.append(name)
                srcsfieldnames.append(data.get('fieldname'))
                varias.append((name,'field',None))
            elif type2 == 'menu-value':
                node = var[3]
                texts = node.get_elements()
                if len(texts) != 1:
                    return 'Error reading value: 1 value needed; ' + unicode(len(texts)) + ' values found.' # admitir vectores / complexos ?
                text = texts[0]
                try:
                    floattext = float(text)
                except ValueError:
                    return "Error converting '" + text + "' to float"
                if Debug: print 'Variable ' + name + ': ' + unicode(floattext)
                varias.append((name,'value',floattext))
#            elif type2 == 'data': # caso non permitido
#                text = var[2]
#                try:
#                    floattext = float(text)
#                except ValueError:
#                    return "Error converting '" + text + "' to float" # admitir vectores / complexos ?
#                print 'Variable ' + name + ': ' + unicode(floattext)
#                varias.append((name,'value',floattext))
            else:
                return 'Error: variable mode not allowed: ' + unicode(type2)

        if self.varias != varias:
            self.revision_varias += 1
        self.varias = varias

        # checkar que todos os src teñan o mesmo numero de items.
        ret = self.check_valid(srcs,srcsnames,srcsfieldnames)
        if isinstance(ret, basestring):
            return ret
        return ret



    def check_valid(self, srcs, srcsnames, srcsfieldnames):
        the_size = None
        the_name = None
        for s,n,fieldname in zip(srcs, srcsnames, srcsfieldnames):
            out = s.GetOutput()

            if self.data.get('fielddomain') == 'cell':
                d = out.GetCellData()
            elif self.data.get('fielddomain') == 'point':
                d = out.GetPointData()
            else:
                return 'Only cell or point data allowed'

            array = d.GetArray(fieldname)
            #array = d.GetAbstractArray(name)
    
            if array is None:
                return 'Field name \'' + fieldname + '\' not found in variable ' + n
    
            size = array.GetNumberOfTuples()
            comp = array.GetNumberOfComponents()

            if Debug: print 'Variable ' + n + ': size ' + unicode(size) + ' comp ' + unicode(comp)

            if the_size is None:
                the_size = size
                the_name = n
            else:
                if the_size != size:
                    return 'Variables ' + the_name + ' and ' + n + ': field sizes do not match: ' + unicode(the_size) + ' and ' + unicode(size)

        return True



    def get_object(self, name, sources, arrays, formula, variables):
        if len(sources) < 1:
            return 'No cells'
        if len(arrays) < 1:
            return 'No fields'
        # colle o primeiro por coller un
        ugrid = sourceVTK2.get_clon(sources[0].GetOutput())
        tsize = arrays[0].GetNumberOfTuples()
        a = sourceVTK2.get_double_array()
        acsize = 1

        vnames = []
        for v in variables:
            vnames.append(v[0])

        lam = psps.create_lambda(formula, vnames)

        if isinstance(lam, basestring):
            return "Exception creating formula: " + lam

        i = 0
        arguments = []
        pos = []
        for v in variables:
            if v[1] == 'value': # valor
                arguments.append(v[2])
            elif v[1] == 'tuple': # tupla
                arguments.append(v[2])
            else: # campo
                pos.append((len(arguments), arrays[len(pos)].GetNumberOfComponents()))
                arguments.append(0.0)

        while i < tsize:

            for p in pos:
                r = []
                for t in xrange(p[1]):
                    r.append(arrays[p[0]].GetValue(i*p[1]+t)) # obten escalar/vector de entrada
                if p[1] == 1:
                    arguments[p[0]] = r[0] # escalar
                else:
                    arguments[p[0]] = tuple(r) # vector

            res = psps.exec_lambda(lam, arguments)
            if isinstance(res, basestring):
                return "Exception evaluating formula: " + res

            if isinstance(res, tuple) or isinstance(res, list):
                cursize = len(res)
            else:
                cursize = 1

            if i == 0:
                acsize = cursize
                a.SetNumberOfComponents(acsize)
                a.SetNumberOfTuples(tsize)
            else:
                if cursize != acsize:
                    return 'Mixed tuple len: ' + unicode(acsize) + ' and ' + unicode(cursize)

            if isinstance(res, tuple) or isinstance(res, list):
                for j in xrange(acsize):
                    a.SetValue(i*acsize + j, res[j]) # escribe vector de saida
            else:
                a.SetValue(i*acsize, res) # escribe escalar de saida                

            i = i + 1

        a.SetName(name)
        if tsize == 0:
            a.SetNumberOfComponents(0)
            a.SetNumberOfTuples(0)

        if self.data.get('fielddomain') == 'cell':
            data = ugrid.GetCellData()
        else:
            data = ugrid.GetPointData()
        data.AddArray(a) # replaces if exists
        # setscalars setvectors

        return ugrid



    def get_sources_arrays(self):
        sources = []
        arrays = []
        for var, data, tracker in zip(self.variables, self.data['formula_data'], self.trackers):
            name = var[0]
            if var[4] == 'menu-field':
                # non válido para os pvd
                src = tracker.get_src_group(1) # ou tracker.get_src_group_f(1, self.fielddata, mnames) "ou sin f"
                if isinstance(src, basestring):
                    return src

                sources.append(src)

                out = src.GetOutput()

                if self.data.get('fielddomain') == 'cell':
                    d = out.GetCellData()
                elif self.data.get('fielddomain') == 'point':
                    d = out.GetPointData()
                else:
                    return 'Only cell or point data allowed'

                fieldname = data.get('fieldname')

                array = d.GetArray(fieldname)
                #array = d.GetAbstractArray(fieldname)
        
                if array is None:
                    return 'Field name \'' + fieldname + '\' not found in variable ' + name

                arrays.append(array)

        return (sources, arrays)



    # private
    def compare_sources(self, srcs1, srcs2):
        if len(srcs1) != len(srcs2):
            return False
        for i in range(len(srcs1)):
            if srcs1[i] is not srcs2[i]:
                return False
        return True



    def get_src(self, labels=None):
        ret = self.combinate()
        if isinstance(ret, basestring):
            return ret

        varias_eq = self.revision_varias_src == self.revision_varias
        self.revision_varias_src = self.revision_varias

        temp = self.get_sources_arrays()
        if isinstance(temp, basestring):
            return temp
        res = self.compare_sources(self.sources, temp[0])

        recalc = False
        if not varias_eq:
            recalc = True
        if not res:
            recalc = True
        if self.src is None:
            recalc = True

        if recalc:
            self.sources = temp[0]

            res = self.get_object(self.data.get('fieldname'), temp[0], temp[1], self.text, self.varias)
            if isinstance(res, basestring):
                return res

            # wrap object into container
            self.src = sourceVTK2.get_wrap(res)
            self.src.Update()
            self.center = None

            self.revision_src += 1

        if labels is not None:
            if self.center is None:
                self.center = self.src.GetOutput().GetCenter()
            labels.append([self.center, self.get_name()])

        return self.src



    # Null / False / True
    def is_changed(self, write=True):
        for t in self.trackers:
            if t is not None:
                res = t.is_changed(write)
                if res is None:
                    return None
                if res is True:
                    return True

        if self.revision_varias_src != self.revision_varias: # esta vez segun src, outras segun tracker... inseguro
            return True

        return False



####
####
####



# clase auxiliar
class TrackerTime(Tracker):
    """Tracker for a concrete time of TrackerFormula2"""


    def __init__(self, fm, tf, index):
        Tracker.__init__(self, fm)
        self.type = 'formula-time'
        self.needs_vtkfiles = False
        self.vtkfile = '(formula-time)'
        self.set_name('formula-time')
        self.tf = tf
        self.index = index
        gofi = self.tf.get_original_files_index(index)
        if isinstance(gofi, list):
            for filename in gofi:
                self.filetracks.append(FileTrack2.FileTrack2(filename))



#    def get_original_files(self):
#        return [unicode(self.index)]



    def get_times(self):
        return self.tf.get_times()



# cache src aqui? creo que non: teria que pedilo igual pa ver se cambiou
    def get_src(self, labels=None):
        return self.tf.get_src_time(labels, self.index)



####
####
####



class TrackerFormula2(Tracker):
    """Tracker for formulas. Second version"""



    # provisional. non updata / facer que update, e logo cambiar por update?
    def fill(self):
        return True



    def __init__(self, fm, node, text, variables, data):
        Tracker.__init__(self, fm)
        self.type = 'formula'
        self.needs_vtkfiles = False
        self.vtkfile = '(formula)'
        self.vardata = []
        self.trackers = {}

        self.node = node
        self.text = text
        self.variables = variables
        self.data = data
        self.times = []
        self.index_calculated = None # None:none -1:general 0...N-1:i

        self.set_name('formula')

        fn = data.get('filenames')
        if fn is not None:
            for f in fn:
                self.filetracks.append(FileTrack2.FileTrack2(f))



    # Null / False / True
    def is_changed(self, write=True):
        vardatanew = self.parse_variables_0()
        if len(vardatanew) != len(self.vardata):
            return True

        ret = self.parse_variables_trackers(vardatanew)
        if ret is not True:
            self.cbc(ret+'\n')
            return None

        ret = self.parse_variables_values(vardatanew)
        if ret is not True:
            self.cbc(ret+'\n')
            return None

        for i in xrange(len(vardatanew)):
            t = vardatanew[i].get('tracker')
            r = self.vardata[i].get('revision')
            va = vardatanew[i].get('value')
            vb = self.vardata[i].get('value')
            if t is not None:
                if r != t.get_revision():
                    return True
                res = t.is_changed(write)
                if res is None:
                    return None
                if res is True:
                    return True
            if va != vb:
                return True
        return False



    def recalculate(self):

        ret = self.check_variables_varnames()
        if ret is not True:
            self.cbc(ret+'\n')
            return False

        ret = self.check_variables_types()
        if ret is not True:
            self.cbc(ret+'\n')
            return False

        temp = self.parse_variables_0()

        ret = self.parse_variables_names(temp)
        if ret is not True:
            self.cbc(ret+'\n')
            return False

        ret = self.parse_variables_trackers(temp)
        if ret is not True:
            self.cbc(ret)
            return False

        # opcional? -values

        self.has_series_ = self.parse_variables_series(temp)

        ret = self.check_vardata_series(temp)
        if isinstance(ret, basestring):
            self.cbc(ret+'\n')
            return False
        if isinstance(ret, list):
            self.times = ret
        else:
            self.times = []

        ret = self.parse_variables_values(temp)
        if ret is not True:
            self.cbc(ret+'\n')
            return False

#        ret = self.parse_variables_srcs(temp, -1)
#        if ret is not True:
#            self.cbc(ret+'\n')
#            return False

#        ret = self.parse_variables_srcs_arrays(temp)
#        if ret is not True:
#            self.cbc(ret+'\n')
#            return False

#        ret = self.check_vardata_srcs_arrays(temp)
#        if ret is not True:
#            self.cbc(ret+'\n')
#            return False

        self.index_calculated = None
        self.vardata = temp
        self.trackers.clear()
        return True



    # que non se dessincronice coas variables calculadas. 'text' e 'variables' non deberan cambiar
    def set_data(self, text, variables, data):
        self.text = text
        self.variables = variables
        self.data = data



    def get_times(self):
        return self.times



    # before update does not give value ?
    # so para pvd
    def get_tracker(self, index):
        if len(self.times) <= 0:
            return ".pvd file with 0 entries"
        if not (index >= 0 and index < len(self.times)):
            return ".pvd: index out of range"

        tracker = self.trackers.get(index)
        if tracker is not None:
            return tracker

        # crear novo tracker intermedio, con index, e referencia a este
        tracker = TrackerTime(self.fm, self, index)

        if tracker is None:
            return 'Unable to get formula-time tracker object'

        self.trackers[index] = tracker

        return tracker



    def check_variables_varnames(self):
        varnames = set()
        for var in self.variables:
            name = var[0]
            if name in varnames:
                return "Error: repeated variable name: " + name
            varnames.add(name)
        return True



    def check_variables_types(self):
        for i in xrange(len(self.variables)):
            var = self.variables[i]
            if var[4] != 'menu-value' and var[4] != 'menu-field':
                return 'Error: variable mode not allowed: ' + unicode(var[4])
        return True



    def check_vardata_srcs_arrays(self, vardata):
        the_size = None
        the_name = None
        for i in xrange(len(vardata)):

#            s = vardata[i].get('src')
            n = vardata[i].get('name')
            array = vardata[i].get('srcarray')
            fieldname = vardata[i].get('srcfieldname')

#            if s is None:
#                continue
            if array is None:
                continue

            size = array.GetNumberOfTuples()
            comp = array.GetNumberOfComponents()

            if Debug: print 'Variable ' + n + ': size ' + unicode(size) + ' comp ' + unicode(comp)

            if the_size is None:
                the_size = size
                the_name = n
            else:
                if the_size != size:
                    return 'Variables ' + the_name + ' and ' + n + ': field sizes do not match: ' + unicode(the_size) + ' and ' + unicode(size)

        return True



# None:non hai pvds []:hai pvd con 0 tempos [...]:hai pvd con tempos
    def check_vardata_series(self, vardata):
        times = None
        for i in xrange(len(vardata)):
            t = vardata[i].get('tracker')
            if t is not None:
################################################################# t.update() ? unha vez non funcionou sen update
                ret = t.update()
                if ret is None:
                    return 'Error updating formula-time sub object'
                if t.has_series():
                    times_new = t.get_times()
                    if times is not None:
                        if len(times) != len(times_new):
                            return 'Error: mixed PVDs with different number of steps'
                        for a, b in zip(times, times_new):
                            if a.get('time') != b.get('time'):
                                return 'Error: mixed PVDs with different time steps'
                    else:
                        times = times_new
        return times



    def parse_variables_0(self):
        # non funciona porque é o mesmo obxecto: return [{}] * len(self.variables)
        tmp = []
        for a in xrange(len(self.variables)):
            tmp.append({})
        return tmp



    def parse_variables_names(self, vardata):
        for i in xrange(len(self.variables)):
            name = self.variables[i][0]
            vardata[i]['name'] = name
        return True



    def parse_variables_trackers(self, vardata):
        for i in xrange(len(self.variables)):
            var = self.variables[i]
            data = self.data['formula_data'][i]
            if var[4] == 'menu-field':
                tracker = var[3].get_tracker5(self.fm, data)
                if isinstance(tracker, basestring):
                    return 'Error filling formula:' + tracker
################################################################# t.update() ?
#                ret = tracker.update()
#                if ret is None:
#                    return 'Error updating formula-time sub object (b)'
#                print 'present tracker', tracker
                vardata[i]['tracker'] = tracker
                vardata[i]['revision'] = -1
            else:
                vardata[i]['tracker'] = None
                vardata[i]['revision'] = -1
#            print 'pre', i, 'tracker', vardata[i]['tracker'] ##########
#        print vardata
        return True



    def parse_variables_series(self, vardata):
        result = False
        for i in xrange(len(vardata)):
            t = vardata[i].get('tracker')
            if t is not None:
                if t.has_series():
                    result = True
        return result



    def parse_variables_values(self, vardata):
        for i in xrange(len(self.variables)):
            var = self.variables[i]
            name = var[0]
            data = self.data['formula_data'][i]
            if var[4] == 'menu-value':
                node = var[3]
                texts = node.get_elements()
                if len(texts) != 1:
                    # admitir vectores / complexos ? / tuplas
                    return 'Error reading value: 1 value needed; ' + unicode(len(texts)) + ' values found.'
                text = texts[0]
                try:
                    numtext = float(text)
                except ValueError:
		    vals = []									#añadido
		    if self.parse_complex(text,'(',')',vals) == -1:				#añadido
			return "Error converting '" + text + "' to a numeric type"		#añadido
		    numtext = vals[0]								#añadido
                if Debug: print 'Variable ' + name + ': ' + unicode(numtext)			#añadido
                vardata[i]['value'] = numtext
            else:
                vardata[i]['value'] = None
        return True


    def parse_complex(self, string,startchar,endchar,lista):
	"""
	Parse a list of complex and check the syntax. Recursive function.

	string: type String.
	startchar: type Character.
	endchar: type Character.
	list: type List.
	"""

	start = string.find(startchar)
	end = string.find(endchar)

	if start<end and start != -1 and end != -1:
	    complexstr = string[start:end+1]
	    try:
		if not len(map(float, complexstr[1:-1].replace(',', ' ').split())) == 2:
		    return -1
		complexparts = map(float, complexstr[1:-1].replace(',', ' ').split())
		lista.append(complex(complexparts[0], complexparts[1]))
		return self.parse_complex(string[end+1:],startchar,endchar,lista)
	    except:
		return -1
	    return 1
	elif (start == -1 and end != -1) or (start != -1 and end == -1):
	    return -1
	else:
	    return 0

    # depende de tracker. modificar index_calculated en cada chamada
    def parse_variables_srcs(self, vardata, index):
        for i in xrange(len(vardata)):
            tracker = vardata[i].get('tracker')
	    data = self.data['formula_data'][i]
	    if tracker is not None and tracker.is_nodepvd:					#añadido
		labels = []									#añadido
		fielddata = {}									#añadido
		fielddata['name'] = data.get('fieldname')					#añadido
		fielddata['domain'] = data.get('fielddomain')					#añadido
		src = tracker.get_src_group_f( 1, fielddata, labels,index)			#añadido
                vardata[i]['src'] = src
                vardata[i]['srcfieldname'] = data.get('fieldname')
	    else:
		if index >= 0 and tracker is not None and tracker.has_series(): # reempraza por tempo 'index'
		    tracker = tracker.get_tracker(index)
                    if not isinstance(tracker, Tracker):
			return unicode(tracker)
		if isinstance(tracker, Tracker):# or tracker is None:
		    # non válido para os pvd (local local?)
		    src = tracker.get_src_group(1) # ou tracker.get_src_group_f(1, self.fielddata, mnames) "ou sin f"
                    if isinstance(src, basestring):
			return "Error getting source object: " + src
                    vardata[i]['src'] = src
                    vardata[i]['srcfieldname'] = data.get('fieldname')
		else:   
                    vardata[i]['src'] = None
                    vardata[i]['srcfieldname'] = None

        return True

# actualizar revision nalgún lado


    def parse_variables_srcs_arrays(self, vardata):
        for i in xrange(len(vardata)):
#            tracker = vardata[i].get('tracker')
            var = self.variables[i]
            data = self.data['formula_data'][i]
            name = var[0]
            src = vardata[i].get('src')
            if src is not None:
                # non válido para os pvd
                out = src.GetOutput()

                if self.data.get('fielddomain') == 'cell':
                    d = out.GetCellData()
                elif self.data.get('fielddomain') == 'point':
                    d = out.GetPointData()
                else:
                    return 'Only cell or point data allowed'

                fieldname = data.get('fieldname')

                array = d.GetArray(fieldname)
                #array = d.GetAbstractArray(fieldname)

                if array is None:
                    return 'Field name \'' + fieldname + '\' not found in variable ' + name

                vardata[i]['srcarray'] = array
            else:
                vardata[i]['srcarray'] = None
        return True



    # private
# quizais non sirva
#    def compare_sources(self, vardata1, vardata2):
#        if len(vardata1) != len(vardata2):
#            return False
#        for i in range(len(vardata1)):
#            if vardata1[i].get('src') is not vardata2[i].get('src'):
#                return False
#        return True



# completar
    def get_object(self, name, formula, variables):
        sources = []
        arrays = []
        for a in variables:
            if a.get('src') is not None and a.get('srcarray') is not None:
                sources.append(a.get('src'))
                arrays.append(a.get('srcarray'))
        if len(sources) < 1:
            return 'No cells'
        if len(arrays) < 1:
            return 'No fields'
        # colle o primeiro por coller un
        ugrid = sourceVTK2.get_clon(sources[0].GetOutput())
        tsize = arrays[0].GetNumberOfTuples()
        a = sourceVTK2.get_double_array()
        acsize = 1

        vnames = []
        for v in variables:
            vnames.append(v.get('name'))

        lam = psps.create_lambda(formula, vnames)

        if isinstance(lam, basestring):
            return "Exception creating formula: " + lam

        i = 0
        arguments = []
        pos = []
        for v in variables:
            if v.get('value') is not None: # valor
                arguments.append(v.get('value'))
            elif v.get('tuple') is not None: # tupla
                arguments.append(v.get('tuple')) # non usado
            else: # campo
 # TODO sincronizar. arrays distintos !!! creo que DONE (nada)
 # sincronizar. arrays distintos !!!
                pos.append((len(arguments), arrays[len(pos)].GetNumberOfComponents()))
                arguments.append(0.0)

        while i < tsize:

            for p in pos:
                r = []
                for t in xrange(p[1]):
                    r.append(arrays[p[0]].GetValue(i*p[1]+t)) # obten escalar/vector de entrada
                if p[1] == 1:
                    arguments[p[0]] = r[0] # escalar
                else:
                    arguments[p[0]] = tuple(r) # vector

            res = psps.exec_lambda(lam, arguments)
            if isinstance(res, basestring):
                return "Exception evaluating formula: " + res

            if isinstance(res, tuple) or isinstance(res, list):
                cursize = len(res)
            else:
                cursize = 1

            if i == 0:
                acsize = cursize
                a.SetNumberOfComponents(acsize)
                a.SetNumberOfTuples(tsize)
            else:
                if cursize != acsize:
                    return 'Mixed tuple len: ' + unicode(acsize) + ' and ' + unicode(cursize)

            if isinstance(res, tuple) or isinstance(res, list):
                for j in xrange(acsize):
                    a.SetValue(i*acsize + j, res[j]) # escribe vector de saida
            else:
                a.SetValue(i*acsize, res) # escribe escalar de saida                

            i = i + 1

        a.SetName(name)
        if tsize == 0:
            a.SetNumberOfComponents(0)
            a.SetNumberOfTuples(0)

        if self.data.get('fielddomain') == 'cell':
            data = ugrid.GetCellData()
        else:
            data = ugrid.GetPointData()
        data.AddArray(a) # replaces if exists
        # setscalars setvectors

        return ugrid



    def get_src(self, labels=None):

        return self.get_src_time(labels)



    def get_src_time(self, labels=None, index=-1):
        recalc = False

        res = self.update()

        if res is None: #fail
            return 'Error updating source file data, TrackerFormula2'
        elif res is True: #changed
            recalc = recalc or True
        elif res is False: #unchanged
            recalc = recalc or False

        if index != self.index_calculated:
            recalc = recalc or True

        # TODO: mais checks para comprobar cambios ?

        if recalc:
            self.index_calculated = None

            # (ou non modificar vardata directamente, crear unha copia)
            ret = self.parse_variables_srcs(self.vardata, index)
            if ret is not True:
                return ret
#                self.cbc(ret+'\n')
#                return False

            ret = self.parse_variables_srcs_arrays(self.vardata)
            if ret is not True:
                return ret
#                self.cbc(ret+'\n')
#                return False

            ret = self.check_vardata_srcs_arrays(self.vardata)
            if ret is not True:
                return ret
#                self.cbc(ret+'\n')
#                return False

            self.index_calculated = index

            res = self.get_object(self.data.get('fieldname'), self.text, self.vardata)
            if isinstance(res, basestring):
                return res

            # wrap object into container
            self.src = sourceVTK2.get_wrap(res)
            self.src.Update()
            self.center = None

            self.revision_src += 1

        if labels is not None:
            if self.center is None:
                self.center = self.src.GetOutput().GetCenter()
            labels.append([self.center, self.get_name()])

        return self.src



    def get_original_files_index(self, index):
        files = []
        if index >= 0:
            for i in xrange(len(self.vardata)):
                tracker = self.vardata[i].get('tracker')
                if tracker is not None and tracker.has_series():
                    tracker2 = tracker.get_tracker(index) # non propagar erro ?
                    if tracker2 is not None and isinstance(tracker2, Tracker):
                        files.extend(tracker2.get_original_files())
        return files


