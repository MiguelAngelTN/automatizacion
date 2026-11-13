#!/usr/bin/env bash
# ===================================================================
# ci-local.sh
# Ejecucion LOCAL del pipeline definido en .github/workflows/ci.yml
# (equivalente a scripts/ci-local.ps1 para Linux / macOS / runners Linux)
# ===================================================================
set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

LOG_DIR="evidencia/logs"
mkdir -p "$LOG_DIR"

echo ""
echo "==============================================================="
echo "  JOB 1/3 - Verificar (JUnit 5 + BDD + cobertura)"
echo "==============================================================="

{
  echo "### java -version"; java -version 2>&1
  echo ""; echo "### mvn -version"; mvn -v 2>&1
  echo ""; echo "### git --version"; git --version
} > "$LOG_DIR/00-entorno.log"

mvn -B clean verify 2>&1 | tee "$LOG_DIR/01-mvn-verify.log"
CODIGO=${PIPESTATUS[0]}
if [ "$CODIGO" -ne 0 ]; then
  echo "FALLO en la etapa de verificacion (codigo $CODIGO)"
  exit "$CODIGO"
fi

if [ "${1:-}" != "--saltar-performance" ]; then
  echo ""
  echo "==============================================================="
  echo "  JOB 2/3 - Performance (Apache JMeter)"
  echo "==============================================================="

  mvn -B clean package -DskipTests > /dev/null 2>&1
  java -cp target/classes com.empresa.pruebas.performance.ServidorPerformance 8080 \
      > "$LOG_DIR/02-servidor.log" 2>&1 &
  PID_SERVIDOR=$!

  LISTO=0
  for i in $(seq 1 30); do
    sleep 1
    if curl -sf http://127.0.0.1:8080/api/salud > /dev/null; then LISTO=1; break; fi
  done
  if [ "$LISTO" -ne 1 ]; then
    echo "ERROR: el servidor bajo prueba no respondio a tiempo"
    kill "$PID_SERVIDOR" 2>/dev/null
    exit 1
  fi
  echo "Servidor bajo prueba listo (PID $PID_SERVIDOR)"

  mkdir -p performance/resultados
  rm -rf performance/reporte-html
  jmeter -n -t performance/performance-login.jmx \
      -l performance/resultados/login.jtl \
      -e -o performance/reporte-html 2>&1 | tee "$LOG_DIR/03-jmeter.log"
  CODIGO=${PIPESTATUS[0]}

  kill "$PID_SERVIDOR" 2>/dev/null
  if [ "$CODIGO" -ne 0 ]; then
    echo "FALLO en la etapa de performance (codigo $CODIGO)"
    exit "$CODIGO"
  fi
fi

echo ""
echo "==============================================================="
echo "  JOB 3/3 - Dashboard de metricas y alertas"
echo "==============================================================="

python3 scripts/generar-dashboard.py \
    --surefire target/surefire-reports \
    --cucumber target/cucumber-results.json \
    --jacoco target/site/jacoco/jacoco.xml \
    --jmeter performance/resultados/login.jtl \
    --salida dashboard/metricas.html 2>&1 | tee "$LOG_DIR/04-dashboard.log"

python3 scripts/verificar-umbrales.py \
    --jmeter performance/resultados/login.jtl \
    --salida dashboard/estado-umbrales.json 2>&1 | tee "$LOG_DIR/05-umbrales.log"
exit $?
