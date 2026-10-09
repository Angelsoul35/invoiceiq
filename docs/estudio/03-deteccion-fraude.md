# 03 — Detección de fraude

## No es un veredicto, son señales

`fraud.py` no dice "esto es fraude". Produce **señales explicables** que mandan la
factura a revisión. La más importante en cuentas por pagar es la **factura
duplicada**: la misma factura pagada dos veces.

## Dos claves complementarias

El `FraudScanner` guarda un pequeño historial y comprueba dos claves:

- `(proveedor, número)` — una reenviada idéntica → `duplicate_invoice_number`
  (severidad error).
- `(proveedor, total, fecha)` — la misma factura con **otro número** →
  `possible_duplicate_payment` (aviso).

Así se cogen tanto el duplicado evidente como el disfrazado.

## Heurísticas sin estado

- `over_approval_limit`: el total iguala o supera el límite de aprobación.
- `unexpected_tax_rate`: la tasa de impuesto implícita (`impuesto / subtotal`) se
  aleja de la esperada más que la tolerancia.

## Alcance y extensiones

El historial está en memoria y por proceso; una extensión natural lo lleva a un
almacén compartido para detectar duplicados entre trabajadores y a lo largo del
tiempo. La normalización del proveedor es directa (minúsculas, sin espacios) y se
amplía con coincidencia difusa ("Acme Ltd" vs "ACME Limited") cuando el catálogo
de proveedores lo pide.
