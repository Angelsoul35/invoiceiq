# 05 — Preguntas de entrevista

### "¿Por qué no dejas que un LLM extraiga y clasifique todo?"
Porque en cuentas por pagar los errores caros (total descuadrado, pago duplicado,
gasto sobre el límite) son hechos que hay que **comprobar**, no **predecir**. La
extracción y la validación son deterministas y auditables; la IA solo sugiere la
categoría, que un humano puede corregir.

### "¿Cómo detectas una factura duplicada?"
Con dos claves: `(proveedor, número)` para la reenviada idéntica (error), y
`(proveedor, total, fecha)` para la misma factura con otro número (aviso). Así
cojo el duplicado evidente y el disfrazado.

### "¿Por qué enteros en céntimos?"
Porque `0,1 + 0,2 != 0,3` en coma flotante y un validador con `float` daría falsos
descuadres. En céntimos la aritmética es exacta; una tolerancia pequeña y
documentada absorbe el redondeo por línea.

### "Cuéntame un bug sutil que cubriste."
El patrón de "Total" sin fronteras de palabra hacía coincidencia dentro de
"Subtotal", cogiendo el subtotal como total. Lo arreglé con `\btotal\b` y lo
protegí con una prueba: es un error que no da excepción, solo cifras mal.

### "¿Tu categorizador está sobreajustado?"
Lo evalúo con un split **disjunto por anclas** (vocabulario de prueba no visto) y
promediando seeds: 0,93 ± 0,06 con una brecha train-test de 0,07. No reporto el
~1,0 de dentro de distribución porque sería mentira.

### "¿Qué falta para producción?"
OCR / parser de maquetación para PDF e imágenes, persistencia del historial de
duplicados, políticas de impuesto y aprobación por proveedor, conciliación a tres
bandas (orden de compra + recepción + factura) y reentrenar el categorizador con
facturas reales etiquetadas.
