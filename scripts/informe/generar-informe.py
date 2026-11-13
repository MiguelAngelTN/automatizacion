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
    # 2. ACTIVIDAD 1
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

    # ==================================================================
    # 3. ACTIVIDAD 2
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

    # ==================================================================
    # 4. CONCLUSIONES
    # ==================================================================
    titulo("4. Conclusiones", nivel=1)
    parrafo("El taller permite observar como la automatizacion de pruebas, cuando se aplica con las buenas practicas discutidas, convierte requerimientos de negocio en criterios verificables, ejecutables, reportados y alertados dentro de un pipeline de integracion continua.")

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
