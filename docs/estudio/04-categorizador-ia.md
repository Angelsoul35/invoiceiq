# 04 — El categorizador de IA

## Qué hace

Mapea el texto de las líneas de una factura (más el proveedor) a una de ocho
**categorías de gasto** (software, viajes, servicios profesionales, etc.), con una
confianza y una explicación (las palabras que más pesaron). Es un `FeatureUnion`
de TF-IDF de palabras (1-2 gramas) y de caracteres (`char_wb`, 3-5) con regresión
logística: lineal y, por tanto, explicable.

## Evaluación por anclas disjuntas (nada de 1,0 falso)

Entrenar y evaluar con las mismas plantillas sintéticas daría ~1,0 sin sentido. La
evaluación hace un **split disjunto por anclas**: retira *palabras ancla completas*
del entrenamiento, así el vocabulario de prueba no se ha visto nunca. Es la
pregunta realista: ¿puede colocar un gasto cuyo término exacto es nuevo?

```
accuracy (media ± std, 6 seeds): 0,93 ± 0,06   # 8 categorías; el azar es ~0,125
train accuracy                  : 1,00
train-test gap                  : 0,07          # acotada -> aprende la raíz, no la plantilla
```

El comando promedia varios seeds **a propósito**: un único split puede salir alto
por suerte, y reportar eso sería el mismo autoengaño que un split aleatorio.

## Validación con datos reales (fin-transaction-category)

La prueba final es dato **real**: el dataset público
`rajeshradhakrishnan/fin-transaction-category` (282 descripciones reales de
movimientos de banco y tarjeta, etiquetadas en ocho categorías de gasto),
vendoreado bajo `datasets/`. El **mismo** categorizador (TF-IDF palabra+carácter +
logística) se entrena sobre él con `python -m invoiceiq.real_benchmark`:

```
CV accuracy : 0,752 ± 0,033
CV macro-F1 : 0,739
train / test: 0,996 / 0,752  (brecha 0,244)  -> bien ajustado
```

Sobre gasto real recogido de extractos, el categorizador llega a **0,75 de accuracy
/ 0,74 de macro-F1** en validación cruzada: **seis veces** la tasa de azar (0,125),
con una banda estrecha (±0,03) entre pliegues. No es un 1,0 memorizado.

La exactitud de entrenamiento sí se satura a ~1,00. No es sobreajuste dañino: un
modelo lineal de bajo sesgo separa sin esfuerzo cadenas de comercio **cortas y muy
distintivas** (`Uber 072515 SFPOOL`, `Starbucks`, `INTRST PYMNT`), de modo que
memoriza el conjunto de entrenamiento mientras **generaliza** a 0,75 en held-out.
El sobreajuste se define por un *held-out* pobre, no por la brecha a secas; aquí el
held-out es fuerte y estable. La prueba decisiva de que la señal es real: al
**barajar las etiquetas**, la accuracy en CV se desploma a ~0,13 (el azar). Si el
modelo solo memorizara ruido, barajar no cambiaría nada.

Las dos evaluaciones se complementan: el split sintético por anclas mide
generalización a *vocabulario* nuevo de línea de factura; este benchmark confirma
el enfoque sobre texto de transacción del mundo real. Entrenar con las facturas
etiquetadas de la propia organización lo lleva aún más lejos.

## Nunca decide solo

Si la confianza está por debajo del umbral, la categoría se marca para **revisión
humana**. Y, sobre todo, la categoría **no afecta** a `is_valid` ni a las señales
de fraude: esas son deterministas. Un error del modelo puede sugerir mal la
categoría, pero no puede dejar pasar un total mal ni esconder un duplicado.
