# automatica-pruebas — Pipeline de Integración Continua, BDD y Performance

**Proyecto:** profesionalización del proceso de pruebas automatizadas de una empresa
de e-commerce (Actividades 1 y 2 — *Evaluación Unidad II de Automatización de Pruebas*).

**Autor:** Miguel Toledo

---

## 1. Objetivos

1. Implementar un flujo completo de **integración continua** para un proyecto Java:
   gestión de versiones con Git, dependencias con Maven, pruebas automatizadas con
   JUnit 5 y un pipeline que compila y ejecuta los tests en cada `push`/`pull request`.
2. Generar **reportes navegables** accesibles para todo el equipo (Allure, Cucumber HTML,
   JaCoCo y dashboard de JMeter).
3. Elevar la calidad con **BDD (Cucumber)**: sesión *Three Amigos*, criterios de aceptación
   en Gherkin, *step definitions* en Java e integración de los escenarios en el pipeline.
4. Incorporar **pruebas de performance** con Apache JMeter, definiendo los indicadores
   monitorizados (TPS, latencia, errores) y un **dashboard** que los consolida.
5. Definir **alertas automáticas** ante fallos o degradaciones detectadas por las pruebas.

---

## 2. Requisitos del entorno

| Herramienta | Versión | Uso |
|---|---|---|
| JDK (Eclipse Temurin) | 17 | Compilación y ejecución de las pruebas |
| Apache Maven | 3.9.x | Gestión de dependencias y ciclo de build |
| Apache JMeter | 5.6.3 | Prueba de performance y dashboard HTML |
| Git | 2.4x+ | Gestión de versiones |
| Python | 3.10+ | Generación del dashboard consolidado y verificación de umbrales |

> En este taller se instalaron versiones *portables* (JDK y Maven) en el equipo del
> autor y se configuraron `JAVA_HOME` y el `PATH` del usuario.

Verificación rápida del entorno:

```bash
java -version
mvn -version
jmeter --version
git --version
python --version
```

---

## 3. Estructura del proyecto

```
automatica-pruebas/
│
├── pom.xml                       # Dependencias y plugins (Surefire, JaCoCo, Allure)
├── README.md                     # Este documento
├── Jenkinsfile                   # Pipeline alternativo para Jenkins
├── .gitignore                    # Exclusiones de artefactos, IDE y secretos
│
├── .github/
│   └── workflows/ci.yml          # Pipeline de GitHub Actions (CI/CD)
│
├── src/main/java/com/empresa/pruebas/
│   ├── modelo/                   # Código de negocio (fuente de la prueba)
│   │   ├── Calculadora.java           # Operaciones aritméticas (sin estado)
│   │   ├── Usuario.java               # Credenciales y estado de la cuenta
│   │   ├── Token.java                 # Sesión emitida al autenticarse
│   │   ├── ServicioAutenticacion.java # Reglas de login
│   │   ├── Producto.java              # Ítem del catálogo
│   │   ├── Carrito.java               # Cálculo de totales y descuentos
│   │   ├── Pedido.java                # Pedido confirmado
│   │   ├── ServicioPedidos.java       # Confirmación de compras
│   │   └── ExcepcionAutenticacion.java
│   └── performance/
│       └── ServidorPerformance.java  # Sistema bajo prueba para JMeter
│
├── src/test/java/com/empresa/pruebas/
│   ├── modelo/                   # Pruebas unitarias atómicas (JUnit 5)
│   │   ├── CalculadoraTest.java           (7 pruebas)
│   │   ├── ServicioAutenticacionTest.java (6 pruebas)
│   │   └── CarritoTest.java               (8 pruebas)
│   └── bdd/pasos/                # Step definitions (Cucumber + PicoContainer)
│       ├── Contexto.java          # Estado compartido por escenario
│       ├── PasosAutenticacion.java
│       └── PasosCompra.java
│
├── src/test/resources/
│   ├── features/                 # Archivos Gherkin
│   │   ├── autenticacion.feature
│   │   └── compra.feature
│   ├── cucumber.properties        # Plugins (pretty, html, json) y ejecución paralela
│   └── junit-platform.properties # Configuración de JUnit Platform y de Cucumber
│
├── performance/
│   └── performance-login.jmx     # Plan de carga de JMeter
│
├── scripts/
│   ├── ci-local.ps1              # Pipeline local para Windows
│   ├── ci-local.sh               # Pipeline local para Linux/macOS
│   ├── generar-dashboard.py      # Dashboard consolidado de métricas
│   └── verificar-umbrales.py     # Evaluación de SLA y disparo de alertas
│
├── monitoreo/
│   ├── umbrales.yml              # Fuente de verdad de los SLA
│   ├── alertas.yml               # Reglas de alerta (formato Prometheus)
│   └── docker-compose.yml        # InfluxDB + Grafana (stack de observabilidad)
│
├── evidencia/                    # Capturas de pantalla y logs de la ejecución
└── dashboard/                    # Dashboard HTML generado (no versionado)
```

---

## 4. Comandos principales

### 4.1 Compilar y ejecutar todo (unitaria + BDD + cobertura + reportes)

```bash
mvn clean verify
```

### 4.2 Ejecutar solo las pruebas unitarias

```bash
mvn clean test -Dgroups=unit
```

### 4.3 Ejecutar solo los escenarios BDD

```bash
mvn clean verify -Dgroups=bdd -Djacoco.skip=true
```

### 4.4 Generar los reportes navegables

| Reporte | Ruta | Contenido |
|---|---|---|
| Allure (unificado) | `target/allure-report/index.html` | JUnit 5 + BDD en un solo panel |
| Cucumber | `target/cucumber-report/cucumber-report.html` | Escenarios, pasos y etiquetas |
| JaCoCo | `target/site/jacoco/index.html` | Cobertura de código por clase y línea |
| JMeter | `performance/reporte-html/index.html` | Dashboard de performance |
| Métricas consolidadas | `dashboard/metricas.html` | Resumen funcional + performance |

### 4.5 Ejecutar la prueba de performance

```bash
# 1) Compilar el sistema bajo prueba
mvn clean package -DskipTests

# 2) Levantar el servidor (en otra terminal)
java -cp target/classes com.empresa.pruebas.performance.ServidorPerformance 8080

# 3) Lanzar el plan de carga
jmeter -n -t performance/performance-login.jmx \
       -l performance/resultados/login.jtl \
       -e -o performance/reporte-html
```

### 4.6 Ejecutar el pipeline completo en local

```bash
powershell -ExecutionPolicy Bypass -File scripts/ci-local.ps1   # Windows
./scripts/ci-local.sh                                          # Linux / macOS
```

El script reproduce **exactamente** los tres *jobs* de `.github/workflows/ci.yml`:
verificación, performance y dashboard con alertas.

### 4.7 Generar el dashboard y verificar los umbrales

```bash
python scripts/generar-dashboard.py --salida dashboard/metricas.html
python scripts/verificar-umbrales.py --salida dashboard/estado-umbrales.json
```

`verificar-umbrales.py` devuelve código de salida `1` cuando un SLA se incumple: eso
hace fallar el pipeline y dispara la alerta automática.

---

## 5. Gestión de versiones (Git)

**Historial inicial.** El proyecto se inicializó en `main` con un primer commit que
incluye el código base, la suite de pruebas, los escenarios BDD y el plan de
performance, seguido de commits de limpieza y de actualización de la evidencia:

```bash
git init
git add .
git commit -m "chore: inicializacion del proyecto automatica-pruebas (...)"
git commit -m "chore: limpiar artefactos temporales de Python del repositorio"
git commit -m "docs: actualizar evidencia final del pipeline y documento de entrega"
```

**Flujo por ramas (a partir de la revisión final).** Cada cambio posterior se hizo en
una rama de corta vida y se integró a `main` con un merge explícito (`--no-ff`), de
modo que el historial muestra qué cambio pertenece a qué rama:

```bash
git checkout -b docs/corregir-documentacion      # erratas, trazabilidad, README
git checkout -b feature/simulacion-alertas       # script y evidencia de alerta simulada
git checkout main && git merge --no-ff <rama>
git log --oneline --graph --all                  # verificación del historial
```

Convenciones de mensajes (Conventional Commits): `feat`, `fix`, `test`, `docs`,
`chore`, `refactor`, `perf`, `build`, `ci`. Esto permite generar el *changelog* de forma
automática y saber de un vistazo qué cambió en cada commit.

Modelo de ramas propuesto para el equipo (en este taller se aplicó solo `main` más
ramas de corta vida):

```
main        : rama estable, recibe cambios vía Pull Request
develop     : integración continua de features
feature/*   : una por funcionalidad
hotfix/*    : correcciones urgentes sobre main
```

---

## 6. Pipeline de Integración Continua

### 6.1 GitHub Actions (`.github/workflows/ci.yml`)

**Disparadores:** `push` a `main`/`develop`, `pull_request` hacia `main`/`develop`,
`workflow_dispatch` manual y etiquetas `v*`.

| Job | Descripción | Artefactos generados |
|---|---|---|
| `verificar` | `mvn -B clean verify`: compila, ejecuta JUnit 5 + Cucumber, aplica el *quality gate* de JaCoCo (≥ 70 % de cobertura) y genera Allure | `target/surefire-reports/`, `target/cucumber-report/`, `target/allure-report/`, `target/site/jacoco/` |
| `performance` | Levanta el sistema bajo prueba y ejecuta el plan de carga con JMeter | `performance/reporte-html/`, `performance/resultados/` |
| `dashboard-y-alertas` | Consolida métricas, evalúa los SLA y publica el resumen en la Pull Request | `dashboard/metricas.html`, `dashboard/estado-umbrales.json` |

Características del pipeline:

- **Ejecución concurrente controlada** (`concurrency` con `cancel-in-progress`): una
  Push nueva cancela la anterior del mismo *branch*.
- **Caché de Maven** (`setup-java` con `cache: maven`) para acelerar los builds.
- **Publicación de artefactos** (`upload-artifact`) aunque el build falle
  (`if: always()`), para poder diagnosticar sin volver a ejecutar.
- **Calidad de código**: JaCoCo con regla `BUNDLE / LINE / COVEREDRATIO ≥ 0.70`; si la
  cobertura baja del umbral, el pipeline falla y bloquea la integración.
- **Resumen en la Pull Request** mediante `$GITHUB_STEP_SUMMARY`.

### 6.2 Jenkins (`Jenkinsfile`)

Pipeline declarativo equivalente con las etapas *Checkout*, *Pruebas unitarias*,
*Pruebas BDD*, *Cobertura*, *Performance* y *Dashboard y alertas*. Publica los reportes
HTML con el plugin *HTML Publisher*, los resultados JUnit con el plugin *JUnit* y
envía un aviso por correo/Slack en el bloque `post { failure { ... } }`.

---

## 7. Pruebas unitarias: atomicidad e independencia

Cada test verifica **una única regla de negocio** y construye su propio *fixture*:

```java
@Test
@DisplayName("La resta de dos valores devuelve el resultado correcto")
void restaDevuelveElResultadoCorrecto() {
    // Arrange
    Calculadora calculadora = new Calculadora();   // instancia propia: sin estado compartido
    // Act
    double resultado = calculadora.resta(10.0d, 4.0d);
    // Assert
    assertThat(resultado).isEqualTo(6.0d);
}
```

Decisiones de diseño:

| Decisión | Justificación |
|---|---|
| **Alta cohesión** | Cada clase de test cubre una sola unidad de negocio (`CalculadoraTest`, `CarritoTest`, `ServicioAutenticacionTest`). |
| **Bajo acoplamiento** | Ningún test depende del estado dejado por otro; la instancia se crea dentro del test o en un `@BeforeEach`. |
| **Sin `@BeforeAll` con estado mutable** | Se evita el orden de ejecución como factor de éxito o fallo. |
| **Una aserción conceptual por test** | Permite identificar con precisión qué regla se rompió. |
| **Assertions de AssertJ** | Mensajes de fallo descriptivos (`as("Se esperaba un token válido")`). |
| **`@DisplayName` en español** | El reporte navegable muestra el comportamiento esperado en lenguaje natural. |
| **`@Tag("unit")`** | Permite separar la suite unitaria de la BDD en el pipeline. |

**Resultado:** 27 pruebas unitarias, todas en verde y sin dependencias entre sí.

---

## 8. BDD (Cucumber)

### 8.1 Sesión *Three Amigos*

Documentada en [`docs/three-amigos.md`](docs/three-amigos.md): roles, preguntas,
historias de usuario, criterios de aceptación en formato *Given/When/Then* y ejemplos
discutidos con el equipo.

### 8.2 Características y escenarios

| Archivo | Escenarios | Scenario Outline | Ejemplos |
|---|---|---|---|
| `autenticacion.feature` | 2 escenarios + 1 esquema | 1 | 3 filas |
| `compra.feature` | 2 escenarios + 1 esquema | 1 | 3 filas |

Total: **10 escenarios BDD** (contando la expansión de los *Scenario Outline*).

Ejemplo de *Scenario Outline*:

```gherkin
@regresion
Esquema del escenario: Aplicación de descuentos por código
  Dado que el carrito está vacío
  Cuando agrego el producto "X-1" con precio <precio> al carrito
  Y aplico el código de descuento "<codigo>"
  Entonces el total del carrito es <total>

  Ejemplos:
    | codigo       | precio | total  |
    | NINGUNO      | 100000 | 100000 |
    | BIENVENIDA10 | 100000 | 90000  |
    | VERANO20     | 100000 | 80000  |
```

### 8.3 Step definitions

- Java + Cucumber 7 + **PicoContainer** para inyección de dependencias: el `Contexto`
  (estado del escenario) se instancia una vez por escenario y se inyecta en los pasos,
  lo que garantiza el aislamiento entre escenarios.
- Se usan **Cucumber Expressions** con los tipos estándar (`{string}`, `{int}`, `{float}`).
- Un hook `@Before` reinicia el estado antes de cada escenario.
- Reporte navegable oficial de Cucumber: `target/cucumber-report/cucumber-report.html`.
- Además, **Allure** agrega los escenarios BDD al reporte unificado de la suite.

### 8.4 Integración con el pipeline

Los escenarios BDD se ejecutan en el mismo comando que las pruebas unitarias
(`mvn verify`) porque ambos motores comparten la plataforma JUnit 5; el job
`verificar` publica el reporte navegable como artefacto.

---

## 9. Pruebas de performance (Apache JMeter)

**Funcionalidad elegida:** `POST /api/login` — el endpoint más crítico del negocio
(autenticación de usuarios), donde un aumento de latencia impacta directamente el
ingreso de clientes.

### 9.1 Perfil de carga

| Parámetro | Valor | Justificación |
|---|---|---|
| Hilos (usuarios virtuales) | 20 | Simula usuarios concurrentes realistas sin saturar el equipo del autor |
| *Ramp-up* | 5 s | La carga sube gradualmente, evitando un pico artificial |
| Duración | 15 s | Ventana suficiente para estabilizar las métricas |
| *Think time* | 100 ms | Evita que el cliente virtual sea infinitamente rápido |
| Aserción | Código de respuesta `200` | Cada petición fallida se contabiliza como error |

### 9.2 Indicadores monitorizados

| Indicador | Definición | Umbral (SLA) |
|---|---|---|
| **TPS** (Throughput) | Transacciones por segundo sostenidas | ≥ 50 |
| **Latencia promedio** | Tiempo medio de respuesta | ≤ 500 ms |
| **Latencia p95** | Percentil 95 de los tiempos de respuesta | ≤ 500 ms |
| **Latencia p99** | Percentil 99 (cola de latencia) | ≤ 1000 ms |
| **Tasa de error** | Muestras fallidas / total | ≤ 1 % |
| **Muestras** | Volumen mínimo para que las métricas sean representativas | ≥ 100 |

> **Por qué p95 y p99:** el promedio oculta la experiencia de los usuarios en el peor
> caso. Los percentiles muestran cuántos usuarios-Earthxguelen la cola de latencia, que
> es justamente donde aparecen los incidentes en producción.

### 9.3 Sistema bajo prueba

`ServidorPerformance` expone un servidor HTTP mínimo (incluido en el JDK, sin
dependencias externas) con los endpoints `/api/salud`, `/api/suma`, `/api/login` y
`/api/pedidos`, para que la prueba de performance sea reproducible en cualquier
máquina.

---

## 10. Dashboard de métricas

`scripts/generar-dashboard.py` consolida en un único HTML autocontenido:

- Pruebas unitarias: total, aprobados, fallidos, omitidos y tiempo por clase.
- Escenarios BDD: total, aprobados y fallidos por característica.
- Cobertura de código (JaCoCo).
- Performance: TPS, latencias (mínima, media, p50, p90, p95, p99), tasa de error.

Además se entrega la configuración de la stack de observabilidad
(`monitoreo/docker-compose.yml` con InfluxDB + Grafana) paraenvironments con Docker,
y las reglas de alerta en `monitoreo/alertas.yml`.

---

## 11. Alertas automáticas

Las alertas se definen en `monitoreo/alertas.yml` (formato compatible con
Prometheus/Alertmanager) y son evaluadas en cada ejecución por
`scripts/verificar-umbrales.py`:

| Severidad | Ejemplo | Canal |
|---|---|---|
| **Crítica** | Fallo de una prueba unitaria, TPS < 50, tasa de error > 1 % | Correo al jefe de QA + Slack `#qa-alertas` + apertura de incidente |
| **Alta** | Latencia p95 > 500 ms, cobertura < 70 % | Slack `#qa-alertas` + correo al equipo de automatización |
| **Media** | Latencia p99 > 1000 ms, menos de 100 muestras | Slack `#qa-alertas` + ticket en el tablero de calidad |

Cuando una alerta se dispara, el script devuelve código de salida `1`, el job del
pipeline se marca como **fallido** y el despliegue queda bloqueado: la alerta es
automática y no depende de que alguien revise el reporte.

### 11.1 Simulación de una alerta

`scripts/simular-alerta.py` toma los resultados reales de JMeter, inyecta una
degradación controlada (8 % de peticiones lentas entre 900 y 1500 ms y 6 % de errores
HTTP 500, con semilla fija) y ejecuta `verificar-umbrales.py` sobre ese resultado:

```bash
python3 scripts/simular-alerta.py
```

Resultado obtenido (`evidencia/logs/03-simulacion-alerta.log`): se disparan tres
alertas (p95 = 1130 ms **alta**, p99 = 1415 ms **media**, tasa de error = 6,17 %
**crítica**), el estado global pasa a `ALERTA` y el código de salida es `1`, que es lo
que hace fallar el job en GitHub Actions/Jenkins. El estado real
(`dashboard/estado-umbrales.json`) no se modifica; el simulado queda en
`dashboard/estado-umbrales-simulado.json`.

---

## 12. Evidencia generada

`evidencia/` contiene las capturas de pantalla y los logs textuales de:

1. Creación del repositorio Git, ramas y commits (`git log`).
2. Ejecución local de la suite unitaria (`mvn test`).
3. Ejecución de los escenarios BDD (`mvn verify -Dgroups=bdd`).
4. Reportes navegables (Allure, Cucumber, JaCoCo).
5. Ejecución del plan de carga y dashboard de JMeter.
6. Ejecución del pipeline completo local y estado de los umbrales.

---

## 13. Decisiones técnicas

Resumen de las decisiones y sus motivos (detalle en
[`docs/decisiones-tecnicas.md`](docs/decisiones-tecnicas.md)):

| Decisión | Alternativas descartadas | Motivo |
|---|---|---|
| Java 17 + Maven + JUnit 5 | Gradle, Ant | Es lo que pide el enunciado y el estándar de la industria |
| Cucumber 7 + PicoContainer | Behave, JBehave | Mantiene un único lenguaje (Java) en todo el taller |
| Allure + Cucumber HTML | Solo Surefire XML | Reporte navegable unificado, requisito explícito del enunciado |
| JMeter 5.6.3 | k6, Gatling | Es Java puro y genera su propio dashboard HTML |
| JaCoCo como *quality gate* | Sin umbral | Convierte la cobertura en un criterio objetivo de aceptación del pipeline |
| Ejecución local del CI con `scripts/ci-local.*` | Solo CI en la nube | Permite validar el pipeline sin depender de una cuenta de GitHub |

---

## 14. Cómo reproducir la entrega

```bash
git clone <url-del-repositorio>
cd automatica-pruebas
mvn clean verify                       # suite completa + reportes
powershell -File scripts/ci-local.ps1  # pipeline completo (incluye performance)
```

Los reportes se pueden abrir con:

```
target/allure-report/index.html
target/cucumber-report/cucumber-report.html
target/site/jacoco/index.html
performance/reporte-html/index.html
dashboard/metricas.html
```
