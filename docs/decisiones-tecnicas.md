# Decisiones técnicas y su justificación

Este documento explica **por qué** se eligió cada tecnología y cada práctica en el
proyecto. Cada decisión incluye las alternativas descartadas y el motivo, que es
precisamente lo que evalúa la pauta en el indicador
*«Correcta definición y automatización de escenarios BDD»* y
*«Estructura y atomicidad de la suite de pruebas»*.

---

## 1. Lenguaje y gestor de dependencias

**Decisión: Java 17 + Apache Maven.**

| Alternativa | Por qué se descartó |
|---|---|
| Gradle | El enunciado pide explícitamente un proyecto Maven con dependencias tipo JUnit; además, en la mayoría de las empresas el pipeline ya está sobre Maven. |
| Ant | Sin gestión de dependencias ni de ciclo de vida; no aporta valor frente a Maven. |
| Java 8 / 11 | Versiones fuera de soporte en muchas organizaciones; Java 17 es LTS y permite Records, `switch` expressions y mejor rendimiento en la JVM. |

**Configuración clave:** `maven.compiler.release=17` garantiza que el bytecode generado
sea compatible con Java 17 sin depender del JDK del usuario.

---

## 2. Framework de pruebas unitarias

**Decisión: JUnit 5 (Jupiter) + AssertJ.**

- **JUnit 5** es el estándar actual; su modelo de *extensiones* permite reutilizar
  configuración sin herencia de clases.
- **AssertJ** se eligió sobre `JUnit Assert` porque sus mensajes de fallo son
  descriptivos y encadenables (`isEqualTo(...).as("mensaje")`), lo que mejora
 签证 la legibilidad de los reportes navegables.

**Atomicidad.** Cada test:
1. Crea su propia instancia del objeto bajo prueba (no se comparte estado).
2. Verifica **una sola regla de negocio**.
3. No depende del orden de ejecución.

```java
// Sin estado compartido: cada test es autónomo
@Test
void restaDevuelveElResultadoCorrecto() {
    Calculadora calculadora = new Calculadora();   // Arrange
    double resultado = calculadora.resta(10.0d, 4.0d);   // Act
    assertThat(resultado).isEqualTo(6.0d);   // Assert
}
```

**Bajo acoplamiento.** Las clases de `modelo/` no dependen de Spring, de la base de datos
ni de la red: son POJO puros. Eso permite ejecutarlos en milisegundos y en cualquier
entorno, que es justamente lo que exige un pipeline rápido.

---

## 3. Framework BDD

**Decisión: Cucumber 7 (Java) + PicoContainer + Cucumber Expressions.**

| Alternativa | Por qué se descartó |
|---|---|
| Behave (Python) | Obliga a mantener dos lenguajes en el mismo taller; el enunciado lo permite, pero Java es el lenguaje del proyecto. |
| JBehave | Menos comunidad y peor integración con el ecosistema JUnit 5 / Allure. |
| Serenity BDD | Más potente, pero curva de aprendizaje alta y muchos artefactos generados; desalineado con el alcance del taller. |
| Expresiones regulares en los pasos | Menos legibles que las Cucumber Expressions y más difíciles de mantener. |

**PicoContainer** se usa para inyectar el `Contexto` (estado del escenario) en los
*step definitions*. El contenedor crea una instancia **por escenario**, lo que garantiza
el aislamiento entre escenarios sin necesidad de un singleton global ni de un `@Before`
que haga limpieza manual.

> **Learning real:** el uso de `{string}` en Cucumber Expressions exige que los valores
> con espacios estén entre comillas (`"un token válido"`). Se ajustó el Gherkin y la
> tabla de `Examples` en consecuencia.

---

## 4. Reportes navegables

**Decisión: Allure + Cucumber HTML + JaCoCo, en paralelo.**

| Reporte | Para qué sirve |
|---|---|
| **Allure** (`target/allure-report/index.html`) | Reporte **unificado** de JUnit 5 + BDD: categorías, etiquetas, historial de reintentos y vista de *timeline*. Es el que el enunciado nombra explícitamente. |
| **Cucumber HTML** (`target/cucumber-report/cucumber-report.html`) | Reporte oficial de Cucumber: se lee en el **idioma del negocio** (los escenarios tal como los escribió el *Three Amigos*). |
| **JaCoCo** (`target/site/jacoco/index.html`) | Cobertura de código línea a línea, que permite ver qué partes del código no están probadas. |
| **JMeter** (`performance/reporte-html/index.html`) | Dashboard de performance con percentiles, TPS y tasa de error. |

Se necesitaba un generador del reporte HTML de Allure dentro del build. Se optó por
`exec-maven-plugin` + `allure-commandline` (descargado por `maven-dependency-plugin`)
en lugar del plugin `allure-maven`, porque así el build es **autocontenido**: no
requiere que el *allure* CLI esté instalado en la máquina ni en el runner.

---

## 5. Métricas de cobertura como criterio de aceptación

**Decisión: JaCoCo con regla `BUNDLE / LINE / COVEREDRATIO ≥ 0.70` en la fase `verify`.**

- La cobertura deja de ser un dato decorativo y pasa a ser un **quality gate**: si baja
  del umbral, el build falla y la rama no se puede integrar.
- El paquete `com.empresa.pruebas.performance` queda **excluido**: es el arnés que hace
  de sistema bajo prueba para JMeter, no lógica de negocio. Excluir infraestructura de
  la métrica de cobertura evita "inflar" el número con código que no tiene sentido
  probar unitarily.

---

## 6. Herramienta de performance

**Decisión: Apache JMeter 5.6.3.**

| Alternativa | Por qué se descartó |
|---|---|
| k6 | Escribes el test en JavaScript: obliga a introducir un segundo lenguaje. Muy bueno, pero menos encajado con un proyecto Java. |
| Gatling | Muy potente, pero requiere Scala y un *build* más complejo para un taller. |

JMeter es Java puro (funciona con el mismo JDK del proyecto), genera su propio
**dashboard HTML** sin Plugins y es el estándar en la industria.

**Perfil de carga:** 20 hilos, *ramp-up* de 5 s, 15 s de duración y *think time* de 100 ms.
Se eligió un perfil moderado para que el pipeline no dependa de la potencia de la
máquina del autor.

---

## 7. Indicadores de performance

Se monitorean **TPS, latencia (mínima, media, p50, p90, p95, p99) y tasa de error**.

- **TPS** mide la capacidad de servicio sostenida.
- **El promedio no basta:** una latencia media de 200 ms puede esconder que el 5 % de
  las peticiones tarda más de 2 s. Los **percentiles** describen la experiencia real
  del usuario en el peor caso.
- **La tasa de error** es la que más rápido detecta una regresión funcional que el
  TPS: el sistema puede seguir respondiendo rápido... pero con errores.

Los umbrales definidos en `monitoreo/umbrales.yml` son los que evalúa
`scripts/verificar-umbrales.py`; si alguno se incumple, el script sale con código `1` y
el pipeline falla, disparando la alerta automática.

---

## 8. Dashboard de métricas

**Decisión: generador HTML propio en Python + stack InfluxDB/Grafana como propuesta de
producción.**

- El generador (`scripts/generar-dashboard.py`) produce un HTML **autocontenido**
  (sin CDN ni dependencias) con los datos reales de la última ejecución. Se optó por no
  usar plantillas externas para que el reporte se pueda abrir sin conexión a internet.
- La stack InfluxDB + Grafana (`monitoreo/docker-compose.yml`) se entrega como la
  propuesta de observabilidad continua en la nube, donde las métricas se acumulan en
  el tiempo y se pueden comparar entre ejecuciones.

---

## 9. Gestión de versiones

**Decisión: Git con flujo *feature branch* + Conventional Commits.**

- `main` es la rama protegida: solo recibe commits vía Pull Request, lo que obliga al
  pipeline a validar cada cambio.
- `develop` concentra la integración de las features.
- `feature/*` una por funcionalidad.
- Los mensajes siguen *Conventional Commits* (`feat`, `fix`, `test`, `docs`, `chore`,
  `perf`, `ci`, `build`, `refactor`): permiten generar el *changelog* automáticamente y
 审查 cambios de un vistazo.

---

## 10. Ejecución del CI

**Decisión: GitHub Actions como motor principal + `Jenkinsfile` equivalente + scripts
de ejecución local.**

- `.github/workflows/ci.yml` es el pipeline principal: se ejecuta automáticamente en
  cada `push` y `pull request` sin necesidad de infraestructura propia.
- `Jenkinsfile` se entrega como alternativa, tal como permite el enunciado
  («Jenkinsfile, .github/workflows/ci.yml»), para equipos que ya usan Jenkins.
- `scripts/ci-local.ps1` y `scripts/ci-local.sh` reproducen **exactamente** los tres
  *jobs* del workflow. Esto permite validar el pipeline en la máquina del autor —
  incluida la evidencia de ejecución — sin depender de una cuenta de GitHub, y deja
  documentado cómo se ejecuta cada etapa.

---

## 11. Estructura de carpetas

```
src/main/java/...        Código de producción
src/test/java/...        Pruebas unitarias y step definitions
src/test/resources/      Configuración de Cucumber y de JUnit Platform
features/                Archivos Gherkin (visibles para negocio y QA)
performance/             Planes de carga de JMeter
scripts/                 Utilidades del pipeline (dashboard, umbrales, CI local)
monitoreo/               Umbrales, reglas de alerta y stack de observabilidad
docs/                    Documentación de la sesión Three Amigos y decisiones
evidencia/               Capturas de pantalla y logs de la ejecución
```

**Criterio:** lo que el *negocio* necesita leer (los `.feature`) está en una carpeta
visible en la raíz; lo que es código de prueba, en `src/test`; lo que es configuración
de la infraestructura de pruebas, en su propia carpeta. Separar `features/` de
`src/test/resources/features/` permite que el negocio lea y discuta los escenarios sin
conocer la estructura de Maven.

---

## 12. Buenas prácticas aplicadas (checklist)

- [x] Código de negocio sin estado global ni dependencias de framework.
- [x] Pruebas unitarias atómicas, independientes y con una aserción conceptual por test.
- [x] Nombres de test descriptivos en español (`@DisplayName`).
- [x] BDD en el idioma del negocio, con trazabilidad criterio → escenario.
- [x] Inyección de dependencias en los pasos (sin estado global).
- [x] Pipeline con tres etapas y dependencias explícitas (`needs`).
- [x] Artefactos publicados incluso cuando el build falla (`if: always()`).
- [x] *Quality gate* de cobertura que bloquea la integración.
- [x] Umbrales de performance con alertas automáticas y severidades.
- [x] `.gitignore` que excluye artefactos, IDE y secretos.
- [x] Mensajes de commit estandarizados (Conventional Commits).
- [x] `README.md` con objetivos, comandos, estructura y justificación.
- [x] Ejecución paralela de escenarios Cucumber (`cucumber.execution.parallel.enabled`).
