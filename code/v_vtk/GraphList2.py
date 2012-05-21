#!/usr/bin/env python
# -*- coding: utf-8 -*-



import os.path



def absolutize(input):
    output = []
    for a in input:
        output.append(os.path.abspath(a))
    return tuple(output)



class GraphList2:



    def __init__(self):
        self.num = 0

        self.nodes = {}
        self.datas = {}
        
        self.views = {} # num -> view



    def get(self, node, filenames, fieldname, typename, extra=None):

        res = self.get_from_node(node)
        
        if res is not None:
            return res
            
        return self.get_from_data(filenames, fieldname, typename, extra)



    def get_from_node(self, node):

        if node in self.nodes:
            num = self.nodes[node]
            if num in self.views:
                return self.views[num]
                
        return None



    def get_from_data(self, filenames, fieldname, typename, extra=None):

        if filenames is not None:
            filenames = absolutize(filenames)

        tpl = (filenames, fieldname, typename, extra)
        
        if tpl in self.datas:
            num = self.datas[tpl]
            if num in self.views:
                return self.views[num]

        return None



    def add(self, node, view, filenames, fieldname, typename, extra=None):
    
        self.nodes[node] = self.num

        if filenames is not None:
            filenames = absolutize(filenames)

        tpl = (filenames, fieldname, typename, extra)
        
        self.datas[tpl] = self.num
        
        self.views[self.num] = view

        self.num += 1



    def rem_view(self, view):

        toerase = []
        
        for k,v in self.views.iteritems():
            if v is view:
                toerase.append(k)
                
        for k in toerase:
            del self.views[k]



    def rem_views(self):
    
        self.views.clear()

        self.nodes.clear()
        self.datas.clear()
