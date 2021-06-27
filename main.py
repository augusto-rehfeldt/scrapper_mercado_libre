import tkinter as tk

from tkinter import ttk

import datetime

import scrapper
import base

import os
from os import listdir

import threading
import webbrowser

from PIL import ImageTk, Image

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

class App():
    def __init__(self, master):
        self.master = master
        self.master.geometry("1100x600")
        self.master.title("Scrapper de artículos Mercado Libre")
        self.master.font = "Verdana 12"
        if not "registros.db" in listdir(os.getcwd()):
            base.crear_base("registros.db", "historial", "id INTEGER PRIMARY KEY, url TEXT NOT NULL, nombre TEXT NOT NULL, precio INTEGER NOT NULL, kilometros INT NOT NULL, año INT NOT NULL, fecha_consulta SMALLDATETIME")
    

        def al_cerrar():
            plt.close()
            self.master.destroy()

        self.master.protocol("WM_DELETE_WINDOW", al_cerrar)

        self.frame_1 = tk.Frame(self.master)
        self.frame_1.pack(fill="x")

        self.frame_2 = tk.Frame(self.master)
        self.frame_2.pack(side="top", anchor="nw")

        self.frame_3 = tk.Frame(self.master)
        self.frame_3.pack(side="left", anchor="nw")

        self.frame_4 = tk.Frame(self.master)
        self.frame_4.pack(side="right", anchor="ne")

        self.tree = ttk.Treeview(self.frame_1, columns = (1,2,3), height=10, show="headings", style="Treeview")

        self.scrollbar_y = ttk.Scrollbar(self.frame_1, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")
        self.tree["yscrollcommand"] = self.scrollbar_y.set
        self.scrollbar_y.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", lambda x: self.mostrar_datos_seleccion("registros.db", "historial", self.tree.item(self.tree.focus())["values"]))

        self.tree.pack(fill="x")

        #menu

        self.boton_actualizar_vista = tk.Button(self.frame_2, text="Actualizar datos")
        self.boton_actualizar_vista["command"] = lambda: self.actualizar_datos(self.master, "registros.db", "historial")
        self.boton_actualizar_vista.pack(side="right")

        self.boton_agregar_enlace = tk.Button(self.frame_2, text="Añadir enlace")
        self.boton_agregar_enlace["command"] = lambda: self.add_enlaces_window()
        self.boton_agregar_enlace.pack(side="right")

        self.actualizar_datos(self.master, "registros.db", "historial")

    def actualizar_datos(self, master, nombre_base, nombre_tabla):
        thread = threading.Thread(target=self.buscar_datos, args=(nombre_base, nombre_tabla,))
        thread.start()


    def crear_vista_base(self, master, nombre_base=False, nombre_tabla=False, campo_referencia=False, dato_busqueda=False):
        """Muestra en un widget treeview los valores de la tabla de una base de datos determinada. Permite scrollear si hay muchos valores o muchas columnas."""
        if not nombre_base:
            print("No se ha especificado la base de datos a acceder.\n")
            return False
        else:
            if not nombre_tabla:
                print("La base de datos especificada no contiene tablas.\n")
                self.tree["columns"] = (1,2,3)
                for row in self.tree.get_children():
                    self.tree.delete(row)
                return False

        contador_campos = 0
        nombres = []
        for campo in base.retornar_esquema(nombre_base, nombre_tabla):
            nombre = campo[1] # escruta el nombre de la columna
            contador_campos += 1
            nombres.append(nombre)

        self.tree["columns"] = tuple([x for x in range(1,contador_campos+1)] if contador_campos>=7 else [x for x in range(1,8)])

        if len(nombres) <= 6:
            for i in range(1,len(self.tree["columns"])+1):
                if i > 6:
                    self.tree.column(f"#{i}",
                                width=886-(140*6),
                                stretch=tk.NO)
                    self.tree.heading(f"#{i}", 
                                    text=f"")
                    break
                elif i <= 6 and i > len(nombres):
                    self.tree.column(f"#{i}",
                                width=140,
                                stretch=tk.NO)
                    self.tree.heading(f"#{i}", 
                                    text=f"")
                else:
                    self.tree.column(f"#{i}",
                                width=140,
                                stretch=tk.NO,
                                anchor='center')
                    self.tree.heading(f"#{i}", 
                                    text=f"{nombres[i-1].title() if nombres[i-1] not in ('id','ID') else nombres[i-1]}",
                                    anchor="center")
        else:
            for i in range(1,len(self.tree["columns"])+1):
                self.tree.column(f"#{i}",
                                width=140,
                                stretch=tk.NO,
                                anchor='center')
                self.tree.heading(f"#{i}", 
                                text=f"{nombres[i-1].title() if nombres[i-1] not in ('id','ID') else nombres[i-1]}",
                                anchor="center")

        if campo_referencia:
            if dato_busqueda:
                if isinstance(dato_busqueda, (str,int,float,bool)):
                    for row in self.tree.get_children():
                        self.tree.delete(row)
                    filas = base.traer_datos(nombre_base, nombre_tabla, campo_referencia, dato_busqueda)
                    for fila in filas:
                        self.tree.insert("", tk.END, values=fila)
                elif isinstance(dato_busqueda, (tuple,list,dict)):
                    for row in self.tree.get_children():
                        self.tree.delete(row)
                    for valor in dato_busqueda:
                        filas = base.traer_datos(nombre_base, nombre_tabla, campo_referencia, valor)
                        for fila in filas:
                            self.tree.insert("", tk.END, values=fila)
            else:
                for row in self.tree.get_children():
                    self.tree.delete(row)
                filas = base.retornar_datos(nombre_base, nombre_tabla)
                for fila in filas:
                    self.tree.insert("", tk.END, values=fila)
        else:
            for row in self.tree.get_children():
                self.tree.delete(row)
            filas = base.retornar_datos_segun_tiempo(nombre_base, nombre_tabla)
            for fila in filas:
                self.tree.insert("", tk.END, values=fila)



    def mostrar_datos_seleccion(self, nombre_base, nombre_tabla, linea_seleccionada):
        for widget in self.frame_3.winfo_children():
            widget.destroy()
        
        for widget in self.frame_4.winfo_children():
            widget.destroy()
        
        label_url = tk.Label(self.frame_3, text="URL:")
        label_url.grid(row=0, column=0, sticky="E", pady=(10, 0))
        label_url_datos = tk.Label(self.frame_3, text=f"Abrir en el navegador", foreground="blue", cursor="exchange", font="Verdana 10")
        label_url_datos.grid(row=0, column=1, sticky="W", pady=(10, 0))
        label_url_datos.bind("<Button-1>", lambda e: webbrowser.open_new(linea_seleccionada[1]))
        label_url_datos.bind("<Enter>", lambda e: hover_url())
        label_url_datos.bind("<Leave>", lambda e: normal_url())

        def hover_url():
            label_url_datos["font"] = "Verdana 10 underline"
        
        def normal_url():
            label_url_datos["font"] = "Verdana 10"


        label_nombre = tk.Label(self.frame_3, text="Nombre del artículo:")
        label_nombre.grid(row=1, column=0, sticky="E")
        label_nombre_datos = tk.Label(self.frame_3, text=f"{linea_seleccionada[2]}", font="Verdana 11", wraplength=200, justify="left")
        label_nombre_datos.grid(row=1, column=1, sticky="W")

        label_precio = tk.Label(self.frame_3, text="Precio:")
        label_precio.grid(row=2, column=0, sticky="E")
        label_precio_datos = tk.Label(self.frame_3, text=f"$ {linea_seleccionada[3]}", font="Verdana 10", wraplength=200)
        label_precio_datos.grid(row=2, column=1, sticky="W")

        label_kilometros = tk.Label(self.frame_3, text="Kilómetros:")
        label_kilometros.grid(row=3, column=0, sticky="E")
        label_kilometros_datos = tk.Label(self.frame_3, text=f"{linea_seleccionada[4]} km", font="Verdana 10")
        label_kilometros_datos.grid(row=3, column=1, sticky="W")

        label_year = tk.Label(self.frame_3, text="Año:")
        label_year.grid(row=4, column=0, sticky="E")
        label_year_datos = tk.Label(self.frame_3, text=f"{linea_seleccionada[5]}", font="Verdana 10")
        label_year_datos.grid(row=4, column=1, sticky="W")

        label_fecha = tk.Label(self.frame_3, text="Última fecha de consulta:")
        label_fecha.grid(row=5, column=0, sticky="E", padx=(10, 0))
        label_fecha_datos = tk.Label(self.frame_3, text=f"{linea_seleccionada[6]}", font="Verdana 10")
        label_fecha_datos.grid(row=5, column=1, sticky="W")

        label_estado = tk.Label(self.frame_3, text="Estado de la publicación:")
        label_estado.grid(row=6, column=0, sticky="E")
        label_estado_datos = tk.Label(self.frame_3, font="Verdana 10")
        label_estado_datos.grid(row=6, column=1, sticky="W")

        boton_borrar_enlace = tk.Button(self.frame_3, text="Borrar publicación de la lista")
        boton_borrar_enlace.grid(row=7, column=1, sticky="W")
        boton_borrar_enlace["command"] = lambda: self.borrar_datos("registros.db", "historial", "url", linea_seleccionada[1])

        imagen_publicacion = tk.Label(self.frame_3, foreground="red", font="verdana 10", width=200)
        imagen_publicacion.grid(row=0, column=2, rowspan=8, padx=(10, 0))

        def crear_disponible():
            try:
                label_estado_datos["text"] = scrapper.checkear_disponible(linea_seleccionada[1])
                if label_estado_datos["text"] == "Disponible":
                    label_estado_datos["foreground"] = "green"
                else:
                    label_estado_datos["foreground"] = "red"
            except:
                pass

        def crear_imagen():
            datos = scrapper.get_imagen_raw(linea_seleccionada[1])
            im = Image.open(BytesIO(datos))
            im = im.resize((200, 180), Image.ANTIALIAS)
            try:
                self.foto = ImageTk.PhotoImage(im)
            except:
                pass
            else:
                try:
                    imagen_publicacion["image"] = self.foto
                    imagen_publicacion["text"] = ""
                except:
                    try:
                        imagen_publicacion["text"] = "Imagen no disponible"
                    except:
                        pass

        def crear_grafico():
            grafico = tk.Label(self.frame_4)
            grafico.pack(side="right", padx=(0, 10))

            precios = []
            fechas = []

            for item in base.retornar_precios_segun_fecha("registros.db", "historial", linea_seleccionada[1]):
                precios.append(item[0])
                fechas.append(item[1])

            plt.clf()
            plt.plot(fechas, precios)
            plt.title("Historial de precios")
            plt.savefig("imagen_mercado.png")
            
            im = Image.open("imagen_mercado.png")
            im = im.resize((400, 300), Image.ANTIALIAS)

            try:
                self.foto_2 = ImageTk.PhotoImage(im)
            except:
                pass
            else:
                try:
                    grafico["image"] = self.foto_2
                except:
                    pass

            if precios[0] < precios[-1]:
                diferencia = precios[-1] - precios[0]
                label_precio_datos["text"] += f" (Aumentó ${diferencia} con respecto al {fechas[0]})"
            elif precios[0] == precios[-1]:
                label_precio_datos["text"] += f" (No hubo cambios de precio con respecto al {fechas[0]})"
            elif precios[0] > precios[-1]:
                diferencia = precios[0] - precios[-1]
                label_precio_datos["text"] += f" (Disminuyó ${diferencia} con respecto al {fechas[0]})"

        threading.Thread(target=crear_disponible).start()
        threading.Thread(target=crear_imagen).start()
        crear_grafico()

    def buscar_datos(self, nombre_base, nombre_tabla):
        def insertar_datos(nombre_base, nombre_tabla, enlace, tiempo_actual):
            try:
                datos = scrapper.get_datos(enlace)
                base.insertar_dict(nombre_base, nombre_tabla, {"url": enlace, 
                                                    "nombre": datos[0], 
                                                    "precio": datos[1],
                                                    "kilometros": datos[2],
                                                    "año": datos[3],
                                                    "fecha_consulta": tiempo_actual,
                                                    })
            except:
                raise
            else:
                print("ok")

        enlaces = scrapper.validar_links(scrapper.agarrar_links()).copy()
        tiempo_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        threads = []

        for enlace in enlaces:
            thread = threading.Thread(target=insertar_datos, args=(nombre_base, nombre_tabla, enlace, tiempo_actual,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        self.crear_vista_base(self.master, nombre_base, nombre_tabla)
            

    def add_enlaces_window(self):
        def add_enlace(enlace_nuevo):
            with open("urls.txt", "a+") as file:
                if enlace_nuevo not in scrapper.validar_links(scrapper.agarrar_links()).copy():
                    file.write(f"{enlace_nuevo}\n")
                    print(f"Se ha añadido el enlace: {enlace_nuevo}.")
                    file.close()

        

        def agregar_enlaces(lista_entries):
            for entry in lista_entries:
                enlace = entry.get()
                enlace = enlace.strip()
                add_enlace(enlace)
            self.actualizar_datos(self.master, "registros.db", "historial")

        def ocultar_ventana_enlaces():
            self.ventana_enlaces.destroy()
            self.boton_agregar_enlace["text"] = "Añadir enlaces nuevos"
            self.boton_agregar_enlace["command"] = lambda: self.add_enlaces_window()

        self.boton_agregar_enlace["text"] = "Ocultar 'enlaces nuevos'"
        self.boton_agregar_enlace["command"] = lambda: ocultar_ventana_enlaces()

        self.ventana_enlaces = tk.Toplevel(self.master)
        self.ventana_enlaces.title("Añadir enlace")
        
        self.ventana_enlaces.protocol("WM_DELETE_WINDOW", lambda: ocultar_ventana_enlaces())

        label_urls = tk.Label(self.ventana_enlaces, text="URL's:")
        label_urls.grid(row=0, column=0)

        lista_entries_url = []

        def crear_row(i, boton=False, boton_2=False):
            if boton:
                boton.destroy()
            
            if boton_2:
                boton_2.destroy()

            entry_url = tk.Entry(self.ventana_enlaces, width=60)
            entry_url.grid(row=i, column=1)

            lista_entries_url.append(entry_url)

            boton_add_row = tk.Button(self.ventana_enlaces, text="+")
            boton_add_row.grid(row=i, column=2)
            boton_add_row["command"] = lambda: crear_row(i+1, boton_add_row, boton_agregar)

            boton_agregar = tk.Button(self.ventana_enlaces, text="Agregar")
            boton_agregar.grid(row=i+1, column=1)
            boton_agregar["command"] = lambda: agregar_enlaces(lista_entries_url)

        entry_url = tk.Entry(self.ventana_enlaces, width=60)
        entry_url.grid(row=0, column=1)

        lista_entries_url.append(entry_url)

        boton_add_row = tk.Button(self.ventana_enlaces, text="+")
        boton_add_row.grid(row=0, column=2)
        boton_add_row["command"] = lambda: crear_row(1, boton_add_row, boton_agregar)

        boton_agregar = tk.Button(self.ventana_enlaces, text="Agregar")
        boton_agregar.grid(row=1, column=1)
        boton_agregar["command"] = lambda: agregar_enlaces(lista_entries_url)

    def borrar_datos(self, nombre_base, nombre_tabla, campo_referencia, valor):
        base.borrar_datos(nombre_base, nombre_tabla, campo_referencia, valor)
        enlaces_previos = scrapper.agarrar_links()
        with open("urls.txt", "w") as file:
            for enlace in enlaces_previos:
                if not enlace == valor:
                    file.write(enlace)
        self.crear_vista_base(self.master, nombre_base, nombre_tabla)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()




