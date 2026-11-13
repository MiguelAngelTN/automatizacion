# language: es
@bdd
Característica: Compra de productos en el catálogo

  Como comprador
  quiero agregar productos al carrito y aplicar códigos de descuento
  para confirmar el pedido con el total correcto

  @critico @smoke
  Escenario: Cálculo del total de un carrito con dos productos
    Dado que el carrito está vacío
    Cuando agrego el producto "LAP-001" con precio 129990 al carrito
    Y agrego el producto "MOU-002" con precio 45990 al carrito
    Entonces el total del carrito es 175980
    Y el carrito tiene 2 items

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

  @regresion
  Escenario: Confirmación de un pedido con descuento aplicado
    Dado que el carrito está vacío
    Cuando agrego el producto "X-1" con precio 100000 al carrito
    Y aplico el código de descuento "BIENVENIDA10"
    Y confirmo el pedido
    Entonces el pedido se confirma con un total de 90000
    Y el pedido tiene un identificador asignado
