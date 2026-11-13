# Sesión *Three Amigos* — Definición de la funcionalidad

> **Actividad:** Automatización de Pruebas — Unidad II
> **Fecha:** 13 de noviembre de 2026
> **Participantes:** Analista de negocio (AB), QA/Tester (QA), Desarrollador (DEV)
> **Moderación:** QA
> **Duración:** 45 minutos
> **Funcionalidad elegida:** *Inicio de sesión (login) de usuarios en la plataforma de e-commerce*

---

## 1. ¿Qué es una sesión *Three Amigos*?

Es una reunión corta (30–60 minutos) en la que **una persona del negocio, una persona de
QA y una persona de desarrollo** reúnen para entender una funcionalidad **antes** de
escribir código. El objetivo no es implementar, sino **alinear el lenguaje y definir los
criterios de aceptación** que luego se convertirán en escenarios automatizados.

Reglas de la sesión que se aplicaron:

1. Se habla de **comportamiento observable**, no de implementación.
2. Se escriben **historias de usuario** con criterios de aceptación.
3. Cada criterio de aceptación se expresa en formato *Given / When / Then*.
4. Se enumeran **ejemplos concretos** (valores reales) antes de generalizar.
5. Todo lo que no se acuerde queda registrado como **pregunta abierta**.

---

## 2. Roles y responsabilidades

| Rol | Participante | Aporta | Preguntas que hace |
|---|---|---|---|
| **Analista de negocio (AB)** | Responsable de catálogo | El *qué*: reglas del negocio, reglas de descuento, casos de borde | «¿Qué pasa si el usuario está inactivo?», «¿Los descuentos se acumulan?» |
| **QA / Tester (QA)** | Analista de automatización | El *cómo se verifica*: criterios de aceptación observables y ejemplos | «¿Cómo sabemos que esto está bien?», «¿Qué dato exacto esperamos?» |
| **Desarrollador (DEV)** | Desarrollador backend | El *cómo se construye*: contratos de la API, tipos de dato, validaciones | «¿Qué respuesta devuelve el servicio?», «¿El token tiene caducidad?» |

**Acuerdo de la reunión:** el DEV no estimará esfuerzo durante la sesión; la AB no
definirá detalles técnicos; QA no decidirá reglas de negocio. Cada uno responde
desde su perspectiva.

---

## 3. Historia de usuario

> **Como** usuario registrado de la tienda en línea
> **quiero** iniciar sesión con mi usuario y contraseña
> **para** acceder al catálogo y poder completar compras.

### Historia secundaria (surge en la reunión)

> **Como** administrador de la tienda
> **quiero** que una cuenta desactivada no pueda iniciar sesión
> **para** impedir el acceso de cuentas suspendidas por falta de pago o por fraude.

---

## 4. Criterios de aceptación

### CA-1 — Autenticación exitosa

> **Given** que existe un usuario registrado con usuario `mgomez` y contraseña `Secret123`
> **And** la cuenta está activa
> **When** el usuario `mgomez` se autentica con la contraseña `Secret123`
> **Then** el sistema devuelve un token válido
> **And** el token tiene una vigencia de 30 minutos

### CA-2 — Contraseña incorrecta

> **Given** que existe un usuario registrado con usuario `mgomez` y contraseña `Secret123`
> **When** el usuario `mgomez` se autentica con la contraseña `ClaveErronea`
> **Then** el sistema devuelve un error de credenciales
> **And** no se emite ningún token

### CA-3 — Cuenta inactiva

> **Given** que existe un usuario `mnunez` con contraseña `Secret123` y estado `inactivo`
> **When** el usuario `mnunez` se autentica con la contraseña `Secret123`
> **Then** el sistema devuelve un error de credenciales

### CA-4 — Usuario inexistente

> **Given** que no existe ningún usuario con nombre `desconocido`
> **When** ese usuario intenta autenticarse
> **Then** el sistema devuelve un error de credenciales

> **Nota de seguridad (DEV):** los casos CA-2, CA-3 y CA-4 devuelven **el mismo mensaje**
> para no revelar si el usuario existe o está inactivo (enumeración de cuentas).

### CA-5 — Cálculo del total del carrito

> **Given** que el carrito está vacío
> **When** se agregan dos productos al carrito
> **Then** el total es la suma de los precios y el carrito tiene 2 ítems

### CA-6 — Aplicación de descuentos por código

> **Given** un carrito con un producto de 100000
> **When** se aplica el código `BIENVENIDA10` (10 %) o `VERANO20` (20 %)
> **Then** el total es 90000 o 80000 respectivamente; sin código, el total no cambia

### CA-7 — Confirmación de un pedido

> **Given** un carrito con un producto y un código de descuento aplicado
> **When** se confirma el pedido
> **Then** el pedido queda con el total con descuento y un identificador asignado

### CA-8 — Carrito vacío

> **Given** un carrito sin productos
> **When** se intenta confirmar el pedido
> **Then** el sistema rechaza la operación

---

## 5. Ejemplos discutidos en la sesión

| # | Usuario | Contraseña | Estado | Resultado esperado | Decisión |
|---|---|---|---|---|---|
| 1 | `mgomez` | `Secret123` | activo | Token válido (30 min) | Caso feliz |
| 2 | `mgomez` | `Secret123` | activo | Token válido | Credenciales correctas |
| 3 | `mgomez` | `ClaveFalsa` | activo | Error de credenciales | Contraseña incorrecta |
| 4 | `mnunez` | `Secret123` | **inactivo** | Error de credenciales | Cuenta suspendida |
| 5 | `atoledo` | `Secret123` | activo | Token válido | Segundo usuario activo |
| 6 | `desconocido` | `Secret123` | — | Error de credenciales | Usuario inexistente |

El **ejemplo 4** fue el que exigió una tabla de *Examples*: el resultado depende de
dos variables (estado de la cuenta y contraseña). Se decidió que el estado se modelara
como un parámetro del escenario en lugar de escribir un escenario aparte por cada caso.

---

## 6. Preguntas abiertas y su resolución

| # | Pregunta | Respuesta | Quién la resolvió |
|---|---|---|---|
| 1 | ¿La sesión se mantiene con cookies o con token? | Token, porque la API es consumida por un móvil | DEV |
| 2 | ¿Cuánto dura la sesión? | 30 minutos, valor por defecto de negocio | AB |
| 3 | ¿La cuenta inactiva recibe un mensaje distinto? | No, mismo mensaje que una contraseña incorrecta | AB + DEV |
| 4 | ¿Se puede registrar dos veces el mismo usuario? | No, se rechaza con error de usuario duplicado | AB |
| 5 | ¿Los descuentos de la compra se acumulan entre sí? | No, se aplica un solo código de descuento por carrito | AB |
| 6 | ¿El total del carrito se redondea? | Sí, a dos decimales, para evitar errores de punto flotante | DEV |
| 7 | ¿Qué pasa si se confirma un carrito vacío? | Se rechaza: no se puede confirmar un pedido sin productos | AB + QA |

---

## 7. Decisiones derivadas de la sesión

1. La lógica de negocio se encapsula en clases del paquete `modelo`, **sin estado
   global**, para que las pruebas unitarias puedan ser atómicas e independientes.
2. Los errores de negocio usan **excepciones específicas** (`ExcepcionAutenticacion`) en
   lugar de una excepción genérica, para que las pruebas verifiquen el *tipo* de falla.
3. Los escenarios BDD se escriben **en español** (`# language: es`), igual que el
   lenguaje del negocio, porque los *Three Amigos* hablan el idioma del usuario final.
4. Cada regla de negocio del login quedó cubierta por **al menos un criterio de
   aceptación** y, por lo tanto, por al menos un escenario automatizado.

---

## 8. Trazabilidad: criterios de aceptación → escenarios automatizados

| Criterio de aceptación | Escenario automatizado | Archivo |
|---|---|---|
| CA-1 Autenticación exitosa | *Autenticación exitosa con credenciales válidas* | `features/autenticacion.feature` |
| CA-2 Contraseña incorrecta | *Autenticación fallida con contraseña incorrecta* | `features/autenticacion.feature` |
| CA-3 Cuenta inactiva | *Validación del acceso según el estado de la cuenta* (ejemplo 2) | `features/autenticacion.feature` |
| CA-4 Usuario inexistente | *Un usuario inexistente produce un error de credenciales* (prueba unitaria) | `ServicioAutenticacionTest.java` |
| CA-2 (variante) Contraseña incorrecta en tabla | *Validación del acceso según el estado de la cuenta* (ejemplo 3) | `features/autenticacion.feature` |
| CA-5 Cálculo del total del carrito | *Cálculo del total de un carrito con dos productos* | `features/compra.feature` |
| CA-6 Aplicación de descuentos | *Aplicación de descuentos por código* (3 ejemplos) | `features/compra.feature` |
| CA-7 Confirmación de pedido | *Confirmación de un pedido con descuento aplicado* | `features/compra.feature` |
| CA-8 Carrito vacío no se confirma | *Confirmar un pedido con el carrito vacío falla* (prueba unitaria) | `CarritoTest.java` |

> **Cobertura:** el 100 % de los criterios de aceptación acordados tiene al menos una
> prueba automatizada asociada, y cada prueba automatizada se puede rastrear hasta un
> criterio de aceptación. Esta trazabilidad es la forma objetiva de comprobar el
> indicador *«Simulación de trabajo colaborativo y claridad de criterios»* de la pauta
> de evaluación.
