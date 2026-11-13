#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar-umbrales.py

Evalua los umbrales (SLA) definidos en monitoreo/umbrales.yml contra los resultados
de la ultima ejecucion del pipeline. Si un umbral se incumple, el script escribe el
estado en un archivo JSON y devuelve codigo de salida 1, lo que hace fallar el job
del pipeline y dispara la alerta automatica.

Uso:
    python3 scripts/verificar-umbrales.py \
        --jmeter performance/resultados/login.jtl \
        --salida dashboard/estado-umbrales.json
"""

import argparse
import json
import os
import sys

# --------------------------------------------------------------------------- #
# Umbrales (ver monitoreo/umbrales.yml - deben mantenerse sincronizados)
# --------------------------------------------------------------------------- #
UMBRALES = {
    "tps_minimo": 50.0,             # transacciones por segundo minimas
    "latencia_p95_maxima_ms": 500.0,
    "latencia_p99_maxima_ms": 1000.0,
    "tasa_error_maxima_pct": 1.0,
    "muestras_minimas": 100,
    "cobertura_minima_pct": 70.0,
    "tasa_fallos_funcional_maxima_pct": 0.0,
}

CANALES = {
    "critico": "correo electronico al jefe de QA + Slack #qa-alertas + creacion de incident",
    "alto": "Slack #qa-alertas + correo al equipo de automatizacion",
    "medio": "Slack #qa-alertas + ticket en el tablero de calidad",
}


def calcular_metricas_jmeter(ruta_jtl):
    """Replica el calculo de metricas de generar-dashboard.py para no depender de el."""
    metricas = {"muestras": 0, "errores": 0, "tps": 0.0, "p95": 0.0, "p99": 0.0, "tasa_error": 0.0}
    if not ruta_jtl or not os.path.isfile(ruta_jtl):
        return metricas
    with open(ruta_jtl, "r", encoding="utf-8", errors="replace") as archivo:
        lineas = archivo.read().splitlines()
    if len(lineas) < 2:
        return metricas

    encabezado = [c.strip().lower() for c in lineas[0].split(",")]
    indice = {nombre: posicion for posicion, nombre in enumerate(encabezado)}
    clave_elapsed = indice.get("elapsed", 1)
    clave_success = indice.get("success", 7)
    clave_timestamp = indice.get("timestamp", 0)

    latencias, marcas, errores = [], [], 0
    for linea in lineas[1:]:
        campos = linea.split(",")
        if len(campos) <= max(clave_elapsed, clave_success):
            continue
        try:
            latencias.append(int(campos[clave_elapsed]))
            marcas.append(int(campos[clave_timestamp]))
        except (ValueError, IndexError):
            continue
        if clave_success < len(campos) and campos[clave_success].strip().lower() != "true":
            errores += 1

    if not latencias:
        return metricas

    latencias.sort()
    muestras = len(latencias)
    metricas["muestras"] = muestras
    metricas["errores"] = errores
    metricas["tasa_error"] = round(errores * 100.0 / muestras, 2)
    duracion_ms = (max(marcas) - min(marcas)) if len(marcas) > 1 else 0
    metricas["tps"] = round(muestras * 1000.0 / duracion_ms, 2) if duracion_ms > 0 else 0.0

    def percentil(pct):
        posicion = int(round((pct / 100.0) * (muestras - 1)))
        return latencias[min(posicion, muestras - 1)]

    metricas["p95"] = percentil(95)
    metricas["p99"] = percentil(99)
    return metricas


def evaluar(nombre, valor, operador, limite):
    if operador == ">=":
        return valor >= limite
    if operador == "<=":
        return valor <= limite
    if operador == ">":
        return valor > limite
    if operador == "<":
        return valor < limite
    return False


def main():
    parser = argparse.ArgumentParser(description="Verifica los umbrales del pipeline")
    parser.add_argument("--jmeter", default="performance/resultados/login.jtl")
    parser.add_argument("--salida", default="dashboard/estado-umbrales.json")
    argumentos = parser.parse_args()

    metricas = calcular_metricas_jmeter(argumentos.jmeter)

    verificaciones = [
        ("Throughput (TPS)", "tps", metricas["tps"], ">=", UMBRALES["tps_minimo"], "critico"),
        ("Latencia p95 (ms)", "p95", metricas["p95"], "<=", UMBRALES["latencia_p95_maxima_ms"], "alto"),
        ("Latencia p99 (ms)", "p99", metricas["p99"], "<=", UMBRALES["latencia_p99_maxima_ms"], "medio"),
        ("Tasa de error (%)", "tasa_error", metricas["tasa_error"], "<=",
         UMBRALES["tasa_error_maxima_pct"], "critico"),
        ("Muestras ejecutadas", "muestras", metricas["muestras"], ">=",
         UMBRALES["muestras_minimas"], "medio"),
    ]

    resultados = []
    alertas = []
    for nombre, clave, valor, operador, limite, severidad in verificaciones:
        cumple = evaluar(clave, valor, operador, limite)
        resultados.append({
            "metrica": nombre,
            "valor": valor,
            "operador": operador,
            "umbral": limite,
            "cumple": cumple,
            "severidad": severidad,
        })
        if not cumple:
            alertas.append({
                "titulo": "Degradacion detectada: {}".format(nombre),
                "severidad": severidad,
                "detalle": "{} = {} (umbral requerido {} {})".format(nombre, valor, operador, limite),
                "canal": CANALES[severidad],
            })

    estado = {
        "generado": metricas,
        "verificaciones": resultados,
        "alertas": alertas,
        "estado_global": "OK" if not alertas else "ALERTA",
    }

    destino = argumentos.salida
    carpeta = os.path.dirname(destino)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(estado, archivo, indent=2, ensure_ascii=False)

    print("[umbrales] Estado global: {}".format(estado["estado_global"]))
    for verificacion in resultados:
        marca = "OK  " if verificacion["cumple"] else "FALLA"
        print("  [{}] {} = {} ({} {})".format(
            marca, verificacion["metrica"], verificacion["valor"],
            verificacion["operador"], verificacion["umbral"]))

    if alertas:
        print("")
        print("[umbrales] ALERTAS A DISPARAR:")
        for alerta in alertas:
            print("  - [{}] {} -> {}".format(alerta["severidad"].upper(),
                                             alerta["titulo"], alerta["canal"]))
        print("")
        print("[umbrales] El pipeline se marca como fallido para bloquear el despliegue.")
        sys.exit(1)

    print("[umbrales] Todos los umbrales se cumplen.")
    sys.exit(0)


if __name__ == "__main__":
    main()
