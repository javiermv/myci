
_spreadsheets_recordados = { }
def leer_google_spreadsheet(doc_id : str, sheet_name : str = None, forget_previous : bool = False) -> list :
    """Lectura de hoja en Google-Spreadsheet.
    
    Parámetros
    ----------
    doc_id : str
        Código identificador del documento en Google-Spreadsheet.
    sheet_name : str, opcional
        Nombre de la hoja a leer (si no se especifica se lee la 1ra hoja).
    forget_previous : bool, opcional
        Deshabilita el 'recuerdo' de una lectura previa, si existe.

    Resultado
    -------
    list
        Una lista con todas las filas de la hoja seleccionada. Las filas son, a su vez, listas de strings.
    """

    if not forget_previous and (doc_id, sheet_name) in _spreadsheets_recordados :
        (book_title, sheet_title, content) = _spreadsheets_recordados[(doc_id, sheet_name)]
        print('Se recordó el contenido de la hoja', sheet_title, 'de', book_title)
        return content

    from google.colab import auth
    auth.authenticate_user()
    import gspread
    from google.auth import default
    creds, _ = default()
    gc = gspread.authorize(creds)
    # ver https://docs.gspread.org/en/v5.7.0/user-guide.html#opening-a-spreadsheet
    workbook = gc.open_by_key(doc_id)
    sheet = workbook.sheet1
    if sheet_name != None :
        sheet = workbook.worksheet(sheet_name)
    result = sheet.get_all_values() # devuelve una lista de filas

    # Saltea filas llenas de celdas vacías o solo con el elem 'a'.
    result = [ row for row in result
            if not all(elem == '' or elem == 'a' for elem in row)
        ]

    _spreadsheets_recordados[(doc_id, sheet_name)] = (workbook.title, sheet.title, result)
    print('Se leyó la hoja', sheet.title, 'de', workbook.title)
    return result
############################################################
def guardar_dict_en_google_spreadsheet(sheets : dict, doc_id : str) :
    """
    param sheets: las claves son los nombres de las hojas; los valores son listas de filas.
    """
    import gspread
    from google.auth import default
    creds, _ = default()
    gc = gspread.authorize(creds)
    # ver https://docs.gspread.org/en/v5.7.0/user-guide.html#opening-a-spreadsheet
    workbook = gc.open_by_key(doc_id)
    for name, rows in sheets.items() :
        sheet = workbook.sheet1 if name == None else workbook.worksheet(name)
        sheet.update(rows)
        print('Se escribieron', len(rows), 'filas en la hoja', sheet.title, 'de', workbook.title)
        _spreadsheets_recordados[(doc_id, name)] = (workbook.title, sheet.title, rows)
    return

# Más adelante, esta función podría reutilizar la de arriba
def guardar_list_en_google_spreadsheet(rows : list, doc_id : str, sheet_name = None) :
    import gspread
    from google.auth import default
    creds, _ = default()
    gc = gspread.authorize(creds)
    # ver https://docs.gspread.org/en/v5.7.0/user-guide.html#opening-a-spreadsheet
    workbook = gc.open_by_key(doc_id)
    sheet = workbook.sheet1
    if sheet_name != None :
        sheet = workbook.worksheet(sheet_name)

    sheet.update(rows)
    print('Se escribieron', len(rows), 'filas en la hoja', sheet.title, 'de', workbook.title)
    _spreadsheets_recordados[(doc_id, sheet_name)] = (workbook.title, sheet.title, rows)
    return

############################################################
def leer_requerimientos() -> dict:
    """ Lectura de la planilla de Requerimientos de inscripción.

    Resultado
    -------
    dict: pasaporte -> Solicitud
        Si bien los datos se leen de la planilla de Requerimientos, la estructura se toma de las Solicitudes.
        
        Solicitud es dict {
                'Correo' : str, 
                'Nombre' : str, 
                'Elecciones' : [ Eleccion ]
            }
        Eleccion es dict, con claves
            [ 'Escuela', 'Codigo', 'Materia', 'Horario', 'Prioridad' ]
        siempre asociadas a str.
    """
    # # from https://stackoverflow.com/a/423596
    # # You can use a global variable within functions by declaring it as `global`
    # global requerimientos

    # # from https://stackoverflow.com/a/843293
    # # To check the existence of a local variable:
    # # if 'myVar' in locals(): ...
    # # To check the existence of a global variable:
    # # if 'myVar' in globals(): ...

    requerimientos = leer_google_spreadsheet(id_requerimientos_de_inscripcion)

    index = { }
    for i, column in enumerate(requerimientos[0]) : # encabezado
        index[column] = i
    #print(index) # {'Correo': 0, 'Nombre': 1, 'Pasaporte': 2, 'Escuela': 3, 'Codigo': 4, 'Materia': 5, 'Horario': 6, 'Prioridad': 7}

    result = { }
    for row in requerimientos[1:] : # saltea encabezado
        pasaporte = row[index['Pasaporte']]
        if not pasaporte in result :
            result[pasaporte] = {
                    'Correo' : row[index['Correo']], 
                    'Nombre' : row[index['Nombre']], 
                    'Elecciones' : [ ]
                }
        eleccion = { }
        atributos = ['Escuela', 'Codigo', 'Materia', 'Horario', 'Prioridad']
        for it in atributos :
            eleccion[it] = row[index[it]]
        
        result[pasaporte]['Elecciones'].append(eleccion)

    key = list(result.keys())[0] # primer elemento
    print('Ejemplo: requerimientos[' + key + ']:', result[key])
    return result
############################################################
def leer_ordenes_SIU3() -> dict :
    """ Leer planilla SIU3 de las Órdenes de inscripción.
    
    Resultado
    ---------
    dict :
        clave pasaporte
        valor [ orden ]
    """
    ordenes_SIU3 = leer_google_spreadsheet(id_ordenes_de_inscripcion, 'SIU3')
    result = { }
    encabezado = ordenes_SIU3[0]
    atributos_eleccion = ['Escuela', 'Codigo', 'Materia', 'Horario', 'Prioridad', 'Decisión']
    for row in ordenes_SIU3[1:] : # saltea encabezado
        orden = { }
        #print('row', row)
        for attr in atributos_eleccion :
            orden[attr] = row[encabezado.index(attr)]

        # TODO: decidir a qué se llama 'orden' y a qué 'eleccion'. Quizás
        # convenga unificar los nombres.

        #print('orden:', orden)
        # ('Escuela', 'Escuela de Humanidades')
        # ('Codigo', 'MA-FC00254')
        # ('Materia', 'Filosofía de la cultura')
        # ('Horario', 'lunes noche')
        # ('Prioridad', 'principal')

        # TODO: definir cómo se llama y cómo se asocia al resto:
        # ('Estado', 'Inscripto')
        # ('Observaciones', '')
        # Problemas:
        # - No se están leyendo los 'Estados' de las Ordenes SIU2
        # - SIU2 no tiene del todo definidos los Estados
        # PROVISORIO...
        # Se agrega
        # Por ahora, la generación de Ordenes no está definiendo el Estado, por
        # lo que row['Estado'] devuelve Index-out-of-bound.
        idx_estado = encabezado.index('Estado')
        estado = row[idx_estado] if idx_estado < len(row) else ''
        orden['Estado'] = estado

        pasaporte = row[encabezado.index('Pasaporte')]
        # OJO que 'pasaporte' puede ser banana si...
        #   orden: {'Escuela': '', 'Codigo': '', 'Materia': 'a', 'Horario': '', 'Prioridad': ''}
        # NOTAR la 'a' en Materia

        if estado == '' :
            print('¡CUIDADO! En la planilla SIU3, el Estado vacío ("") se asume ' +
                  "'Inscripto' para el pasaporte", pasaporte, "en la orden", orden)

        if not pasaporte in result :
            result[pasaporte] = [ ]
        result[pasaporte].append(orden)
    return result
############################################################
def leer_ordenes_SIU2(sheet_name : str) -> dict :
    ordenes_SIU2 = leer_google_spreadsheet(id_ordenes_de_inscripcion, sheet_name)
    # atributos_eleccion = ['Escuela', 'Codigo', 'Materia', 'Horario', 'Prioridad'] # SIU3
    # atributos_eleccion = ['Materia', 'Horario', 'Prioridad'] # SIU2 original
    atributos_eleccion = ['Materia', 'Horario', 'Prioridad', 'Estado'] # SIU2 emparchado
    result = convertir_en_dict(ordenes_SIU2, 'Pasaporte', atributos_eleccion)
    return result
############################################################
def convertir_en_dict(rows : list, key_name : str, cols : list) -> dict :
    result = { }
    encabezado = rows[0]
    for row in rows[1:] : # saltea encabezado
        value = { }
        #print('row', row)
        for col in cols :
            value[col] = row[encabezado.index(col)]

        key = row[encabezado.index(key_name)]
        # OJO que key o value pueden ser banana en filas con celdas vacías.

        if not key in result :
            result[key] = [ ]
        result[key].append(value)
    return result
############################################################
_encabezado_incoming_recordado = None
def leer_encabezado_incoming() -> list :
    global _encabezado_incoming_recordado
    if _encabezado_incoming_recordado == None :
        # al leer incoming se define el encabezado recordado
        leer_listado_incoming()
    return _encabezado_incoming_recordado

_listado_incoming_recordado = None
def leer_listado_incoming(reportar_sin_pasaporte : bool = True) -> dict :
    """ Lectura de `incoming/listado.php`.

    Resultado
    ---------
    dict: pasaporte -> Persona

        Persona es dict, con claves [
            'Fecha', 'Apellido', 'Nombre', 'Nacionalidad', 'Carrera', 
            'Universidad', 'Pais', 'Email', 'Email Alternativo', 'Periodo', 
            'Anio', 'Sexo', 'Pasaporte', 'Fecha Nacimiento', 'E-Mail Responsable'
        ]
        siempre asociadas a str, aunque no siempre están todas presentes.

    Pendiente
    ---------
        * Definir cómo procesar a las personas sin pasaporte.
    """

    # from https://stackoverflow.com/a/423596
    # You can use a global variable within functions by declaring it as `global`
    global _listado_incoming_recordado
    if _listado_incoming_recordado != None :
        print('Se recordó incoming/listado.php.')
        return _listado_incoming_recordado

#    require = "!pip install xmltodict"

    from xml.dom import minidom
    import requests
    import xmltodict

    # en listado.php falta:
    #   - <! DOCTYPE html>
    #   - La codificación de caracteres del documento no fue declarada
    url = "http://www.unsam.edu.ar/internacional/incoming/listado.php"
    response = requests.get(url) # TARDA
    #print('encoding', response.apparent_encoding) # encoding Windows-1252

    # FALLAN MISERABLEMENTE
    #dom = minidom.parseString(str)
    #data = xmltodict.parse(response.content, encoding='Windows-1252')

    # Correcciones necesarias para poder parsear
    str = response.content.decode('Windows-1252')
    str = str.replace("border=1", "border='1'") # entrecomillado del atributo
    str = str.replace("&", "&")             # encoding del '&'.
    #print(str)
    # dom = minidom.parseString(str)
    # print(dom)
    # #dom.getElementsByTagName("tr")[0]
    # print(dom.getElementsByTagName("tr")) # tr: table-row
    # for elem in dom.getElementsByTagName("tr") : # tr: table-row # FUNCIONA
    #     elem.getElementsByTagName...

    dict = xmltodict.parse(str)
    # print('dict-224', dict) # {'table': {'@border': '1', 'tr': [{'td': 
    #       ['Fecha', 'Apellido', 'Nombre', 'Nacionalidad', 'Carrera', 'Universidad', 'Pais', 'Email', 'Email Alternativo', 'Periodo', 'Anio', 'Sexo', 'Pasaporte', 'Fecha Nacimiento', 'E-Mail Responsable']}, 
    #   {'td': [None, 'López', 'Cecilia', 'Argentina', 'Psicopedagogía', 'Free Mover', 'Argentina', 'snielson@unsam.edu.ar', 'snielson@unsam.edu.ar', None, None, None, None, None, None]}, , ...}]}}
    dict = dict['table']['tr'] # lista de {'td': [valores]}
    encabezado = dict.pop(0)['td'] # ['Fecha', 'Apellido', 'Nombre', 'Nacionalidad', 'Carrera', 'Universidad', 'Pais', 'Email', 'Email Alternativo', 'Periodo', 'Anio', 'Sexo', 'Pasaporte', 'Fecha Nacimiento', 'E-Mail Responsable']
    # index_pasaporte = encabezado.index('Pasaporte')
    global _encabezado_incoming_recordado
    _encabezado_incoming_recordado = encabezado
    # print('encabezado', encabezado)
    #print(dict)
    #  {'td': [None, 'López', 'Cecilia', 'Argentina', 'Psicopedagogía', 'Free Mover', 'Argentina', 'snielson@unsam.edu.ar', 'snielson@unsam.edu.ar', None, None, None, None, None, None]}, {'td': [None, 'Rodríguez Sánchez', 'Adrián Gerardo', 'Mexicana', 'Posgrado en Historiografía', 'Free Mover', 'Argentina', 'adrian.geros@gmail.com', 'adrian.geros@gmail.com', None, None, None, None, None, None]}, ...]}]
    #index_pasaporte = encabezado.index('Pasaporte')

    # Diccionario Pasaporte -> Persona
    result = { }

    for row in dict :
        #values = row['td']     #[None, 'López', 'Cecilia', 'Argentina', 'Psicopedagogía', 'Free Mover', 'Argentina', 'snielson@unsam.edu.ar', 'snielson@unsam.edu.ar', None, None, None, None, None, None]
        #pasaporte = tr['td'][index_pasaporte]
        persona = { }
        for index, value in enumerate(row['td']) :
            if value != None : # saltea valores de celdas vacías
                persona[encabezado[index]] = value
            # si no hay pasaporte, ¿usamos 'Email'?
            #if index == index_pasaporte and value == None and reportar_sin_pasaporte:
            #    print("Esta persona no tiene definido el pasaporte: ", persona)
        if 'Pasaporte' in persona :
            pasaporte = persona.pop('Pasaporte')
            result[pasaporte] = persona
        elif reportar_sin_pasaporte :
            print("Esta persona no tiene definido el pasaporte: ", persona)

    _listado_incoming_recordado = result    
    print('Leído:', url)
    # print("La variable 'incoming' es un diccionario Pasaporte -> DatosPersonales.")
    # print('Las claves del diccionario DatosPersonales son: ', encabezado)
    # print('Por ejemplo: "incoming[1234] == { Apellido : Messi, Nombre : Lionel, Pais : Argentina }".')

    return result

############################################################
    
def find_changes(new_row, old_row) -> dict :
    """busca las diferencias entre dos versiones de una fila
    
    Resultado
    ---------
    dict: 
    clave posición donde difieren las filas [i]
    Valor es una dupla viejo valor y nuevo valor para fila [i]
    """
    if len(new_row) > len(old_row):
        raise ValueError("Se asume que la vieja fila puede tener más columnas pero no menos.")

    result = {} # dict vacio
    for i in range(len(new_row)):
        if new_row[i] != old_row[i]:
            result[i] = (old_row[i], new_row[i])

    return result # si todos son iguales devuelve un dict vacio sino te da info combinada de los cambios en cada posición

def explain_changes(header:list, changes:dict) -> list :
    """genera una explicación a partir de los cambios detectados en find_change
    
    Resultado
    ---------
    Cada elemento indica el encabezado de la posición del cambio y muestra el valor viejo y el nuevo
    
    """
    result = []
    for i, change in changes.items() :
        result.append(header[i] + ': ' + change[0] + ' -> ' + change[1])
    return result
