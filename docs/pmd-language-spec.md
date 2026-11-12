# Especificación del lenguaje PMD

**Nombre:** Pableras Markdown (PMD) · **Versión:** 1.0.0 · **IR de destino:** 1.1.0 · **Catálogo de referencia:** `xmind-md.study` 1.0.0  
**Estado:** especificación aprobada en Fase 4; parser no implementado.  
**Fecha:** 2026-11-12.

## 1. Propósito y alcance

PMD es un lenguaje de autoría basado en Markdown enriquecido para describir mapas de estudio: jerarquía, contenido, semántica, estructuras compuestas, referencias de estilo y anotaciones. No es el Markdown nativo de XMind, no es una copia textual del IR y no permite escribir directamente `content.json`.

Flujo objetivo:

```text
Markdown fuente → interpretación humana/IA → PMD → parser/validador → IR 1.1.0
               → catálogo/resolución de estilos → adaptador → XMind
```

La IA identifica estructura y significado y propone roles/referencias; no decide los valores visuales efectivos. El parser valida sintaxis y referencias. El resolutor aplica el catálogo determinísticamente.

Las palabras **MUST**, **MUST NOT**, **SHOULD** y **MAY** expresan requisito, prohibición, recomendación y opción.

## 2. Principios normativos

1. Markdown es la base del contenido y de la jerarquía.
2. Solo encabezados ATX crean temas. Listas, tablas Markdown, párrafos, citas y bloques de código son contenido.
3. Jerarquía, rol semántico, estructura y estilo visual son conceptos distintos.
4. Roles y estilos se declaran por separado.
5. Estructuras compuestas referencian temas por ID; nunca duplican títulos o contenido.
6. Las referencias adelantadas se resuelven después de construir el árbol.
7. Ausencia, valor explícito y `null` tienen semánticas distintas.
8. El literal `inherited` no es una instrucción PMD.
9. La sintaxis neutral no contiene clases ni propiedades privadas de XMind.
10. Nada desconocido se descarta silenciosamente.
11. Una misma entrada, catálogo y versión produce el mismo IR o diagnósticos deterministas.
12. PMD 1.0.0 genera IR 1.1.0; no redefine IR 1.0.0.

## 3. Modelo de documento y front matter

Un archivo representa un mapa, una hoja y un único tema raíz. Contiene front matter YAML obligatorio, seguido del cuerpo Markdown enriquecido y sus directivas.

Ejemplo mínimo:

```yaml
---
pmd_version: "1.0.0"
title: Constitución Española
id: map_constitucion
catalog:
  id: xmind-md.study
  version: "1.0.0"
---
```

Campos de nivel superior:

| Campo | Tipo | Obligatorio | Función |
|---|---|---:|---|
| `pmd_version` | string | Sí | Versión exacta del lenguaje |
| `title` | string | No | Título del mapa; por defecto el del tema raíz |
| `id` | string | No | ID estable del mapa |
| `author` | string | No | Autoría |
| `description` | string | No | Descripción |
| `catalog` | mapping | Condicional | Identidad y versión exacta del catálogo |
| `inheritance` | mapping | No | Política de herencia visual |
| `metadata` | mapping | No | Metadatos descriptivos adicionales |
| `extensions` | mapping | No | Extensiones namespaced |

`catalog` contiene `id` y `version`. Es obligatorio si se usa cualquier `role`, `style_ref` o regla del catálogo. No se admite resolver contra una versión implícita o «latest». Puede omitirse en documentos sin referencias a catálogo.

`inheritance.mode` admite `catalog` (por defecto; aplica la política del catálogo) o `none` (desactiva la herencia PMD por primer hijo en todo el documento). PMD 1.0.0 no permite redefinir el algoritmo del catálogo.

Las claves desconocidas en mappings cerrados son error. Las extensiones deben vivir en `extensions.<namespace>`; este campo no permite eludir la validación de los campos normalizados.

### 3.1 YAML

Se rechazan claves duplicadas, alias/ciclos, tags personalizados, valores no representables en JSON, NaN e infinito. Las fechas deben escribirse como cadenas ISO 8601 para evitar conversiones implícitas dependientes de la biblioteca. Las listas conservan su orden.

## 4. Encabezados y jerarquía

Los encabezados ATX H1–H6 crean temas:

```md
# Constitución Española
## Título I. De los derechos y deberes fundamentales
### Capítulo segundo
#### Artículo 14
##### Apartado 1
```

- El primer encabezado debe ser H1 y crea la raíz.
- Solo puede existir un H1.
- H2–H6 se anidan bajo el encabezado abierto de nivel inferior más próximo.
- Se permiten saltos de nivel.
- El nivel de encabezado expresa anidamiento, no rol ni estilo.
- El texto del encabezado es el título; el énfasis inline no asigna estilos al tema.
- Si no hay `parent`, el padre se infiere por la pila de niveles ATX. Si la directiva declara `parent`, ese ID prevalece y puede apuntar a un tema declarado antes o después.
- `parent` no cambia el título ni crea un nodo adicional. Cada tema tiene un único padre; la raíz no declara `parent`; el grafo final debe ser un árbol conectado y sin ciclos.
- Los encabezados dentro de código cercado son literales.
- Setext, atributos de encabezado y HTML no forman parte del perfil PMD 1.0.0.

**Las listas no crean temas.** Numeración jurídica como `1.`, `a)` o `b)` sigue siendo contenido, salvo que el autor la eleve explícitamente a encabezado. Las tablas Markdown pipe también son contenido. No se infiere `tree_table` de listas, tablas pipe, negritas ni de la mera existencia de hermanos.

## 5. Directiva de tema `:::pmd`

### 5.1 Asociación

Una directiva YAML `:::pmd` se coloca inmediatamente antes del encabezado al que se aplica:

```md
:::pmd
id: articulo_14
role: legal.article
style_ref: visual.legal.article
:::
#### Artículo 14. Igualdad ante la ley
```

Se permite espacio en blanco entre directiva y encabezado, pero no otro bloque Markdown. Solo puede haber una directiva pendiente. Una directiva sin encabezado posterior es error. Se consume al crear el tema y no afecta a hermanos.

### 5.2 Campos cerrados

| Campo | Tipo | Correspondencia IR |
|---|---|---|
| `id` | string | `Topic.id` |
| `parent` | string | Relación padre-hijo del árbol; no es un campo propio del Topic IR |
| `kind` | string | `Topic.kind` |
| `role` | string | `Topic.semantic_role` |
| `style_ref` | string | `Topic.style.ref` |
| `style_overrides` | mapping | `Topic.style.overrides` |
| `structure` | mapping | `Topic.structure` |
| `labels` | lista de strings | `Topic.annotations.labels` |
| `markers` | lista de mappings | `Topic.annotations.markers` |
| `task` | mapping | `Topic.annotations.task` |
| `layout` | mapping | `Topic.layout` |
| `links` | lista de mappings | `Topic.links` |
| `extensions` | mapping | `Topic.extensions` |

No se admiten claves desconocidas. Se utiliza `role` como forma compacta de autoría; el IR mantiene el nombre `semantic_role`. El campo opcional `parent` declara el ID del tema padre y prevalece sobre el padre inferido por nivel de encabezado; permite representar árboles con más de seis niveles sin convertir listas en temas. Si varios temas declaran el mismo padre, su orden en `children` es el orden de aparición en el documento.

### 5.3 Kind y rol

`kind` admite `attached`, `detached`, `callout` y `summary`; la raíz MUST ser `attached`. Si se omite, se aplica el valor por defecto del IR. Se validan las restricciones de disposición del tipo elegido.

`role` describe qué representa el tema, no su posición ni apariencia. Ejemplos: `legal.article`, `legal.exception`, `legal.obligation`, `table.header_cell`, `table.body_cell`. Se valida contra el catálogo declarado. Un rol desconocido es error en el modo estricto PMD 1.0.0; no se sustituye por otro ni se infiere del color, nivel de encabezado o texto literal.

### 5.4 Referencia visual y overrides

`style_ref` identifica un estilo visual del catálogo, por ejemplo `visual.legal.article`; no es un rol semántico. Se valida su existencia y compatibilidad con el destinatario.

`style_overrides` permite excepciones locales por propiedad:

```yaml
style_overrides:
  topic:
    fill:
      color: "#F6A04D"
    text:
      color: "#263B5A"
```

Las rutas, tipos y rangos deben cumplir el catálogo. Los overrides no cambian el rol ni la estructura.

Semántica de propiedad:
- Ausente: no aporta valor; permite actuar a las demás capas.
- Valor explícito: aporta valor en su capa.
- `null`: reinicio al default general del catálogo; bloquea capas inferiores.
- Cadena `"inherited"`: inválida como valor visual PMD 1.0.0; no activa herencia.

La herencia por primer hijo es política del catálogo. Las excepciones parciales usan `style_ref` u overrides locales y afectan solo a las propiedades declaradas.

### 5.5 Anotaciones

`labels` es una lista ordenada de cadenas. `markers` es una lista ordenada de mappings con `group` y `value`; puede incluir `id` explícito, y si se omite el parser genera uno determinista. Los IDs de etiquetas y notas también se generan determinísticamente cuando el IR los requiere. `task` sigue el contrato de anotaciones IR y sus estados, progreso, fechas y asignación admitidos. Anotaciones, roles y estilos son conceptos independientes.

## 6. Estructura compuesta `tree_table`

Se declara en el tema contenedor. Las celdas son temas hijos directos identificados por ID; título, contenido, anotaciones, recursos y estilo residen en cada tema hijo.

```md
:::pmd
id: articulo_14
role: legal.article
structure:
  type: tree_table
  rows:
    - cells: [cabecera, cuerpo]
:::
#### Artículo 14

:::pmd
id: cabecera
role: table.header_cell
:::
##### Cabecera
Texto de cabecera.

:::pmd
id: cuerpo
role: table.body_cell
:::
##### Cuerpo
Texto de contenido.
```

Reglas:
- En PMD 1.0.0 solo se admite `structure.type: tree_table`.
- `rows` es lista ordenada no vacía; cada fila tiene una lista `cells` no vacía.
- Cada celda referencia un hijo directo del contenedor. En la sintaxis PMD, cada entrada de `cells` es el ID textual del hijo; el parser la normaliza a `TreeTableCell(topic_id=<id>)`.
- No se repiten IDs y todos los hijos directos deben aparecer exactamente una vez.
- El orden de filas y celdas es significativo.
- El rol de celda se declara en el tema referenciado; no se duplica en el descriptor. La lista abreviada de IDs en PMD se convierte en objetos `{topic_id: ...}` en IR 1.1.0, conservando el orden.
- No hay celdas vacías, referencias a nietos, celdas combinadas, rowspan/colspan ni celdas sin tema propio.
- Una celda puede contener otra estructura, siguiendo el árbol.

La estructura no crea ni reordena temas. Las referencias pueden apuntar a encabezados posteriores y se resuelven al finalizar la construcción del árbol. La tabla de árbol no es un bloque Markdown ni se infiere de una tabla pipe.

## 7. Herencia visual por primer hijo

Por defecto se aplica la política del catálogo seleccionado. En el catálogo de referencia, el primer hijo de cada grupo aporta el estilo efectivo de referencia; los siguientes hijos reciben solo propiedades ausentes. En `tree_table`, cada fila es un grupo independiente.

- La fuente se resuelve sin heredar de sus hermanos.
- Las reglas semánticas, estilos explícitos y overrides locales del hijo prevalecen conforme al orden de resolución del catálogo.
- La resolución es top-down y recursiva.
- No se comparte estilo entre filas.
- `inheritance.mode: none` desactiva esta política para el documento.
- Las excepciones son por propiedad; PMD 1.0.0 no incluye una directiva para copiar o heredar el estilo completo.

Esta es una política PMD, no una afirmación sobre la herencia nativa de XMind Desktop.

## 8. Contenido, notas, enlaces y recursos

El contenido ordinario posterior a un encabezado pertenece al tema activo hasta el siguiente encabezado o directiva global. PMD 1.0.0 adopta el perfil implementado y delimitado en `docs/grammar.md` §15.1; no afirma compatibilidad CommonMark/GFM completa. Listas anidadas siguen siendo contenido.

Nota asociada al tema activo:

```md
:::pmd-note
Observación de estudio. Puede contener Markdown del perfil admitido.
:::
```

Una nota no crea tema, conserva el orden de varias notas y no puede preceder a la raíz.

Se utiliza Markdown para enlaces e imágenes:
- Externo: `[BOE](https://www.boe.es/)`.
- Interno: `[Artículo 14](topic:articulo_14)`.
- Imagen: `![Descripción](assets/imagen.svg)`.

Las rutas relativas se resuelven respecto al documento. No se descargan URLs remotas. Los enlaces internos deben resolver a IDs existentes. Enlaces de referencia y destinos con paréntesis anidados quedan fuera del perfil.

Directivas globales, fuera de bloques de código:
- `:::pmd-relationship`: relación entre dos temas.
- `:::pmd-boundary`: agrupación visual.
- `:::pmd-summary`: resumen de uno o varios temas.

Su cuerpo es YAML conforme al contrato IR de la entidad correspondiente. Las referencias se resuelven al final; los IDs globales son únicos; las listas conservan el orden. Una relación exige dos temas distintos; límite y resumen exigen al menos un tema. Campos no normalizados deben ir bajo `extensions`.

## 9. IDs y referencias

Los IDs explícitos son cadenas no vacías y únicas en el mapa. Deben declararse explícitamente en temas referenciados por estructura, enlaces, relaciones, límites o resúmenes. Los IDs de entidades auxiliares son obligatorios.

Si un tema no declara ID, el parser genera uno determinista:
1. Normalizar la ruta de origen a separadores `/` y Unicode NFC.
2. Construir la ruta de encabezados según la pila sintáctica ATX (antes de aplicar overrides `parent`); normalizar cada título a NFC conservando el texto.
3. Añadir el ordinal 1-based del tema entre encabezados con igual título normalizado bajo el mismo padre inferido por la pila ATX.
4. Unir los componentes con U+0000 y calcular SHA-256 UTF-8.
5. Usar `auto-` + los primeros 16 caracteres hexadecimales minúsculos.

Si no hay ruta de origen se usa `<memory>`. Colisiones con IDs explícitos o generados son error; no se resuelven con sufijos dependientes del orden. El campo `parent` debe resolver a un tema del documento; la relación final debe ser acíclica, conectada y con un solo padre por tema. Los IDs son opacos, no títulos ni etiquetas semánticas.

## 10. Escapes y delimitadores

- Bloques de código cercados protegen todo su contenido.
- Los delimitadores `:::` ocupan línea propia.
- Una directiva literal se escribe dentro de código o se escapa según el perfil Markdown.
- `:::pmd` solo es directiva de tema antes de un encabezado.
- `:::pmd-note`, `:::pmd-relationship`, `:::pmd-boundary` y `:::pmd-summary` deben cerrarse con `:::`.
- Directivas `:::pmd-*` desconocidas son error.
- `:::xmind` y `:::xmind-*` son directivas legacy distintas; no se reinterpretan. Solo podrán procesarse mediante modo de compatibilidad explícito.
- Las cercas de código tienen prioridad léxica. No se permiten directivas PMD anidadas.

## 11. Versionado y compatibilidad

- `pmd_version: "1.0.0"` es obligatorio.
- Un parser no compatible debe rechazar la versión; no ignorará campos desconocidos.
- Ampliaciones aditivas sin cambio de interpretación pueden publicarse como 1.1.0.
- Cambios incompatibles de gramática o semántica requieren 2.0.0.
- La versión del catálogo es independiente y se fija exactamente.
- PMD 1.0.0 produce IR 1.1.0 incluso si no usa roles/estructuras.
- La sintaxis preexistente `:::xmind` no se modifica.

## 12. Correspondencia PMD → IR

| PMD | IR 1.1.0 |
|---|---|
| Front matter `title/id/author/description` | `MindMap` y `metadata` |
| Encabezados | `Topic.title` y `children` |
| `id/kind/role` | `Topic.id/kind/semantic_role` |
| `parent` | Relación de pertenencia en `Topic.children`; no se serializa como propiedad del Topic |
| `style_ref/style_overrides` | `Topic.style.ref/overrides` |
| `structure` | `Topic.structure`; cada ID de `cells` se normaliza a `TreeTableCell.topic_id` |
| `inheritance.mode` | Política de resolución PMD registrada como metadato de autoría; no altera el contrato IR 1.1.0 |
| `labels/markers/task` | `Topic.annotations` |
| Bloques Markdown | `Topic.content` |
| Nota | `Topic.annotations.notes` |
| Imagen/adjunto | `assets` y `Topic.resources` |
| Enlace | `Topic.links` |
| Relación/límite/resumen | Entidades de `Sheet` |
| Catálogo/versión PMD | `MindMap.metadata` |

El árbol es la única fuente de títulos y contenido de las celdas. `tree_table` solo almacena referencias ordenadas.

Las referencias de estilo del catálogo PMD son referencias de autoría, no nombres del YAML `style_sets/styles` que consume `resolve_ir_styles()`. El parser conserva las referencias y valida el contrato, pero no afirma que el resolutor IR 1.x ejecute el catálogo PMD. La integración del catálogo y la resolución quedan fuera de Fase 4.

## 13. Errores y diagnósticos

Los diagnósticos deben incluir ruta, línea, columna, directiva y campo cuando sea posible. Son errores: front matter ausente/duplicado o YAML inválido; versión no soportada; catálogo ausente/inexistente cuando se necesita; raíz ausente o varios H1; directiva de tema sin destino o mal asociada; claves duplicadas/desconocidas; ID vacío/duplicado; rol o estilo inexistente/incompatible; kind inválido; estructura desconocida; filas/celdas vacías; referencias a padre inexistente, autorreferencia o ciclo; referencias a hijo inexistente/no directo; referencias repetidas o hijos omitidos; propiedad visual inválida o literal `inherited`; entidad global incompleta/duplicada; referencias internas irresolubles; directiva desconocida/sin cierre; contenido no soportado que no pueda preservarse sin pérdida.

El parser SHOULD acumular errores independientes si puede continuar con seguridad. No devuelve IR válido con errores estructurales. Advertencias y errores deben distinguirse y las advertencias no pueden ocultar pérdidas.

## 14. Algoritmo de análisis

1. Validar front matter y versión.
2. Proteger bloques de código.
3. Tokenizar encabezados y directivas PMD.
4. Construir el árbol desde encabezados y asignar IDs.
5. Asociar directivas de tema con su encabezado siguiente.
6. Asociar contenido y notas al tema activo.
7. Registrar estructuras y referencias globales.
8. Resolver referencias de padres explícitos, celdas de tabla, enlaces y entidades.
9. Validar roles, estilos, propiedades, cardinalidad y catálogo.
10. Construir IR 1.1.0 y ejecutar su validación.
11. Emitir IR solo sin errores; ordenar diagnósticos por posición y código estable.

El AST sintáctico puede ser temporal; no se crea un segundo modelo de dominio. IR sigue siendo el único modelo de ejecución.

## 15. Ejemplos de referencia

- [Constitución Española — jerarquía legal y tabla de árbol](../examples/pmd/constitucion-estructura.pmd.md).
- [Tabla de árbol — patrón de Tema1](../examples/pmd/tabla-arbol-tema1.pmd.md).

Son fixtures de especificación, todavía no parseados por el runtime.

## 16. Cierre de Fase 4

- [x] Modelo de documento y front matter versionado.
- [x] Relación entre Markdown, encabezados, listas y contenido, con `parent` explícito para árboles de profundidad superior a H6.
- [x] Roles separados de estilos visuales.
- [x] Sintaxis tree_table con referencias a IDs.
- [x] Herencia y excepciones por propiedad.
- [x] Metadatos, anotaciones, notas, enlaces, recursos y entidades globales.
- [x] IDs, referencias adelantadas, escapes, errores y compatibilidad.
- [x] Correspondencia con IR 1.1.0.
- [x] Ejemplos legislativo y de tabla de árbol.

**Fuera de alcance:** parser, validador runtime, loader y resolución PMD del catálogo, conversión IA, ampliación del adaptador XMind, pruebas Desktop y publicación. Corresponden a fases posteriores.
