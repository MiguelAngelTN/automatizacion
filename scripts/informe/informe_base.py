#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar-informe.py

Construye el documento Word de entrega (Miguel_Toledo.docx) a partir del contenido
del proyecto y de la evidencia generada en evidencia/capturas.

Formato exigido por el enunciado:
  * Tipo de letra: Arial 12
  * Interlineado: 1,15
  * Nombre del archivo: Miguel_Toledo.docx
"""

import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAPTURAS = os.path.join(RAIZ, "evidencia", "capturas")
SALIDA = os.path.join(RAIZ, "entrega", "Miguel_Toledo.docx")

FUENTE = "Arial"
FUENTE_CODIGO = "Consolas"
TAMANO = 12
GRIS = RGBColor(0x44, 0x44, 0x44)
AZUL = RGBColor(0x1F, 0x4E, 0x79)

documento = Document()

# --------------------------------------------------------------------------- #
# Configuracion general del documento
# --------------------------------------------------------------------------- #


def configurar_estilos():
    normal = documento.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(TAMANO)
    normal.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(atributo), FUENTE)
    formato = normal.paragraph_format
    formato.line_spacing = 1.15
    formato.space_after = Pt(6)
    formato.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for nombre in ("Heading 1", "Heading 2", "Heading 3", "Title"):
        try:
            estilo = documento.styles[nombre]
        except KeyError:
            continue
        estilo.font.name = FUENTE
        estilo.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        rpr = estilo.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        for atributo in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(atributo), FUENTE)


def configurar_pagina():
    for seccion in documento.sections:
        seccion.top_margin = Cm(2.5)
        seccion.bottom_margin = Cm(2.5)
        seccion.left_margin = Cm(3.0)
        seccion.right_margin = Cm(2.5)


def numerar_paginas():
    for seccion in documento.sections:
        parrafo = seccion.footer.paragraphs[0]
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = parrafo.add_run("Pagina ")
        run.font.name = FUENTE
        run.font.size = Pt(9)
        campo = OxmlElement("w:fldSimple")
        campo.set(qn("w:instr"), "PAGE")
        parrafo._p.append(campo)


# --------------------------------------------------------------------------- #
# Utilidades de contenido
# --------------------------------------------------------------------------- #


def titulo(texto, nivel=1):
    parrafo = documento.add_heading(texto, level=nivel)
    for run in parrafo.runs:
        run.font.name = FUENTE
        run.font.size = Pt({1: 16, 2: 13, 3: 12}.get(nivel, 12))
        run.font.bold = True
        run.font.color.rgb = AZUL if nivel > 1 else RGBColor(0x00, 0x00, 0x00)
    parrafo.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
    parrafo.paragraph_format.space_after = Pt(6)
    parrafo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    parrafo.paragraph_format.line_spacing = 1.15
    return parrafo


def parrafo(texto="", negrita=False, cursiva=False, tamano=TAMANO, alineacion=None,
            color=None, espacio_antes=0, espacio_despues=6):
    p = documento.add_paragraph()
    run = p.add_run(texto)
    run.font.name = FUENTE
    run.font.size = Pt(tamano)
    run.bold = negrita
    run.italic = cursiva
    if color is not None:
        run.font.color.rgb = color
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(espacio_despues)
    p.paragraph_format.space_before = Pt(espacio_antes)
    if alineacion is not None:
        p.alignment = alineacion
    return p


def vinetas(items, estilo="List Bullet"):
    for item in items:
        p = documento.add_paragraph(style=estilo)
        run = p.add_run(item)
        run.font.name = FUENTE
        run.font.size = Pt(TAMANO)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def numerada(items):
    vinetas(items, estilo="List Number")


def codigo(texto, titulo_opcional=None):
    """Bloque de codigo con fuente monoespaciada y sombreado."""
    if titulo_opcional:
        parrafo(titulo_opcional, cursiva=True, tamano=10, color=GRIS, espacio_antes=6, espacio_despues=2)
    tabla = documento.add_table(rows=1, cols=1)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    celda = tabla.cell(0, 0)
    sombrear(celda, "F4F6F8")
    celda.text = ""
    for indice, linea in enumerate(texto.rstrip("\n").split("\n")):
        p = celda.paragraphs[0] if indice == 0 else celda.add_paragraph()
        run = p.add_run(linea if linea else " ")
        run.font.name = FUENTE_CODIGO
        run.font.size = Pt(9)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    documento.add_paragraph().paragraph_format.space_after = Pt(4)
    return tabla


def sombrear(celda, color_hex):
    tc_pr = celda._tc.get_or_add_tcPr()
    sombreado = OxmlElement("w:shd")
    sombreado.set(qn("w:val"), "clear")
    sombreado.set(qn("w:color"), "auto")
    sombreado.set(qn("w:fill"), color_hex)
    tc_pr.append(sombreado)


def bordered(celda):
    tc_pr = celda._tc.get_or_add_tcPr()
    bordes = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        elemento = OxmlElement(f"w:{lado}")
        elemento.set(qn("w:val"), "single")
        elemento.set(qn("w:sz"), "4")
        elemento.set(qn("w:color"), "9AA5B1")
        bordes.append(elemento)
    tc_pr.append(bordes)


def tabla(encabezados, filas, anchos=None, tamano=10):
    t = documento.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    celdas = t.rows[0].cells
    for indice, encabezado in enumerate(encabezados):
        celdas[indice].text = ""
        p = celdas[indice].paragraphs[0]
        run = p.add_run(str(encabezado))
        run.font.name = FUENTE
        run.font.size = Pt(tamano)
        run.bold = True
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        sombrear(celdas[indice], "1F4E79")
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for indice_fila, fila in enumerate(filas):
        celdas = t.add_row().cells
        for indice, valor in enumerate(fila):
            celdas[indice].text = ""
            p = celdas[indice].paragraphs[0]
            run = p.add_run(str(valor))
            run.font.name = FUENTE
            run.font.size = Pt(tamano)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            if indice_fila % 2 == 1:
                sombrear(celdas[indice], "F2F6FA")
    if anchos:
        for indice, ancho in enumerate(anchos):
            for fila in t.rows:
                fila.cells[indice].width = Cm(ancho)
    documento.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def imagen(nombre_archivo, pie=None, ancho=15.5):
    ruta = os.path.join(CAPTURAS, nombre_archivo)
    if not os.path.isfile(ruta):
        parrafo("[Falta la evidencia: {}]".format(nombre_archivo), cursiva=True, color=GRIS)
        return
    # Se guarda la ruta relativa al documento para que Word la resuelva bien
    p = documento.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(ruta, width=Cm(ancho))
    if pie:
        sub = documento.add_paragraph()
        run = sub.add_run(pie)
        run.font.name = FUENTE
        run.font.size = Pt(9)
        run.italic = True
        run.font.color.rgb = GRIS
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub.paragraph_format.space_after = Pt(10)


def salto_pagina():
    documento.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def leer(relative, default=""):
    try:
        with open(os.path.join(RAIZ, relative), "r", encoding="utf-8") as archivo:
            return archivo.read()
    except OSError:
        return default
