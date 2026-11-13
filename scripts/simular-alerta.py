#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simular-alerta.py

Demuestra que las alertas automaticas se disparan. Toma los resultados reales de
JMeter (performance/resultados/login.jtl), les inyecta una degradacion controlada y
ejecuta scripts/verificar-umbrales.py sobre el resultado degradado.

Degradacion inyectada (semilla fija: el resultado es reproducible):
  - 8 % de las muestras responde con latencia entre 900 y 1500 ms (cola de latencia).
  - 6 % de las muestras falla (HTTP 500, success=false).

Esto NO modifica los resultados reales ni el estado real (dashboard/estado-umbrales.json):
escribe en performance/resultados/login-degradado.jtl y en
dashboard/estado-umbrales-simulado.json.

Uso:
    python3 scripts/simular-alerta.py
Codigo de salida: el mismo que devuelve verificar-umbrales.py (1 = alerta disparada).
"""

import os
import random
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "performance", "resultados", "login.jtl")
SALIDA_JTL = os.path.join(RAIZ, "performance", "resultados", "login-degradado.jtl")
SALIDA_ESTADO = os.path.join(RAIZ, "dashboard", "estado-umbrales-simulado.json")
VERIFICADOR = os.path.join(RAIZ, "scripts", "verificar-umbrales.py")

PCT_LENTAS = 0.08
PCT_FALLIDAS = 0.06


def degradar():
    azar = random.Random(42)
    with open(ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        lineas = f.read().splitlines()
    encabezado, filas = lineas[0], lineas[1:]
    campos_h = [c.strip().lower() for c in encabezado.split(",")]
    i_elapsed = campos_h.index("elapsed")
    i_codigo = campos_h.index("responsecode")
    i_ok = campos_h.index("success")

    lentas = fallidas = 0
    resultado = [encabezado]
    for fila in filas:
        c = fila.split(",")
        x = azar.random()
        if x < PCT_LENTAS:
            c[i_elapsed] = str(azar.randint(900, 1500))
            lentas += 1
        elif x < PCT_LENTAS + PCT_FALLIDAS:
            c[i_codigo] = "500"
            c[i_ok] = "false"
            fallidas += 1
        resultado.append(",".join(c))
    with open(SALIDA_JTL, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(resultado) + "\n")
    print("[simulacion] Muestras reales: {} | lentas inyectadas: {} | fallidas inyectadas: {}".format(
        len(filas), lentas, fallidas))


def main():
    if not os.path.isfile(ENTRADA):
        print("[simulacion] No existe {}. Ejecute antes el plan de JMeter.".format(ENTRADA))
        return 2
    degradar()
    print("[simulacion] Ejecutando verificar-umbrales.py sobre el resultado degradado...\n")
    proceso = subprocess.run(
        [sys.executable, VERIFICADOR, "--jmeter", SALIDA_JTL, "--salida", SALIDA_ESTADO])
    print("\n[simulacion] Codigo de salida del verificador: {}".format(proceso.returncode))
    if proceso.returncode != 0:
        print("[simulacion] Resultado esperado: la alerta se dispara y el pipeline falla.")
    return proceso.returncode


if __name__ == "__main__":
    sys.exit(main())
