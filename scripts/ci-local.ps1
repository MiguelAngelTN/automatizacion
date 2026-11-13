<#
    ci-local.ps1

    Ejecucion LOCAL del pipeline definido en .github/workflows/ci.yml.
    Reproduce paso a paso los mismos jobs y comandos que ejecuta el runner de
    GitHub Actions, de modo que se pueda validar el pipeline sin depender del
    servicio en la nube.

    Uso:
        powershell -ExecutionPolicy Bypass -File scripts/ci-local.ps1
#>

[CmdletBinding()]
param(
    [switch]$SaltarPerformance,
    [string]$Directorio = (Get-Location).Path
)

$ErrorActionPreference = 'Continue'
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

$logDir = Join-Path $raiz 'evidencia\logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Escribir([string]$mensaje) {
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Cyan
    Write-Host "  $mensaje" -ForegroundColor Cyan
    Write-Host "===============================================================" -ForegroundColor Cyan
}

function Ejecutar([string]$comando, [string]$archivoLog) {
    Write-Host "`n> $comando" -ForegroundColor Yellow
    Write-Host "  (salida completa en $archivoLog)" -ForegroundColor DarkGray
    $salida = & cmd.exe /c "$comando 2>&1"
    $codigo = $LASTEXITCODE
    $salida | Out-File -FilePath $archivoLog -Encoding utf8
    $salida | Select-Object -Last 25 | Write-Host
    return $codigo
}

Escribir "JOB 1/3 - Verificar (JUnit 5 + BDD + cobertura)"

Write-Host "`n> Versiones del entorno" -ForegroundColor Yellow
$entorno = @()
$entorno += "java -version`n$((& java -version 2>&1) -join "`n")"
$entorno += "mvn -version`n$((& mvn -v 2>&1) -join "`n")"
$entorno += "git --version -> $(& git --version)"
$entorno -join "`n`n" | Out-File (Join-Path $logDir '00-entorno.log') -Encoding utf8
$entorno | Write-Host

$codigo = Ejecutar 'mvn -B clean verify' (Join-Path $logDir '01-mvn-verify.log')
if ($codigo -ne 0) {
    Escribir "FALLO en la etapa de verificacion (codigo $codigo). El pipeline se detiene aqui."
    exit $codigo
}

Escribir "JOB 1/3 - Reportes generados"
foreach ($reporte in @('target/surefire-reports', 'target/cucumber-report', 'target/allure-report', 'target/site/jacoco')) {
    if (Test-Path $reporte) {
        Write-Host "  OK  $reporte" -ForegroundColor Green
    } else {
        Write-Host "  --  $reporte (no generado)" -ForegroundColor DarkYellow
    }
}

if (-not $SaltarPerformance) {
    Escribir "JOB 2/3 - Performance (Apache JMeter)"

    & mvn -B clean package -DskipTests | Out-Null

    $servidor = Start-Process -FilePath 'java' `
        -ArgumentList '-cp', 'target/classes', 'com.empresa.pruebas.performance.ServidorPerformance', '8080' `
        -RedirectStandardOutput (Join-Path $logDir '02-servidor.log') `
        -RedirectStandardError (Join-Path $logDir '02-servidor-error.log') `
        -PassThru -NoNewWindow

    Write-Host "  Servidor bajo prueba iniciado (PID $($servidor.Id)); esperando..." -ForegroundColor Yellow
    $listo = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        try {
            $respuesta = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/api/salud' -UseBasicParsing -TimeoutSec 2
            if ($respuesta.StatusCode -eq 200) { $listo = $true; break }
        } catch { }
    }
    if (-not $listo) {
        Write-Host "  ERROR: el servidor no respondio a tiempo" -ForegroundColor Red
        Stop-Process -Id $servidor.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
    Write-Host "  Servidor listo: $((Invoke-WebRequest -Uri 'http://127.0.0.1:8080/api/salud' -UseBasicParsing).Content)" -ForegroundColor Green

    New-Item -ItemType Directory -Force -Path 'performance\resultados' | Out-Null
    if (Test-Path 'performance\reporte-html') { Remove-Item 'performance\reporte-html' -Recurse -Force }

    $codigoPerf = Ejecutar 'jmeter -n -t performance/performance-login.jmx -l performance/resultados/login.jtl -e -o performance/reporte-html' (Join-Path $logDir '03-jmeter.log')

    Stop-Process -Id $servidor.Id -Force -ErrorAction SilentlyContinue
    Write-Host "  Servidor detenido." -ForegroundColor DarkGray

    if ($codigoPerf -ne 0) {
        Escribir "FALLO en la etapa de performance (codigo $codigoPerf)"
        exit $codigoPerf
    }
}

Escribir "JOB 3/3 - Dashboard de metricas y alertas"

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = 'python3' }

& $python 'scripts/generar-dashboard.py' `
    --surefire 'target/surefire-reports' `
    --cucumber 'target/cucumber-results.json' `
    --jacoco 'target/site/jacoco/jacoco.xml' `
    --jmeter 'performance/resultados/login.jtl' `
    --salida 'dashboard/metricas.html' 2>&1 | Tee-Object -FilePath (Join-Path $logDir '04-dashboard.log')

& $python 'scripts/verificar-umbrales.py' `
    --jmeter 'performance/resultados/login.jtl' `
    --salida 'dashboard/estado-umbrales.json' 2>&1 | Tee-Object -FilePath (Join-Path $logDir '05-umbrales.log')
$codigoUmbrales = $LASTEXITCODE

Escribir "PIPELINE FINALIZADO"
Write-Host "  Reporte navegable Allure : target/allure-report/index.html"
Write-Host "  Reporte navegable Cucumber: target/cucumber-report/cucumber-report.html"
Write-Host "  Cobertura JaCoCo          : target/site/jacoco/index.html"
Write-Host "  Reporte JMeter           : performance/reporte-html/index.html"
Write-Host "  Dashboard de metricas    : dashboard/metricas.html"
Write-Host "  Estado de umbrales       : dashboard/estado-umbrales.json"
exit $codigoUmbrales
