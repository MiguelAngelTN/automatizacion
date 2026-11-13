#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar-dashboard.py

Construye un dashboard HTML autocontenido (sin dependencias externas) que consolida
las metricas de la ejecucion del pipeline:

  * Pruebas funcionales unitarias (JUnit 5) -> informes XML de Surefire
  * Pruebas funcionales BDD (Cucumber)      -> target/cucumber-results.json
  * Cobertura de codigo                     -> target/site/jacoco/jacoco.xml
  * Pruebas de performance                  -> .jtl generado por Apache JMeter

Uso:
    python3 scripts/generar-dashboard.py \
        --surefire target/surefire-reports \
        --cucumber target/cucumber-results.json \
        --jacoco target/site/jacoco/jacoco.xml \
        --jmeter performance/resultados/login.jtl \
        --salida dashboard/metricas.html
"""

import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# --------------------------------------------------------------------------- #
# Lectores de resultados
# --------------------------------------------------------------------------- #


def leer_surefire(directorio):
    """Agrega los informes XML de Surefire (pruebas unitarias JUnit 5)."""
    resumen = {
        "tests": 0, "fallos": 0, "errores": 0, "omitidos": 0,
        "tiempo": 0.0, "clases": [], "fuente": "JUnit 5 (Surefire)",
    }
    if not directorio or not os.path.isdir(directorio):
        return resumen
    for archivo in sorted(os.listdir(directorio)):
        if not (archivo.startswith("TEST-") and archivo.endswith(".xml")):
            continue
        try:
            raiz = ET.parse(os.path.join(directorio, archivo)).getroot()
        except ET.ParseError:
            continue
        tests = int(raiz.get("tests", 0))
        fallos = int(raiz.get("failures", 0))
        errores = int(raiz.get("errors", 0))
        omitidos = int(raiz.get("skipped", 0))
        tiempo = float(raiz.get("time", 0.0))
        resumen["tests"] += tests
        resumen["fallos"] += fallos
        resumen["errores"] += errores
        resumen["omitidos"] += omitidos
        resumen["tiempo"] += tiempo
        resumen["clases"].append({
            "clase": raiz.get("name", archivo),
            "tests": tests,
            "fallos": fallos,
            "errores": errores,
            "omitidos": omitidos,
            "tiempo": round(tiempo, 3),
        })
    return resumen


def leer_cucumber(ruta_json):
    """Agrega los escenarios BDD a partir del JSON de Cucumber."""
    resumen = {
        "escenarios": 0, "aprobados": 0, "fallidos": 0, "omitidos": 0,
        "pasos": 0, "caracteristicas": [], "fuente": "Cucumber (BDD)",
    }
    if not ruta_json or not os.path.isfile(ruta_json):
        return resumen
    with open(ruta_json, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    for caracteristica in datos:
        elementos = caracteristica.get("elements", []) or []
        total = 0
        aprobados = 0
        fallidos = 0
        omitidos = 0
        for elemento in elementos:
            pasos = elemento.get("steps", []) or []
            if not pasos:
                continue
            total += 1
            resumen["pasos"] += len(pasos)
            estados = [p.get("result", {}).get("status", "unknown") for p in pasos]
            if any(estado == "failed" for estado in estados):
                fallidos += 1
            elif all(estado == "skipped" for estado in estados):
                omitidos += 1
            else:
                aprobados += 1
        resumen["escenarios"] += total
        resumen["aprobados"] += aprobados
        resumen["fallidos"] += fallidos
        resumen["omitidos"] += omitidos
        resumen["caracteristicas"].append({
            "nombre": caracteristica.get("name", ""),
            "archivo": caracteristica.get("uri", ""),
            "escenarios": total,
            "aprobados": aprobados,
            "fallidos": fallidos,
        })
    return resumen


def leer_jacoco(ruta_xml):
    """Extrae la cobertura global de lineas del informe JaCoCo."""
    resumen = {"lineas": 0, "cubiertas": 0, "omitidas": 0, "porcentaje": 0.0,
               "fuente": "JaCoCo"}
    if not ruta_xml or not os.path.isfile(ruta_xml):
        return resumen
    try:
        raiz = ET.parse(ruta_xml).getroot()
    except ET.ParseError:
        return resumen
    for contador in raiz.findall(".//counter"):
        if contador.get("type") == "LINE":
            cubierta = int(contador.get("covered", 0))
            omitida = int(contador.get("missed", 0))
            resumen["cubiertas"] = cubierta
            resumen["omitidas"] = omitida
            resumen["lineas"] = cubierta + omitida
            if resumen["lineas"]:
                resumen["porcentaje"] = round(cubierta * 100.0 / resumen["lineas"], 2)
    return resumen


def leer_jmeter(ruta_jtl):
    """Calcula TPS, percentiles de latencia y tasa de error desde el .jtl de JMeter."""
    resumen = {
        "muestras": 0, "errores": 0, "tps": 0.0, "min": 0.0, "max": 0.0,
        "promedio": 0.0, "p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0,
        "tasa_error": 0.0, "duracion": 0.0, "fuente": "Apache JMeter",
    }
    if not ruta_jtl or not os.path.isfile(ruta_jtl):
        return resumen

    latencias = []
    marcas = []
    errores = 0
    with open(ruta_jtl, "r", encoding="utf-8", errors="replace") as archivo:
        lineas = archivo.read().splitlines()
    if not lineas:
        return resumen

    indice = {}
    encabezado = [c.strip() for c in lineas[0].split(",")]
    for posicion, nombre in enumerate(encabezado):
        indice[nombre.lower()] = posicion
    inicio = 1 if indice else 0

    clave_elapsed = indice.get("elapsed", 1)
    clave_success = indice.get("success", 7)
    clave_timestamp = indice.get("timestamp", 0)

    for linea in lineas[inicio:]:
        if not linea.strip():
            continue
        campos = linea.split(",")
        if len(campos) <= max(clave_elapsed, clave_success):
            continue
        try:
            latencias.append(int(campos[clave_elapsed]))
        except (ValueError, IndexError):
            continue
        try:
            marcas.append(int(campos[clave_timestamp]))
        except (ValueError, IndexError):
            pass
        if clave_success < len(campos) and campos[clave_success].strip().lower() != "true":
            errores += 1

    if not latencias:
        return resumen

    latencias.sort()
    muestras = len(latencias)
    resumen["muestras"] = muestras
    resumen["errores"] = errores
    resumen["min"] = latencias[0]
    resumen["max"] = latencias[-1]
    resumen["promedio"] = round(sum(latencias) / muestras, 2)
    resumen["tasa_error"] = round(errores * 100.0 / muestras, 2)

    def percentil(porcentaje):
        if not latencias:
            return 0
        posicion = int(round((porcentaje / 100.0) * (muestras - 1)))
        return latencias[min(posicion, muestras - 1)]

    resumen["p50"] = percentil(50)
    resumen["p90"] = percentil(90)
    resumen["p95"] = percentil(95)
    resumen["p99"] = percentil(99)

    if len(marcas) > 1:
        duracion_ms = max(marcas) - min(marcas)
        resumen["duracion"] = round(duracion_ms / 1000.0, 2)
        if duracion_ms > 0:
            resumen["tps"] = round(muestras * 1000.0 / duracion_ms, 2)
    return resumen


# --------------------------------------------------------------------------- #
# Generacion del dashboard
# --------------------------------------------------------------------------- #

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Dashboard de Metricas - Pipeline de Pruebas</title>
<style>
  :root {{
    --fondo:#0f172a; --panel:#1e293b; --borde:#334155; --texto:#e2e8f0;
    --ok:#22c55e; --alerta:#f59e0b; --error:#ef4444; --acento:#38bdf8;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:'Segoe UI',Arial,sans-serif; background:var(--fondo); color:var(--texto); }}
  header {{ background:linear-gradient(90deg,#1e3a8a,#0e7490); padding:22px 32px; }}
  header h1 {{ margin:0 0 6px; font-size:24px; }}
  header p {{ margin:0; opacity:.85; font-size:13px; }}
  .contenedor {{ padding:24px 32px 48px; }}
  .seccion {{ margin-bottom:34px; }}
  .seccion h2 {{ font-size:17px; border-left:4px solid var(--acento); padding-left:10px; margin-bottom:14px; }}
  .rejilla {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; }}
  .tarjeta {{ background:var(--panel); border:1px solid var(--borde); border-radius:10px; padding:16px; }}
  .tarjeta .etiqueta {{ font-size:12px; text-transform:uppercase; letter-spacing:.6px; opacity:.75; }}
  .tarjeta .valor {{ font-size:27px; font-weight:700; margin-top:6px; }}
  .ok {{ color:var(--ok); }} .alerta {{ color:var(--alerta); }} .error {{ color:var(--error); }}
  table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:8px; overflow:hidden; font-size:13px; }}
  th,td {{ padding:9px 12px; text-align:left; border-bottom:1px solid var(--borde); }}
  th {{ background:#0b1220; font-weight:600; }}
  .barra {{ height:9px; background:#0b1220; border-radius:5px; overflow:hidden; margin-top:8px; }}
  .barra > span {{ display:block; height:100%; background:var(--acento); }}
  footer {{ padding:18px 32px; font-size:12px; opacity:.6; border-top:1px solid var(--borde); }}
  code {{ background:#0b1220; padding:2px 6px; border-radius:4px; font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>Dashboard de Metricas de Pruebas</h1>
  <p>Generado el {generado} &nbsp;|&nbsp; Proyecto <code>automatica-pruebas</code> &nbsp;|&nbsp;
     Pipeline de Integracion Continua (JUnit 5 + Cucumber BDD + JMeter)</p>
</header>
<div class="contenedor">

  <div class="seccion">
    <h2>Resumen ejecutivo</h2>
    <div class="rejilla">
      <div class="tarjeta">
        <div class="etiqueta">Pruebas unitarias</div>
        <div class="valor {clase_ut}">{ut_ok}/{ut_total}</div>
        <div class="etiqueta">{ut_fallos} fallo(s) de {ut_total} test(s)</div>
      </div>
      <div class="tarjeta">
        <div class="etiqueta">Escenarios BDD</div>
        <div class="valor {clase_bdd}">{bdd_ok}/{bdd_total}</div>
        <div class="etiqueta">{bdd_fallos} fallo(s) de {bdd_total} escenario(s)</div>
      </div>
      <div class="tarjeta">
        <div class="etiqueta">Cobertura de lineas</div>
        <div class="valor {clase_cov}">{jacoco_pct}%</div>
        <div class="barra"><span style="width:{jacoco_pct}%"></span></div>
      </div>
      <div class="tarjeta">
        <div class="etiqueta">Throughput (TPS)</div>
        <div class="valor {clase_tps}">{jmeter_tps}</div>
        <div class="etiqueta">transacciones/segundo en {jmeter_duracion}s</div>
      </div>
      <div class="tarjeta">
        <div class="etiqueta">Latencia p95</div>
        <div class="valor {clase_p95}">{jmeter_p95} ms</div>
        <div class="etiqueta">p50 {jmeter_p50} ms &middot; p99 {jmeter_p99} ms</div>
      </div>
      <div class="tarjeta">
        <div class="etiqueta">Tasa de error</div>
        <div class="valor {clase_err}">{jmeter_error}%</div>
        <div class="etiqueta">{jmeter_errores} error(es) de {jmeter_muestras} muestras</div>
      </div>
    </div>
  </div>

  <div class="seccion">
    <h2>Pruebas unitarias (JUnit 5)</h2>
    <table>
      <tr><th>Clase de prueba</th><th>Tests</th><th>Fallos</th><th>Errores</th><th>Omitidos</th><th>Tiempo (s)</th></tr>
      {filas_ut}
    </table>
  </div>

  <div class="seccion">
    <h2>Escenarios BDD (Cucumber)</h2>
    <table>
      <tr><th>Caracteristica</th><th>Archivo</th><th>Escenarios</th><th>Aprobados</th><th>Fallidos</th></tr>
      {filas_bdd}
    </table>
  </div>

  <div class="seccion">
    <h2>Metricas de performance (Apache JMeter)</h2>
    <table>
      <tr><th>Metrica</th><th>Valor</th><th>Umbral configurado</th><th>Estado</th></tr>
      {filas_perf}
    </table>
  </div>

</div>
<footer>
  Reportes navegables complementarios: <code>target/allure-report/index.html</code> (Allure),
  <code>target/cucumber-report/cucumber-report.html</code> (Cucumber),
  <code>target/site/jacoco/index.html</code> (JaCoCo) y
  <code>performance/reporte-html/index.html</code> (JMeter).
</footer>
</body>
</html>
"""


def clase(estado):
    return {"ok": "ok", "alerta": "alerta", "error": "error"}.get(estado, "")


def construir_html(datos):
    ut = datos["unitarias"]
    bdd = datos["bdd"]
    cov = datos["cobertura"]
    perf = datos["performance"]

    ut_total = ut["tests"]
    ut_fallos = ut["fallos"] + ut["errores"]
    ut_ok = max(ut_total - ut_fallos - ut["omitidos"], 0)
    clase_ut = clase("ok" if ut_total and ut_fallos == 0 else ("error" if ut_fallos else ""))

    bdd_total = bdd["escenarios"]
    bdd_fallos = bdd["fallidos"]
    bdd_ok = bdd["aprobados"]
    clase_bdd = clase("ok" if bdd_total and bdd_fallos == 0 else ("error" if bdd_fallos else ""))

    pct = cov["porcentaje"]
    clase_cov = clase("ok" if pct >= 70 else ("alerta" if pct >= 50 else "error"))

    tps = perf["tps"]
    clase_tps = clase("ok" if tps >= 50 else ("alerta" if tps >= 20 else "error"))
    clase_p95 = clase("ok" if perf["p95"] <= 500 else ("alerta" if perf["p95"] <= 1000 else "error"))
    clase_err = clase("ok" if perf["tasa_error"] <= 1 else ("alerta" if perf["tasa_error"] <= 5 else "error"))

    filas_ut = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            c["clase"], c["tests"], c["fallos"], c["errores"], c["omitidos"], c["tiempo"])
        for c in ut["clases"]) or "<tr><td colspan='6'>Sin datos</td></tr>"

    filas_bdd = "".join(
        "<tr><td>{}</td><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            c["nombre"], c["archivo"], c["escenarios"], c["aprobados"], c["fallidos"])
        for c in bdd["caracteristicas"]) or "<tr><td colspan='5'>Sin datos</td></tr>"

    filas_perf = "".join([
        "<tr><td>Throughput (TPS)</td><td>{}</td><td>&ge; 50</td><td class='{}'>{}</td></tr>".format(
            tps, clase_tps, "Cumple" if tps >= 50 else "Incumple"),
        "<tr><td>Latencia promedio</td><td>{} ms</td><td>&le; 500 ms</td><td class='{}'>{}</td></tr>".format(
            perf["promedio"], clase("ok" if perf["promedio"] <= 500 else "alerta"),
            "Cumple" if perf["promedio"] <= 500 else "Revisar"),
        "<tr><td>Latencia p95</td><td>{} ms</td><td>&le; 500 ms</td><td class='{}'>{}</td></tr>".format(
            perf["p95"], clase_p95, "Cumple" if perf["p95"] <= 500 else "Incumple"),
        "<tr><td>Latencia p99</td><td>{} ms</td><td>&le; 1000 ms</td><td class='{}'>{}</td></tr>".format(
            perf["p99"], clase("ok" if perf["p99"] <= 1000 else "alerta"),
            "Cumple" if perf["p99"] <= 1000 else "Revisar"),
        "<tr><td>Tasa de error</td><td>{} %</td><td>&le; 1 %</td><td class='{}'>{}</td></tr>".format(
            perf["tasa_error"], clase_err, "Cumple" if perf["tasa_error"] <= 1 else "Incumple"),
        "<tr><td>Muestras ejecutadas</td><td>{}</td><td>&ge; 100</td><td class='{}'>{}</td></tr>".format(
            perf["muestras"], clase("ok" if perf["muestras"] >= 100 else "alerta"),
            "Cumple" if perf["muestras"] >= 100 else "Revisar"),
    ])

    return PLANTILLA.format(
        generado=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        clase_ut=clase_ut, ut_ok=ut_ok, ut_total=ut_total, ut_fallos=ut_fallos,
        clase_bdd=clase_bdd, bdd_ok=bdd_ok, bdd_total=bdd_total, bdd_fallos=bdd_fallos,
        clase_cov=clase_cov, jacoco_pct=pct,
        clase_tps=clase_tps, jmeter_tps=tps, jmeter_duracion=perf["duracion"],
        clase_p95=clase_p95, jmeter_p95=perf["p95"], jmeter_p50=perf["p50"], jmeter_p99=perf["p99"],
        clase_err=clase_err, jmeter_error=perf["tasa_error"], jmeter_errores=perf["errores"],
        jmeter_muestras=perf["muestras"],
        filas_ut=filas_ut, filas_bdd=filas_bdd, filas_perf=filas_perf,
    )


def main():
    parser = argparse.ArgumentParser(description="Genera el dashboard de metricas del pipeline")
    parser.add_argument("--surefire", default="target/surefire-reports")
    parser.add_argument("--cucumber", default="target/cucumber-results.json")
    parser.add_argument("--jacoco", default="target/site/jacoco/jacoco.xml")
    parser.add_argument("--jmeter", default="performance/resultados/login.jtl")
    parser.add_argument("--salida", default="dashboard/metricas.html")
    argumentos = parser.parse_args()

    datos = {
        "unitarias": leer_surefire(argumentos.surefire),
        "bdd": leer_cucumber(argumentos.cucumber),
        "cobertura": leer_jacoco(argumentos.jacoco),
        "performance": leer_jmeter(argumentos.jmeter),
    }

    destino = argumentos.salida
    carpeta = os.path.dirname(destino)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as archivo:
        archivo.write(construir_html(datos))

    print("[dashboard] Reporte generado en: {}".format(destino))
    print("[dashboard] Unitarias: {}/{} | BDD: {}/{} | Cobertura: {}% | TPS: {} | p95: {} ms | Errores: {}%".format(
        datos["unitarias"]["tests"], datos["unitarias"]["tests"] - datos["unitarias"]["fallos"],
        datos["bdd"]["aprobados"], datos["bdd"]["escenarios"], datos["cobertura"]["porcentaje"],
        datos["performance"]["tps"], datos["performance"]["p95"], datos["performance"]["tasa_error"]))


if __name__ == "__main__":
    main()
