# Guía de estudio — InvoiceIQ

Guía en español para entender el proyecto a fondo y defenderlo en una entrevista.
El código y la documentación técnica están en inglés (como en un entorno
profesional); esta guía explica el *porqué*.

## Orden sugerido

1. [01 — Extracción de datos](01-extraccion.md) — del texto a números exactos.
2. [02 — Validación aritmética](02-validacion-aritmetica.md) — por qué cuadra o no.
3. [03 — Detección de fraude](03-deteccion-fraude.md) — facturas duplicadas y señales.
4. [04 — El categorizador de IA](04-categorizador-ia.md) — y su evaluación honesta.
5. [05 — Preguntas de entrevista](05-preguntas-de-entrevista.md)

## La idea en una frase

Primero lo **determinista y auditable** (extraer, comprobar que las cuentas
cuadran, detectar duplicados), y solo al final la IA, que **sugiere** la
categoría de gasto y manda a revisión si duda. Un error del modelo nunca deja
pasar un total mal ni esconde un duplicado.
