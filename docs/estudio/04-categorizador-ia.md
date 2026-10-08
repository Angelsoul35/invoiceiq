# 04 — El categorizador de IA

## Qué hace

Mapea el texto de las líneas de una factura (más el proveedor) a una de ocho
**categorías de gasto** (software, viajes, servicios profesionales, etc.), con una
confianza y una explicación (las palabras que más pesaron). Es un `FeatureUnion`
de TF-IDF de palabras (1-2 gramas) y de caracteres (`char_wb`, 3-5) con regresión
logística: lineal y, por tanto, explicable.

## Evaluación honesta (nada de 1,0 falso)

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

## Nunca decide solo

Si la confianza está por debajo del umbral, la categoría se marca para **revisión
humana**. Y, sobre todo, la categoría **no afecta** a `is_valid` ni a las señales
de fraude: esas son deterministas. Un error del modelo puede sugerir mal la
categoría, pero no puede dejar pasar un total mal ni esconder un duplicado.
