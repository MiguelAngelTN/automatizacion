#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura PNG de los reportes HTML navegables usando Chrome headless."""

import os
import subprocess

PROJECT_ROOT = r"C:\Users\USUARIO\Desktop\automatica"
CHROME_BIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DESTINO = os.path.join(PROJECT_ROOT, "evidencia", "capturas")
os.makedirs(DESTINO, exist_ok=True)

CASOS = [
    ("reporte-allure.png", os.path.join(PROJECT_ROOT, "target", "allure-report", "index.html"), 1600, 1100),
    ("reporte-cucumber.png", os.path.join(PROJECT_ROOT, "target", "cucumber-report", "cucumber-report.html"), 1600, 1400),
    ("reporte-jacoco.png", os.path.join(PROJECT_ROOT, "target", "site", "jacoco", "index.html"), 1600, 1100),
    ("reporte-jmeter.png", os.path.join(PROJECT_ROOT, "performance", "reporte-html", "index.html"), 1600, 1400),
    ("dashboard-metricas.png", os.path.join(PROJECT_ROOT, "dashboard", "metricas.html"), 1600, 1300),
]

for nombre, ruta, ancho, alto in CASOS:
    if not os.path.isfile(ruta):
        print("  --  {} (no existe, se omite)".format(ruta))
        continue
    destino = os.path.join(DESTINO, nombre)
    comando = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--screenshot={}".format(destino),
        "--window-size={}".format(str(ancho) + "," + str(alto)),
        "--virtual-time-budget=8000",
        "file:///{}".format(ruta.replace(" ", "%20").replace("\\", "/")),
    ]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=120)
    except Exception as error:  # noqa: BLE001
        print("  !!  error ejecutando chrome para {}: {}".format(ruta, error))
        continue
    if os.path.isfile(destino):
        print("  OK  {}".format(destino))
    else:
        print("  !!  no se pudo capturar {}".format(ruta))
        print("     stdout: {}".format(resultado.stdout[-500:]))
        print("     stderr: {}".format(resultado.stderr[-800:]))
print("LISTO")
