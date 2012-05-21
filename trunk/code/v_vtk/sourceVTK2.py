#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import FilePVD

    
def get_clon(o):

    # aqui para no importarlo siempre
    import vtk

    ugrid = vtk.vtkUnstructuredGrid()
    ugrid.SetPoints(o.GetPoints())
    ugrid.SetCells(o.GetCellTypesArray(), o.GetCellLocationsArray(), o.GetCells())
    
    return ugrid



def get_double_array():
    
    # aqui para no importarlo siempre
    import vtk

    return vtk.vtkDoubleArray()



def get_wrap(o):

    # aqui para no importarlo siempre
    import vtk

    src = vtk.vtkPassThrough()
    src.SetInput(o)
    return src    



def get_source(filename):

    print 'sourceVTK2: creating Reader for ', filename

    # aqui para no importarlo siempre
    import vtk
    
    filenameencoded = filename.encode(sys.getfilesystemencoding()) # necesario en Windows por lo menos

    if filename.lower().endswith('.pvd'):
	times = FilePVD.read(filename)
	type = 'pvd'
	src = [type,filenameencoded,times]
#	fileinitime = times[0].get('file')
#	filenameencoded = fileinitime.encode(sys.getfilesystemencoding())
#    	if fileinitime.lower().endswith('.vtk'):
#            type = 'vtk'
#            src = vtk.vtkUnstructuredGridReader()
#            src.ReadAllScalarsOn()
#            src.ReadAllVectorsOn()
#            src.SetFileName(filenameencoded)
#    	elif fileinitime.lower().endswith('.vtu'):
#            type = 'vtu'
#            src = vtk.vtkXMLUnstructuredGridReader()
#            src.SetFileName(filenameencoded)
    else:
	if filename.lower().endswith('.vtk'):
            type = 'vtk'
	    src = vtk.vtkUnstructuredGridReader()
            src.ReadAllScalarsOn()
            src.ReadAllVectorsOn()
            src.SetFileName(filenameencoded)
	elif filename.lower().endswith('.vtu'):
            type = 'vtu'
            src = vtk.vtkXMLUnstructuredGridReader()
            src.SetFileName(filenameencoded)
	else:
            return 'sourceVTK2: file extension of \''+filename+'\' not recognized'

	try:
	    src.Update()
	except Exception, x:
	    return 'sourceVTK2: unable to read '+ type +' file: \''+filename+'\': ' + repr(x)
    
    	unselect_source(src)

#    print 'prints'
#    prints(src)
    
    return src



def unselect_source(src):

    ou = src.GetOutput()
    pd = ou.GetPointData()
    cd = ou.GetCellData()
    pd.SetActiveVectors(None)
    cd.SetActiveVectors(None)
    pd.SetActiveScalars(None)
    cd.SetActiveScalars(None)


# en caso de len(sources) == 0:
#ERROR: In /build/buildd/vtk-5.2.1/Filtering/vtkDemandDrivenPipeline.cxx, line 725
#vtkStreamingDemandDrivenPipeline (0x8b02000): Input port 0 of algorithm vtkAppendFilter(0x8b01d60) has 0 connections but is not optional.

def get_append(sources):
    print 'sourceVTK2: creating Append'

    # aqui para no importarlo siempre
    import vtk
    
    src = vtk.vtkAppendFilter()
# A patch is needed for run MergePointsOff(). You can find the patch at:
# http://www.vtk.org/Bug/view.php?id=12460
#    if int(str.split(vtk.vtkVersion.GetVTKVersion())[0]) == 5:
#	if int(str.split(vtk.vtkVersion.GetVTKVersion())[1]) == 6:
#	    src.MergePointsOff()
    # comentado en favor doutro metodo
    #complement_missing_fields(sources) # #
    for s in sources:
        src.AddInputConnection(s.GetOutputPort())
    return src



def config_append(src, sources):
    print 'sourceVTK2: configuring Append'
    src.RemoveAllInputs()
    # comentado en favor doutro metodo
    #complement_missing_fields(sources) # #
    for s in sources:
        src.AddInputConnection(s.GetOutputPort())
    return src



def get_void():
    """ return an empty object suitable for representing """

    # aqui para no importarlo siempre
    import vtk

    u = vtk.vtkUnstructuredGrid()
    src = vtk.vtkPassThrough()
    src.SetInput(u)

    print 'void bounds', src.GetOutput().GetBounds() # 1 -1 1 -1 1 -1

    return src



def get_values(src, cell_point, name, discard=[]):
    """ returns string or list """

    out = src.GetOutput()

    if cell_point == 'cell':
        d = out.GetCellData()
    elif cell_point == 'point':
        d = out.GetPointData()
    else:
        return 'only cell or point data allowed'

    array = d.GetArray(name)
    #array = d.GetAbstractArray(name)
    
    if array is None:
        return 'field name \'' + name + '\' not found in ' + cell_point + 'data'
    
    size = array.GetNumberOfTuples()
    #print 'size', size
    comp = array.GetNumberOfComponents()
    #print 'comp', comp

    if comp != 1:
        return 'the number of components of \'' + name + '\' is not 1' # ou []

    v = set()

    for i in range(size):
        v.add(array.GetValue(i))
            
    if discard is not None:
        for d in discard:
            v.discard(d)

    l = sorted(v)
    
    return l



def printn(ds):
    pdp = ds.GetPointData()
    print 'point na', pdp.GetNumberOfArrays()
    for i in range(pdp.GetNumberOfArrays()):
        print 'name', i, pdp.GetArrayName(i), pdp.GetAbstractArray(i).GetNumberOfComponents()
    #print 'point nc', pdp.GetNumberOfComponents()
    pdc = ds.GetCellData()
    print 'cell na', pdc.GetNumberOfArrays()
    for i in range(pdc.GetNumberOfArrays()):
        print 'name', i,  pdc.GetArrayName(i), pdc.GetAbstractArray(i).GetNumberOfComponents()
    #print 'cell nc', pdc.GetNumberOfComponents()



def prints(src):
    printn(src.GetOutput())



# non permitidos nomes duplicados dentro de celldata (ou pointdata) de cada source
# non permitidos campos co mesmo nome e distinto numero de componentes en celldata (ou pointdata) do conxunto dos sources
def complement_missing_fields(sources):
    print 'Complementing'
    namesp = {}
    namesc = {}

    # ler todos os campos
    for s in sources:
        o = s.GetOutput()
        pd = o.GetPointData()
        cd = o.GetCellData()
        pdn = pd.GetNumberOfArrays()
        cdn = cd.GetNumberOfArrays()
        for i in range(pdn):
            name = pd.GetArrayName(i)
            namesp[name] = pd.GetAbstractArray(i).GetNumberOfComponents()
        for i in range(cdn):
            name = cd.GetArrayName(i)
            namesc[name] = cd.GetAbstractArray(i).GetNumberOfComponents()

    # completar os que faltan
    i = 0
    for s in sources:
        added = False
        namespl = {}
        namescl = {}

        o = s.GetOutput()
        pd = o.GetPointData()
        cd = o.GetCellData()
        pn = o.GetNumberOfPoints()
        cn = o.GetNumberOfCells()
        pdn = pd.GetNumberOfArrays()
        cdn = cd.GetNumberOfArrays()
        for i in range(pdn):
            name = pd.GetArrayName(i)
            namespl[name] = True
        for i in range(cdn):
            name = cd.GetArrayName(i)
            namescl[name] = True

        for n, c in namesp.items():
            if n not in namespl:
                add_missing_field(i, 'point', pd, pn, n, c)
                added = True

        for n, c in namesc.items():
            if n not in namescl:
                add_missing_field(i, 'cell', cd, cn, n, c)
                added = True

        if added: # necesario ?
            s.Update()

        i += 1


def add_missing_field(index, domain, data, number, name, components):

    # aqui para no importarlo siempre
    import vtk
    
    print 'Adding', index, domain, type(data), name, components
    #a = vtk.vtkBitArray()
    a = vtk.vtkDoubleArray()
    a.SetNumberOfComponents(components)
    a.SetNumberOfTuples(number)
    a.SetName(name)

    risco = True
    if risco: # quizais mais rápido
        l = components * number
        n = 0
        while n < l:
            a.SetValue(n,0.0)
            n += 1
    else: # quizais máis seguro
        t = 0
        while t < number:
            c = 0
            while c < components:
                a.SetComponent(t,c,0.0)
                c += 1
            t += 1
    # inicializar a cero ? DEBO [en vectores sobre todo]
    #a.Allocate(number, 1000) # 1000 ?
    # non deixa todo a 0 con bit

    data.AddArray(a)



# False not True yes None error
def has_field(src, field):
    if field is None:

        return True

    d = None

    if field.get('domain') == 'point':
        d = src.GetOutput().GetPointData()
    elif field.get('domain') == 'cell':
        d = src.GetOutput().GetCellData()

    if d is None:
        return None

    a = None
    
    if False:
        # ou iterar, para normalizar
        a = d.GetArray(field.get('name'))
    else:
        n = d.GetNumberOfArrays()
        for i in range(n):
            name = d.GetArrayName(i)
            if name == field.get('name'):
                a = d.GetAbstractArray(i)

    if a is None:
        return False
        
    c = a.GetNumberOfComponents()
    
    if field.get('components') is not None:
        if c.GetNumberOfComponents() != field.get('components'):
            return False



    return True

