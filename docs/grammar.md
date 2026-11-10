# Gramática inicial de XMind MD

## Objetivo

La sintaxis debe seguir siendo Markdown legible. Las directivas propias se limitan a metadatos que complementan los encabezados.

## Encabezados

Los niveles `#` a `######` definen la jerarquía. Se permite saltar niveles; la relación padre-hijo se determina por el encabezado anterior de nivel inferior.

## Directivas

| Directiva | Función |
|---|---|
| `@conjunto(NOMBRE)` | Selecciona un conjunto de estilos para el siguiente tema y sus descendientes, salvo cambio posterior. |
| `@estilo(NOMBRE)` | Selecciona un estilo concreto del conjunto aplicable para el siguiente tema. |

Las directivas deben aparecer en líneas independientes inmediatamente antes del encabezado al que se aplican. En esta primera implementación, un conjunto se propaga a los descendientes.

## Contenido

El texto normal y las listas se guardan como líneas de contenido del tema activo. Todavía no se convierten en subtemas. Las citas, tablas, enlaces, imágenes, marcadores, relaciones y límites se incorporarán mediante extensiones de gramática explícitas.

## Ejemplo

```md
@conjunto(TAI_LEGISLACION)
# Constitución

## Título I

@estilo(concepto_importante)
### Artículo 14
```

## Decisiones pendientes

- Sintaxis para notas y enlaces.
- Sintaxis para marcadores e iconos.
- Sintaxis para relaciones, boundaries y summaries.
- Sistema de herencia, combinación y sobrescritura de estilos.
- Reglas de escape para texto literal que empiece por `@`.
