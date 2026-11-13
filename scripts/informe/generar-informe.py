#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar-informe.py

Construye el documento Word de entrega final del taller:
    entrega/Miguel_Toledo.docx

Cumple el formato exigido por la pauta de evaluacion:
    * Tipo de letra: Arial 12
    * Interlineado: 1,15
    * Nombre del archivo: Miguel_Toledo.docx
"""

import os

import informe_base as base
from informe_base import (AZUL, GRIS, TAMANO, codigo, imagen, numerada, parrafo,
                          salto_pagina, tabla, titulo, vinetas)

DOCUMENTO_SALIDA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "entrega", "Miguel_Toledo.docx")


def main():
    base.configurar_estilos()
    base.configurar_pagina()
    base.numerar_paginas()
    DOCUMENTO = base.documento

    # ==================================================================
    # PORTADA
    # ==================================================================
    for _ in range(10):
        DOCUMENTO.add_paragraph()
    titulo("TALLER DE AUTOMATIZACION DE PRUEBAS", nivel=1)
    parrafo("Evaluacion de la Unidad II - Automatizacion de Pruebas", negrita=True, tamano=13, espacio_antes=2, espacio_despues=2)
    parrafo("Flujo de integracion continua, pruebas BDD, pruebas de performance y reporting", tamano=11, espacio_antes=2, espacio_despues=2)
    for _ in range(8):
        DOCUMENTO.add_paragraph()
    titulo("Autor", nivel=2)
    parrafo("Miguel Toledo", negrita=True)
    parrafo("Miguel8ayea@gmail.com", color=GRIS)
    titulo("Fecha", nivel=2)
    parrafo("13 de noviembre de 2026")

    salto_pagina()

    # ==================================================================
    # 1. OBJETIVOS
    # ==================================================================
    titulo("1. Objetivos del trabajo", nivel=1)
    parrafo("El presente taller tiene por objetivo medir la correcta internalizacion y aplicacion de los conceptos de integracion continua, BDD, pipelines, atomicidad de tests, metricas y reporting, trabajo colaborativo y buenas practicas de automatizacion, abordados durante las unidades I y II del material de estudio.")
    titulo("1.1 Objetivos particulares", nivel=2)
    vinetas([
        "Implementar un flujo basico de integracion continua para un proyecto Java con Maven y JUnit 5.",
        "Construir una suite de pruebas unitarias atomicas e independientes.",
        "Diseñar escenarios de BDD con Cucumber a partir de una sesion de los Three Amigos.",
        "Configurar una prueba de performance con Apache JMeter y definir indicadores de SLO.",
        "Generar reportes navegables (Allure, Cucumber, JaCoCo, JMeter) y un dashboard de metricas.",
        "Definir alertas automaticas ante fallos o degradaciones detectadas por las pruebas.",
    ])

    salto_pagina()

    # ==================================================================
    # 2. ACTIVIDAD 1: PRUEBAS UNITARIAS Y FLUJO DE INTEGRACION CONTINUA
    # ==================================================================
    titulo("2. Actividad 1: Pruebas unitarias y flujo de integracion continua", nivel=1)
    titulo("2.1 Inicializacion del repositorio Git", nivel=2)
    parrafo("La primera actividad requiere documentar la creacion de ramas y commits frecuentes con mensajes claros. Los comandos ejecutados y los resultados se resumen en la siguiente tabla:")
    tabla(
        ["Accion", "Comando", "Resultado"],
        [
            ["Inicializar repositorio", "git init", "Repositorio creado"],
            ["Crear rama feature", "git checkout -b feature/pruebas-unitarias-junit", "Rama creada"],
            ["Agregar archivos", "git add .", "Archivos indexados"],
            ["Commit inicial", 'git commit -m "chore: inicializa proyecto Maven"', "Commit creado"],
            ["Historial", "git log --oneline -n 10", "Ramas y commits visibles"],
        ],
        anchos=[5.0, 6.0, 5.0],
    )
    imagen("reporte-allure.png", pie="Reporte navegable generado por Allure durante la ejecucion local del pipeline.")

    salto_pagina()

    titulo("2.2 Suite de pruebas unitarias atomicas e independientes", nivel=2)
    parrafo("Se construyo una suite de pruebas unitarias con JUnit 5 y AssertJ, aplicando las siguientes decisiones de diseno:")
    vinetas([
        "Alta cohesion: cada clase de pruebas cubre una sola unidad de negocio (CalculadoraTest, ServicioAutenticacionTest, CarritoTest).",
        "Bajo acoplamiento: cada test crea su propia instancia y no depende del estado de otros tests.",
        "Atomicidad: cada test verifica una sola regla de negocio (una asercion conceptual por test).",
        "Independencia: sin estado compartido entre tests; el orden de ejecucion no afecta el resultado.",
        "Sin framework de inyeccion: las clases del dominio son POJOs puros sin estado global.",
    ])
    parrafo("Como quality gate de cobertura se aplico JaCoCo con un umbral minimo del 70 por ciento sobre el bundle de codigo, configurado en el pom.xml. Cuando la cobertura queda por debajo del umbral, el pipeline falla y bloquea la integracion.")

    salto_pagina()

    titulo("2.3 Reportes y pipeline de integracion continua", nivel=2)
    parrafo("El flujo de integracion continua se implemento con GitHub Actions (workflow principal) y Jenkins (alternativa declarativa), ambos ejecutando el mismo comando: mvn clean verify. El job de verificacion compila, ejecuta las pruebas unitarias y BDD, aplica el quality gate de JaCoCo y publica los reportes navegables.")
    vinetas([
        "GitHub Actions: dispara en push/pull_request a main y develop; publica artefactos de reportes.",
        "Jenkins: alternativa con etapas Checkout, pruebas unitarias, BDD, cobertura, performance y dashboard.",
        "Local: scripts/ci-local.ps1 (Windows) y scripts/ci-local.sh (Linux/macOS) reproducen los tres jobs del pipeline.",
    ])

    salto_pagina()

    # ==================================================================
    # 3. ACTIVIDAD 2: BDD, PERFORMANCE, REPORTING Y ALERTAS
    # ==================================================================
    titulo("3. Actividad 2: BDD, performance, reporting y alertas", nivel=1)
    titulo("3.1 Sesion Three Amigos", nivel=2)
    parrafo("La sesion se realizo con los tres roles: Analista de Negocio, QA/Tester y Desarrollador. Se definieron historias de usuario y criterios de aceptacion en formato Given/When/Then, junto con ejemplos concretos.")
    vinetas([
        "Rol Analista de Negocio: define el que (reglas de negocio) y por que (valor).",
        "Rol QA/Tester: define como se verifica (criterios de aceptacion observables).",
        "Rol Desarrollador: define como se construye (contratos, tipos de dato, validaciones).",
    ])
    salto_pagina()

    titulo("3.2 Automatizacion BDD con Cucumber", nivel=2)
    parrafo("Los criterios de aceptacion definidos en la sesion se convirtieron en escenarios Gherkin en los archivos features/autenticacion.feature y features/compra.feature, con step definitions en Java (Cucumber Expressions + PicoContainer). Se aplicaron escenarios con etiquetas @bdd, @critico, @smoke y @regresion.")
    vinetas([
        "Gherkin en idioma del negocio con sintaxis valida para Cucumber 7.",
        "Step definitions con tipos estandar {string}, {int}, {float}; valores con espacios entre comillas.",
        "Contexto compartido por escenario (PicoContainer): aislamiento garantizado.",
        "Reporte navegable HTML de Cucumber en target/cucumber-report/cucumber-report.html.",
        "Allure integra los escenarios BDD al reporte unificado.",
    ])

    salto_pagina()

    titulo("3.3 Prueba de performance con Apache JMeter", nivel=2)
    parrafo("Se eligio Apache JMeter (Recomendado) y se aplico un perfil de carga sobre el endpoint POST /api/login del sistema bajo prueba (ServidorPerformance).")
    tabla(
        ["Parametro", "Valor"],
        [
            ["Hilos (usuarios virtuales)", "20"],
            ["Ramp-up", "5 segundos"],
            ["Duracion", "15 segundos"],
            ["Think time", "100 ms"],
            ["Asercion", "Codigo de respuesta 200"],
        ],
    )
    parrafo("Las metricas monitorizadas fueron TPS, latencias (minima, media, p50, p90, p95, p99) y tasa de error, con umbrales configurados en monitoreo/umbrales.yml: TPS >= 50, p95 <= 500 ms, p99 <= 1000 ms, tasa de error <= 1 por ciento y muestras minimas de 100. El resultado final de la ejecucion fue satisfactorio.")

    salto_pagina()

    titulo("3.4 Dashboard y alertas automaticas", nivel=2)
    parrafo("El dashboard de metricas se genero con scripts/generar-dashboard.py a partir de los resultados de JUnit 5, Cucumber, JaCoCo y JMeter, y los umbrales se evaluaron con scripts/verificar-umbrales.py. Las reglas de alerta se definieron en monitoreo/alertas.yml (formato Prometheus/Alertmanager). Cuando un umbral se incumple, el script devuelve codigo de salida distinto de cero, lo que hace fallar el pipeline y dispara la alerta automaticamente.")
    parrafo("Como complemento se dispone del stack de observabilidad con InfluxDB y Grafana (monitoreo/docker-compose.yml y monitoreo/grafana-dashboard.json) para la visualizacion continua de las metricas.")

    salto_pagina()

    # ==================================================================
    # 4. CONCLUSIONES
    # ==================================================================
    titulo("4. Conclusiones", nivel=1)
    parrafo("El taller permite observar como la automatizacion de pruebas, cuando se aplica con las buenas practicas discutidas, convierte requerimientos de negocio en criterios verificables, ejecutables, reportados y alertados dentro de un pipeline de integracion continua.")
    parrafo("Se logro un pipeline completo y reproducible: desde el repositorio Git hasta el reporte de performance, pasando por pruebas unitarias, BDD, cobertura y dashboard. Todos los umbrales definidos se cumplen en la ultima ejecucion, y la documentacion del proceso quedo registrada en el repositorio.")

    salto_pagina()

    # ==================================================================
    # 5. ANEXOS
    # ==================================================================
    titulo("5. Anexos", nivel=1)
    titulo("5.1 Comandos principales", nivel=2)
    codigo(
        'mvn clean verify\n'
        'mvn clean test -Dgroups=unit\n'
        'mvn verify -Dgroups=bdd -Djacoco.skip=true\n'
        'mvn clean package -DskipTests\n'
        'jmeter -n -t performance/performance-login.jmx -l performance/resultados/login.jtl -e -o performance/reporte-html\n',
        titulo_opcional="Comandos de build, pruebas y performance.",
    )
    titulo("5.2 Estructura del proyecto", nivel=2)
    codigo(
        'src/main/java/com/empresa/pruebas/modelo/   Codigo de negocio\n'
        'src/test/java/com/empresa/pruebas/            Pruebas unitarias y step definitions\n'
        'src/test/resources/features/                 Archivos Gherkin\n'
        'performance/                                 Planes de carga JMeter\n'
        'scripts/                                     Utilidades del pipeline\n'
        'monitoreo/                                   Umbrales y alertas\n'
        'docs/                                        Documentacion del taller',
    )

    base.documento.save(DOCUMENTO_SALIDA)
    print("[informe] Documento generado en: {}".format(DOCUMENTO_SALIDA))
    print("[informe] Tamano: {} bytes".format(os.path.getsize(DOCUMENTO_SALIDA)))


if __name__ == "__main__":
    main()
