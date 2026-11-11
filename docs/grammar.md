# Gramática Markdown enriquecida de XMind MD

**Versión de gramática:** 1.0-draft (subconjunto implementado documentado)  
**Contrato IR objetivo:** 1.0.0  
**Estado:** subconjunto 1.0-draft implementado y probado; no equivale a CommonMark/GFM completos. La matriz de cobertura y las restricciones vigentes están en la sección 15.

## 1. Objetivo y principios

XMind MD utiliza Markdown como lenguaje principal y añade directivas acotadas para expresar características que Markdown no define.

Principios:

1. El contenido ordinario debe seguir siendo Markdown legible.
2. Los encabezados definen exclusivamente la jerarquía de temas.
3. Cada archivo produce un mapa con una hoja y un único tema raíz.
4. No existen temas flotantes: todo tema se crea mediante un encabezado dentro del árbol.
5. Las directivas propias deben tener delimitadores explícitos y parámetros YAML.
6. Una directiva de tema se aplica al encabezado inmediatamente siguiente, nunca a un encabezado posterior de forma accidental.
7. El contenido se convierte en bloques IR estructurados; no se almacena como una colección de líneas sin tipo.
8. Las referencias se resuelven después de construir el árbol, de modo que pueden apuntar a temas declarados más adelante.
9. Las características desconocidas no se descartan silenciosamente.
10. El parser no genera archivos XMind ni interpreta propiedades privadas de un motor de salida.

## 2. Organización del documento

Un archivo tiene estas secciones, en este orden lógico:

1. Front matter YAML opcional.
2. Cuerpo Markdown, que contiene el árbol de temas y su contenido.
3. Directivas globales XMind opcionales, que pueden aparecer en el cuerpo y se extraen del flujo de contenido.

La hoja y el tema raíz se derivan del primer encabezado válido. El título del mapa será, por defecto, el título del tema raíz.

### 2.1 Front matter

El front matter es un bloque YAML delimitado por `---` al principio del archivo.

Campos iniciales:

| Campo | Tipo | Función |
|---|---|---|
| `title` | string | Título explícito del mapa; si falta, se usa el encabezado raíz |
| `id` | string | Identificador estable del mapa |
| `author` | string | Autor |
| `description` | string | Descripción |
| `style_set` | string | Conjunto de estilos predeterminado |
| `layout.structure` | string | Estructura visual de la hoja |
| `layout.direction` | string | Orientación o distribución |
| `styles` | mapping | Definiciones de estilos locales al documento |
| `style_sets` | mapping | Conjuntos de estilos locales al documento |
| `extensions` | mapping | Metadatos de extensiones |

Ejemplo:

~~~yaml
---
title: Constitución Española
id: map_constitucion
author: Material de estudio
style_set: TAI_LEGISLACION
layout:
  structure: mind_map
  direction: balanced
styles:
  concepto_importante:
    topic:
      text:
        color: "#C62828"
        bold: true
---
~~~

El front matter no crea temas. Las claves desconocidas se rechazan salvo que estén dentro de `extensions`, para detectar errores tipográficos.

## 3. Encabezados y jerarquía

Los encabezados ATX de Markdown, niveles 1 a 6, crean temas:

~~~md
# Tema raíz
## Rama
### Subrama
#### Detalle
~~~

Reglas:

- El primer encabezado del documento debe ser el tema raíz.
- Debe existir exactamente un encabezado raíz.
- Los encabezados posteriores se anidan bajo el encabezado anterior de nivel inferior más próximo.
- Se permite saltar niveles; por ejemplo, de `##` a `####`.
- Un encabezado de nivel igual o inferior cierra los temas abiertos de ese nivel o niveles inferiores.
- El nivel Markdown es una ayuda de sintaxis; no se conserva como propiedad visual obligatoria del IR.
- Los encabezados Setext (`===` y `---`) no crean temas en la gramática 1.0. Los IDs generados dependen de la ruta del archivo, la ruta jerárquica de títulos y la ocurrencia entre hermanos; para conservar IDs al renombrar o mover temas, se recomienda declarar `id` explícitamente.
- Los encabezados dentro de bloques de código cercados no crean temas.
- El texto del encabezado se interpreta literalmente como título. El formato inline dentro de los encabezados no se transforma en estilos IR.

No se admiten dos temas raíz en un mismo archivo. Para otro mapa se utiliza otro archivo Markdown.

## 4. Directivas de tema

### 4.1 Sintaxis general

Una directiva de tema se escribe en un bloque cercado propio, inmediatamente antes del encabezado al que se aplica:

~~~md
:::xmind
style_set: TAI_LEGISLACION
style: concepto_importante
id: topic_articulo_14
labels:
  - IMPORTANTE
:::
### Artículo 14
~~~

El bloque comienza con `:::xmind` y termina con `:::`. Su contenido debe ser un mapping YAML.

Reglas de asociación:

- Solo puede existir un bloque `:::xmind` pendiente antes de un encabezado.
- Puede haber líneas vacías entre la directiva y el encabezado. No se admiten comentarios Markdown intermedios en la implementación actual.
- No puede haber párrafos, listas, citas, imágenes ni otros bloques de contenido entre ambos.
- Si aparece otra directiva de tema antes del encabezado, se produce un error.
- Si llega el final del archivo sin el encabezado de destino, se produce un error.
- La directiva se consume al crear el tema y no afecta a hermanos posteriores.

### 4.2 Propiedades admitidas

| Propiedad | Función |
|---|---|
| `id` | ID estable del tema |
| `kind` | Tipo semántico: `attached`, `callout` o `summary` |
| `style_set` | Selecciona el conjunto para este tema y sus descendientes |
| `style` | Selecciona un estilo para este tema |
| `style_overrides` | Modificaciones visuales locales |
| `labels` | Lista de etiquetas |
| `markers` | Lista de marcadores |
| `task` | Estado y progreso de tarea |
| `layout` | Propiedades locales de disposición |
| `links` | Enlaces asociados al tema |
| `extensions` | Propiedades específicas de motores o futuras extensiones |

Las propiedades de anotación pueden representarse también mediante directivas específicas de bloque cuando necesiten contenido extenso.

### 4.3 Ámbito de conjuntos y estilos

- `style_set` se hereda a los descendientes.
- Un `style_set` declarado en un descendiente reemplaza el conjunto heredado solo para esa rama.
- `style` se aplica exclusivamente al tema cuyo encabezado sigue a la directiva.
- `style_overrides` se aplica exclusivamente al tema actual.
- Los estilos no se propagan a hermanos.
- Las propiedades no definidas en un nivel inferior conservan el valor heredado.

## 5. Contenido Markdown

El contenido situado bajo un tema y antes del siguiente encabezado pertenece al tema activo.

Se admiten bloques Markdown:

| Markdown | Bloque IR |
|---|---|
| Párrafo | `paragraph` |
| Lista ordenada/no ordenada | `list` con elementos anidados |
| Tabla | `table` con filas y celdas |
| Bloque de código | `code` |
| Cita | `quote` |
| Fórmula delimitada según extensión admitida | `equation` |
| Imagen | `image` referenciada a un asset |
| Separador horizontal | `divider` |
| Texto con énfasis, enlaces o código inline | Fragmentos `runs` dentro del bloque correspondiente |

Los párrafos, listas y tablas conservan el orden de aparición. Las listas anidadas siguen siendo listas, no temas. Solo un encabezado crea un tema.

### 5.1 Código

Los bloques cercados de Markdown se convierten en bloques `code`. La etiqueta de lenguaje se conserva:

~~~md
```python
def ejemplo():
    return True
```
~~~

### 5.2 Enlaces e imágenes

Se utiliza la sintaxis Markdown estándar:

~~~md
[Boletín Oficial del Estado](https://www.boe.es/)
![Escudo](assets/escudo.png)
~~~

- Los enlaces dentro de texto se conservan como enlaces de fragmento.
- Una imagen se convierte en bloque de contenido `image` y referencia un asset del mapa.
- Las rutas relativas se resuelven respecto al archivo Markdown.
- No se descargan recursos remotos durante el parsing.
- Los enlaces internos a temas pueden usar el ID explícito del tema como destino: `[Artículo 14](topic:topic_articulo_14)`. La referencia se valida al construir el IR.\n- Los enlaces inline admitidos usan la forma `[texto](destino)` sin paréntesis anidados en el destino. No se implementan enlaces de referencia, autolinks ni destinos con paréntesis sin escapar.\n- Las imágenes inline dentro de párrafos o celdas no se consideran recursos completos; utiliza una imagen independiente en su propia línea.

## 6. Notas y directivas de bloque

Las notas son distintas del contenido principal del tema. Se declaran con un bloque cercado:

~~~md
:::xmind-note
Este contenido se incorpora a las notas del tema activo.

Puede contener **Markdown**, listas y enlaces.
:::
~~~

Reglas:

- La nota se asocia al tema activo.
- Puede haber varias notas en un tema; se conserva su orden.
- Una nota no crea un tema.
- No se permite una nota antes del tema raíz.

## 7. Marcadores, etiquetas y tareas

Pueden declararse en la directiva de tema:

~~~md
:::xmind
labels:
  - IMPORTANTE
  - EXAMEN
markers:
  - group: priority
    value: 1
  - group: progress
    value: 25
task:
  status: in_progress
  progress: 25
  due_date: 2026-12-15
:::
### Artículo 14
~~~

Reglas:

- `labels` es una lista ordenada de cadenas.
- `markers` es una lista de objetos con `group` y `value`.
- `task` admite `status`, `progress`, `start_date`, `due_date` y `assignee`.
- `progress` es un entero entre 0 y 100.
- Las fechas usan ISO 8601 (`YYYY-MM-DD`).
- Los nombres de grupos y valores de marcadores son extensibles; el adaptador determina cuáles puede representar.

## 8. Relaciones, límites y resúmenes

Estas entidades no crean temas ni alteran el árbol. Se declaran mediante directivas globales y referencian IDs de tema.

### 8.1 Relación

~~~md
:::xmind-relationship
id: rel_igualdad
source: topic_articulo_1
target: topic_articulo_14
title: Principio relacionado
style: relacion_default
:::
~~~

### 8.2 Límite (boundary)

~~~md
:::xmind-boundary
id: boundary_derechos
topics:
  - topic_articulo_14
  - topic_articulo_15
title: Derechos y principios
style: agrupacion_derechos
:::
~~~

### 8.3 Resumen (summary)

~~~md
:::xmind-summary
id: summary_igualdad
topics:
  - topic_articulo_14
  - topic_articulo_15
title: Igualdad y no discriminación
style: resumen
:::
~~~

Reglas comunes:

- Las directivas globales pueden aparecer en cualquier punto fuera de bloques de código.
- Se extraen del flujo de contenido y no se convierten en párrafos del tema activo.
- Todas las referencias deben resolverse después de analizar el documento completo.
- Los IDs referenciados deben existir.
- Los IDs de las entidades globales deben ser únicos en el mapa.
- Una relación requiere dos temas distintos.
- Un límite y un resumen requieren al menos un tema.
- Los temas incluidos en límites y resúmenes se mantienen en el orden declarado.

## 9. Estilos: YAML externo y Markdown

Se admiten dos fuentes:

1. Archivo YAML externo indicado por la CLI.
2. Front matter y directivas locales del Markdown.

El archivo externo puede contener `style_sets` y `styles`:

~~~yaml
style_sets:
  TAI_LEGISLACION:
    topic:
      typography:
        font_family: Arial
        font_size: 14
    styles:
      concepto_importante:
        topic:
          text:
            color: "#C62828"
            bold: true

styles:
  relacion_default:
    relationship:
      line:
        color: "#607D8B"
        width: 1.5
~~~

Precedencia de menor a mayor:

1. Valores predeterminados del sistema.
2. Tema visual/configuración general del mapa.
3. Conjunto de estilos efectivo.
4. Estilo concreto.
5. `style_overrides` local.

La fusión se realiza recursivamente por propiedad. Una propiedad ausente hereda; un valor explícito sustituye; `null` solicita restablecimiento según la semántica de la propiedad.

Si el mismo nombre de conjunto o estilo está definido en YAML externo y en el documento, la definición del documento prevalece para ese nombre, pero se recomienda evitar duplicidades. La CLI debe poder advertir de ellas.

## 10. Sintaxis literal y escape

- Un bloque de código cercado protege todo su contenido: ninguna directiva ni encabezado interior se interpreta.
- Para mostrar literalmente una línea que comience por `:::xmind`, debe incluirse en un bloque de código o escaparse como texto Markdown con una barra inversa delante de los dos puntos iniciales.
- Los delimitadores de directivas deben ocupar una línea propia.
- Las directivas desconocidas con prefijo `:::xmind-` producen error, para evitar que un error tipográfico se ignore.
- Los bloques cercados ordinarios de Markdown no se confunden con directivas.
- El YAML debe ser válido y no debe contener claves duplicadas.

## 11. Errores y validación

El parser debe emitir errores con archivo, línea y tipo de directiva cuando corresponda.

Errores obligatorios:

- Front matter mal formado o duplicado.
- Ausencia de encabezado raíz.
- Más de un tema raíz.
- Directiva de tema sin encabezado de destino.
- Directivas de tema consecutivas sin encabezado entre ellas.
- YAML inválido en cualquier directiva.
- Propiedad no reconocida en una directiva cerrada.
- ID duplicado.
- Referencia a tema inexistente.
- Relación que se conecta consigo misma.
- Referencia a asset inexistente.
- Lista, tabla o bloque cercado mal formado cuando impida recuperar la estructura.
- Directiva global con campos obligatorios ausentes.

El parser debe acumular errores independientes cuando sea seguro continuar, pero no debe producir un IR considerado válido si existen errores estructurales.

## 12. Compatibilidad, extensiones y pérdida de información

- La gramática define la entrada; el IR define la representación neutral.
- Las propiedades específicas de XMind se declaran bajo `extensions.xmind`.
- Las extensiones de otros motores usan su propio espacio de nombres.
- Los bloques Markdown no reconocidos que puedan conservarse íntegramente se representarán como `raw`, con formato declarado.
- No se debe descartar contenido desconocido silenciosamente.
- El adaptador de salida informa de las propiedades que no puede representar.

## 13. Ejemplo completo

El archivo `examples/constitucion.md` debe actuar como fixture de referencia. Debe incluir front matter, jerarquía, estilos, contenido estructurado, anotaciones, recursos y entidades globales.

## 14. Límites de la versión 1.0

La especificación fija la sintaxis y la semántica previstas. No implica que el parser actual implemente ya todas estas construcciones.

La implementación se hará por fases y cada bloque gramatical deberá disponer de pruebas positivas, negativas y de serialización al IR. Las funciones no implementadas deben indicarse en la documentación y en los mensajes de la CLI.


## 15. Estado real del parser (auditoría de tarea 7)

La gramática de este documento describe un subconjunto propio de Markdown enriquecido. **No debe interpretarse como compatibilidad completa con CommonMark o GitHub Flavored Markdown (GFM).** La matriz siguiente delimita el comportamiento que debe comprobarse en código y pruebas.

### 15.1 Construcciones implementadas

| Construcción | Comportamiento implementado | Restricciones |
|---|---|---|
| Front matter | YAML al inicio, delimitado por `---` o `...`; claves duplicadas y campos superiores desconocidos rechazados | Un único bloque inicial; no se admiten varios front matter |
| Encabezados | ATX H1–H6; una raíz H1; IDs explícitos o deterministas | Setext no admitido; título literal, sin formato inline; sin atributos de encabezado |
| Jerarquía | Se anidan por el encabezado abierto de nivel inferior más próximo | Se permiten saltos de nivel; no se conservan niveles como propiedad visual IR |
| Directiva `:::xmind` | YAML asociado al encabezado siguiente; valida propiedades reconocidas y varios tipos | Solo una directiva pendiente; comentarios o contenido intermedio no admitidos |
| Directivas legacy | `@conjunto(...)` y `@estilo(...)` | Compatibilidad transitoria; no utilizar en documentos nuevos |
| Notas | `:::xmind-note` asociada al tema activo; formato inline convertido a runs | El cuerpo se trata como una nota de texto; no se estructuran listas, tablas, citas ni código internos |
| Directivas globales | Relaciones, límites y resúmenes YAML; referencias y unicidad de IDs validadas tras el árbol | No se admiten propiedades arbitrarias fuera de las documentadas |
| Párrafos | Líneas consecutivas no vacías se unen con espacios; bloques separados por líneas vacías | No se conservan saltos duros ni blandos como nodos separados |
| Formato inline | Negrita (`**...`/`__...__`), cursiva (`*...*`/`_..._`), tachado (`~~...~~`), código inline y enlaces inline | Sin anidamiento de énfasis, escapes CommonMark completos, enlaces de referencia ni destinos con paréntesis anidados |
| Enlaces a temas | `[texto](topic:ID)` se convierte en enlace IR de tipo `topic` y se valida | El ID debe existir en el mismo mapa |
| Listas | Ordenadas y no ordenadas; anidamiento por sangría de espacios o tabuladores | No se admiten párrafos continuados, listas separadas por líneas vacías ni contenido mixto complejo; el tipo de lista anidada no se conserva como propiedad independiente |
| Tablas | Tablas pipe con fila de encabezado, separador y filas de igual anchura; pipe escapado (`\\|`) dentro de celdas | No se admiten celdas multilínea; la alineación del separador no se conserva |
| Citas | Líneas consecutivas que comienzan por `>` | Sin bloques anidados ni párrafos múltiples |
| Código cercado | Cercas de tres o más acentos graves o virgulillas; cierre con el mismo carácter y longitud igual o mayor | No es un parser CommonMark completo; no se admiten bloques de código indentados |
| Separador | Una línea formada por al menos tres guiones, asteriscos o guiones bajos (con espacios opcionales) | No se admiten variantes HTML |
| Imagen | Imagen Markdown independiente en su propia línea; se crea asset y referencia del tema | No se comprueba la existencia física del fichero ni se descargan URLs remotas |
| Procedencia | Temas y bloques principales conservan archivo y rango de líneas | No se conserva todavía procedencia por celda, elemento de lista, run inline, nota ni directiva global |

### 15.2 Construcciones no implementadas o limitadas explícitamente

- Encabezados Setext, HTML embebido, bloques HTML y comentarios HTML.
- Fórmulas matemáticas y bloques `equation`.
- Bloques `raw` declarados por el usuario; el tipo se reserva para conversiones internas.
- Enlaces de referencia, autolinks, enlaces con destinos que contienen paréntesis anidados y sintaxis de título de destino.
- Imágenes inline con inventario completo de assets, imágenes remotas y adjuntos/audio.
- Énfasis anidado, escapes completos de caracteres Markdown, subrayado y tachado alternativo.
- Listas con párrafos continuados, listas laxas, tareas Markdown `- [ ]`, elementos con varios bloques y mezcla compleja de listas ordenadas/no ordenadas.
- Tablas multilínea, alineación visual y sintaxis extendida GFM.
- Citas anidadas, atribución de citas y varios párrafos estructurados en una misma cita.
- Notas con bloques estructurados; por ahora se conserva el texto y se reconoce su formato inline.
- Atributos de encabezado, identificadores automáticos de ancla y extensiones de Markdown de terceros.
- Diagnósticos acumulados: el parser detiene el análisis en el primer error estructural que impide continuar.

### 15.3 Procedencia y contrato IR

Cada tema conserva el archivo y la línea de su encabezado. Los bloques principales de contenido conservan `source.file`, `source.line_start` y `source.line_end` en los datos del bloque IR. Los rangos son inclusivos. La procedencia granular de subelementos queda pendiente.

El parser canónico utiliza `parse_markdown_ir()` y `parse_file_ir()`. La conversión debe preservar el orden de los bloques, el orden de los temas y las referencias internas. La salida se comprueba con `validate_mind_map()`; la validación semántica no implica que el adaptador XMind pueda exportar todas las capacidades.

### 15.4 Política de compatibilidad

La gramática implementada se limita a las construcciones de la sección 15.1. Las construcciones de la sección 15.2 deben rechazarse cuando puedan confundirse con sintaxis admitida, o permanecer como texto literal cuando su interpretación sea inequívoca. No se debe anunciar compatibilidad CommonMark/GFM completa ni descartar silenciosamente contenido que el parser haya reconocido como estructura.
