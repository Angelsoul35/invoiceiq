# 02 — Validación aritmética

## Lo que comprueba

`validate.py` no adivina: **comprueba**. Tres reglas de aritmética, todas en
céntimos y con una pequeña tolerancia de redondeo:

1. **Por línea:** `cantidad × precio_unitario == importe`.
2. **Subtotal:** la suma de los importes de línea == subtotal.
3. **Total:** `subtotal + impuesto == total`.

Más comprobaciones de estructura y sentido: falta de total (error), falta de
número de factura o de proveedor (aviso), y fecha de vencimiento anterior a la de
emisión (aviso).

## Por qué céntimos y tolerancia

En coma flotante, `0,1 + 0,2 != 0,3`, así que un validador con `float` daría
falsos descuadres. Con enteros en céntimos la aritmética es exacta. La
**tolerancia** (`IQ_ARITHMETIC_TOLERANCE_CENTS`, por defecto 2) absorbe el
redondeo legítimo por línea: si tres unidades a 3,33 se facturan como 10,00
(3×333 = 999 céntimos), la diferencia de 1 céntimo no es un error.

## Severidades

Cada hallazgo tiene un **código** estable (p. ej. `total_mismatch`) y una
**severidad** (`error`/`warning`/`info`). `is_valid` es verdadero cuando no hay
ningún hallazgo de severidad `error`. Eso permite conectar el sistema a una cola
de revisión: los errores paran el pago, los avisos lo marcan.
