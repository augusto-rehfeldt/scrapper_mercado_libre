import requests
import validators

import pprint

from bs4 import BeautifulSoup

def agarrar_links():
    direcciones = []
    with open("urls.txt", "r") as file:
        for linea in file.readlines():
            linea = linea.strip()
            direcciones.append(linea)
        file.close()
    print(len(direcciones))
    return direcciones

def validar_links(lista: list):
    enlaces = []
    for link in lista:
        if validators.url(link):
            enlaces.append(link)
        else:
            print(f"'' no es un enlace válido.")
    return enlaces

def get_datos(direccion):
    r = requests.get(direccion)
    indicador_nombre = '<h1 class="ui-pdp-title">'
    if (indicador_nombre) in r.text:
        html_nombre = r.text[r.text.find(indicador_nombre) : r.text.find(indicador_nombre)+100]
        soup_nombre = BeautifulSoup(html_nombre, "html.parser")
        nombre = soup_nombre.h1.string.strip()
    indicador_precio = '<span class="price-tag-fraction">'
    if (indicador_precio) in r.text:
        html_precio = r.text[r.text.find(indicador_precio) : r.text.find(indicador_precio)+100]
        soup_precio = BeautifulSoup(html_precio, "html.parser")
        precio = soup_precio.span.string.strip()
        if "." in precio:
            precio = precio.replace(".", "")
    indicador_kilometros_year = '<span class="ui-pdp-subtitle">'
    if (indicador_kilometros_year) in r.text:
        html_kilometros_year = r.text[r.text.find(indicador_kilometros_year) : r.text.find(indicador_precio)+100]
        soup_kilometros_year = BeautifulSoup(html_kilometros_year, "html.parser")
        kilometros_year = soup_kilometros_year.span.string.strip()
        kilometros_year = kilometros_year.replace("·", "|").replace(".", "").split("|")
        return [nombre, precio, kilometros_year[0].strip(), kilometros_year[1].replace("km", "").strip()]

def checkear_disponible(direccion):
    try:
        r = requests.get(direccion)
    except:
        return "Ya no está disponible"
    else:
        indicador_activo = '<span class="andes-button__content">Preguntar</span>'
        if indicador_activo in r.text:
            return "Disponible"
        else:
            return "Ya no está disponible"

def get_imagen_raw(direccion):
    r = requests.get(direccion)
    indicador_imagen = '<img data-zoom="'
    if indicador_imagen in r.text:
        html_imagen = r.text[r.text.find(indicador_imagen) : r.text.find(indicador_imagen)+500]
        soup_imagen = BeautifulSoup(html_imagen, "html.parser")
        url_imagen = soup_imagen.img
        datos = requests.get(url_imagen["data-zoom"], stream=True).raw.read()
        return datos
    return False