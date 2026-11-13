#!/usr/bin/env bash
# ===================================================================
# capturar-reportes.sh
# Genera capturas PNG de los reportes navegables (Allure, Cucumber,
# JaCoCo, JMeter y el dashboard de metricas) usando Chrome en modo
# headless. Cada imagen se guarda en evidencia/capturas/.
# ===================================================================
set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

DESTINO="evidencia/capturas"
mkdir -p "$DESTINO"

CHROME=""
for ruta in \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "$(command -v google-chrome || true)" \
  "$(command -v chromium || true)"; do
  if [ -n "$ruta" ] && [ -f "$ruta" ]; then CHROME="$ruta"; break; fi
done

if [ -z "$CHROME" ]; then
  echo "ERROR: no se encontro Chrome/Chromium para capturar los reportes."
  exit 1
fi

capturar() {
  local archivo="$1"
  local salida="$2"
  local ancho="${3:-1600}"
  local alto="${4:-1100}"
  if [ ! -f "$archivo" ]; then
    echo "  --  $archivo (no existe, se omite)"
    return
  fi
  local uri
  uri="$(python -c "import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_uri())" "$archivo")"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
            --screenshot="$DESTINO/$salida" --window-size="$ancho,$alto" "$uri" > /dev/null 2>&1
  if [ -f "$DESTINO/$salida" ]; then
    echo "  OK  $DESTINO/$salida"
  else
    echo "  !!  no se pudo capturar $archivo"
  fi
}

echo "Generando capturas de los reportes navegables..."
capturar "target/allure-report/index.html"              "reporte-allure.png"        1600 1100
capturar "target/cucumber-report/cucumber-report.html"  "reporte-cucumber.png"      1600 1400
capturar "target/site/jacoco/index.html"                "reporte-jacoco.png"        1600 1100
capturar "performance/reporte-html/index.html"          "reporte-jmeter.png"        1600 1400
capturar "dashboard/metricas.html"                      "dashboard-metricas.png"    1600 1300

echo "Listo."
