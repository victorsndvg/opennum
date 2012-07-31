#!/usr/bin/env python
# -*- coding: utf-8 -*-



import trees
import config
import NoDeep
import os.path
import Source # para procesar cadenas fuente mesh=...
import Formulas as psps # para postproceso



class Node():

    def __init__(self):
        self.children = []
        self.attribs = {}
        self.tag = u'-'
        self.parent = NoDeep.NoDeep(None)

        # supoño que os defaults, que son deepcopy'ed, non teñen nada nestes atributos.
        # se o tivesen, habería que protexelos con NoDeep
        self.data = {} # custom data
        self.dependencies = {} # nodeep
        self.influences = {} # nodeep



    def get_data(self):
        return self.data



    # merges two Node
    # necesitase chamar a self.set_children_parents() despois
    # now replaces children
    def combine(self, node):
        #self.children.extend(node.children)
        self.children = node.children[:]
        for a in node.attribs:
            self.attribs[a] = node.attribs[a]



# true <=> there is a place to create a plot
    def plot_able(self):
        return (self.tag == u'struct' or self.tag == u'leaf') and \
            self.get_attribs().get(config.PLOTTED) != config.VALUE_TRUE and \
            ( self.get_attribs().get(config.PLOT) is not None ) # cambiado de PLOT_TYPE a PLOT


# true <=> there is a plot indicated
    def plot_has(self):
        return (self.tag == u'struct' or self.tag == u'leaf') and \
            self.get_attribs().get(config.PLOTTED) == config.VALUE_TRUE and \
            ( self.get_attribs().get(config.PLOT) is not None ) # cambiado de PLOT_TYPE a PLOT



# returns next struct that has a plot or None
    def plot_next_has(self):
        this = self.get_parent()
        while this is not None:
            if this.plot_has():
                return this
            this = this.get_parent()
        return None



# applies function to all plots. self is last
    def apply_to_all_plots(self, func):
        temp = self.plot_next_has()
        while temp is not None:
            func(temp)
            temp = temp.plot_next_has()
        if self.plot_has():
            func(self)



# applies function to parent plots.
    def apply_to_parent_plots(self, func):
        temp = self.plot_next_has()
        while temp is not None:
            func(temp)
            temp = temp.plot_next_has()



    def add_parameters(self, data):
        for child in self.get_children():
            child.add_parameters(data)



    def get_parent(self):
        return self.parent.geti()



    def set_parent(self, parent):
        self.parent.seti(parent)



    def set_children_parents(self):
        for child in self.children:
            child.set_parent(self)
            child.set_children_parents()



    def get_path(self, sep=u'/', root=False):
        path = []
        this = self
        while this is not None:
            path.append(this.get_name())
            this = this.get_parent()
        if not root and len(path)>0:
            del path[-1]
        path.reverse()
        return sep + sep.join(path)



    def get_top(self):
        last = self
        top = self
        while top is not None:
            last = top
            top = top.get_parent()
        return last



    def get_first_attrib(self, name):
        this = self
        while this is not None:
            value = this.get_attribs().get(name)
            if value is not None:
                return value
            this = this.get_parent()
        return None



    def del_childs_by_name(self, name):
        index = len(self.children) - 1
        while index>=0:
            if self.children[index].get_name() == name:
                del self.children[index]
            index -= 1



    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)



    def add_child_start(self, child):
        child.set_parent(self)
        self.children.insert(0,child)



    def del_child(self, index):
        del self.children[index]



    def del_children(self):
        del self.children[:]



    def get_children(self):
        return self.children



    def get_to_source(self):
        result = []
        for child in self.get_children():
            result.append(child.get_name())
        return result


    # obtiene un conjunto razonable de valores, exigiendo o no que estén seleccionados
    def get_to_source_if_sel_if(self):
        # código parejo en Widget.py
        selection = self.get_attribs().get('selection')

        sel = False

        if self.tag == 'struct':
            sel = selection == 'single'
        elif self.tag == 'leaf':
            type = self.get_attribs().get('type')
            if type == "charlist" and self.get_attribs().get(u'showfile') is None:
                sel = True

        result = []
        for child in self.get_children():
            if not sel or child.get_attribs().get(config.AT_SELECTED):
                result.append(child.get_name())
        return result



    # leaf type = file, folder # leaf with source => not selected elements missing
    def get_first_name(self):
        if self.get_tag() != 'leaf': # isinstance requires import
            print 'Warning: called get_first_name() not on a Leaf'
        ch = self.get_children()
        if len(ch)>0:
            return ch[0].get_name()
        else:
            return ''

    # leaf type = file, folder # leaf with source => not selected elements missing
    def get_first_selected_name(self):
        if self.get_tag() != 'leaf': # isinstance requires import
            print 'Warning: called get_first_name() not on a Leaf'
        ch = self.get_children()
        if len(ch)>0:
	    for child in ch:
		if (child.get_attribs().get(u'selected')==u'true'):
		    return child.get_name()
        else:
            return None



    # para saber se hai que mostar algo á esquerda
    def has_source(self):
        return self.attribs.get(config.AT_SOURCE) is not None or \
            self.attribs.get(config.AT_SHOWVALUES) == config.VALUE_TRUE



    def get_attribs(self):
        return self.attribs



    def get_name(self):
        name = self.attribs.get(u'name')
        if name is not None:
            return name
        else:
            return u'-'

    def get_title(self):
        title = self.attribs.get(u'title')
        if title is not None:
            return title
        else:
            return u'-'



    def set_name(self, name):
        self.get_attribs()[u"name"]=name


    def set_title(self, title):						#añadido
        self.get_attribs()[u"title"]=title				#añadido



    def get_tag(self):
        return self.tag



    def is_hidden(self):
        return self.get_attribs().get(config.AT_HIDDEN) == config.VALUE_TRUE



    def load(self, item):
        self.tag = item.tag
        self.attribs = item.attrib.copy() # dictionary with attributes: name="...", selected="...", ...
        #print self.get_attribs()


    @staticmethod
    def filter_attribs(old):
        valid = set()
        valid.add(u'name')
        valid.add(u'type')
        valid.add(u'subtype')
        valid.add(u'totalnum')
        new = {}
        for attrib in old:
            if attrib in valid:
                # .copy()
                new[attrib] = old[attrib]
        return new

        
        #############



    def get_name_for_mesh(self):
        mesh_name = self.attribs.get(config.PLOT_MESH_NAME)
        if mesh_name is None:
            # old behaviour
            #return self.get_name()
            ch = self.get_children()
            if len(ch) == 0:
                return '(empty)'
            elif len(ch) > 1:
                return '(overflow)'
            else:
                return ch[0].get_name()

        parsed = self.parse_source_string_1(mesh_name)
        if parsed[0] is None:
            print u'Error parsing "mesh_name" source string in Node.get_name_for_mesh'
        elif parsed[0] == 0: # data
            return parsed[1]
        elif parsed[0] == 2: # menu
            res = self.parse_path_varx(parsed[1],True,False)
            if isinstance(res, basestring):
                print u'Error parsing "mesh_name" "menu:": ' + res
            elif len(res) != 1:
                print u'Error: "mesh_name": len != 1'
            else:
                return res[0]
        else:
            print u'"mesh_name" attribute only allows "data:" and "menu:" prefixes'
            
        return "!" # None causa erros



    def get_data5(self, pointers=False):

        result = {'filenames':[],'filesmesh':[],'filenames_mn':[],'filesmesh_mn':[],'filenames_for':[]}
        
        # default value
        result['fieldtype'] = 'scalar' # vector

        mesh = self.get_attribs().get(config.PLOT_MESH)
        add_mesh = self.get_attribs().get(config.PLOT_ADD_MESH)
        point = self.get_attribs().get(config.PLOT_POINT_DATA)
        cell = self.get_attribs().get(config.PLOT_CELL_DATA)
        data = self.get_attribs().get(config.PLOT_DATA)
        formula = self.get_attribs().get(config.PLOT_FORMULA) # pointers?

        evolution = self.get_attribs().get(config.PLOT_EVOLUTION)
        if evolution is None:
            result['evolution'] = 'Time'
            result['evolution_lower'] = 'time'
            result['evolution_upper'] = 'Time'
        else: # mellorable loxica de maiuscula/minuscula
            result['evolution'] = evolution
            evu = evolution
            if len(evolution) > 0:
                evu = evu[0].lower() + evu[1:]
            result['evolution_lower'] = evu
            evu = evolution
            if len(evolution) > 0:
                evu = evu[0].upper() + evu[1:]
            result['evolution_upper'] = evu

        interpolation = self.get_attribs().get(config.PLOT_INTERPOLATION)
        result['interpolation'] = interpolation != config.VALUE_FALSE

        # esto podría sobrar: dim en el mismo elemento del gráfico, frente a en el leaf file
        #dim1 = self.get_attribs().get(config.AT_DIM)
        #if dim1 is not None:
        #    try:
        #        result['dim'] = int(dim1)
        #    except ValueError:
        #        return 'Incorrect dimension: ' + dim1

        # whether computes dependences or not
        if pointers:
            objects = []
        else:
            objects = None

        field = None
        if point is not None:
            result['fielddomain'] = 'point'
            field = point
        if cell is not None:
            result['fielddomain'] = 'cell'
            field = cell

        if point is not None and cell is not None:
            return u'Both "celldata" and "pointdata" attributes present'
        
        if data is not None and (mesh is not None or add_mesh is not None or point is not None or cell is not None):
            return u'"data" attribute is incompatible with "mesh","add_mesh","pointdata","celldata"'
        if data is not None and formula is not None:
            return u'"data" attribute is incompatible with "formula" attribute'
#        if (mesh is not None or add_mesh is not None or point is not None or cell is not None) and formula is not None: # ou compatible con point/cell para indicar o tipo de datos
#            return u'"mesh","add_mesh","pointdata","celldata" attributes are incompatible with "formula" attribute'
        if (mesh is not None or add_mesh is not None) and formula is not None:
            return u'"mesh","add_mesh" attributes are incompatible with "formula" attribute'
        if data is None and mesh is None and formula is None:
            return u'Missing "mesh" or "data" or "formula" attributes'


        if formula is not None:
            fv = psps.extract_parts(formula)
            if isinstance(fv, basestring):
                return 'Error in formula: ' + fv
            result['formula_text'] = fv[0]
            result['formula_vars'] = fv[1]
            result['formula_data'] = []
            result['formula_is'] = True
            # encher recursivamente outras
            for i in xrange(len(result['formula_vars'])):
                var = result['formula_vars'][i]
                name = var[0]
                type_ = var[1]
                path = var[2]

                # extra
                if type_ == 'menu': # or type_ == 'field' or type_ == 'value':

                    # sen variables
                    #node = self.get_node_from_path(path) # ou outra funcion que permita o uso de variables
                    #if isinstance(node, basestring): # error
                    #    return "Invalid path: " + node
                    #if node is None: # invalid node
                    #    return "Invalid path: " + path

                    # con variables (por se acaso, xa que so admite un nodo)
                    nodes = self.parse_path_varx(path, True, False, objects, True, None) # objects duplicados abaixo ?
                    print 'parse_path_varx.objects', map(Node.get_path, objects)
                    if isinstance(nodes, basestring): # error
                        return "Invalid path: " + nodes
                    if nodes is None: # invalid node
                        return "Invalid path: " + path
                    if len(nodes) != 1:
                        return "Invalid number of referenced nodes: " + unicode(len(nodes))
                    node = nodes[0]

                else:
                    node = None
                var.append(node) # 3

                type2 = None
                if type_ == 'menu':
                    if node.get_attribs().get(config.PLOT_MESH) is not None or \
                        node.get_attribs().get(config.PLOT_FORMULA) is not None: # se ten grafico
                        type2 = 'menu-field'
                    elif node.get_tag() == 'leaf' and node.get_attribs().get(config.AT_TYPE) == 'float': # se e un leaf float
                        type2 = 'menu-value'
                    else:
                        return 'Type of node unknown'
                else:
                    type2 = type_
                var.append(type2) # 4

                if type2 == 'menu-field':
                    res = node.get_data5(pointers)
                    if isinstance(res, basestring):
                        return 'Error in dependence of formula: ' + res
                    if objects is not None:
                        objects.extend(res.get('dependencies')) # objects duplicados arriba ?
                        print 'subdata.dependencies', map(Node.get_path,res.get('dependencies'))

                    if res.get('fielddomain') != result.get('fielddomain'):
                        return 'Mismatched field domains: ' + unicode(result.get('fielddomain')) + ' and ' + unicode(res.get('fielddomain'))
                    result['formula_data'].append(res)
                    result['filenames_for'].extend(res.get('filenames'))
                    result['filenames'].extend(res.get('filenames'))
                elif type2 == 'menu-value':
                    if objects is not None:
                        objects.append(node)
                    result['formula_data'].append(None)
                elif type2 == 'data': # non permitido este caso
                    result['formula_data'].append(None)
                else:
                    result['formula_data'].append(None)


        if mesh is not None: # >=0
            mesh_names = []
            # type, string
            parsed = self.parse_source_string_1(mesh)
            if parsed[0] is None:
                return u'Error parsing "mesh" source string'
            elif parsed[0] == 1: # file
                res = self.parse_path_varx(parsed[1],False,False,objects,mesh_names=mesh_names)
            elif parsed[0] == 2: # menu
                res = self.parse_path_varx(parsed[1],True,True,objects,mesh_names=mesh_names)
            else:
                return u'"mesh" attribute only allows "file:" and "menu:" prefixes'

            if isinstance(res, basestring):
                return res

            result['filesmesh1'] = res
            result['filesmesh'].extend(res)
            result['filenames'].extend(res) # mesh files are always first files
            result['filesmesh1_mn'] = mesh_names
            result['filesmesh_mn'].extend(mesh_names)
            result['filenames_mn'].extend(mesh_names)


        if add_mesh is not None: # >=0
            mesh_names = []
            # type, string
            parsed = self.parse_source_string_1(add_mesh)                
            if parsed[0] is None:
                return u'Error parsing "add_mesh" source string'
            elif parsed[0] == 1: # file
                res = self.parse_path_varx(parsed[1],False,False,objects,mesh_names=mesh_names)
            elif parsed[0] == 2: # menu
                res = self.parse_path_varx(parsed[1],True,True,objects,mesh_names=mesh_names)
            else:
                return u'"add_mesh" attribute only allows "file:" and "menu:" prefixes'

            if isinstance(res, basestring):
                return res

            result['filesmesh2'] = res
            result['filesmesh'].extend(res)
            result['filenames'].extend(res) # add_mesh files are always second files
            result['filesmesh2_mn'] = mesh_names
            result['filesmesh_mn'].extend(mesh_names)
            result['filenames_mn'].extend(mesh_names)


        if field is not None: # solo 1
            mesh_names = []
            tupf = self.parse_source_string_2(field, objects, mesh_names=mesh_names)
            if tupf[0] is None:
                return u'Error parsing "' + result.get('fielddomain') + 'data" source string'
            if tupf[0] != 0 and tupf[0] != 1 and tupf[0] != 2:
                return u'"celldata" and "pointdata" attributes only allow "data:", "file:" and "menu:" prefixes'
            if tupf[2] is not None and result.get('dim') is None:
                result['dim'] = tupf[2]
            if tupf[0] == 1 or tupf[0] == 2:
                result['filenames'].append(tupf[1]) # field, if present, is last file
                result['filesfield'] = [tupf[1]]
                result['filenames_mn'].extend(mesh_names)
                result['filesfield_mn'] = mesh_names

                # en caso de fichero de campo: poner campo = nombre de fichero
                # o bien: poner nombre fijo
                
                temp = os.path.basename(tupf[1])
                
                i = temp.rfind('.')
                if i <= 0: # correcto <= en vez de <, porque: para '.mff' proporciona '.mff', no ''
                    temp2 = temp
                else:
                    temp2 = temp[:i]

                result['fieldname'] = temp2.replace(' ','_')

            elif tupf[0] == 0:
                result['fieldname'] = tupf[1]

        if data is not None: # test.gr2 por exemplo # solo 1
            # type, string, dim(int or None)
            tupm = self.parse_source_string_2(data, objects)
            if tupm[0] is None:
                return u'Error parsing "data" source string'
            if tupm[0] != 1 and tupm[0] != 2:
                return u'"data" attribute only allows "file:" and "menu:" prefixes'

            result['filesdata'] = [tupm[1]]
            result['filenames'].append(tupm[1])

        print 'DEBUG: get_data5.filenames: ', result['filenames']

        if objects is not None:
            print 'start pointers for', self.get_path()
            # un plot pode ter varios structs !!!
            #clear ?
            #self.set_dependencies(objects, True)
            for o in objects:
                print ':', o.get_path()
            print 'end pointers', 'total', len(objects)
            
        result['dependencies'] = objects
        
        return result







    def get_tracker5(self, filemanager, predata=None):
	#para multiples pvds is_nodepvd = True
	is_nodepvd = False                                             #añadido

        if predata is not None:
            data = predata
        else:
            data = self.get_data5()

        if isinstance(data, basestring):
            return data

        tracker = None
        
        filenames = data.get('filenames')
        meshfilenames = data.get('filesmesh') # todas
        mesh1filenames = data.get('filesmesh1') # principales
        mesh2filenames = data.get('filesmesh2') # secundarias
        fieldfilenames = data.get('filesfield')
        datafilenames = data.get('filesdata')
        numfilenames = len(filenames)

        fm_mn = data.get('filesmesh_mn') # nomes de mallas
        ff_mn = data.get('filesfield_mn') # nomes de campos

        fortext = data.get('formula_text')
        forvars = data.get('formula_vars')
        if fortext is not None and forvars is not None:
            tracker = filemanager.get_tracker_formula(self, fortext, forvars, data)
            tracker.set_data(fortext, forvars, data)
#            if isinstance(res, basestring):
#                return u'Error processing formula: ' + res
            return tracker

        if numfilenames == 0:
            return filemanager.get_tracker_void()
            #return 'No filenames present'

        if datafilenames is not None:
            if len(datafilenames) == 1:
                return filemanager.get_tracker_file(datafilenames[0]) # data
            elif len(datafilenames) > 1:
                return u'Only one data file allowed'


        fieldfilename = None
        if fieldfilenames is not None:
            if len(fieldfilenames) == 1:
                fieldfilename = fieldfilenames[0]
            elif len(fieldfilenames) > 1:
                return u'Only one field file allowed'


        if meshfilenames is None:
            return filemanager.get_tracker_void()
            #return u'No mesh files'
        elif len(meshfilenames) == 0:
            return filemanager.get_tracker_void()
            #return u'No mesh files'
        #elif mesh1filenames is None or len(mesh1filenames) == 0:
        #    # restriccion artificial: >=1. necesitaria de modificar algun tracker
        #    return u'No main file'
        #    # this ?
        elif len(meshfilenames) == 1:
            if fieldfilename is None  or not fieldfilename.lower().endswith('.mff'):
                if meshfilenames[0] == '':
                    return 'Empty mesh file name'
                tracker = filemanager.get_tracker_mesh_file(meshfilenames[0])
                if tracker is None:
                    return 'Unsupported filename extension of file \'' + meshfilenames[0] + '\''
                else:
                    tracker.set_size1(len(mesh1filenames))
                    if fm_mn is not None and len(fm_mn) == 1:
                        tracker.set_name(fm_mn[0])
                    return tracker
            else:
                if meshfilenames[0].lower().endswith('.mfm') and fieldfilename.lower().endswith('.mff'):
                    tracker = filemanager.get_tracker_mfm_mff_files(meshfilenames[0], fieldfilename, \
                        {'dim':data.get('dim'), 'fieldname':data.get('fieldname'), \
                        'fielddomain':data.get('fielddomain'), 'fieldtype':data.get('fieldtype')})
                    tracker.set_size1(len(mesh1filenames))
                    if fm_mn is not None and ff_mn is not None and len(fm_mn) == 1 and len(ff_mn) == 1:
                        tracker.set_name(fm_mn[0]+' + '+ff_mn[0])
                    return tracker
                else:
                    if meshfilenames[0] == '':
                        return 'Empty mesh file name'
                    if fieldfilename == '':
                        return 'Empty field file name'
                    return u'Unsupported filename extensions for mesh and field ('+ \
                        meshfilenames[0]+' , '+fieldfilename+'): Allowed .mfm and .mff'
        else:
            trackers = []
            if fieldfilename is None  or not fieldfilename.lower().endswith('.mff'):
                # crea trackers para todos los ficheros
                i = 0
		#comprobacion de trackernodefile de pvd
		if meshfilenames[0].lower().endswith('.pvd'):			#añadido
		    is_nodepvd = True						#añadido
                for meshfile in meshfilenames:
                    if meshfile == '':
                        return 'Empty mesh file name'
                    trackertemp = filemanager.get_tracker_mesh_file(meshfile)
                    if trackertemp is None:
                        return 'Unsupported filename extension of file \'' + meshfile + '\''
                        
                    if fm_mn is not None and len(fm_mn) > i:
                        trackertemp.set_name(fm_mn[i])
		    #Si trackernodefiles de pvd inicializamos los trackervtk para obtener tiempos
		    if is_nodepvd:						#añadido
			trackertemp.recalculate()				#añadido


                    trackers.append(trackertemp)

                    i += 1
            else:
                # anhade el mismo campo a todas las mallas
                i = 0
                for meshfile in meshfilenames:
                    if meshfile.lower().endswith('.mfm') and fieldfilename.lower().endswith('.mff'):
                        trackertemp = filemanager.get_tracker_mfm_mff_files(meshfile, fieldfilename, \
                            {'dim':data.get('dim'), 'fieldname':data.get('fieldname'), \
                            'fielddomain':data.get('fielddomain'), 'fieldtype':data.get('fieldtype')})
                            
                        if fm_mn is not None and ff_mn is not None and len(fm_mn) > i and len(ff_mn) == 1:
                            trackertemp.set_name(fm_mn[i]+' + '+ff_mn[0])

                        trackers.append(trackertemp)
                    else:
                        if meshfile == '':
                            return 'Empty mesh file name'
                        if fieldfilename == '':
                            return 'Empty field file name'
                        return u'Unsupported filename extensions for mesh and field ('+ \
                            meshfile+' , '+fieldfilename+'): Allowed .mfm and .mff'
                    i += 1
            
            tracker = filemanager.get_tracker_node_files(self, is_nodepvd)		#añadido
            
            tracker.set_trackers(trackers, len(mesh1filenames)) # lonxitude do grupo 1 / grupo 2
            # que non cambie o tracker sempre por esto,
            # que se chama veces e veces
            # si polos cambios dos trackers
            


        return tracker








    # return ( type[None,0,1,2] , data/file/menu )
    @staticmethod
    def parse_source_string_1(source):
        ret = (None,'')
        if source is None:
            return ret
        i = source.find(':')
        if i < 0:
            return ret
        pre = source[:i]
        post = source[i+1:]
        if pre == u'data':
            pretype = 0
        elif pre == u'file':
            pretype = 1
        elif pre == u'menu':
            pretype = 2
        else:
            return ret
        return (pretype, post)



    # return ( type[None,0,1,2] , data/file , dim )
    def parse_source_string_2(self, source, objects=None, mesh_names=None):
        ret = (None,'',None)
        if source is None:
            return ret
        i = source.find(':')
        if i < 0:
            return ret
        pre = source[:i]
        post = source[i+1:]
        file = post
        dim = None
        if pre == u'data':
            pretype = 0
        elif pre == u'file':
            pretype = 1
            if mesh_names is not None:
                mesh_names.append(os.path.basename(file))
        elif pre == u'menu':
            pretype = 2
        else:
            return ret

        if pretype == 2:
            node = self.get_node_from_path(post)
            if isinstance(node, basestring):
                return ret
            else:
                # filename
                file = node.get_first_selected_name()
		if file is None:
		    file = node.get_first_name()

                if objects is not None: # punteiros
                    objects.append(node)

                # filenamedim
                dimstr = node.get_attribs().get(u'dim')
                if dimstr is not None:
                    try:
                        dim = int(dimstr)
                    except ValueError:
                        print u'Error: dim: \''+dimstr+'\'\n'
                        
                if mesh_names is not None:
                    mesh_names.append(node.get_name_for_mesh())

        return (pretype, file, dim)



    #nova
    # for_leaf_file: colle o primeiro valor se o hai e se non, ''
    # !for_leaf_file: colle todos os valores
    def get_from_path(self, path, for_leaf_file=False, objects=None, for_node=False):
        temp = Source.Source.parse_simple_path(path) # avalia escapes \x
        if not isinstance(temp,list):
            return 'Parsing path: \'' + temp + '\''
        node = self.get_node_from_segments(temp)
        if node is None:
            return u'Path not found: \'' + path + '\''
        else:
            if for_node:
                if objects is not None:
                    objects.append(node) # anhado nodo a lista de dependencias # repetido
                return ([node], None, [node])

            # pidese o nome do elemento actual ou ben os dous seus fillos ?
            get_name = len(temp)>0 and temp[-1] == 3 # 3:"..."
            dim = node.get_attribs().get('dim')
            if get_name:
                array = [node.get_name()]
            else:
                if for_leaf_file:
                    # para leaf type=file, retorna 'nombre' o '' en caso de no tener fichero
                    array = [node.get_first_name()]
                else:
                    # para otros nodos, retorna lista de hijos: [] ... ['a'] ... ['a','b'] ...
                    #array = node.get_to_source()
                    # lista de hijos: todos o solo seleccionados, segun proceda
                    array = node.get_to_source_if_sel_if()

                if objects is not None:
                    objects.append(node) # anhado nodo a lista de dependencias # repetido
                    
            return ( array, {'dim':dim}, [node] )



# nova
# source string nova
# path = []
# file_ou_menu
# distinguese FILE de MESH
# falta fallar se non ten elementos, como coller sempre '' para ficheiros -> feito
# como só se emprega para "mesh='...'", sempre serán nomes de ficheiros, excepto variables interiores
# for_node => is_menu
# en for_node pode devolver varios nodos !!! sempre lista
# len mesh_names must be equal to len return_value
    def parse_path_var(self, path, is_menu, for_leaf_file=False, objects=None, for_node=False, mesh_names=None):
        # is_menu: true: buscar en el menu (menu:) ; false: para construir un nombre de fichero (file:)
        # for_leaf_file: especial para cando precisa nomes de ficheiro,
        #   o resultado final e unha lista de ficheiros obtidos de leaf_file
        # for_node: devolve listas de nodos en vez de listas de cadeas => debese usar con is_menu True
        parts = Source.Source.extract_var(path)
        if isinstance(parts,list):
            if parts[1] is None: # no hay variables
                if not is_menu:
                    txt = Source.Source.desescape(parts[0])
                    if mesh_names is not None:
                        mesh_names.append(os.path.basename(txt)) # ou self.get_name_for_mesh()
                    return [txt]
                array = self.get_from_path(parts[0], for_leaf_file, objects, for_node) #
                if isinstance(array, tuple):
                    if mesh_names is not None:
                        mesh_names.extend(map(Node.get_name_for_mesh, array[2]))
                    return array[0] # list
                else:
                    return 'Error parsing \''+parts[0]+'\': ' + array
            else: # hay una variable
                array = self.get_from_path(parts[1], False, objects, False) #
                if isinstance(array, tuple):
                    total = []
                    for a in array[0]:
                        # escapar 'a' que proven dun nome e vai ser desescapada
                        if is_menu:
                            aesc = Source.Source.escape(a)
                            str = parts[0] + aesc + parts[2]
                            array2 = self.get_from_path(str, for_leaf_file, objects, for_node)
                            if isinstance(array2, tuple):
                                if mesh_names is not None:
                                    mesh_names.extend(map(Node.get_name_for_mesh, array2[2]))
                                total.extend(array2[0])
                            else:
                                return 'Error parsing \'' + str + '\': ' + array2
                        else:
                            txt = Source.Source.desescape(parts[0]) + a + Source.Source.desescape(parts[2])
                            total.append(txt)
                            if mesh_names is not None: # ou self.get_name_for_mesh()
                                mesh_names.append(os.path.basename(txt))
                    return total
                else:
                    return 'Error in variable \''+parts[1]+'\': '+ array
        else:
            return 'Error extracting variable from \''+path+'\': ' + parts



# switch para escoller parser antigo (só unha variable) ou novo (variables ilimitadas)
# posteriormente comentar/eliminar: ret1, parse_path_var
# mesh_names acumula chamando os dous
    def parse_path_varx(self, path, is_menu, for_leaf_file=False, objects=None, for_node=False, mesh_names=None):
#        ret1 = self.parse_path_var(path, is_menu, for_leaf_file, objects, for_node, mesh_names)
        ret2 = self.parse_path_vars(path, is_menu, for_leaf_file, objects, for_node, mesh_names)
#        print 'var1/2:', path, ret1, ret2
        return ret2



# adaptacion de parse_path_var para varias variables. tera que ser compatible coa version anterior...
    def parse_path_vars(self, path, is_menu, for_leaf_file=False, objects=None, for_node=False, mesh_names=None):

        temp = Source.Source.extract_vars(path)
        
        if isinstance(temp, tuple):
            tree = temp[0]
        else:
            return 'Error extracting variables from \'' + path + '\': ' + temp

        if isinstance(tree, list):
            strings = self.parse_inner_vars(tree, objects, False)
            if not isinstance(strings, list):
                return 'Error parsing variables: ' + strings # non se dá o caso

            result = []

            if is_menu:
                for string in strings:
                    one = self.get_from_path(string, for_leaf_file, objects, for_node)
                    if isinstance(one, tuple):
                        result.extend(one[0])
                        if mesh_names is not None:
                            mesh_names.extend(map(Node.get_name_for_mesh, one[2]))
                    else: # se non existe non ten por que dar erro, so descarta
                        pass
            else:
                for string in strings:
                    txt = Source.Source.desescape(string)
                    result.append(txt)
                    if mesh_names is not None: # ou self.get_name_for_mesh()
                        mesh_names.append(os.path.basename(txt))

            return result

        else:

            return 'Error extracting variables from \'' + path + '\': '



# parsea niveles (opcionalmente inferiores) da arbore de variables.
    def parse_inner_vars(self, tree, objects=None, process=True):
        strings = None
        for element in tree:
            if isinstance(element, list):
                morestrings = self.parse_inner_vars(element, objects)
                if isinstance(morestrings, basestring):
                    return morestrings
                if strings is None:
                    strings = morestrings
                else:
                    newstrings = []
                    for i in xrange(len(strings)):
                        for j in xrange(len(morestrings)):
                            newstrings.append(strings[i] + morestrings[j])
                    strings = newstrings
            else:
                if strings is None:
                    strings = [element]
                else:
                    for i in xrange(len(strings)):
                        strings[i] += element

        if strings is None:
            strings = []

        if process:
            result = []
            for string in strings:
                one = self.get_from_path(string, False, objects, False)
                if isinstance(one, tuple):
                    for a in one[0]: # escapar 'a' que proven dun nome e vai ser desescapada
                        aesc = Source.Source.escape(a)
                        result.append(aesc)
                else: # se non existe non ten por que dar erro, so descarta
                    pass
#                   return 'Error in variable \'' + string + '\': ' + one
            return result
        else:
            return strings



# novo
# segments de Sources.Sources.parse_simple_path(path)
# 1 e 2 e 3 para '.' e '..' e '...'
# entrada: procesados (sen '\')
    def get_node_from_segments(self, segments):
        this = self

        l = len(segments)

        if l < 1: # non posible
            return this

        if l == 1 and segments[0] == '': # inicialmente cadea baleira
            return this

        if segments[0] == '': # empeza por barra
            this = self.get_top()
            ri = 1
        else:
            ri = 0

        if l > 0 and segments[-1] == '': # para admitir '/', '/lugar/', '/a/b/c/'
            rf = l-1 # acababa en barra => non influe
        else:
            rf = l # non acababa en barra => non influe

        rango = range(ri,rf)

        for index in rango:
            if segments[index] == 1: # .
                continue
            if segments[index] == 2: # ..
                this = this.get_parent()
                continue
            if segments[index] == 3: # ...
                continue
            children = this.get_children()
            name = segments[index]
            match = None
            for a in children:
                if a.get_name()==name:
                    match = a
                    break
            if match is not None:
                this = match
            else:
                this = None
                break
        return this



    # returns: string or node
    def get_node_from_path(self, path):
        temp = Source.Source.parse_simple_path(path) # avalia escapes \x
        if not isinstance(temp,list):
            return 'Parsing path: \'' + temp + '\''
        node = self.get_node_from_segments(temp)
        if node is None:
            return u'Path not found: \'' + path + '\''
        return node



    # def get_source_menus(self, path):
        # menus = self.get_top()
        # node = menus.get_node_from_path(path)
        # if node is None:
            # return 'Path \'' + path + '\' not found'
        # return node.get_to_source()



    def get_source_showvalues(self):

        # mesh="..." ( pointdata="data:..." | celldata="data:..." ) showvalues="true"
        showvalues = self.get_attribs().get(config.AT_SHOWVALUES)
        if showvalues != config.VALUE_TRUE:
            return 'Error: missing \'source="..."\' or \'showvalues="true"\''

        data = self.get_data5()
        
        if isinstance(data, basestring):
            return data
        
        print 'data', data
        
        field = data.get('fieldname')
        
        if field is None:
            return 'Error: No field specified for \'showvalues="true"\''
        
        # text
        window = self.get_top().get_window()
        filemanager = window.filemanager
        cb = AuxCall(window)
        callback = cb.call
        callbacks = cb.calls
        
        callbacks(u'Reading references from mesh file ...\n')

        tracker = self.get_tracker5(filemanager, data)

        print 'tracker.node', tracker
        
        if isinstance(tracker, basestring):
            return tracker

        result = tracker.update()

        if result is None:
            callbacks(u'References: error\n')
            return 'Error reading references from mesh file'

        refs = tracker.get_refs()

        # si no se obtuvieron las referencias al convertir de mfm o unv a vtk,
        # obtenerlas posteriormente del vtkUnstructuredGridReader o vtkXMLUnstructuredGridReader
        if refs is None:
            callbacks(u'References: Read VTK\n')

            fielddata = {}
            fielddata['name'] = field
            fielddata['domain'] = data.get('fielddomain')

            # obtiene solo los principales (no adicionales) que tengan campo. para: TrackerNodeFiles y otros
            src = tracker.get_src_group_f(1, fielddata)

            # obtiene solo los principales (no adicionales) para: TrackerNodeFiles
            #src = tracker.get_src_group(1)

            if src is None: # xa nunca entra: nunca devolve None. pode devolver un UnstructuredGrid baleiro
                return 'Error reading references: no main meshes found'
            if isinstance(src, basestring): # temp
                return 'Error reading references: ' + src
            from v_vtk import sourceVTK2
            rs = sourceVTK2.get_values(src, data.get('fielddomain'), field, [0]) # cache able in tracker
            if not isinstance(rs,list):
                return 'Error calculating references: ' + rs
            return map(str, rs)
        else:
            if result is True:
                callbacks(u'References: Read\n')
            elif result is False:
                callbacks(u'References: Cached\n')

        if refs is None or field not in refs or refs.get(field) is None:
            res = 'Error reading references: source field \'' + field + '\' does not exist'
        else:
            res = refs.get(field)

        return res



# if node has_source() call
    def get_source_all(self):
    
        # source = "data:..." "menu:..."
        source = self.get_attribs().get(config.AT_SOURCE)
        if source is not None:
            parsed = self.parse_source_string_1(source) #### rewrite to not go to other nodes (?)
            if parsed[0] is None:
                return u'Can not parse "source" string value'
	    #parsed[0] == 1 => type == file: list file lines
            elif parsed[0] == 1:				#añadido
		sourcefile = open(parsed[1])			#añadido
		source = []					#añadido
		try:						#añadido
		    line = sourcefile.readline()		#añadido
		    while line:					#añadido
			line = line.strip('\n')	.strip()		#añadido
			source.append(line)			#añadido
			line = sourcefile.readline()		#añadido
		finally:					#añadido
	    	    sourcefile.close()				#añadido
		return source
	    elif parsed[0] != 2:
                return u'Can not parse "source" string value: only allows "menu:" and "file:" prefix'
            source_path = parsed[1]
            
            #novo 1
            # necesario con variables y paths relativos
            # para obtener lista de materiales del tipo especificado en otro leaf
            return self.parse_path_varx(source_path,True,False)
            
            #vello 1
            #return self.get_source_menus(source_path)

        return self.get_source_showvalues()



    # es llamada desde otros sitios
    # menus no usado aqui
    def get_remote_source(self, menus):
        res = self.get_source_all()
        if isinstance(res, basestring):
            return 'Error obtaining references: ' + res
        return res



# dependencies, influences
    
    # primario
    def set_dependencies(self, objects, deep=False):
        self.dependencies = {}
        if objects is None:
            return
        for o in objects:
            self.dependencies[id(o)] = o
            if deep:
                o.add_influence(self)

    # secundario
    def add_dependencies(self, objects, deep=False):
        if objects is None:
            return
        for o in objects:
            self.dependencies[id(o)] = o
            if deep:
                o.add_influence(self)

    def clear_dependencies(self, deep=False):
        if deep:
            for key, value in self.dependencies.items():
                value.remove_influence(self)
        self.dependencies = {}


    def add_influence(self, i):
        self.influences[id(i)] = i

    def is_dependency(self, o):
        return self.dependencies.get(id(o)) is o

    def remove_influence(self, value):
        if id(value) in self.influences:
            del self.influences[id(value)]

    def call_influences(self, func):
        for key, value in self.influences.items():
            if value.is_dependency(self):
                func(value, self) # actualiza grafico

    def has_influences(self):
        for key, value in self.influences.items():
            if value.is_dependency(self):
                return True
        return False
# / dependencies, influences



class AuxCall():
    def __init__(self, window):
        self.window = window

    def call(self, text):
        if self.window is not None:
            self.window.add_text(text)
            self.window.process_pending()

    def calls(self, text):
        if self.window is not None:
            self.window.add_text(text)

