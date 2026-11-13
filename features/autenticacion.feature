# language: es
@bdd
Característica: Autenticación de usuarios en la plataforma de e-commerce

  Como usuario registrado
  quiero iniciar sesión en la plataforma
  para poder acceder al catálogo y realizar compras

  Antecedentes:
    Dado que existe un usuario registrado con usuario "mgomez" y contrasena "Secret123"

  @critico @smoke
  Escenario: Autenticación exitosa con credenciales válidas
    Cuando el usuario "mgomez" se autentica con la contrasena "Secret123"
    Entonces el resultado es "un token válido"
    Y el token tiene una vigencia de 30 minutos

  @critico
  Escenario: Autenticación fallida con contraseña incorrecta
    Cuando el usuario "mgomez" se autentica con la contrasena "ClaveErronea"
    Entonces el resultado es "un error de credenciales"

  @regresion
  Esquema del escenario: Validación del acceso según el estado de la cuenta
    Dado que existe un usuario "mgomez" con contrasena "Secret123" y estado "activo"
    Y existe un usuario "mnunez" con contrasena "Secret123" y estado "inactivo"
    Cuando el usuario <usuario> se autentica con la contrasena <contrasena>
    Entonces el resultado es <resultado>

    Ejemplos:
      | usuario  | contrasena  | resultado                   |
      | "mgomez" | "Secret123" | "un token válido"           |
      | "mnunez" | "Secret123" | "un error de credenciales"  |
      | "mgomez" | "ClaveFalsa"| "un error de credenciales"  |
