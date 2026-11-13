#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar-capturas.py

Convierte los logs textuales de la ejecucion en imagenes PNG que representam
una captura de pantalla de terminal, para incorporarlas como evidencia en la
entrega del taller.

La captura NO inventa contenido: renderiza literalmente la salida real de los
comandos ejecutados.

Uso:
    python scripts/generar-capturas.py --log evidencia/logs/01-mvn-verify.log \
        --salida evidencia/capturas/01-mvn-verify.png --titulo "mvn clean verify"
"""

import argparse
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

# Paleta (estilo terminal oscuro)
FONDO = (18, 18, 24)
FONDO_BARRA = (38, 38, 46)
TEXTO = (222, 222, 228)
TEXTO_SUAVE = (140, 140, 150)
VERDE = (74, 222, 128)
ROJO = (255, 92, 92)
AMARILLO = (250, 204, 21)
AZUL = (96, 180, 250)
MORADO = (198, 146, 233)

FUENTES = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def obtener_fuente(tamano):
    for ruta in FUENTES:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def color_linea(linea):
    """Devuelve el color segun el contenido de la linea (estilo de un log real)."""
    if re.search(r"\[ERROR\]|BUILD FAILURE|FAIL|Exception|ERROR ", linea):
        return ROJO
    if re.search(r"\[WARNING\]|ADVERTENCIA", linea):
        return AMARILLO
    if re.search(r"BUILD SUCCESS|Tests run:.*Failures: 0.*Errors: 0", linea):
        return VERDE
    if re.search(r"\[INFO\]", linea):
        return (150, 150, 160)
    if re.search(r"^\s*(commit |Author:|Date:)", linea):
        return MORADO
    if re.search(r"^\s*(feat|fix|test|docs|chore|perf|ci|build|refactor)(\(.*\))?:", linea):
        return VERDE
    if re.search(r"^\s*\* ", linea):
        return VERDE
    if re.search(r"^\s*[|+]", linea):
        return TEXTO_SUAVE
    return TEXTO


def renderizar(texto, salida, titulo, tamano_fuente=13, ancho_max=175):
    fuente = obtener_fuente(tamano_fuente)
    fuente_titulo = obtener_fuente(tamano_fuente + 1)

    lineas = texto.replace("\t", "    ").splitlines()

    # Recorta lineas vacias al inicio y limita el numero de lineas mostradas
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    if not lineas:
        lineas = ["(sin salida)"]

    ancho_texto = fuente.getbbox("M")[2] if hasattr(fuente, "getbbox") else 8
    ancho_caracter = max(ancho_texto, 8)

    margen = 16
    alto_barra = 34
    alto_linea = tamano_fuente + 6

    ancho_util = min(ancho_max, max(len(l) for l in lineas) + 2)
    ancho = margen * 2 + ancho_caracter * ancho_util
    alto = alto_barra + margen * 2 + alto_linea * len(lineas)

    imagen = Image.new("RGB", (ancho, alto), FONDO)
    dibujo = ImageDraw.Draw(imagen)

    # Barra de titulo con los botones de la ventana
    dibujo.rectangle([0, 0, ancho, alto_barra], fill=FONDO_BARRA)
    for indice, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        x = 14 + indice * 20
        dibujo.ellipse([x, 11, x + 12, 23], fill=color)
    texto_titulo = f"{titulo}"
    ancho_titulo = dibujo.textlength(texto_titulo, font=fuente_titulo)
    dibujo.text(((ancho - ancho_titulo) / 2, 8), texto_titulo, font=fuente_titulo, fill=TEXTO_SUAVE)

    # Lineas de salida
    y = alto_barra + margen
    for linea in lineas:
        dibujo.text((margen, y), linea, font=fuente, fill=color_linea(linea))
        y += alto_linea

    carpeta = os.path.dirname(salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    imagen.save(salida)
    print("[captura] {} ({}x{} px)".format(salida, imagen.width, imagen.height))


def main():
    parser = argparse.ArgumentParser(description="Genera capturas PNG de los logs del pipeline")
    parser.add_argument("--log", required=True, help="Archivo de log a renderizar")
    parser.add_argument("--salida", required=True, help="PNG de salida")
    parser.add_argument("--titulo", default=None, help="Titulo de la ventana")
    parser.add_argument("--fuente", type=int, default=13, help="Tamano de la fuente")
    parser.add_argument("--inicio", type=int, default=0, help="Linea inicial (0 = todo)")
    parser.add_argument("--fin", type=int, default=0, help="Linea final (0 = hasta el final)")
    argumentos = parser.parse_args()

    if not os.path.isfile(argumentos.log):
        print("[captura] ERROR: no existe el log {}".format(argumentos.log))
        sys.exit(1)

    with open(argumentos.log, "r", encoding="utf-8", errors="replace") as archivo:
        lineas = archivo.read().splitlines()

    if argumentos.inicio or argumentos.fin:
        fin = argumentos.fin if argumentos.fin else len(lineas)
        lineas = lineas[argumentos.inicio:fin]

    titulo = argumentos.titulo or os.path.basename(argumentos.log)
    renderizar("\n".join(lineas), argumentos.salida, titulo, argumentos.fuente)


if __name__ == "__main__":
    main()
