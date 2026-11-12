# Formato JSON de XMind: estructura, estilos y estrategia de conversión

**Estado:** documentación técnica basada en la exportación real `themes/Tema1/content.json` y en el generador actual del repositorio.  
**Fecha:** 2026-11-12.

## 1. Dos JSON distintos en el proyecto

Hay que distinguir:

1. **JSON de XMind Desktop**: `content.json` dentro de un libro `.xmind`. Describe hojas, temas, estilos, marcadores, metadatos y configuración de presentación. Tema1 es una exportación real de XMind Desktop.
2. **JSON IR de XMind MD**: salida del adaptador `json_adapter.py`. Serializa el modelo intermedio neutral (IR 1.0.0), no el formato interno de XMind.

No son intercambiables. El JSON IR es nuestro contrato neutral; `content.json` es un formato de intercambio/almacenamiento de XMind que el adaptador debe generar.

## 2. Libro XMind moderno: contenedor

El adaptador actual genera un archivo ZIP moderno con estas entradas:

| Entrada | Función |
|---|---|
| `mimetype` | Tipo MIME del libro; se escribe sin compresión |
| `content.json` | Hojas, temas, relaciones y datos estructurales |
| `metadata.json` | Creador, modificador, versiones de estructura/layout, hoja activa y fecha |
| `manifest.json` | Registro de entradas y tipos MIME |
| `Thumbnails/thumbnail.png` | Miniatura PNG |

El MIME empleado por el código es `application/vnd.xmind.workbook`. El generador define `dataStructureVersion = "3"` y `layoutEngineVersion = "5"`.

Este es el perfil que implementa actualmente nuestro adaptador; no debe suponerse que todas las versiones históricas de XMind usan exactamente el mismo contenedor o estructura.

## 3. Estructura de content.json observada

Tema1 tiene un array de hojas. La hoja principal contiene, entre otros:

- `id`: identificador de hoja.
- `class: "sheet"`.
- `rootTopic`: tema raíz recursivo.
- `title`: título de hoja.
- `style`: estilo asociado a la hoja.
- `theme`: perfiles generales para mapa, temas y elementos auxiliares.
- `extensions`: datos adicionales identificados por proveedor.

El tema contiene habitualmente:

- `id`, `class: "topic"`, `title`.
- `children`, agrupados por tipo de relación (por ejemplo `attached`).
- `structureClass`: clase de estructura del árbol/tema cuando está declarada.
- `style`: objeto de estilo local, con `id` y `properties`.
- `markers`, `labels`, `notes`, `href` y otros datos cuando existen.
- `position`, `customWidth`, `branch` y otras propiedades geométricas/layout cuando se declaran.

No todos los campos aparecen en todos los temas. La ausencia de un campo no debe tratarse automáticamente como valor por defecto universal.

## 4. Árbol y tipos de relación

La jerarquía se codifica mediante objetos anidados en `children`. En Tema1, los hijos aparecen bajo `children.attached`. El tipo de colección de hijos importa: no se debe aplanar el árbol ni asumir que toda relación padre-hijo tiene el mismo tipo.

El generador actual agrupa hijos por `topic.kind` en el objeto `children`. Los tipos aceptados por el perfil inicial del adaptador son `attached`, `detached` y `callout`; el tema raíz debe ser `attached`.

Un tema subordinado puede tener geometría, estructura y estilo propios. La profundidad del árbol no basta para reconstruir su apariencia.

## 5. structureClass y shape-class son conceptos diferentes

Esta distinción es esencial:

- `structureClass` es un campo del objeto tema que identifica la estructura del tema/árbol. En Tema1, `Articulo` declara `org.xmind.ui.treetable.toptitle`.
- `shape-class` es una propiedad dentro de `style.properties` y define la forma visual. En las celdas `Cabecera` y `cuerpo` aparece `org.xmind.internal.topicShape.treeTableCell`.

No fusionar ambos campos en un único concepto PMD. Una estructura de tabla puede contener celdas que además tienen un estilo visual propio.

Las cadenas `org.xmind...` son identificadores internos del ecosistema XMind. PMD debería utilizar nombres neutrales como `tree_table`, `table_title` y `table_cell`, y mantener el mapeo a XMind en el adaptador.

## 6. Estilos: perfiles generales y estilos locales

### 6.1 Perfiles generales

El objeto `theme` de Tema1 contiene perfiles como:

- `map`
- `centralTopic`
- `mainTopic`
- `subTopic`
- `floatingTopic`
- `summaryTopic`
- `calloutTopic`
- `importantTopic`, `minorTopic`, `expiredTopic`
- `boundary`, `summary`, `relationship`
- perfiles adicionales por nivel, como `level6`.

Estos perfiles describen valores generales del tema visual. No equivalen a un catálogo semántico como `articulo`, `apartado` o `excepcion`.

### 6.2 Estilo explícito por tema

Un objeto `style` local suele tener:

```json
{
  "id": "identificador-del-estilo",
  "properties": {
    "fo:font-size": "13",
    "fo:font-weight": "700",
    "fo:color": "#613204ff",
    "svg:fill": "#EEEEEEFF",
    "shape-class": "org.xmind.internal.topicShape.treeTableCell"
  }
}
```

Las propiedades son un diccionario extensible de claves técnicas. Ejemplos observados en Tema1:

- Tipografía: `fo:font-family`, `fo:font-size`, `fo:font-weight`, `fo:font-style`, `fo:color`, `fo:text-transform`, `fo:text-decoration`, `fo:text-align`.
- Relleno: `svg:fill`, `fill-pattern`.
- Líneas y bordes: `line-color`, `line-width`, `line-pattern`, `border-line-color`, `border-line-width`, `border-line-pattern`.
- Forma y conexión: `shape-class`, `line-class`, `arrow-end-class`.
- Alineación: `alignment-by-level`.

No se debe asumir que esta lista sea exhaustiva ni que todas las claves sean admitidas por cada versión de XMind.

### 6.3 Ausente, explícito e inherited

En el JSON aparecen al menos tres estados que deben conservarse:

1. La propiedad no está presente.
2. La propiedad tiene un valor concreto.
3. La propiedad está presente con el valor literal `inherited`.

En Tema1, `cuerpo` declara `border-line-color`, `border-line-width` y `border-line-pattern` con valor `inherited`. El perfil general `theme` también utiliza `inherited` en varias propiedades.

No equiparar `inherited` con propiedad ausente, ni asumir que significa heredar del padre o del primer hermano sin probar la semántica concreta en XMind. La herencia PMD por primer hijo es una regla declarativa propia, independiente.

### 6.4 IDs de estilo

Los estilos locales incluyen un `id` propio. En Tema1 los IDs de tema y los IDs de estilo son distintos. Nuestro adaptador genera IDs de estilo deterministas a partir del mapa y del tema; la exportación XMind de referencia utiliza IDs propios de XMind. No reutilizar IDs de una exportación ajena como identidad PMD.

## 7. Marcadores y anotaciones

Los marcadores se expresan como lista de objetos:

```json
"markers": [
  {"markerId": "flag-red"},
  {"markerId": "task-oct"}
]
```

Tema1 los utiliza en `Titulo` y `Articulo`. Los marcadores son anotaciones funcionales y deben mantenerse separados de los estilos de forma, tipografía y relleno.

El formato también puede contener etiquetas, notas, enlaces (`href`) y datos de tarea. La presencia y forma exacta debe verificarse con fixtures adicionales. El adaptador actual transforma las etiquetas, marcadores, notas y enlaces del IR dentro del perfil que implementa; no todas las anotaciones IR están soportadas.

## 8. SVG como vista derivada y herramienta de correlación

El SVG exportado desde XMind puede incluir:

- Grupos `g`, rutas `path`, máscaras y recortes.
- Títulos dentro de `foreignObject` con XHTML/CSS.
- Recursos de imagen y fuentes embebidas.
- Atributos `data-view-id` que relacionan partes de la vista con entidades.

En Tema1, los diez títulos aparecen en `foreignObject` y sus `data-view-id="topic-title:<id>"` corresponden a los IDs de los temas JSON. Esto permite correlacionar tema y vista sin analizar el texto visualmente.

El SVG es una referencia útil para fidelidad visual y diagnóstico, no una fuente de verdad semántica ni un requisito de copiar su XML interno. Objetivo vigente: generar un SVG lo más fiel posible a la apariencia original, sin identidad byte a byte ni reproducción exacta de IDs/atributos.

## 9. Perfil del generador actual del repositorio

Código: `src/xmind_md/adapters/xmind_adapter.py`.

El adaptador:

1. Recibe IR 1.0.0, nunca Markdown.
2. Comprueba capacidades y rechaza construcciones no soportadas.
3. Genera IDs XMind deterministas mediante UUIDv5 a partir del ID del mapa y de la entidad.
4. Convierte temas recursivamente y agrupa hijos por `kind`.
5. Traduce un subconjunto de propiedades neutrales a claves de XMind mediante `_STYLE_KEYS`.
6. Escribe `content.json`, `metadata.json`, `manifest.json`, `mimetype` y una miniatura PNG dentro del ZIP.

### 9.1 Traducciones de estilo implementadas

| Propiedad neutral | Clave XMind generada |
|---|---|
| `shape` | `shape-class` |
| `text.font_family` | `fo:font-family` |
| `text.font_size` | `fo:font-size` |
| `text.font_weight` / `text.bold` | `fo:font-weight` |
| `text.italic` | `fo:font-style` |
| `text.color` | `fo:color` |
| `text.decoration` | `fo:text-decoration` |
| `background.color` / `background.fill` | `svg:fill` |
| `border.color` / `line.color` | `line-color` |
| `border.width` / `line.width` | `line-width` |
| `border.pattern` / `line.pattern` | `line-pattern` |

La tabla describe el código actual, no el conjunto completo de propiedades XMind. Propiedades desconocidas se rechazan; no se descartan silenciosamente.

### 9.2 Limitaciones actuales relevantes

Entre las capacidades que el adaptador rechaza o no exporta en el perfil inicial:

- Assets e imágenes.
- Boundaries y summaries.
- Layout de hoja distinto del perfil básico.
- Metadatos de hoja y extensiones no soportadas.
- Tareas.
- Bloques de contenido `image` y `raw`.
- Algunos estilos/propiedades no incluidos en el mapa de traducción.
- Reinicio de estilo mediante `null`.
- Varias restricciones de enlaces y notas con estilo.

Consultar siempre la validación en `_validate_supported_features()` y la matriz [xmind-adapter.md](xmind-adapter.md), porque el perfil puede evolucionar.

## 10. Estrategia de conversión recomendada

La conversión debe utilizar tres representaciones con responsabilidades diferentes:

```text
Markdown fuente / contenido de estudio
              |
              v
IA: interpretación semántica y estructural
              |
              v
PMD: intención explícita y referencias al catálogo
              |
              v
Parser + validador PMD
              |
              v
IR neutral: árbol, bloques, anotaciones, estilos
              |
              v
Resolutor determinista de estilos
              |
              v
Adaptador XMind: JSON XMind + contenedor ZIP
              |
              v
XMind Desktop
```

El JSON XMind debe ser responsabilidad del adaptador, no de la IA. La IA debe generar conceptos PMD neutrales, no inventar IDs internos, clases privadas ni claves de serialización de XMind.

Para importar un XMind existente hacia PMD/IR se necesitará un lector separado que:
- Abra el ZIP y valide entradas.
- Analice `content.json` y `metadata.json`.
- Preserve IDs de origen como procedencia, sin convertirlos automáticamente en IDs PMD.
- Interprete estructura, clases, estilos, anotaciones y recursos.
- Mantenga valores desconocidos en extensiones o los registre como pérdida.
- Correlacione SVG si se proporciona, para estudiar apariencia y verificar correspondencia.
- Informe de forma explícita los elementos no interpretados.

## 11. Pruebas de compatibilidad pendientes

Para consolidar la documentación del formato se necesitan varios archivos XMind Desktop de distintas características y, si es posible, distintas versiones:

- Árbol básico con ramas attached.
- Temas detached y callout.
- Tabla de árbol con cabecera, filas y celdas de distinto estilo.
- Relaciones, boundaries y summaries.
- Marcadores, etiquetas, notas y enlaces.
- Imágenes y adjuntos.
- Estilos heredados, ausentes, explícitos y `inherited`.
- Layout, posición, anchura y temas plegados.

Cada fixture debe documentar la versión de XMind, el caso que representa y las entradas del ZIP. No generalizar el comportamiento de Tema1 a todos los casos.

## 12. Referencias internas

- [Análisis de referencia Tema1](reference-analysis-tema1.md).
- [Intercambio Markdown ↔ XMind](xmind-markdown-behavior.md).
- [Matriz del adaptador](xmind-adapter.md).
- [Especificación IR](ir-specification.md).
- [Arquitectura](architecture.md).
- Código: `src/xmind_md/adapters/xmind_adapter.py`, `src/xmind_md/adapters/json_adapter.py`.
- Fixture real: `themes/Tema1/content.json` y `themes/Tema1/Tema1.svg`.

## 13. Estado de conocimiento

| Tema | Estado |
|---|---|
| Estructura y propiedades presentes en Tema1 | Observado directamente |
| Correspondencia de IDs JSON ↔ SVG en Tema1 | Observado directamente |
| Estructura ZIP generada por nuestro adaptador | Verificado en código y pruebas del proyecto |
| Traducciones de estilo implementadas | Verificado en código |
| Compatibilidad completa con todas las versiones XMind | No afirmada |
| Significado universal de cada clave privada `org.xmind...` | Requiere fixtures/documentación adicional |
| Reglas completas de herencia nativa XMind | Pendiente de investigación controlada |
| Lector XMind → PMD/IR | No implementado |


## 14. Investigación de repositorios y modelo oficial

La investigación adicional está desarrollada en [xmind-official-sdk-research.md](xmind-official-sdk-research.md). Se han identificado tres repositorios oficiales TypeScript/MIT:

- **xmind-sdk-js**: SDK oficial; usa xmind-model y genera/valida libros mediante Workbook, Sheet, Topic, Marker, Note y Zipper.
- **xmind-model**: interfaces, clases y esquemas JSON Schema Draft-07 para hojas, temas, estilos, marcadores, notas, relaciones, límites, resúmenes, imágenes y extensiones.
- **xmind-generator**: generador oficial con un serializador explícito de un perfil ZIP + JSON y recursos.

### 14.1 Hallazgos que amplían el formato

- El documento se representa como array de hojas.
- La hoja puede incluir rootTopic, style, topicPositioning, topicOverlapping, theme, relationships, legend y settings.
- Los temas tienen colecciones children por tipo: attached, detached, summary y callout en xmind-model.
- class (familias de estilo), structureClass (estructura) y style.properties (propiedades visuales locales) son conceptos separados.
- El modelo contempla entidades auxiliares explícitas para Relationship, Boundary, Summary, Marker, Notes, Image, Numbering y Extension.
- El modelo de estilo combina perfiles de Theme, clases del componente y propiedades locales. No se ha encontrado una especificación completa y actual del algoritmo de herencia del Desktop.

### 14.2 Perfiles ZIP distintos: no mezclar implementaciones

xmind-sdk-js incluye content.json, metadata.json, content.xml, manifest.json y recursos; el Zipper consultado no añade mimetype ni miniatura. xmind-generator genera content.json, metadata.json, manifest.json y resources; declara dataStructureVersion = "2" y tampoco añade mimetype, content.xml ni miniatura. Nuestro adaptador actual declara dataStructureVersion = "3" y layoutEngineVersion = "5", e incluye mimetype y thumbnail. Tema1 es otra referencia real exportada por Desktop.

Por tanto, estos repositorios son fuentes oficiales de implementación, pero sus perfiles de serialización no deben combinarse ni sustituir automáticamente el formato actual del proyecto. La diferencia de versiones debe validarse con XMind Desktop.

