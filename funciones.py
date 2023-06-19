
_spreadsheets_recordados = { }
def leer_google_spreadsheet(doc_id : str, sheet_name : str = None) -> list :
    """Lectura de hoja en Google-Spreadsheet.
    
    Parámetros
    ----------
    doc_id : str
        Código identificador del documento en Google-Spreadsheet.
    sheet_name : str, opcional
        Nombre de la hoja a leer (si no se especifica se lee la 1ra hoja).

    Resultado
    -------
    list
        Una lista con todas las filas de la hoja seleccionada. Las filas son, a su vez, listas de strings.
    """

    if (doc_id, sheet_name) in _spreadsheets_recordados :
        (book_title, sheet_title, content) = _spreadsheets_recordados[(doc_id, sheet_name)]
        print('Se recordó el contenido de la hoja', sheet_title, 'de', book_title)
        return content

    from google.colab import auth
    auth.authenticate_user()
    import gspread
    from google.auth import default
    creds, _ = default()
    gc = gspread.authorize(creds)
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
