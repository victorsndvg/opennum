#!/usr/bin/env python
# -*- coding: utf-8 -*-



class Source():


    # funciona de momento
    # non so interpreta escapes de '/' '\/' -> interpretaos todos
    #'' -> ['']
    #'a' -> ['a']
    #'/' -> ['','']
    #'/a/' -> ['','a','']
    #'a/a' -> ['a','a']
    # 'a\/a' -> ['a/a']
    # '.' -> [1]
    # '..' -> [2]
    # '...' -> [3]
    # '\.' -> ['.']
    # '\.\.' -> ['..']
    # entrada: sen procesar
    # saida: procesado. '\/' sempre. outros nunca
    @staticmethod
    def parse_simple_path(path):
        partes_sp = []
        partes_np = []
        parte_sp = '' # '\' si procesados: ex: 'ab/c/../\'
        parte_np = '' # '\' non procesados: ex: 'ab\/c/\.\./\\'
        i = 0
        while i < len(path):
            c = path[i]
            if c == '\\':
                if i + 1 < len(path):
                    parte_sp += path[i+1]
                    parte_np += path[i] + path[i+1]
                    i += 2
                    continue
                else:
                    return u'missing char after escape char \'\\\''
            if c == '/':
                # codigo repe linhas abaixo
                if parte_np == '.': # nodo actual
                    partes_np.append(1)
                    partes_sp.append(1)
                elif parte_np == '..': # nodo superior
                    partes_np.append(2)
                    partes_sp.append(2)
                elif parte_np == '...': # nome actual
                    partes_np.append(3)
                    partes_sp.append(3)
                else:
                    partes_np.append(parte_np)
                    partes_sp.append(parte_sp)
                parte_sp = ''
                parte_np = ''
            else:
                parte_sp += path[i]
                parte_np += path[i]

            i += 1

        # codigo repe linhas arriba
        if parte_np == '.': # nodo actual
            partes_np.append(1)
            partes_sp.append(1)
        elif parte_np == '..': # nodo superior
            partes_np.append(2)
            partes_sp.append(2)
        elif parte_np == '...': # nome actual
            partes_np.append(3)
            partes_sp.append(3)
        else:
            partes_np.append(parte_np)
            partes_sp.append(parte_sp)

        return partes_sp



    # admite 0 o 1 variable
    # prefijo
    # variable
    # sufijo    
    # entrada: sen procesar
    # saida: sen procesar. eliminados '$()' que estaban sen escapar
    @staticmethod
    def extract_var(path):
        strings = ['',None,'']
        # prefix variable suffix
        i = 0
        mode = 0
        while i < len(path):
            c = path[i]
            if c == '\\':
                if i + 1 < len(path):
                    strings[mode] += c
                    strings[mode] += path[i + 1]
                    i += 2
                    continue
                else:
                    return u'missing char after escape char \'\\\''

            elif c == '$':
                if i + 1 < len(path):
                    if path[i + 1] == '{':
                        if mode == 0:
                            mode = 1
                            strings[1] = ''
                            i += 2
                            continue
                        else:
                            return u'only one variable allowed: \'${...}\'. extra \'${\''

            elif c == '}':
                if mode == 1:
                    mode = 2
                    i += 1
                    continue
                elif mode == 2:
                    return u'extra \'}\''
                elif mode == 0:
                    return u'misplaced \'}\''

            strings[mode] += c
            i += 1
            
        if mode == 1:
            return u'missing \'}\''

        return strings



    @staticmethod
    def escape(string):
        result = ''
        for c in string:
            if c=='\\' or c == '.' or c == '$' or c == '{' or c == '}':
                result += '\\'
            result += c
        return result



    @staticmethod
    def desescape(string):
        result = ''
        i = 0
        while i < len(string):
            if string[i] == '\\':
                if (i + 1) < len(string):
                    result += string[i+1]
                    i += 2
                else:
                    pass # error '\' al final
            else:
                result += string[i]
                i += 1
        return result



    # admite calquera numero de variables aniñadas ou non
    # non retorna cadeas baleiras, retorna listas (baleiras ou non)
    # cada variable é devolta como unha lista
    # cada cacho de camiño é devolto como unha cadea
    @staticmethod
    def extract_vars(path, start=0, inside=False):
        result = []
        current = ''
        i = start
        next = len(path)
        closed = False
        while i < len(path):
            c = path[i]
            if c == '\\':
                if i + 1 < len(path):
                    current += c
                    current += path[i + 1]
                    i += 2
                    continue
                else:
                    return u'missing char after escape char \'\\\''
            if c == '$':
                if i + 1 < len(path):
                    if path[i + 1] == '{':
                        if len(current) > 0:
                            result.append(current)
                        current = ''
                        temp = Source.extract_vars(path, i + 2, True)
                        if isinstance(temp, basestring):
                            return temp
                        i = temp[1]
                        result.append(temp[0])
                        continue
                    else:
                        return u'extra \'$\''
#            if c == '{':
#                pass
            if c == '}':
                closed = True
                if not inside:
                    return u'extra \'}\''
                else:
                    next = i + 1
                    break

            current += c
            i += 1

        if inside and not closed:
            return u'missing \'}\''

        if len(current) > 0:
            result.append(current)

        return (result, next)

