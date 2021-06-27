import sqlite3

def crear_base(nombre_base=False, nombre_tabla=False, formato=False):
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            print(f"Err: {err}")
        else:
            print("Se ha creado la base.")
            cursor = conn.cursor()
            if nombre_tabla:
                if formato:
                    try:
                        cursor.execute(f"CREATE TABLE IF NOT EXISTS {nombre_tabla}({formato});")
                    except sqlite3.OperationalError as err:
                        print(f"Err: {err}")
                    else:
                        conn.commit()
                        print("Se ha creado la tabla.")
            conn.close()

def retornar_esquema(nombre_base=False, nombre_tabla=False):
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            print(f"Err: {err}")
        else:
            if nombre_tabla:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                valores = cursor.fetchall()
                conn.close()
                return valores
            conn.close()

def retornar_datos(nombre_base=False, nombre_tabla=False):
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            print(f"Err: {err}")
        else:
            cursor = conn.cursor()
            if nombre_tabla:
                cursor.execute(f"SELECT * FROM {nombre_tabla}")
                valores = cursor.fetchall()
                conn.close()
                return valores
            conn.close()

def insertar_dict(nombre_base=False, nombre_tabla=False, diccionario=False):
    """Ingresa valores insertos en un diccionario, según su tipo hace una sola operación, o varias para ingresar múltiples valores. 
    
    Retorna True o False dependiendo de si la operación fue exitosa, o no."""
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            print(f"Err: {err}")
        else:
            cursor = conn.cursor()
            if nombre_tabla:
                if diccionario:
                    if all(isinstance(diccionario[key], (tuple, list, set, dict)) for key in diccionario.keys()):
                        if all(len(diccionario[key]) > 1 for key in diccionario.keys()):
                            if all(len(diccionario[key]) == len(diccionario[list(diccionario.keys())[0]]) for key in diccionario.keys()):
                                for i in range(0, len(diccionario[list(diccionario.keys())[0]])):
                                    valores = [diccionario[key][i] for key in diccionario.keys()]
                                    try:
                                        cursor.execute(f"""INSERT INTO {nombre_tabla}({', '.join(str(x) for x in [key for key in diccionario.keys()])}) 
                                                        VALUES ({str('?, '*len(diccionario.keys()))[:-2]})""", valores)
                                    except sqlite3.OperationalError as err:
                                        print(f"Error en la carga del diccionario: {err}")
                                        return False
                                    else:
                                        print(f"{valores} subido a la base.")
                                        conn.commit()
                                return True
                            else:
                                print("Uno o más campos están vacíos o tienen un número diferente de valores. No se puede completar la subida de datos a la base.")
                                return False

                        else:
                            if all(len(diccionario[key]) == 1 for key in diccionario.keys()):
                                valores = [diccionario[key][0] for key in diccionario.keys()]
                                try:
                                    cursor.execute(f"""INSERT INTO {nombre_tabla}({', '.join(str(x) for x in [key for key in diccionario.keys()])}) 
                                                    VALUES ({str('?, '*len(diccionario.keys()))[:-2]})""", valores)
                                except sqlite3.OperationalError as err:
                                    print(f"Err: {err}")
                                    return False
                                else:
                                    print(f"{valores} subido a la base.")
                                    conn.commit()
                                    return True
                            else:
                                print("Uno o más campos están vacíos o tienen un número diferente de valores. No se puede completar la subida de datos a la base.")
                                return False

                    elif all(isinstance(diccionario[key], (str,int,float,bool)) for key in diccionario.keys()):
                        valores = [diccionario[key] for key in diccionario.keys()]
                        try:
                            cursor.execute(f"""INSERT INTO {nombre_tabla}({', '.join(str(x) for x in [key for key in diccionario.keys()])}) 
                                            VALUES ({str('?, '*len(diccionario.keys()))[:-2]})""", valores)
                        except sqlite3.OperationalError as err:
                            print(f"Err: {err}")
                            return False
                        else:
                            print(f"{valores} subido a la base.")
                            conn.commit()
                            return True

                    else:
                        if any(diccionario[key] == None for key in diccionario.keys()):
                            valores = [diccionario[key] for key in diccionario.keys()]
                            try:
                                cursor.execute(f"""INSERT INTO {nombre_tabla}({', '.join(str(x) for x in [key for key in diccionario.keys()])}) 
                                                VALUES ({str('?, '*len(diccionario.keys()))[:-2]})""", valores)
                            except sqlite3.OperationalError as err:
                                print(f"Err: {err}")
                                return False
                            except sqlite3.IntegrityError as err:
                                print(f"El campo '{str(err).split('.')[-1]}' no puede estar vacío.")
                                return False
                            else:
                                print(f"{valores} subido a la base.")
                                conn.commit()
                                return True
                        print("Error. Ha introducido un tipo de dato no reconocido, o colecciones junto a no colecciones.")
                        return False

            conn.close()


def borrar_datos(nombre_base=False, nombre_tabla=False, campo_referencia=False, valores=False):
    """Elimina datos de la tabla según valores de un campo determinado, indicados previamente."""
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            print(f"Err: {err}")
        else:
            cursor = conn.cursor()
            if nombre_tabla:
                if campo_referencia:
                    if valores:
                        if isinstance(valores, (str, int, float, bool)):
                            valores = [valores]
                            try:
                                cursor.execute(f"SELECT * FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valores)
                            except sqlite3.OperationalError as err:
                                print(f"Err: {err}")
                            else:
                                nro_entradas = len(cursor.fetchall())
                                if nro_entradas > 0:
                                    try:
                                        cursor.execute(f"DELETE FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valores)
                                    except sqlite3.OperationalError as err:
                                        print(f"Err: {err}")
                                    else:
                                        print(f"{nro_entradas} entradas eliminadas con éxito.")
                                        conn.commit()
                                else:
                                    print("No hay entradas con ese valor.")
                        elif isinstance(valores, (tuple, list, set)):
                            for valor in valores:
                                print(f"Valor: {valor}")
                                valor = [valor]
                                try:
                                    cursor.execute(f"SELECT * FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valor)
                                except sqlite3.OperationalError as err:
                                    print(f"Err: {err}")
                                else:
                                    nro_entradas = len(cursor.fetchall())
                                if nro_entradas > 0:
                                    try:
                                        cursor.execute(f"DELETE FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valor)
                                    except sqlite3.OperationalError as err:
                                        print(f"Err: {err}")
                                    else:
                                        print(f"{nro_entradas} entradas eliminadas con éxito.")
                                        conn.commit()
                                else:
                                    print("No hay entradas con ese valor.")
                        else:
                            print("error.")
            conn.close()

def traer_datos(nombre_base=False, nombre_tabla=False, campo_referencia=False, valores=False):
    """Selecciona los datos que coinciden con los valores proporcionados según un campo de referencia dado, y los retorna."""
    if nombre_base:
        try:
            conn = sqlite3.connect(nombre_base)
        except sqlite3.OperationalError as err:
            return f"Err: {err}"
        else:
            cursor = conn.cursor()
            if nombre_tabla:
                if campo_referencia:
                    if valores:
                        if isinstance(valores, (str, int, float, bool)):
                            valores = [valores]
                            try:
                                cursor.execute(f"SELECT * FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valores)
                            except sqlite3.OperationalError as err:
                                conn.close()
                                return f"Err: {err}"
                            else:
                                valores_final = cursor.fetchall()
                                conn.close()
                                return valores_final
                        elif isinstance(valores, (tuple, list, set)):
                            valores_final = []
                            for valor in valores:
                                valor = [valor]
                                try:
                                    cursor.execute(f"SELECT * FROM {nombre_tabla} WHERE {campo_referencia} = (?)", valor)
                                except sqlite3.OperationalError as err:
                                    conn.close()
                                    return f"Err: {err}"
                                else:
                                    valores_final.append(cursor.fetchall())
                            conn.close()
                            return valores_final
                        else:
                            conn.close()
                            return "Error. Ha introducido un tipo de dato no reconocido."
            conn.close()

def retornar_datos_segun_tiempo(nombre_base=False, nombre_tabla=False):
    if nombre_base:
        if nombre_tabla:
            try:
                conn = sqlite3.connect(nombre_base)
            except sqlite3.OperationalError as err:
                return f"Err: {err}"
            else:
                cursor = conn.cursor()
                try:
                    cursor.execute(f"""WITH ranked_messages AS (
  SELECT m.*, ROW_NUMBER() OVER (PARTITION BY nombre ORDER BY id DESC) AS rn
  FROM {nombre_tabla} AS m
)
SELECT id, url, nombre, precio, año, kilometros, fecha_consulta FROM ranked_messages WHERE rn = 1 ORDER BY precio DESC;""")
                except sqlite3.OperationalError as err:
                    conn.close()
                    return f"Err: {err}"
                else:
                    valores_final = cursor.fetchall()
                    conn.close()
                    return valores_final

def retornar_precios_segun_fecha(nombre_base=False, nombre_tabla=False, url=False):
    if nombre_base:
        if nombre_tabla:
            if url:
                try:
                    conn = sqlite3.connect(nombre_base)
                except sqlite3.OperationalError as err:
                    return f"Err: {err}"
                else:
                    cursor = conn.cursor()
                    try:
                        cursor.execute(f"SELECT t.precio, date(t.fecha_consulta) FROM {nombre_tabla} t WHERE url = (?) AND t.fecha_consulta in (SELECT max(fecha_consulta) from {nombre_tabla} group by date(fecha_consulta))", (url,))
                    except sqlite3.OperationalError as err:
                        conn.close()
                        return f"Err: {err}"
                    else:
                        valores_final = cursor.fetchall()
                        conn.close()
                        return valores_final