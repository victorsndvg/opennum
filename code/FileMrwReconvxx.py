#!/usr/bin/env python
# -*- coding: utf-8 -*-



import FileMrw
import FileMrwVTK
import FileMrwVTU



# vertex
LNV1 = 2
LNV2 = 3
LNV3 = 4
LNVs = {1:LNV1, 2:LNV2, 3:LNV3}

# edges
LNE2 = 3
LNE3 = 6

# faces
LNF3 = 4

# number of submesh cell vertex
SM1 = 1
SM2 = 2
SM3 = 3

Format1 = 'int'
Format2 = 'double'



class FileMrwReconvxx(FileMrw.FileMrw):



    def __init__(self, callback=None):
        FileMrw.FileMrw.__init__(self, callback)
        self.clear()



    def clear(self):
        self.submeshed = False

        self.firstline = 8
        
        self.nel = 0
        self.nnod = 0
        self.nver = 0

        self.dim = None
        self.lnn = 0
        self.lnv = 0
        self.lne = 0
        self.lnf = 0
        
        self.nsm = 0 # number of submesh items

        self.nn = []
        self.mm = []
        self.nrc = []
        self.nra = []
        self.nrv = []
        self.z = []
        self.nsd = []
        self.znew = []

        # transform z to znew with nn and mm
        self.transform = False # se transforma:
        self.mmnn = None # mm ou nn
        self.numvn = None # numero de nodos ou vertices
        self.lnvn = None # local num de nodos ou vertices
        self.zz = None # old or new z

        # cells
        self.sm = [] # submesh points array
        self.nrsm = [] # submesh reference numbers array
        self.smn = [] # submesh name array
        
        self.nrvtovtk = None #

        self.sets = {}
        self.sets['element_ref'] = set()
        self.sets['face_ref'] = set()
        self.sets['edge_ref'] = set()
        self.sets['vertex_ref'] = set()


        
    # dict of sets of integer
    def get_refs(self):
        return self.sets



    def get_dim(self):
        return self.dim



# modifies self even if read is unsuccessfull
    def read(self, filename, attribs):
        self.clear()
        FileMrw.FileMrw.read(self, filename, attribs)

        data = FileMrw.FileMrw.split(self.filename)

        if data[u'error'] is not None:
            return data[u'error']

        result = self.read2(data[u'data'])

        return result



    # inclúe \n para o log. os outros metodos non
    def read2(self, data):
        askdim = self.attribs.get('dim')

        count = len(data)

        if count < self.firstline:
            return u'too few data'

        t = FileMrw.FileMrw.read_ints(data, 0, 1)
        if t is False:
            return u'ValueError (nel)'
        self.nel = t[0]

        t = FileMrw.FileMrw.read_ints(data, 1, 1)
        if t is False:
            return u'ValueError (nnod)'
        self.nnod = t[0]

        t = FileMrw.FileMrw.read_ints(data, 2, 1)
        if t is False:
            return u'ValueError (nver)'
        self.nver = t[0]

        t = FileMrw.FileMrw.read_ints(data, 3, 1)
        if t is False:
            return u'ValueError (dim)'
        self.dim = t[0]

        t = FileMrw.FileMrw.read_ints(data, 4, 1)
        if t is False:
            return u'ValueError (lnn)'
        self.lnn = t[0]

        t = FileMrw.FileMrw.read_ints(data, 5, 1)
        if t is False:
            return u'ValueError (lnv)'
        self.lnv = t[0]

        t = FileMrw.FileMrw.read_ints(data, 6, 1)
        if t is False:
            return u'ValueError (lne)'
        self.lne = t[0]

        t = FileMrw.FileMrw.read_ints(data, 7, 1)
        if t is False:
            return u'ValueError (lnf)'
        self.lnf = t[0]

        self.cc( \
            u'nel ' + unicode(self.nel) + u' nnod ' + unicode(self.nnod) + u' nver ' + unicode(self.nver) + \
            u' dim ' + unicode(self.dim) + u' lnn ' + unicode(self.lnn) + u' lnv ' + unicode(self.lnv) + \
            u' lne ' + unicode(self.lne) + u' lnf ' + unicode(self.lnf) + \
            u'\n')

        if askdim is not None and self.dim != askdim:
            return u'Dimensions do not match: ' + unicode(self.dim) + '!=' + unicode(askdim)

        if not ( self.nel >= 0 and self.nnod >= 0 and self.nver >= 0 and \
            self.dim >= 0 and self.lnn >= 0 and self.lnv >= 0 and self.lne >= 0 and self.lnf >= 0 ) :
            return 'Negative cardinal'

        num_nn = self.lnn * self.nel
        num_mm = self.lnv * self.nel
        num_nrc = self.lnf * self.nel
        num_nra = self.lne * self.nel
        num_nrv = self.lnv * self.nel
        num_z = self.dim * self.nver
        num_nsd = self.nel

        nv = self.nnod == self.nver

        if self.nnod == self.nver: # and self.lnn == self.lnv:
            num_nn = 0
        if self.dim < 3:
            num_nrc = 0
        if self.dim < 2:
            num_nra = 0

        self.element_type = FileMrwReconvxx.check_type(nv, self.dim, self.lnn, self.lnv, self.lne, self.lnf)

        if self.element_type is None:
            return u'Element type not supported'

#        if self.lnv * self.nel != self.nver: # non é así: pode haber vertices usados por dous
#            return 'nel * lnv != nver'
#
#        if self.lnn * self.nel != self.nnod: # non é así: pode haber vertices usados por dous
#            return 'nel * lnn != nnod'

        print 'element_type:', self.element_type

        expected = self.firstline + num_nn + num_mm + num_nrc + num_nra + num_nrv + num_z + num_nsd
#        if count != expected:
#            return u'Incorrect number of words ( counted ' + unicode(count) + u' != expected ' + unicode(expected) + u' )'

        n = self.firstline

        self.cc('nn ' + unicode(num_nn) + ' ')
        q = FileMrw.FileMrw.read_ints_1(data, n, num_nn) # _1 => -1
        if q is False:
            return u'ValueError (nn)'
        self.nn = q
        n += num_nn

        self.cc('mm ' + unicode(num_mm) + ' ')
        q = FileMrw.FileMrw.read_ints_1(data, n, num_mm) # _1 => -1
        if q is False:
            return u'ValueError (mm)'
        self.mm = q
        n += num_mm

        self.cc('nrc ' + unicode(num_nrc) + ' ')
        q = FileMrw.FileMrw.read_ints(data, n, num_nrc)
        if q is False:
            return u'ValueError (nrc)'
        self.nrc = q
        n += num_nrc
                
        self.cc('nra ' + unicode(num_nra) + ' ')
        q = FileMrw.FileMrw.read_ints(data, n, num_nra)
        if q is False:
            return u'ValueError (nra)'
        self.nra = q
        n += num_nra

        self.cc('nrv ' + unicode(num_nrv) + ' ')
        q = FileMrw.FileMrw.read_ints(data, n, num_nrv)
        if q is False:
            return u'ValueError (nrv)'
        self.nrv = q
        n += num_nrv
                
        self.cc('z ' + unicode(num_z) + ' ')
        q = FileMrw.FileMrw.read_floats(data, n, num_z)
        if q is False:
            return u'ValueError (z)'
        self.z = q
        n += num_z

        self.cc('nsd ' + unicode(num_nsd) + ' ')
        q = FileMrw.FileMrw.read_ints(data, n, num_nsd)
        if q is False:
            return u'ValueError (nsd)'
        self.nsd = q
        n += num_nsd
                
#        if n != count:
#            return u'Incorrect number of read words ( read ' + unicode(n) + u' != counted ' + unicode(count) + u' )'


        self.cc('\n')

        
        if self.element_type.get('type') == 'p2':
            self.transform = True

        if self.transform:
            self.znew = FileMrwReconvxx.transform_p2_z(self.dim, self.nnod, self.z, self.mm, self.nn, self.lnv, self.lnn, \
                                                        self.element_type.get('extra'))
            if isinstance(self.znew, basestring):
                return self.znew

            self.mmnn = self.nn
            self.lnvn = self.lnn
            self.numvn = self.nnod
            self.zz = self.znew
        else:
            self.mmnn = self.mm
            self.lnvn = self.lnv
            self.numvn = self.nver
            self.zz = self.z



        # redundante: no constructor
        # incluyen 0 si hay
        self.sets['element_ref'] = set()
        self.sets['face_ref'] = set()
        self.sets['edge_ref'] = set()
        self.sets['vertex_ref'] = set()

        verbose = False

        #self.cc(u'set nsd ')
        self.sets['element_ref'] = set(self.nsd)
        if verbose:
            self.cc(u'set element_ref # ' + unicode(sorted(list(self.sets['element_ref']))) + '\n')
        else:
            self.cc(u'set element_ref # ' + unicode(len(self.sets['element_ref'])) + ' ')

        if self.dim >= 3:
            #self.cc(u'set nrc ')
            self.sets['face_ref'] = set(self.nrc)
            if verbose:
                self.cc(u'set face_ref # ' + unicode(sorted(list(self.sets['face_ref']))) + '\n')
            else:
                self.cc(u'set face_ref # ' + unicode(len(self.sets['face_ref'])) + ' ')

        if self.dim >= 2:
            #self.cc(u'set nra ')
            self.sets['edge_ref'] = set(self.nra)
            if verbose:
                self.cc(u'set edge_ref # ' + unicode(sorted(list(self.sets['edge_ref']))) + '\n')
            else:
                self.cc(u'set edge_ref # ' + unicode(len(self.sets['edge_ref'])) + ' ')

        if self.dim >= 1:
            #self.cc(u'set nrv ')
            self.sets['vertex_ref'] = set(self.nrv)
            if verbose:
                self.cc(u'set vertex_ref # ' + unicode(sorted(list(self.sets['vertex_ref']))) + '\n')
            else:
                self.cc(u'set vertex_ref # ' + unicode(len(self.sets['vertex_ref'])) + ' ')

        self.cc(u'-end read-\n')

        return True

    def binary_search(self,seq,search):    
        #Devolve center se atopamos o punto, senon -(center+1) sendo (center+1) a posicion correspondente
        right = len(seq)
        left = 0
        previous_center = -1
        if ((len(seq) == 0) or (search < seq[0])):
            return -1
        while True:
            center = (left + right) / 2
            candidate = seq[center]
            if search == candidate:
                return center
            if center == previous_center:
                return -(center+2) #- 2 - center
            elif search < candidate:
                right = center
            else:
                left = center
            previous_center = center
    
    def search_arround(self,seqPointMin,seqPoint1,seqPoint2,position,min,point1,point2):
        #busca unha aresta ou cara preto dunha posicion dada en puntos onde coincide o vertice menor
        #devolve -1 se atopa a aresta ou a cara, cero en caso contrario
        #Se a dimension == 2 seqPointMed e pointMed son None
        i = position
        while min==seqPointMin[i]:
            if point1 == seqPoint1[i]: 
                if seqPoint2 == None:
                    return True
                else:#3 dimensions
                    if point2 == seqPoint2[i]:
                        return True
            if i == 0:
                break
            else:
                i -= 1
                
        if position == (len(seqPointMin)-1):    
            return False
        else:
            i = position+1
        
        while min==seqPointMin[i]:
            if point1 == seqPoint1[i]:
                if seqPoint2 == None:
                    return True
                else:#3 Dimensions
                    if point2 == seqPoint2[i]:
                        return True
            if i == (len(seqPointMin)-1):
                return False
            else:
                i += 1
        return False
            
            

    def calculate_submesh(self, force=False):
        if not self.submeshed or force:
            self.nsm = 0
            #del self.smn[:]
            #del self.sm[:]
            #del self.nrsm[:]
            self.smn = []
            self.sm = []
            self.nrsm = []

            if self.element_type['element']=='line': # was: dim 1
# xa calculado máis abaixo para todas as dimensións
#                if self.transform:
#                    vers = self.element_type.get('points')
#                else:
#                    vers = LNV1
#
#                # point_ref
#                i = 0
#                smn = []
#                smr = []
#                for value in self.nrv:
#                    if a != 0:
#                        # line : p0 p1
#                        n = i // LNV1 # number of line
#                        r = i % LNV1 # number of point
#                        if r == 0:
#                            pointA = self.mmnn[n*LNV1+0]
#                        elif r == 1:
#                            pointA = self.mmnn[n*LNV1+1]
#                        smn.append(pointA)
#                        smr.append(value)
#                    i += 1
#
#                self.sm.append(smn)
#                self.nrsm.append(smr)
#                self.smn.append('nrv')
                pass
            elif self.element_type['element']=='triangle': # was: dim 2

                if self.transform:
                    vers = self.element_type.get('points')
                else:
                    vers = LNV2

                # edge_ref
                i = 0
                smn = []
                smnMin = []
                smnMax = []
                smr = []
                for value in self.nra:
                    if value != 0:
                        # triangle : p0 p1 p2
                        #
                        # edge0 : p0 p1
                        # edge1 : p1 p2
                        # edge2 : p2 p0
                        #
                        n = i // LNE2 # number of triangle
                        r = i % LNE2 # number of edge
                        if r == 0:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+1]
                        elif r == 1:
                            pointA = self.mmnn[n*vers+1]
                            pointB = self.mmnn[n*vers+2]
                        elif r == 2:
                            pointA = self.mmnn[n*vers+2]
                            pointB = self.mmnn[n*vers+0]
                            
                        #NOVO: eliminacion de arestas duplicadas
                        if pointA < pointB:
                            min = pointA
                            max = pointB
                        else:
                            min = pointB
                            max = pointA

                        posicion = self.binary_search(smnMin,min)
                            
                        if(posicion<0): #punto non atopado na lista
                            smnMin.insert(-(posicion+1),min)
                            smnMax.insert(-(posicion+1),max)
                            smr.insert(-(posicion+1),value)
                        else: 
                            if (not self.search_arround(smnMin,smnMax,None,posicion,min,max,None)):
                                smnMin.insert(posicion,min)
                                smnMax.insert(posicion,max)
                                smr.insert(posicion,value)                                          
                            
                        #NOVO: eliminacion de arestas duplicadas
                    i += 1
                    
                #NOVO: escritura dos puntos na lista de arestas
                for i in range(len(smnMin)):
                    smn.append(smnMin[i])
                    smn.append(smnMax[i])
                #NOVO: escritura dos puntos la lista de arestas
                
                self.sm.append(smn)
                self.nrsm.append(smr)
                self.smn.append('edge_ref')

            elif self.element_type['element']=='tetrahedron': # was: dim 3

                if self.transform:
                    vers = self.element_type.get('points')
                else:
                    vers = LNV3

                # face_ref
                i = 0
                smn = []
                smnMin = []
                smnPoint1 = []
                smnPoint2 = []
                smr = []
                for value in self.nrc:
                    if value != 0:
                        # tetrahedron : p0 p1 p2 p3
                        #
                        # face0 : p0 p2 p1
                        # face1 : p0 p3 p2
                        # face2 : p0 p1 p3
                        # face3 : p1 p2 p3
                        #
                        n = i // LNF3 # number of tetrahedron
                        r = i % LNF3 # number of face
                        if r == 0:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+2]
                            pointC = self.mmnn[n*vers+1]
                        elif r == 1:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+3]
                            pointC = self.mmnn[n*vers+2]
                        elif r == 2:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+1]
                            pointC = self.mmnn[n*vers+3]
                        elif r == 3:
                            pointA = self.mmnn[n*vers+1]
                            pointB = self.mmnn[n*vers+2]
                            pointC = self.mmnn[n*vers+3]
                        
                        
                        #NOVO: eliminacion de caras duplicadas
                        if pointA<pointB and pointA<pointC:
                            min = pointA
                            if pointB<pointC:
                                point1 = pointB
                                point2 = pointC
                            else:
                                point1 = pointC
                                point2 = pointB
                        elif pointB<pointA and pointB<pointC:
                            min = pointB
                            if pointA<pointB:
                                point1 = pointA
                                point2 = pointC
                            else:
                                point1 = pointC
                                point2 = pointA
                        else:
                            min = pointC
                            if pointA<pointB:
                                point1 = pointB
                                point2 = pointA
                            else:
                                point1 = pointA
                                point2 = pointB
                        
                        posicion = self.binary_search(smnMin,min)
                        if(posicion<0): #punto non atopado na lista
                            smnMin.insert(-(posicion+1),min)
                            smnPoint1.insert(-(posicion+1),point1)
                            smnPoint2.insert(-(posicion+1),point2)                            
                            smr.insert(-(posicion+1),value)
                        else: 
                            if (not self.search_arround(smnMin,smnPoint1,smnPoint2,posicion,min,point1,point2)):
                                smnMin.insert(posicion,min)
                                smnPoint1.insert(posicion,point1)
                                smnPoint2.insert(posicion,point2)
                                smr.insert(posicion,value)    
                        
                        #NOVO: eliminacion de caras duplicadas
                            
                    i += 1
                    
                    
                #NOVO: escritura dos puntos la lista de caras
                for i in range(len(smnMin)):
                    smn.append(smnMin[i])
                    smn.append(smnPoint1[i])
                    smn.append(smnPoint2[i])
                #NOVO: escritura dos puntos na lista de caras
                
                
                self.sm.append(smn)
                self.nrsm.append(smr)
                self.smn.append('face_ref')

                ###

                # edge_ref
                i = 0
                smnMin = []
                smnMax = []
                smn = []
                smr = []
                for value in self.nra:
                    if value != 0:
                        # tetrahedron : p0 p1 p2 p3
                        #
                        # edge 0 :
                        # edge 1 :
                        # edge 2 :
                        # edge 3 :
                        # edge 4 :
                        # edge 5 :
                        #
                        n = i // LNE3 # number of tetrahedron
                        r = i % LNE3 # number of edge
                        if r == 0:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+1]
                        elif r == 1:
                            pointA = self.mmnn[n*vers+1]
                            pointB = self.mmnn[n*vers+2]
                        elif r == 2:
                            pointA = self.mmnn[n*vers+2]
                            pointB = self.mmnn[n*vers+0]
                        elif r == 3:
                            pointA = self.mmnn[n*vers+0]
                            pointB = self.mmnn[n*vers+3]
                        elif r == 4:
                            pointA = self.mmnn[n*vers+1]
                            pointB = self.mmnn[n*vers+3]
                        elif r == 5:
                            pointA = self.mmnn[n*vers+2]
                            pointB = self.mmnn[n*vers+3]
                            
                        #NOVO: eliminacion de arestas duplicadas
                        if pointA < pointB:
                            min = pointA
                            max = pointB
                        else:
                            min = pointB
                            max = pointA

                        posicion = self.binary_search(smnMin,min)
                            
                        if(posicion<0): #punto non atopado na lista
                            smnMin.insert(-(posicion+1),min)
                            smnMax.insert(-(posicion+1),max)
                            smr.insert(-(posicion+1),value)
                        else: 
                            if (not self.search_arround(smnMin,smnMax,None,posicion,min,max,None)):
                                smnMin.insert(posicion,min)
                                smnMax.insert(posicion,max)
                                smr.insert(posicion,value)                                          
                        #NOVO: eliminacion de arestas duplicadas
                    i += 1
                    
                #NOVO: escritura dos puntos na lista de arestas
                for i in range(len(smnMin)):
                    smn.append(smnMin[i])
                    smn.append(smnMax[i])
                #NOVO: escritura dos puntos la lista de arestas

                self.sm.append(smn)
                self.nrsm.append(smr)
                self.smn.append('edge_ref')

            else:
                return False

            # submesh vertex ; CELL_DATA
            # nrv. reduntant points: repeat
            # outra posibilidade: convertelos a POINT_DATA, posiblemente sobreescribindo valores
#            smn = []
#            smr = []



            # aqui ou fora de calculate_submesh ?
            if self.transform:
                self.nrvtovtk = [0] * self.numvn
                element = 0
                while element < self.nel:
                    for p in range(self.lnv):
                        point = self.mmnn[element*self.lnvn+p]
                        self.nrvtovtk[point] = self.nrv[element*self.lnv+p]
                    element += 1
            else:
                self.nrvtovtk = [0] * self.nver
                i = 0
                for value in self.nrv:
                    if value != 0:
                        point = self.mm[i]
                        self.nrvtovtk[point] = value
 #                   smn.append(point)
 #                   smr.append(value)
                    i += 1
 #           self.sm.append(smn)
 #           self.nrsm.append(smr)
 #           self.smn.append('nrv')


            # calcula o número de elementos da submalla
            self.nsm = 0
            for s in self.nrsm:
                self.nsm += len(s)

            self.submeshed = True
            self.cc('generated ' + unicode(self.nsm) + ' submesh cells')

            return True
        else:
            return True



    def to_vtk(self):
        return self.to_vtk_vtu('vtk')



    def to_vtu(self):
        return self.to_vtk_vtu('vtu')



# creates a FileVTK object
    def to_vtk_vtu(self, mode):
        if mode == 'vtk':
            vtk = FileMrwVTK.FileMrwVTK(self.callback)
        elif mode == 'vtu':
            vtk = FileMrwVTU.FileMrwVTU(self.callback)
        else:
            vtk = FileMrwVTK.FileMrwVTK(self.callback) # por defecto

        if self.submeshed:
            string = unicode(self.nel) + '+' + unicode(self.nsm) + ' cells'
        else:
            string = unicode(self.nel) + ' cells'

        vtk.set_comm('Data ' + unicode(self.dim) + 'D ' + string)


        # coordinates
        self.cc('POINTS ')
        if self.dim == 1:
            p = []
            for a in self.zz:
                p.append(a)
                p.append(0.0)
                p.append(0.0)
            vtk.set_points(p)

        elif self.dim == 2:
            i = 0
            f = len(self.zz)
            p = []
            while i < f:
                p.append(self.zz[i])
                p.append(self.zz[i+1])
                p.append(0.0)
                i += 2
            vtk.set_points(p)

        elif self.dim == 3:
            vtk.set_points(self.zz[:])


        # cells
        self.cc('CELLS ')
        t = 0
        incr = self.lnvn
        etype = self.element_type.get('vtknum')
        while t < len(self.mmnn):
            vtk.add_cell_type(self.mmnn[t:t+incr], etype)
            t += incr


# submesh cells
        i = 0
        while i < len(self.nrsm):

            if len(self.nrsm[i]) > 0:
                r = len(self.sm[i]) // len(self.nrsm[i])
            else:
                r = 0

            t = -1
            if r == 1:
                t = 1 # point
            elif r == 2:
                t = 3 # line
            elif r == 3:
                t = 5 # triangle

            c = 0
            while c < len(self.nrsm[i]):
                vtk.add_cell_type(self.sm[i][c*r:(c+1)*r], t)
                c += 1

            i += 1

# mesh references
        self.cc('CELL_DATA ')
        cd = []
        cd.extend(self.nsd)
        cd.extend([0]*self.nsm)
        vtk.add_cell_data('SCALARS','element_ref',Format1,None,cd)

# submesh references
        i = 0
        while i < len(self.nrsm):
            cd = []

            cd.extend([0]*self.nel)

            j = 0
            while j < i:
                cd.extend([0]*len(self.nrsm[j]))
                j += 1

            cd.extend(self.nrsm[i])

            j = i + 1
            while j < len(self.nrsm):
                cd.extend([0]*len(self.nrsm[j]))
                j += 1

            vtk.add_cell_data('SCALARS',self.smn[i],Format1,None,cd)

            i += 1
            
        if self.nrvtovtk is not None:
            self.cc('POINT_DATA ')
            vtk.add_point_data('SCALARS','vertex_ref',Format1,None,self.nrvtovtk)

        return vtk



    @staticmethod
    def check_type(nv, dim, lnn, lnv, lne, lnf):
        # nv : nnod == nver

        result = None

        # a - Lagrange P1

        # a.1

        # tetrahedros en 3D
        if nv and dim == 3 and lnn == 4 and lnv == 4 and lne == 6 and lnf == 4:
            result = {'element':'tetrahedron', 'type':'p1', 'vtknum':10}

        # triangulos en 2D
        elif nv and dim == 2 and lnn == 3 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p1', 'vtknum':5}

        # linhas en 1D
        elif nv and dim == 1 and lnn == 2 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p1', 'vtknum':3}

        # a.2

        # triangulos en 3D
        elif nv and dim == 3 and lnn == 3 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p1', 'vtknum':5}

        # lihas en 3D
        elif nv and dim == 3 and lnn == 2 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p1', 'vtknum':3}

        # lihas en 2D
        elif nv and dim == 2 and lnn == 2 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p1', 'vtknum':3}

        # b - Raviart - Thomas

        # b.1

        # tetrahedros en 3D
        elif not nv and dim == 3 and lnn == 4 and lnv == 4 and lne == 6 and lnf == 4:
            result = {'element':'tetrahedron', 'type':'rt', 'vtknum':10}

        # triangulos en 2D
        elif not nv and dim == 2 and lnn == 3 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'rt', 'vtknum':5}

        # b.2

        # triangulos en 3D
        elif not nv and dim == 3 and lnn == 3 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'rt', 'vtknum':5}

        # c - Lagrange P1 + baricentro

        # c.1

        # tetrahedros en 3D
        elif not nv and dim == 3 and lnn == 5 and lnv == 4 and lne == 6 and lnf == 4:
            result = {'element':'tetrahedron', 'type':'p1b', 'vtknum':10}

        # triangulos en 2D
        elif not nv and dim == 2 and lnn == 4 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p1b', 'vtknum':5}

        # c.2

        # triangulos en 3D
        elif not nv and dim == 3 and lnn == 4 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p1b', 'vtknum':5}

        # d - Lagrange P2

        # d.1

        # tetrahedros en 3D
        elif not nv and dim == 3 and lnn == 10 and lnv == 4 and lne == 6 and lnf == 4:
            result = {'element':'tetrahedron', 'type':'p2', 'vtknum':24}

        # triangulos en 2D
        elif not nv and dim == 2 and lnn == 6 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p2', 'vtknum':22}

        # linhas en 1D
        elif not nv and dim == 1 and lnn == 3 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p2', 'vtknum':21}

        # d.2

        # triangulos en 3D
        elif not nv and dim == 3 and lnn == 6 and lnv == 3 and lne == 3 and (lnf == 0 or lnf == 1):
            result = {'element':'triangle', 'type':'p2', 'vtknum':22}

        # lihas en 3D
        elif not nv and dim == 3 and lnn == 3 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p2', 'vtknum':21}

        # lihas en 2D
        elif not nv and dim == 2 and lnn == 3 and lnv == 2 and (lne == 0 or lne == 1) and (lnf == 0 or lnf == 1):
            result = {'element':'line', 'type':'p2', 'vtknum':21}


        # e - Nèdèlec

        # e.1

        # tetrahedros en 3D; extra para eddy_currents_3d malla total
        elif not nv and dim == 3 and lnn == 6 and lnv == 4 and lne == 6 and lnf == 4:
            result = {'element':'tetrahedron', 'type':'?', 'vtknum':10}

        ########################

        if result is None:
            return None

        extra = None

        # vértices usados para interpolar as coordenadas (z) dos nodos
        if result.get('type') == 'p2':
            result['points'] = lnn
            if result.get('element') == 'line':
                extra = [[0,1]]
            elif result.get('element') == 'triangle':
                extra = [[0,1],[1,2],[2,0]]
            elif result.get('element') == 'tetrahedron':
                extra = [[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]]

        result['extra'] = extra

        return result



    @staticmethod
    def transform_p2_z(zdim, nnod, z, mm, nn, lnv, lnn, extra):
        nel = len(nn) // lnn

        extranodes = lnn - lnv

        if extranodes < 0:
            return "transform_p2_z: lnn < lnv"

        if extra is None or len(extra) != extranodes:
            return "transform_p2_z: extra wrong"

        znew = [0.0] * zdim * nnod

        temp = [0.0] * zdim

        element = 0
        while element < nel:

            for vertex in range(lnv):
                pointm = mm[element*lnv+vertex]
                pointn = nn[element*lnn+vertex]
                znew[pointn*zdim:(pointn+1)*zdim] = z[pointm*zdim:(pointm+1)*zdim]

            for extranode in range(extranodes):
                comb = extra[extranode]
                point0m = mm[element*lnv+comb[0]]
                point1m = mm[element*lnv+comb[1]]
                pointn = nn[element*lnn+lnv+extranode]
                z0m = z[point0m*zdim:(point0m+1)*zdim]
                z1m = z[point1m*zdim:(point1m+1)*zdim]
                for d in range(zdim):
                    temp[d] = (z0m[d]+z1m[d])/2.0
                znew[pointn*zdim:(pointn+1)*zdim] = temp

            element += 1

        return znew

