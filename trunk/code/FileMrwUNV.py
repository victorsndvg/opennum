#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import FileMrw
import FileMrwVTK
import FileMrwVTU
import FileMrwModulef
import time



# LIMITACIONS DA VERSION ACTUAL:
# conversion a VTK, VTU:
# 1)
# contase con que os nodos estan ordenados no ficheiro .unv segun a sua 'label'
# e tenhen labels consecutivas empezando en 1
# 2)
# so soporta elementos de tipo # 112 (prisma), 115 (hexaedro), 111 (tetraedro), 44 (cuadrilatero), 41 (triangulo), 11 (linha)
# 3)
# soporta nsd, nrc, nra, nrv
#
# conversion a Modulef:
# 1)
# contase con que os nodos estan ordenados no ficheiro .unv segun a sua 'label'
# e tenhen labels consecutivas empezando en 1
# 2)
# conversion 3D,2D,1D
# 3)
# espera nodos, e elementos ordeados de 1 a n
# 4)
# so soporta elementos de tipo 111 (tetraedro), 41 (triangulo), 11 (linha)
# 5)
# Control de erros?


Format1 = 'int'
Format2 = 'double'

epsilon = 1.0e-20

class UNV(FileMrw.FileMrw):
    
    def __init__(self,callback=None):
        FileMrw.FileMrw.__init__(self, callback)
        self.nodes = None
        self.elements = None
        self.groups = None
        
        # calculados en to_vtk()
        self.refs = {}
        self.refs['element_ref'] = None
        self.refs['face_ref'] = None
        self.refs['edge_ref'] = None
        self.refs['vertex_ref'] = None


    # dict of ordered lists of integers
    def get_refs(self):
        return self.refs


    @staticmethod
    def get_info_vtk(size, ide):

        if size == 8 and ide == 115: # 115 Solid Linear Brick
            return (3,12) # VTK_HEXAHEDRON (=12)

        elif size == 6 and ide == 112: # 112 Solid Linear Wedge
            return (3,13) # VTK_WEDGE (=13)

        elif size == 4 and ide == 111: # 111 Solid Linear Tetrahedron
            return (3,10) # VTK_TETRA (=10)

        elif size == 4 and ide == 44: # 44  Plane Stress Linear Quadrilateral
            return (2,9) # VTK_QUAD (=9)

        elif size == 3 and ide == 41: # 41 Plane Stress Linear Triangle
            return (2,5) # VTK_TRIANGLE (=5)

        elif size == 2 and ide == 11: # 11 Rod
            return (1,3) # VTK_LINE (=3)

        elif size == 3 and ide == 22: # 2 Tapered beam
            return (1,21) # VTK_QUADRATIC_EDGE (=21)

        elif size == 6 and ide == 42: # 42 Plane Stress Parabolic Triangle 
            return (2,22) # VTK_QUADRATIC_TRIANGLE (=22)

        elif size == 10 and ide == 118: # 118 Solid Parabolic Tetrahedron
            return (3,24) # VTK_QUADRATIC_TETRA (=24)

#        elif size == 1:
#            return (0,1) # VTK_VERTEX (=1)

        return None # (dim, VTK_id)




    class Node:

        def __init__(self,record1,record2):
            self.AssignValues(record1,record2)
            
        def AssignValues(self,record1,record2):
            self.label = record1[0]         #-- node label
            self.coordSys = record1[1]      #-- export coordinate system number
            self.coordSysDisp = record1[2]  #-- displacement coordinate system number
            self.color = record1[3]         #-- color
            self.coords = record2           #-- node coordinates
            
        def GetValues(self):
            print self.label
            print self.coordSys
            print self.coordSysDisp
            print self.color
            print self.coords
            
    class Element:

        def __init__(self,record1,record2,record3):
            self.AssignValues(record1,record2,record3)
            
        def AssignValues(self,record1,record2,record3):
            self.label = record1[0]        #-- element label
            self.feDescID = record1[1]     #-- fe descriptor id
            self.physProp = record1[2]     #-- physical property table number
            self.matProp = record1[3]      #-- material property table number
            self.color = record1[4]        #-- color
            self.numNodes = record1[5]     #-- number of nodes on element
            if record3 == None: #Non-Beam elements
                self.nodeLabels = record2  #-- node labels defining element
            else: #Beam elements
                #record2 non se utiliza nos Beam elements??
                self.nodeLabels = record3  #-- node labels defining element
    
    class Group:
        
        def __init__(self,record1,record2,record3):
            self.AssignValues(record1,record2,record3)
            
        def AssignValues(self,record1,record2,record3):
            self.groupNumber = record1[0]      #-- group number
            self.constSet = record1[1]         #-- active constraint set no. for group
            self.restSet = record1[2]          #-- active restraint set no. for group
            self.loadSet = record1[3]          #-- active load set no. for group
            self.dofSet = record1[4]           #-- active dof set no. for group
            self.temperatureSet = record1[5]   #-- active temperature set no. for group
            self.contactSet = record1[6]       #-- active contact set no. for group
            self.numEntities = record1[7]      #-- number of entities in group
            self.groupName = record2           #-- group name
            self.entities = record3            #-- entities array[type code,tag,node leaf id,component/ ham id.]

    def openFile(self,filename):
        file=open(filename)
        return file
    
    def searchFlag(self,file):
        loop = True
        flag = '    -1' #indica o comezo e final dun dataset
        found = False
        while loop:
            line = file.readline()
            if line.startswith(flag):
                loop = False
                found = True
            elif not line: #Se nos atopamos co EOF
                found = False
                loop = False           
        return found
                            
    def searchDataSet(self,file):
        loop = True
    
        while loop:
            if self.searchFlag(file):
                dataSet = file.readline()
                if dataSet:
                    if int(dataSet)==2411: #Dataset 2411
                        self.nodes = self.readUNV2411(file)
                    elif int(dataSet)==2412: #Dataset 2412
                        self.elements = self.readUNV2412(file)
                    elif int(dataSet)==2467: #Dataset 2467
                        self.groups = self.readUNV2467(file)
                    elif not self.searchFlag(file): #No caso de que sexa outro dataset
                        loop = False
            else:
                loop = False
                
    def readUNV2411(self,file):
        """Metodo que le o contido dun dataset 2411 dun ficheiro de malla UNV"""
        loop = True
        endDataSet = '    -1'
        nodes = []
        cont = 0
        while loop:
            line1 = file.readline()
            if not line1 or line1.startswith(endDataSet):
                loop = False
            else:
                record1 = map(int, line1.split())
                line2 = file.readline()
                record2 = map(float, line2.split())
                cont += 1
                nodes.append(self.Node(record1,record2))
        return nodes
    
    
    def readUNV2412(self,file):
        """Metodo que le o contido dun dataset 2412 dun ficheiro de malla UNV"""
        loop = True
        endDataSet = '    -1'
        elements = []
        cont = 0
        while loop:
            record3 = None
            line1 = file.readline() 
            if not line1 or line1.startswith(endDataSet): #Se nos atopamos co EOF
                loop = False
            else:
                record1 = map(int, line1.split())
		record2 = []
		while (len(record2)<record1[-1]):
		    line2 = file.readline()
                    record2.extend(map(int, line2.split()))
                if (record1[1] >= 11) and (record1[1]<=32): #Beam elements 11 = Rod
                    line3 = file.readline()
                    record3 = map(int, line3.split())
                cont += 1
                elements.append(self.Element(record1,record2,record3))
        return elements
    
     
    def readUNV2467(self,file):
        """Metodo que le o contido dun dataset 2467 dun ficheiro de malla UNV"""   
        loop = True
        endDataSet = '    -1'
        groups = []
        while loop:
            entities=[]
            line1 = file.readline()
            if line1.startswith(endDataSet):
                loop = False
            else:
                record1 = map(int,line1.split())
                record2 = file.readline()
                for cont in range((record1[7]+1)//2):
                    record = map(int,file.readline().split())
                    entities.append(record[0:4])
                    if len(record)>4:                        
                        entities.append(record[4:8])
                groups.append(self.Group(record1,record2,entities))
        return groups
                
    def read(self,filename):
        print 'Reading file ' + filename + ' ...'
        try:
            self.file = self.openFile(filename)
            try:
                self.searchDataSet(self.file)            
            except ValueError:
                return 'Error: unknown format'
        except IOError:
            return 'Error: opening file'
        return None



    def to_vtk(self):
        return self.to_vtk_vtu('vtk')



    def to_vtu(self):
        return self.to_vtk_vtu('vtu')





    def to_vtk_vtu(self, mode):
        """ returns an object of class FileMrwVTK or an error string """
    
        # repensar este bloque. debera self.nodes, self.elements e self.groups
        # inicializarse a [] no construtor ? en vez de None ?
        if self.nodes is None:
            return 'self.nodes None'
        if self.elements is None:
            return 'self.elements None'
        #if self.groups is None:
        #    return 'self.groups None'
            
        if mode == 'vtk':
            vtk = FileMrwVTK.FileMrwVTK(None)
        elif mode == 'vtu':
            vtk = FileMrwVTU.FileMrwVTU(None)
        else:
            vtk = FileMrwVTK.FileMrwVTK(None) # por defecto

        # POINTS
        # suponho que os puntos estan ordenados no ficheiro .unv segun a sua 'label'
        # e tenhen labels consecutivas empezando en 1
        # test preliminar
        if len(self.nodes)>0:
            if self.nodes[0].label != 1:
                return 'First node label is not 1 [not yet supported]'
        
        z = []
        for node in self.nodes:
            z.extend(node.coords)
        vtk.set_points(z)

        maxdim = 0
        # CELLS
	isfirst_triangle = True
	isfirst_tetra = True
	t3_ordering = None
	t4_ordering = None
        for element in self.elements:
            translated = []
            # suponho que as labels empezan a contar en 1 (VTK empeza en 0)
            # suponho que a orde de vertices e a mesma en UNV e VTK

            info = UNV.get_info_vtk(len(element.nodeLabels),element.feDescID)

            if info is not None:
		if info == (2,22) and isfirst_triangle:
		    isfirst_triangle= False
		    t3_ordering = self.node_ordering(element.nodeLabels, info)
		if info == (3,24) and isfirst_tetra:
		    isfirst_tetra= False
		    t4_ordering = self.node_ordering(element.nodeLabels, info)

            for n in element.nodeLabels:
                translated.append(n-1)

	    if t3_ordering is not None and info == (2,22):
                aux = [translated[t3_ordering[0]],translated[t3_ordering[1]],translated[t3_ordering[2]], \
		       translated[t3_ordering[3]],translated[t3_ordering[4]],translated[t3_ordering[5]]]
		translated = aux

	    if t4_ordering is not None and info == (3,24):
                aux = [translated[t4_ordering[0]],translated[t4_ordering[1]],translated[t4_ordering[2]], \
		       translated[t4_ordering[3]],translated[t4_ordering[4]],translated[t4_ordering[5]], \
		       translated[t4_ordering[6]],translated[t4_ordering[7]],translated[t4_ordering[8]], \
                       translated[t4_ordering[9]]]
		translated = aux

#	    if len(translated) == 6:
#                aux = [translated[0],translated[2],translated[4],translated[1],translated[3],translated[5]]
#		translated=aux

            if info is not None:
                vtk.add_cell_type(translated, info[1])
                if maxdim < info[0]:
                    maxdim = info[0]
            else:
                return 'Unknown element id ('+unicode(element.feDescID)+') and nodes size ('+unicode(size)+')'


        if self.groups is None:
            ngroups = 0
        else:
            ngroups = len(self.groups)
        string = unicode(len(self.nodes)) + ' points ' + unicode(len(self.elements)) + ' cells ' + unicode(ngroups) + ' groups' 

        vtk.set_comm('Data from .unv ' + unicode(maxdim) + 'D ' + string)


        # SUBMALLAS / nsd / nrc / nra / nrv / num -> element_ref face_ref edge_ref vertex_ref vertex_num element_num

        # array de puntos .. id [0..n-1] -> [1..n]
        # para ter os numeros disponhibles para as etiquetas
        vtk.add_point_data_sequential()
        
        # array de elementos .. [1..n] para los de dimensión máxima y 0 para el resto
        array = []
        index = 1
        for element in self.elements:
            dim = -1
            info = UNV.get_info_vtk(len(element.nodeLabels),element.feDescID)
            if info is not None:
                dim = info[0]
            if dim == maxdim:
                array.append(index)
                index += 1
            else:
                array.append(0)
        vtk.add_cell_data_sequential(array)
        
        # reset de references e subdomains
        self.refs['element_ref'] = []
        self.refs['face_ref'] = []
        self.refs['edge_ref'] = []
        self.refs['vertex_ref'] = []
        
        nsd_ = [0]*len(self.elements)
        nrc_ = None
        nra_ = None
        nrv_ = None
        if maxdim > 2:
            nrc_ = [0]*len(self.elements)
        if maxdim > 1:
            nra_ = [0]*len(self.elements)
        if maxdim > 0:
            nrv_ = [0]*len(self.nodes)
        
        warning_etc = 0
        warning_dim = 0
        nsdset = set()
        nrcset = set()
        nraset = set()
        nrvset = set()

        tempgroups = self.groups
        if tempgroups is None:
            tempgroups = []

        for group in tempgroups: # orden creciente => refs ordenadas

            value = group.groupNumber

            for e in group.entities:

                etype = e[0]
                enode = e[1]
                edim = None

                if etype == 8: # 8: finite elements

                    element = self.elements[enode-1]
                    info = UNV.get_info_vtk(len(element.nodeLabels),element.feDescID)
                    if info is not None:
                        edim = info[0]

                elif etype == 7: # 7: nodes: grupos de puntos

                    edim = 0

                else:

                    warning_etc += 1
                    continue

                if edim == maxdim:
                    # almacenaxe de subdominios
                    if value not in nsdset:
                        nsdset.add(value)
                        self.refs['element_ref'].append(value)
                    nsd_[enode-1] = value
                elif edim == 2:
                    # almacenaxe de nrc
                    if value not in nrcset:
                        nrcset.add(value)
                        self.refs['face_ref'].append(value)
                    nrc_[enode-1] = value
                elif edim == 1:
                    # almacenaxe de nra
                    if value not in nraset:
                        nraset.add(value)
                        self.refs['edge_ref'].append(value)
                    nra_[enode-1] = value
                elif edim == 0:
                    # almacenaxe de nrv
                    if value not in nrvset:
                        nrvset.add(value)
                        self.refs['vertex_ref'].append(value)
                    nrv_[enode-1] = value
                else:
                    warning_dim += 1


        if warning_etc != 0:
            print u'Warning: ' + unicode(warning_etc) + ' \'entity type code\' != 8 and != 7'
        if warning_dim != 0:
            print u'Warning: ' + unicode(warning_dim) + ' entities with unsupported dimension'
        
        vtk.add_cell_data('SCALARS','element_ref',Format1,None,nsd_)
        if nrc_ is not None:
            vtk.add_cell_data('SCALARS','face_ref',Format1,None,nrc_)
        if nra_ is not None:
            vtk.add_cell_data('SCALARS','edge_ref',Format1,None,nra_)
        if nrv_ is not None:
            vtk.add_point_data('SCALARS','vertex_ref',Format1,None,nrv_)
        
        return vtk



    def to_mfm_line_format(self, array):
        aux = []
        for a in array:
            aux.extend(a)
        return aux


    def issingular_edge(self,lista1,lista2):
	import sys
	if isinstance(lista1,list) and isinstance(lista2,list):
	    eps = sys.float_info.epsilon
	    if len(lista1) == len(lista2) == 3:
		res = [0,0,0]
		maxval = None 
		for i in range(3):
		    res[i] = abs((lista1[i]-lista2[i]))
		return max(res)<eps
	    else:
		return 'Lists length must agree.'
	else:
	    return 'Wrong data type.'
    

    def ismidpoint(self,lista1,lista2,lista3):
	import sys
	if isinstance(lista1,list) and isinstance(lista2,list) and isinstance(lista3,list):
	    eps = sys.float_info.epsilon
	    if len(lista1) == len(lista2) == len(lista3) == 3:
		res = [0,0,0]
		maxval = None 
		for i in range(3):
		    res[i] = abs(((lista2[i]+lista3[i])/2-lista1[i]))
		return max(res)<eps
	    else:
		return 'Lists length must agree.'
	else:
	    return 'Wrong data type.'

    def coord_diff(self,lista1,lista2):
	if isinstance(lista1,list) and isinstance(lista2,list):
	    if len(lista1) == len(lista2) == 3:
		res = [0,0,0]
		for i in range(3):
		    res[i] = lista1[i]-lista2[i]
		return res
	    else:
		return 'Lists length must agree.'
	else:
	    return 'Wrong data type.'


    def node_ordering(self, nodelist, info):
	# (2,22) # VTK_QUADRATIC_TRIANGLE (=22)
	# (3,24) # VTK_QUADRATIC_TETRA (=24)
#	if info != (2,22) or info != (3,24):
#	    return 'Non quadratic (Nedelec) mesh'

	vertexlist = [i for i in nodelist]
	midpointlist = []
	edgelist = []
	labels = []
	for node in self.nodes:
	    labels.append(node.label)
	####################################################
	# Localizacion de puntos medios
	lennodelist = len(nodelist)
	node_index= [0*i for i in range(lennodelist)]
	for i in range(lennodelist):
	    node_index[i] = self.binary_search(labels,nodelist[i])   
	for i in range(lennodelist):
	    i_node = node_index[i]
	    ismidpointb = False
	    for j in range(lennodelist):
		if not ismidpointb:
		    j_node = node_index[j]
		    for k in range(j+1,lennodelist):
			k_node = node_index[k]
			if not self.issingular_edge(self.nodes[j_node].coords,self.nodes[k_node].coords) and \
			    self.ismidpoint(self.nodes[i_node].coords,self.nodes[j_node].coords,self.nodes[k_node].coords):
			    ismidpointb = True
			    midpointlist.append(nodelist[i])
			    edgelist.append([nodelist[j],nodelist[k]])
			    vertexlist.remove(nodelist[i])
	####################################################3
	# Reordenacion dos nodos segun el orden de los vertices	
	for i in range(len(vertexlist)-1):
	    for j in range(len(edgelist)-1):
		if (vertexlist[i] == edgelist[j][0] or vertexlist[i] == edgelist[j][1]) and \
		   (vertexlist[i+1] == edgelist[j][0] or vertexlist[i+1] == edgelist[j][1]):
		    aux = midpointlist[j]
		    midpointlist[j] = midpointlist[i]
		    midpointlist[i] = aux
	####################################################3
	# Reordenacion,, determinante positivo
	auxnodelist = vertexlist + midpointlist
	orderlist= [0*i for i in range(lennodelist)]
	coord0 = self.nodes[node_index[0]].coords
	coord1 = self.nodes[node_index[1]].coords
	coord2 = self.nodes[node_index[2]].coords
	if info == (2,22):
	    a2 = self.coord_diff(coord1,coord0)
	    a3 = self.coord_diff(coord2,coord1)
	    if (a2[0]*a3[1]-a2[1]*a3[0])<0:
		aux = auxnodelist[2]
		auxnodelist[2] = auxnodelist[1]
		auxnodelist[1] = aux
		aux = auxnodelist[3]
		auxnodelist[3] = auxnodelist[5]
		auxnodelist[5] = aux
	    for i in range(lennodelist):
		for j in range(lennodelist):
		    if nodelist[i] == auxnodelist[j]:
			orderlist[j] = i
	    return orderlist
	if info == (3,24):
	    coord3 = self.nodes[node_index[3]].coords
	    a2 = self.coord_diff(coord1,coord0)
	    a3 = self.coord_diff(coord2,coord0)
	    a4 = self.coord_diff(coord3,coord0)
	    if (a2[0]*a3[1]*a4[2]+a2[2]*a3[0]*a4[1]+a2[1]*a3[2]*a4[0]- \
		a2[2]*a3[1]*a4[0]-a2[1]*a3[0]*a4[2]-a2[0]*a3[2]*a4[1])<0:
		aux = auxnodelist[4]
		auxnodelist[4] = auxnodelist[6]
		auxnodelist[6] = aux
		aux = auxnodelist[8]
		auxnodelist[8] = auxnodelist[9]
		auxnodelist[9] = aux
	    for i in range(lennodelist):
		for j in range(lennodelist):
		    if nodelist[i] == auxnodelist[j]:
			orderlist[j] = i
	    return orderlist
	return None
		   
    
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




#    def unv2mfmSubMeshF2PY(self,dimension,elements,vertex,edges,faces,tetras,mfm): 
#        mfm.nrv = [0 for i in range((dimension+1)*len(elements))]
#        mfm.nsd = [0 for i in range(len(elements))]
#        
#        if dimension == 2:
#            mfm.nra = [0 for i in range(3*len(elements))]
#        elif dimension == 3:
#            mfm.nra = [0 for i in range(6*len(elements))]
#            mfm.nrc = [0 for i in range((dimension+1)*len(elements))]
#            
#        if len(vertex)>0:
#            mfm.nrv = subMesh.getnrv(dimension,len(elements),elements,len(vertex),vertex)
#        if len(edges)>0:
#            mfm.nra = subMesh.getnra(dimension,len(elements),elements,len(edges),edges)
#        if len(faces)>0:
#            if dimension == 2:
#                mfm.nsd = subMesh.getnsd(dimension,len(elements),elements,len(faces),faces)
#            if dimension == 3:
#                mfm.nrc = subMesh.getnrc(dimension,len(elements),elements,len(faces),faces)      
#        if len(tetras)>0:
#            mfm.nsd = subMesh.getnsd(dimension,len(elements),elements,len(tetras),tetras)




#NOVO: binary search                            
            
    def unv2mfmSubMesh(self,dimension,elements,vertex,edges,faces,tetras,mfm):

        mfm.nsd = [0] * len(elements)
        mfm.nrv = [0] * ((dimension+1)*len(elements))
        
        if dimension == 2:
            mfm.nra = [0] * (3*len(elements))
        elif dimension == 3:
            mfm.nra = [0] * (6*len(elements))
            mfm.nrc = [0] * (4*len(elements))
        
        #listas de vertices de tetraedros 
        tetras1 = tetras[0] #lista de vertices menores de tetraedros (ordeada)
        tetras2 = tetras[1]
        tetras3 = tetras[2]
        tetras4 = tetras[3]
        tetrasGroup = tetras[4]            
        #listas de vertices de caras
        faces1 = faces[0] #lista de vertices menores de caras
        faces2 = faces[1]
        faces3 = faces[2]
        facesGroup = faces[3]
        #listas de vertices de arestas. [edges1[0],edges2[0]] --> e unha aresta, edgesGroup[0] e a referencia
        edges1 = edges[0] #lista de vertices menores de arestas (ordeada)
        edges2 = edges[1]
        edgesGroup = edges[2] 
        vertex1 = vertex[0]
        vertexGroup = vertex[1]

        if dimension == 1:
            for i in range(len(elements)): # len(elements[i]) = 2

                if len(edges1)>0:
                    sortedElement = sorted(elements[i])
                    #Buscamos o vertice menor de cada aresta na lista de vertices menores
                    posicion = self.binary_search(edges1,sortedElement[0])
                    if posicion>=0:
                        index = posicion-1
                        #Recorremos os vertices menores iguais
                        while (index>=0) and (edges1[index] == edges1[posicion]):
                            posicion=index
                            index -=1
                        index = posicion
                        while (index<len(edges1) and (edges1[index]==edges1[posicion])):
                            #se atopamos unha aresta como subdominio...
                            if (edges1[index] in elements[i]) and (edges2[index] in elements[i]):
                                mfm.nsd[i] = edgesGroup[index]
                            index +=1

                if len(vertex1)>0:
                    for index in range(len(elements[i])):
                        posicion = self.binary_search(vertex1,elements[i][index])
                        if posicion>=0: # antes estaba en >, non >=
                            mfm.nrv[2*i+index] = vertexGroup[posicion]


        if dimension == 2: # len(elements[i]) = 3
            for i in range(len(elements)):

                #Recorremos todolas caras da malla
                if len(faces1)>0:
                    sortedElement = sorted(elements[i])
                    #Buscamos o vertice menor de cada cara na lista de vertices menores
                    posicion = self.binary_search(faces1,sortedElement[0])
                    if posicion>=0:
                        index = posicion-1
                        #Recorremos os vertices menores iguais
                        while (index>=0) and (faces1[index] == faces1[posicion]):
                            posicion=index
                            index -=1
                        index = posicion
                        while (index<len(faces1) and (faces1[index]==faces1[posicion])):
                            #se atopamos unha cara como subdominio...
                            if ((faces1[index] in elements[i]) and (faces2[index] in elements[i])
                                and (faces3[index] in elements[i])):
                                mfm.nsd[i] = facesGroup[index]
                            index +=1

                if len(edges1)>0:
                    posiciones = []
                    sortedElement = sorted(elements[i])
                    posiciones.append(self.binary_search(edges1,sortedElement[0]))
                    posiciones.append(self.binary_search(edges1,sortedElement[1]))
                    #posicion = self.binary_search(edges1,sortedElement[0]) ### !!! estaba sen comentar
                    for posicion in posiciones:
                        if posicion>=0:
                            index = posicion-1
                            while (index>=0) and (edges1[index] == edges1[posicion]):
                                posicion=index
                                index -=1
                            index = posicion
                            while (index<len(edges1) and (edges1[index]==edges1[posicion])):
                                if ((edges1[index] in elements[i]) and (edges2[index] in elements[i])):
                                    aux = []
                                    aux.extend([elements[i].index(edges1[index]),elements[i].index(edges2[index])])
                                    aux.sort()
                                    if aux == [0,1]:
                                        numline = 0
                                    elif aux == [1,2]:
                                        numline = 1
                                    elif aux == [0,2]:
                                        numline = 2
                                    mfm.nra[3*i+numline] = edgesGroup[index]
                                index +=1

                if len(vertex1)>0:
                    for index in range(len(elements[i])):
                        posicion = self.binary_search(vertex1,elements[i][index])
                        if posicion>=0: # antes estaba en >, non >=
                            mfm.nrv[3*i+index] = vertexGroup[posicion]


        if dimension == 3:
            for i in range(len(elements)): # len(elements[i]) = 4

                if len(tetras1)>0:
                    sortedElement = sorted(elements[i])
                    posicion = self.binary_search(tetras1,sortedElement[0])
                    if posicion>=0:
                        index = posicion-1
                        while (index>=0) and (tetras1[index] == tetras1[posicion]):
                            posicion=index
                            index -=1
                        index = posicion
                        while (index<len(tetras1) and (tetras1[index]==tetras1[posicion])):
                            if ((tetras1[index] in elements[i]) and (tetras2[index] in elements[i])
                                and (tetras3[index] in elements[i]) and (tetras4[index] in elements[i])):
                                mfm.nsd[i] = tetrasGroup[index]
                            index +=1

                if len(faces1)>0:
                    posiciones = []
                    sortedElement = sorted(elements[i])
                    posiciones.append(self.binary_search(faces1,sortedElement[0]))
                    posiciones.append(self.binary_search(faces1,sortedElement[1]))
                    for posicion in posiciones:
                        if posicion>=0:
                            index = posicion-1
                            while (index>=0) and (faces1[index] == faces1[posicion]):
                                posicion=index
                                index -=1
                            index = posicion
                            while (index<len(faces1) and (faces1[index]==faces1[posicion])):
                                if ((faces1[index] in elements[i]) and (faces2[index] in elements[i])
                                    and (faces3[index] in elements[i])):
                                    aux = []
                                    aux.extend([elements[i].index(faces1[index]),elements[i].index(faces2[index]),
                                                elements[i].index(faces3[index])])
                                    aux.sort()
                                    if aux == [0,1,2]:
                                        numface = 0
                                    elif aux == [0,2,3]:
                                        numface = 1
                                    elif aux == [0,1,3]:
                                        numface = 2
                                    elif aux == [1,2,3]:
                                        numface = 3
                                    mfm.nrc[(dimension+1)*i + numface] = facesGroup[index]
                                index +=1

                if len(edges1)>0:
                    posiciones = []
                    sortedElement = sorted(elements[i])
                    posiciones.append(self.binary_search(edges1,sortedElement[0]))
                    posiciones.append(self.binary_search(edges1,sortedElement[1]))
                    posiciones.append(self.binary_search(edges1,sortedElement[2]))
                    for posicion in posiciones:
                        if posicion>=0:
                            index = posicion-1
                            while (index>=0) and (edges1[index] == edges1[posicion]):
                                posicion=index
                                index -=1
                            index = posicion
                            while (index<len(edges1) and (edges1[index]==edges1[posicion])):
                                if ((edges1[index] in elements[i]) and (edges2[index] in elements[i])):
                                    aux = []
                                    aux.extend([elements[i].index(edges1[index]),elements[i].index(edges2[index])])
                                    aux.sort()
                                    if aux == [0,1]:
                                        numline = 0
                                    elif aux == [1,2]:
                                        numline = 1
                                    elif aux == [0,2]:
                                        numline = 2
                                    elif (aux == [0,3]):
                                        numline = 3
                                    elif aux == [1,3]:
                                        numline = 4
                                    elif aux == [2,3]:
                                        numline = 5
                                    mfm.nra[6*i+numline] = edgesGroup[index]
                                index +=1

                    if len(vertex1)>0:
                        for index in range(len(elements[i])):
                            posicion = self.binary_search(vertex1,elements[i][index])
                            if posicion>=0: # antes estaba en >, non >=
                                mfm.nrv[4*i+index] = vertexGroup[posicion]
#/NOVO: binary search



    def to_mfm(self):
        """ returns an object of class FileMrwModulef or an error string """
    
        # repensar este bloque. debera self.nodes, self.elements e self.groups
        # inicializarse a [] no construtor ? en vez de None ?
        if self.nodes is None:
            return 'self.nodes None'
        if self.elements is None:
            return 'self.elements None'
        #if self.groups is None:
        #    return None

        mfm = FileMrwModulef.FileMrwModulef()
        
        mfm.numNodes = len(self.nodes)
        mfm.numVertex = len(self.nodes)

        # POINTS
        # suponho que os puntos estan ordenados no ficheiro .unv segun a sua 'label'
        # e tenhen labels consecutivas empezando en 1
        # test preliminar
        if mfm.numNodes>0:
            if self.nodes[0].label != 1:
                return 'First node label is not 1 [not yet supported]'      
        
        lines = []
        triangles = []
        tetrahedrons  = []
        dimension = 0

        dims_other = [0, 0, 0, 0]
        dims_supported = [0, 0, 0, 0]

        for element in self.elements:
            t = element.feDescID
            if t == 11: #linhas
                lines.append(element.nodeLabels)
                dims_supported[1] += 1 # 1D
            elif t == 41: #triangulos
                triangles.append(element.nodeLabels)
                dims_supported[2] += 1 # 2D
            elif t == 111: #tetraedros
                tetrahedrons.append(element.nodeLabels)
                dims_supported[3] += 1 # 3D
            else: # no soportados
                if t <= 39:
                    dims_other[1] += 1 # 1D
                elif t <= 99:
                    dims_other[2] += 1 # 2D
                elif t <= 119:
                    dims_other[3] += 1 # 3D
                elif t <= 169:
                    pass # no se tienen en cuenta: [120,169]
                elif t == 171 or t == 172:
                    dims_other[2] += 1 # 2D
                else:
                    pass # no se tienen en cuenta: [173,inf)

        ds = len(dims_supported) - 1
        while ds >= 0 and dims_supported[ds] == 0:
            ds -= 1
        do = len(dims_other) - 1
        while do >= 0 and dims_other[do] == 0:
            do -= 1

        if do >= ds and do != -1:
            return 'Unsupported elements of dimension greater or equal than supported elements (' + unicode(do) + '>=' + unicode(ds) + ')'



        vertex = []
        edges = []
        faces = []
        tetra = []
        
#NOVO: binary search
        vertexGroup = [] #lista de numeros de referencia a vertices
        line1 = [] #lista de vertices menores das arestas(ordeada)
        line2 = [] 
        linesGroup = [] #lista de numeros de referencia de arestas
        triangle1 = [] #lista de vertices menores das caras (ordeada)
        triangle2 = [] 
        triangle3 = []
        trianglesGroup = [] #lista de numeros de referencia a caras
        tetrahedron1 = [] #lista de vertices de tetraedros (ordeada)
        tetrahedron2 = []
        tetrahedron3 = []
        tetrahedron4 = []
        tetrahedronsGroup = [] #lista de numeros de referencia a tetraedros
#/NOVO: binary search
        
        if self.groups is None:
            temp = []
        else:
            temp = self.groups

        for group in temp:
            numGroup = group.groupNumber
            for entity in group.entities:
                if entity[0] == 7: # nodes
                    #vertex.append([entity[1],numGroup])
#NOVO: binary search
                    posicion = self.binary_search(vertex,entity[1])
                    if posicion<0:
                        posicion = -(posicion+1)
                    vertex.insert(posicion,entity[1])
                    vertexGroup.insert(posicion,numGroup)
#/NOVO: binary search
                elif entity[0] == 8: # finite elements
                    if self.elements[entity[1]-1].feDescID == 11:
                        #edges.append(self.elements[entity[1]-1].nodeLabels + [numGroup]) # f2py
#NOVO: binary search 
                        #(ordeamos e separamos os vertices das arestas en diferentes listas)
                        sortedNodeLabels = sorted(self.elements[entity[1]-1].nodeLabels)
                        min = sortedNodeLabels[0] 
                        num1 = sortedNodeLabels[1]
                        posicion = self.binary_search(line1,min)
                        if posicion<0:
                            posicion = -(posicion+1)
                        line1.insert(posicion,min)
                        line2.insert(posicion,num1)
                        linesGroup.insert(posicion,numGroup)
#/NOVO: binary search
                    elif self.elements[entity[1]-1].feDescID == 41:
                        #faces.append(self.elements[entity[1]-1].nodeLabels + [numGroup]) # f2py
#NOVO: binary search 
                        #(ordeamos e separamos os vertices das caras en diferentes listas)
                        sortedNodeLabels =sorted(self.elements[entity[1]-1].nodeLabels)
                        min = sortedNodeLabels[0]
                        num1 = sortedNodeLabels[1]
                        num2 = sortedNodeLabels[2]
                        posicion = self.binary_search(triangle1,min)
                        if posicion<0:
                            posicion = -(posicion+1)
                        triangle1.insert(posicion,min)
                        triangle2.insert(posicion,num1)
                        triangle3.insert(posicion,num2)
                        trianglesGroup.insert(posicion,numGroup)
#/NOVO: binary search
                    elif self.elements[entity[1]-1].feDescID == 111:
                        #tetra.append(self.elements[entity[1]-1].nodeLabels + [numGroup]) # f2py
#NOVO: binary search 
                        #(ordeamos e separamos os vertices dos tetraedros en diferentes listas)
                        sortedNodeLabels = sorted(self.elements[entity[1]-1].nodeLabels)
                        min = sortedNodeLabels[0]
                        num1 = sortedNodeLabels[1]
                        num2 = sortedNodeLabels[2]
                        num3 = sortedNodeLabels[3]
                        posicion = self.binary_search(tetrahedron1,min)
                        if posicion<0:
                            posicion = -(posicion+1)
                        tetrahedron1.insert(posicion,min)
                        tetrahedron2.insert(posicion,num1)
                        tetrahedron3.insert(posicion,num2)
                        tetrahedron4.insert(posicion,num3)
                        tetrahedronsGroup.insert(posicion,numGroup)
#/NOVO: binary search

#NOVO: binary search                        
        tetrahedronG = [tetrahedron1,tetrahedron2,tetrahedron3,tetrahedron4,tetrahedronsGroup]
        triangleG = [triangle1,triangle2,triangle3,trianglesGroup]
        lineG = [line1,line2,linesGroup]
        vertexG =  [vertex,vertexGroup]
#/NOVO: binary search       

        if len(tetrahedrons) > 0:
            dimension = 3
            mfm.numElements = len(tetrahedrons)
            mfm.mm = self.to_mfm_line_format(tetrahedrons)
            #self.unv2mfmSubMeshF2PY(dimension,tetrahedrons,vertex,edges,faces,tetra,mfm) # f2py
#NOVO: binary search
            self.unv2mfmSubMesh(dimension,tetrahedrons,vertexG,lineG,triangleG,tetrahedronG,mfm)
#/NOVO: binary search
        elif len(triangles) > 0:
            dimension = 2
            mfm.numElements = len(triangles)
            mfm.mm = self.to_mfm_line_format(triangles)
            #self.unv2mfmSubMeshF2PY(dimension,triangles,vertex,edges,faces,tetra,mfm) # f2py
#NOVO: binary search
            self.unv2mfmSubMesh(dimension,triangles,vertexG,lineG,triangleG,tetrahedronG,mfm)
#/NOVO: binary search
        elif len(lines) > 0:
            dimension = 1
            mfm.numElements = len(lines)
            mfm.mm = self.to_mfm_line_format(lines)
            #self.unv2mfmSubMeshF2PY(dimension,lines,vertex,edges,faces,tetra,mfm)
#NOVO: binary search
            #non moi probado
            self.unv2mfmSubMesh(dimension,lines,vertexG,lineG,triangleG,tetrahedronG,mfm)
#/NOVO: binary search
        
        z = []

        zdim = dimension

        if dimension == 0: # baleiro
            mfm.dim = zdim
            mfm.lnn = 2
            mfm.lnv = 2
            mfm.lne = 0
            mfm.lnf = 0


        if dimension == 1:
            # false: all 0 ; true: not all 0
            # solo se reduce la dimensionalidad para (z=0) o (z=0 y y=0)
            coordY = False
            coordZ = False
            for node in self.nodes:
                if (not coordY) and (abs(node.coords[1]) > epsilon): #(node.coords[1] != 0):
                    coordY = True
                if (not coordZ) and (abs(node.coords[2]) > epsilon): #(node.coords[2] != 0):
                    coordZ = True
                    break

            if coordZ: 
                zdim = 3
                for node in self.nodes:
                    z.append(node.coords)
            else:
                if coordY:
                    zdim = 2
                    for node in self.nodes:
                        z.append(node.coords[0:2])
                else:
                    zdim = 1
                    for node in self.nodes:
                        z.append(node.coords[0:1])

            mfm.dim = zdim
            mfm.lnn = 2
            mfm.lnv = 2
            mfm.lne = 0
            mfm.lnf = 0


        if dimension == 2:
            # false: all 0 ; true: not all 0
            # solo se reduce la dimensionalidad para (z=0)
            coordZ = False
            for node in self.nodes:
                if (abs(node.coords[2]) > epsilon): #(node.coords[2] != 0):
                    coordZ = True
                    break

            if coordZ:
                zdim = 3
                for node in self.nodes:
                    z.append(node.coords)
            else:
                zdim = 2
                for node in self.nodes:
                    z.append(node.coords[0:2])

            mfm.dim = zdim
            mfm.lnn = 3
            mfm.lnv = 3
            mfm.lne = 3
            if mfm.dim == 2: # non se espera nrc porque dim == 2
                mfm.lnf = 1
            else:
                mfm.lnf = 0 # así non se espera nrc, porque non o escribe, pero con dim == 3 esperase


        if dimension == 3:
            zdim = 3
            for node in self.nodes:
                z.append(node.coords)

            mfm.dim = zdim
            mfm.lnn = 4
            mfm.lnv = 4
            mfm.lne = 6
            mfm.lnf = 4

        print 'dimension', dimension, '; zdim', zdim

        mfm.z = self.to_mfm_line_format(z)

        return mfm


def translate_mfm(origin, destiny):
    """Translates a .unv file to a .mfm file. Returns None if ok, else returns error string."""

    unv = UNV()
    error = unv.read(origin)
    if error is not None:
        return error

    print 'Converting to ' + destiny + ' ...'

    mfm = unv.to_mfm()

    if not isinstance(mfm, FileMrwModulef.FileMrwModulef):
        return "Error converting to .mfm: " + mfm
    
    result = mfm.save(destiny)
    if result is not True:
        return "Error saving .mfm file"

    print 'File converted'

    return None



def translate_vtk(origin, destiny):
    """Translates a .unv file to a .vtk/.vtu file. Returns None if ok, else returns error string."""
    
    unv = UNV()
    error = unv.read(origin)
    if error is not None:
        return error

    print 'Converting to ' + destiny + ' ...'

    name = "?"
    if destiny.endswith('.vtk'):
        vtk = unv.to_vtk()
        name = 'vtk'
    elif destiny.endswith('.vtu'):
        vtk = unv.to_vtu()
        name = 'vtu'
    else:
        return "Error: file extension not in (vtk, vtu)"

    if not isinstance(vtk, FileMrwVTK.FileMrwVTK):
        return "Error converting to ." + name + ": " + vtk

    # optional
    # warning
    res = vtk.check()
    if res is not True:
        print name+'.check():', res
        print 'Aborting'
        return "Error checking ."+name+" file data"
    
    result = vtk.save(destiny)
    
    if result is not True:
        return "Error saving ."+name+" file"

    print 'File converted'
    
    return None



if __name__=='__main__':
    """ Main program """

    args = len(sys.argv)

    if not (args == 3):
        print '\t converts UNV mesh to VTK, VTU or MFM mesh\n'
        print 'use: python FileMrwUNV.py origin.unv destiny.vtk\n'
        print 'use: python FileMrwUNV.py origin.unv destiny.vtu\n'
        print 'use: python FileMrwUNV.py origin.unv destiny.mfm\n'
        sys.exit(1)

    origin = sys.argv[1]
    destiny = sys.argv[2]

    if not origin.endswith('.unv'):
        print 'Error: Origin file must have .unv extension'
        sys.exit(1)

    if destiny.endswith('.vtk') or destiny.endswith('.vtu'):
        err = translate_vtk(origin, destiny)
        if err is not None:
            print 'Error translating:', err
    elif destiny.endswith('.mfm'):
        err = translate_mfm(origin, destiny)
        if err is not None:
            print 'Error translating:', err
    else:
        print 'Error: Destiny file must have .vtk, .vtu or .mfm extension'

