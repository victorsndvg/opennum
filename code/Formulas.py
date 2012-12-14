#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import *
import string


# escalares
# vectores de 3 componentes

    # fn: field name
    # sv: scalar 0 vector 1
    # pc: point 0 cell 1

    # return: False: non calculado
    # return: None: xa estaba calculado
    # return: True: calculado
def calculate_field(src, fn, sv, pc, formula, extra):

        a = self.get_array(src, fn, sv, pc)

        if a is None:
            return False



def get_array(src, fn, sv, pc):
        if src is None or fn is None or sv is None or pc is None:
            return None
        if sv != 0 and sv != 1:
            return None
        if pc != 0 and pc != 1:
            return None

        if pc == 0:
            t = src.GetPointData()
        elif pc == 1:
            t = src.GetCellData()

        if sv == 0:
            r = t.GetScalars()
        elif sv == 1:
            r = t.GetVectors()

        return r

def real(var):
	return var.real

def imag(var):
	return var.imag

def create_lambda(formula, variables):

        #make a list of safe functions
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', \
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10', \
                     'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
        #use the list to filter the local namespace
#        safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        #use the list to filter the global namespace
        safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ])
        #add any needed builtins back in.
        safe_dict['abs'] = abs
        safe_dict['int'] = int
        safe_dict['float'] = float
        safe_dict['complex'] = complex
        safe_dict['imag'] = imag
        safe_dict['real'] = real

        func = 'lambda ' + ','.join(variables) + ': ' + formula

        globales = safe_dict
        globales["__builtins__"] = None

        try:
            lam = eval(func, globales)
#            lam = eval(func, {"__builtins__":None}, safe_dict)
#            lam = eval(func)
        except Exception, e:
            return unicode(e)

        return lam



def exec_lambda(function, arguments):

        try:
            res = function(*arguments) # calcula funcion
        except Exception, e:
            return unicode(e)
        return res



def split_b(text, limit):
        parts = []
        i = 0
        temp = ''
        while i < len(text):
            c = text[i]
            if c == '\\':
                if i + 1 < len(text):
                    if text[i+1] == limit:
                        temp += text[i+1]
                    else:
                        temp += text[i] + text[i+1]
                    i += 2
                    continue
                else:
                    print u'missing char after escape char \'\\\'' # might be error
                    i += 1
                    continue
            elif c == limit:
                parts.append(temp)
                temp = ''
            else:
                temp += c
            i = i + 1
        parts.append(temp)
        return parts



def check_b(varname):
        if len(varname) < 1:
            return False
        if varname[0] not in string.ascii_letters and varname[0] != '_':
            return False
        for l in varname[1:]:
            if l not in string.ascii_letters and l not in string.digits and l != '_':
                return False
        reserved = ['and','del','from','not','while',
            'as','elif','global','or','with',
            'assert','else','if','pass','yield',
            'break','except','import','print',
            'class','exec','in','raise',
            'continue','finally','is','return',
            'def','for','lambda','try']
        if varname in reserved:
            return False
        return True



# formula="a+b*c+d;a=../tal/cual;b=.;c=10.0;d=/Outro/alto" c=10.0 non permitido ? ex:nodo con número de elemento e campo (cal coller? prioridade? escolla?)
# ou "c=field:../tal" "c=value:../tal" "c=data:10.0"
# ; -> separa partes
# \; -> ;
def extract_parts(text):
        proc1 = split_b(text, ';') # ten en conta "\;" e tradúceos a ";"
        if len(proc1) < 1:
            return "Missing formula"
        if len(proc1[0]) < 1:
            return "Empty formula"
        formula = proc1[0]
        variables = []
        for i in range(1,len(proc1)):
            proc2 = split_b(proc1[i], '=') # ten en conta "\=" e tradúceos a "="
            if len(proc2) != 2:
                return "Variable number " + unicode(i) + " invalid. Only one '=' symbol allowed"
            name = proc2[0]
            typepath = split_b(proc2[1],':')
            if len(typepath) != 2:
                return "Variable number " + unicode(i) + " (" + name + ") invalid. Must include 'menu:'"
                # or 'field:' or 'value:' or 'data:'" # quitar3ultimos
            type_ = typepath[0]
            if type_ != 'menu': # and type_ != 'field' and type_ != 'value' and type_ != 'data': # quitar3ultimos
                return "Variable number " + unicode(i) + " (" + name + ") invalid. Must include 'menu:'"
                # or 'field:' or 'value:' or 'data:'" # quitar3ultimos
            path = typepath[1]
            if not check_b(name): # invalid python name
                return "'" + name + "' is not a valid variable name"
            variables.append([name,type_,path])
        return (formula, variables)




