#!/usr/bin/env python
# -*- coding: utf-8 -*-



import vtk



class TimeManager2():
    """clase que gestiona los ficheros de una serie temporal especificada en un .pvd"""
    
    def __init__(self):
        self.tracker = None
        self.revision = -1
        self.trackerA = None
        self.tracker1 = None
        self.tracker2 = None
        self.indexA = None
        self.index1 = None
        self.index2 = None
        self.mode = None # 1: direct 2: interpolate
        self.range = [0.0, 0.0]
        self.times = []
        self.time = None
        self.src = None
        self.src1 = None
        self.src2 = None
        self.mesh_names = []

        self.changes = {}
        # new==True : new self.src object
        # change==True : self.src object with data changed

        self.attr_fn = None
        self.attr_sv = None
        self.attr_pc = None
        self.assigner = None

        self.interpolation = True



    def set_interpolation(self, value):
        self.interpolation = value



    def get_time(self):
        return self.time



    def get_range(self):
        return self.range



    # workaround because: vtkInterpolateDataSetAttributes only interpolates active attributes
    # none for deactivate
    # field name, sv: scalar_0 vector_1, pc: point_0 cell_1
    def set_attributes(self, fn, sv, pc):
        self.attr_fn = fn
        self.attr_sv = sv
        self.attr_pc = pc

        # para obter rangos
        if self.attr_fn is not None and self.attr_sv is not None and self.attr_pc is not None:
            self.assigner = vtk.vtkAssignAttribute()
            self.assigner.Assign(self.attr_fn,self.attr_sv,self.attr_pc)
        else:
            self.assigner = None



    def set_tracker(self, tracker):

        if self.tracker is not tracker:
        
            self.tracker = tracker
            self.revision = -1
            
        if self.tracker.get_revision() != self.revision:
        
            self.times = self.tracker.get_times()

            if len(self.times)>0:
                self.range[0] = self.times[0].get('time')
                self.range[1] = self.times[-1].get('time')
            else:
                self.range[0] = self.range[1] = 0.0

            res = None
               
            if self.mode == 1:
                i = self.indexA
                self.indexA = None
                res = self.recalculate(i)
            elif self.mode == 2:
                self.index1 = None
                self.index2 = None
                res = self.recalculateTime(self.time)
                
            if isinstance(res, basestring):
                return res
            
            self.revision = self.tracker.get_revision()

        return True



    def get_times(self):
        return self.times



    def action_next(self):
        if self.mode == 1:
            return self.recalculate(self.indexA + 1)
        elif self.mode == 2:
            return self.recalculate(self.index2)
        else:
            return True



    def action_previous(self):
        if self.mode == 1:
            return self.recalculate(self.indexA - 1)
        elif self.mode == 2:
            return self.recalculate(self.index1)
        else:
            return True



    def action_first(self):
        return self.recalculate(0)



    def action_last(self):
        return self.recalculate(-2)



    def action_goto_index(self, index):
        return self.recalculate(index)



    def action_goto_time(self, time):
        return self.recalculateTime(time)



    def get_status(self):
        """ return whether position can be modified in each sense """
        if self.mode == 1:
            return {'previous':self.indexA != 0, 'next': self.indexA != (len(self.times) - 1)}
        elif self.mode == 2:
            return {'previous':True,'next':True}
        else:
            return {'previous':False,'next':False}



    def get_filenames(self):
        if self.mode is None:
            return None
        result = self.tracker.get_original_files()

        if self.mode == 1:
            if self.tracker.is_nodepvd:
                for tr in self.trackerA:
                    result.extend(tr.get_original_files())
            else:
                result.extend(self.trackerA.get_original_files())
        if self.mode == 2:
            result.extend(self.tracker1.get_original_files())
            result.extend(self.tracker2.get_original_files())

        return result



    def get_src(self, mnames=None):
        if mnames is not None:
            mnames.extend(self.mesh_names)
        return self.src



    def recalculate(self, index):
        if self.tracker is None:
            return 'TimeManager: object not initialized'

        # -2 => last
        
        # reread times. not by the moment
    
        if len(self.times) <= 0:
            return 'TimeManager: Error: .pvd file with 0 entries'

        if index == -2:
            index = len(self.times) - 1
        if index >= len(self.times):
            index = len(self.times) - 1
        if index < 0:
            index = 0

        # no necesario mode==1 porque si mode==2 tendria indexA a None
        if self.mode == 1 and index == self.indexA:
            return True

        mnames = []

        tracker = self.tracker.get_tracker(index)
        if isinstance(tracker, basestring):
            return tracker
        else:
            if self.tracker.is_nodepvd:
                src = []
                for tr in tracker:
                    src.append(tr.get_src(mnames))
            else:
                src = tracker.get_src(mnames)
            if isinstance(src, basestring):
                return src
                    

        # tambien posible reutilizar ficheros de mode == 2

        self.src = src
        self.mesh_names = mnames
        self.trackerA = tracker
        self.mode = 1
        self.time = self.times[index].get('time')
        self.indexA = index
        self.index1 = None
        self.index2 = None
        self.changes['new'] = True
        self.changes['changed'] = True

        return True



    def recalculateTime(self, time):
        
        if len(self.times) <= 0:
            return 'TimeManager: Error: .pvd file with 0 entries'
            
        if len(self.times) == 1:
            pi = pf = 0
        else:
            # posicion mayor tal que time >= t
            pi = 0
            while pi < len(self.times) and time >= self.times[pi].get('time'):
                pi += 1
            if pi > 0:
                pi -= 1

            # posicion menor tal que time <= t
            pf = 0
            while pf < len(self.times) and time > self.times[pf].get('time'):
                pf += 1
            if pf >= len(self.times):
                pf -= 1

        print 'pi, pf', pi, pf

        if pi == pf:
            return self.recalculate(pi)

        # para que non interpole tempo/frecuencia
        if self.interpolation is not True:
            return self.recalculate(pi) # redondea cara á esquerda

        ti = self.times[pi].get('time')
        tf = self.times[pf].get('time')

        print 'ti, tf', ti, tf
        
        if ti == tf:
            return self.recalculate(pi)

        # [0,1]
        factor = (time - ti)/(tf - ti)
        
        print 'factor', factor
        
        # tambien posible reutilizar ficheros de mode == 1

        mnames = []

        # si ha cambiado el primer fichero ...
        if not (self.mode == 2 and self.index1 == pi):
            print '#1 si ha cambiado el primer fichero ..'
            tracker = self.tracker.get_tracker(pi)
            if isinstance(tracker, basestring):
                return tracker
            else:
                src = tracker.get_src(mnames)
                if isinstance(src, basestring):
                    return src
            self.tracker1 = tracker
            self.src1 = src

        # si ha cambiado el segundo fichero ...
        if not (self.mode == 2 and self.index2 == pf):
            print '#2 si ha cambiado el segundo fichero ...'
            tracker = self.tracker.get_tracker(pf)
            if isinstance(tracker, basestring):
                return tracker
            else:
                src = tracker.get_src(mnames)
                if isinstance(src, basestring):
                    return src
            self.tracker2 = tracker
            self.src2 = src

        # si ha cambiado algun fichero
        if not (self.mode == 2 and self.index1 == pi and self.index2 == pf):
            print '#3 si ha cambiado algun fichero'

            self.src = vtk.vtkInterpolateDataSetAttributes()
            
            #self.src.AddInput(self.src1.GetOutput())
            #self.src.AddInput(self.src2.GetOutput())

            #workaround: porque solo interpola atributos activos
            if self.attr_fn is not None and self.attr_sv is not None and self.attr_pc is not None:
                a1 = vtk.vtkAssignAttribute()
                a2 = vtk.vtkAssignAttribute()
                a1.Assign(self.attr_fn,self.attr_sv,self.attr_pc)
                a2.Assign(self.attr_fn,self.attr_sv,self.attr_pc)
                a1.SetInputConnection(self.src1.GetOutputPort())
                a2.SetInputConnection(self.src2.GetOutputPort())
                self.src.AddInputConnection(a1.GetOutputPort())
                self.src.AddInputConnection(a2.GetOutputPort())
            else:
                self.src.AddInputConnection(self.src1.GetOutputPort())
                self.src.AddInputConnection(self.src2.GetOutputPort())
            
            self.changes['new'] = True
            self.changes['changed'] = True

        # si aprendo como reutilizar self.src, [SetInput], no construye un self.src nuevo siempre

        self.src.SetT(factor)
        self.src.Update()

        self.mesh_names = mnames
        self.mode = 2
        self.time = time
        self.indexA = None
        self.index1 = pi
        self.index2 = pf
        self.changes['changed'] = True

        return True





    def changes_clear(self):
        self.changes = {}


    # "new" + "changed"
    # or
    # "changed"
    # or
    # empty
    def changes_get(self):
        return self.changes

    #Returns a list with the field range
    def get_source_range(self,src):
        r = None
        if self.attr_pc == 0:
            if self.attr_sv == 0 and src.GetOutput().GetPointData().GetScalars(self.attr_fn) is not None:
                r = src.GetOutput().GetPointData().GetScalars(self.attr_fn).GetRange(-1)
            elif self.attr_sv == 1 and src.GetOutput().GetPointData().GetVectors(self.attr_fn) is not None:
                r = src.GetOutput().GetPointData().GetVectors(self.attr_fn).GetRange(-1)
        elif self.attr_pc == 1:
            if self.attr_sv == 0 and src.GetOutput().GetCellData().GetScalars(self.attr_fn) is not None:
                r = src.GetOutput().GetCellData().GetScalars(self.attr_fn).GetRange(-1)
            elif self.attr_sv == 1 and src.GetOutput().GetCellData().GetVectors(self.attr_fn) is not None:
                r = src.GetOutput().GetCellData().GetVectors(self.attr_fn).GetRange(-1)
        if r is None:
            return r
            r = src.GetOutput().GetScalarRange()

        return list(r)


    def get_file_range(self, index):
        tracker = self.tracker.get_tracker(index)
        if isinstance(tracker, basestring):
            return tracker
        else:
            if self.tracker.is_nodepvd:
                src = []
                for tr in tracker:
                    src.append(tr.get_src())

            else:
                src = tracker.get_src()
                if isinstance(src, basestring):
                    return src

        if self.assigner is not None:
            if self.tracker.is_nodepvd:
                import sourceVTK2
                r = None
                self.assigner = sourceVTK2.get_append(src)
                self.assigner.Update()
                for s in src:
                    aux = self.get_source_range(s)
                    if aux is not None:
                        if r is None:
                            r = aux
                        else:
                            if aux[0] < r[0]:
                                r[0]  = aux[0]
                            if aux[-1] > r[-1]:
                                r[-1]  = aux[-1]
            else:
                self.assigner.SetInputConnection(src.GetOutputPort())
                self.assigner.Update()
                r = self.get_source_range(src)
        else:
            r = self.get_source_range(src)
        
        print 'i', index, 't', self.times[index].get('time'), 'r', r
        
        return r



    def get_value_range(self, timerange, callback):
        """ Return the range of values reached in the given time range.
            self.times must be ordered.
        """
        # requires ordered sequence in self.times

        # esto sólo, provoca que falle a interacción
        #def callback(args1, args2):
        #    if cb is not None:
        #        cb(args1, args2)

        limits = None

        IniA = None # antes de Inicio
        IniB = None # despois de Inicio
        FinA = None # antes de Fin
        FinB = None # despois de Fin
        facIniA = None # factor para IniA respecto de IniB
        facFinB = None # factor para FinB respecto de FinA
        
        for i in range(len(self.times)):
            t = self.times[i].get('time')
            if t is not None:
                if t <= timerange[0]:
                    IniA = i
                if t <= timerange[1]:
                    FinA = i
                if t >= timerange[0] and IniB is None:
                    IniB = i
                if t >= timerange[1] and FinB is None:
                    FinB = i

        if not self.interpolation: # para intervalos de frecuencia, ... que non se interpolan (interpolation="false")
            IniA = IniB
            FinB = FinA

        if IniA is not None and IniB is not None and IniA != IniB:
            tA = self.times[IniA].get('time')
            tB = self.times[IniB].get('time')
            t = timerange[0]
            if tB != tA:
                facIniA = (tB - t) / (tB - tA)

        if FinA is not None and FinB is not None and FinA != FinB:
            tA = self.times[FinA].get('time')
            tB = self.times[FinB].get('time')
            t = timerange[1]
            if tB != tA:
                facFinB = (t - tA) / (tB - tA)

        calls = 0
        if facIniA is not None:
            calls += 2
        if IniB is not None and FinA is not None and FinA >= IniB:
            calls += FinA - IniB + 1
        if facFinB is not None:
            calls += 2

        done = 0

        res = callback(done, calls)
        if res is False:
            return False

        print 'novo', IniA, IniB, FinA, FinB, 'fac:', facIniA, facFinB, 'calls', calls

        if facIniA is not None:
            IniAr = self.get_file_range(IniA)
            if isinstance(IniAr, basestring):
                return IniAr
            done += 1
            res = callback(done, calls)
            if res is False:
                return False
            IniBr = self.get_file_range(IniB)
            if isinstance(IniBr, basestring):
                return IniBr
            done += 1
            res = callback(done, calls)
            if res is False:
                return False

            limits = TimeManager2.expand_range(limits, \
                TimeManager2.interpolate_range(IniAr, IniBr, facIniA))

        if IniB is not None and FinA is not None:
            for i in range(IniB, FinA + 1): # alcanza os dous extremos
                temp = self.get_file_range(i)
                if isinstance(temp, basestring):
                    return temp
                done += 1
                res = callback(done, calls)
                if res is False:
                    return False
                limits = TimeManager2.expand_range(limits, temp)
        
        if facFinB is not None and not (IniA == FinA and IniB == FinB):
            FinAr = self.get_file_range(FinA)
            if isinstance(FinAr, basestring):
                return FinAr
            done += 1
            res = callback(done, calls)
            if res is False:
                return False
            FinBr = self.get_file_range(FinB)
            if isinstance(FinBr, basestring):
                return FinBr
            done += 1
            res = callback(done, calls)
            if res is False:
                return False

            limits = TimeManager2.expand_range(limits, \
                TimeManager2.interpolate_range(FinBr, FinAr, facFinB))
        
        if limits is None:
            return 'empty range'
        
        return limits



    @staticmethod
    def expand_range(current, next):
        if current is None:
            return list(next)
        current = list(current)
        if next[0] < current[0]:
            current[0] = next[0]
        if next[1] > current[1]:
            current[1] = next[1]
        return current



    @staticmethod
    def interpolate_range(first, second, factorFirst):
        return (first[0] * factorFirst + second[0] * (1.0 - factorFirst), \
            first[1] * factorFirst + second[1] * (1.0 - factorFirst))

