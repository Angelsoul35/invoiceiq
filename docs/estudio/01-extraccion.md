# 01 — Extracción de datos

## Qué hace

`extract.py` convierte el **texto** de una factura en un objeto `Invoice`
estructurado: proveedor, número, fechas, líneas de detalle y totales. Todos los
importes se guardan en **céntimos** (enteros), nunca en coma flotante.

## La frontera honesta

Las facturas reales son PDF o imágenes escaneadas. Convertir eso en texto es un
problema de **OCR / modelo de maquetación** que un sistema de producción resuelve
*antes* de este módulo. Este proyecto es honesto sobre ese límite: solo se encarga
del paso exacto de *texto* a *números*, para que cada cifra sea trazable a un
fragmento del texto de origen y no "alucinada". El parser apunta a un formato de
texto etiquetado habitual (ver `docs/architecture.md`).

## Un detalle que importa: los límites de palabra

El patrón que busca "Total" usa fronteras de palabra (`\btotal\b`). Sin ellas,
`total` haría coincidencia **dentro** de "Subtotal", y el extractor cogería el
subtotal como si fuera el total — un error silencioso que corrompería todas las
comprobaciones posteriores. Es el tipo de bug que no da error, solo resultados
mal, por eso se cubre con una prueba específica.

## De dinero a céntimos

`money_to_cents` quita símbolos de moneda y separadores de miles, interpreta el
número y lo multiplica por 100 redondeando. "1,234.56" → 123456. Trabajar en
enteros hace que las sumas sean exactas (ver la guía 02).
