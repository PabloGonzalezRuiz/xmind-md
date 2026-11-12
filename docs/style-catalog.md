# Catálogo semántico y visual de estilos PMD

**Versión del contrato de catálogo:** 1.0.0 (diseño de Fase 3)  
**Estado:** especificación propuesta para revisión; no implementada en el runtime.  
**Relacionados:** [ADR-001](decisions/ADR-001-pmd-ir-architecture.md), [ADR-002](decisions/ADR-002-ir-semantic-structures.md), [sistema de estilos](style-system.md), [diseño PMD](pmd-design.md).

## 1. Propósito y límites

El catálogo permite que una persona o una IA seleccione estilos por significado y contexto, sin repetir propiedades visuales ni escribir nombres internos de XMind. El catálogo es una biblioteca de diseño independiente del documento PMD y del resolutor IR 1.x.

Este contrato no cambia IR 1.1.0, la sintaxis Markdown existente, el YAML runtime `config/styles.yaml` ni el adaptador XMind. La IA propone roles/referencias; el futuro parser validará; el motor resolverá. La IA no determina el valor visual final.

## 2. Separación de conceptos

| Concepto | Identifica | Ejemplo | Dónde vive |
|---|---|---|---|
| Rol semántico | Qué significa el contenido | `legal.article` | `Topic.semantic_role` |
| Estructura | Cómo se relacionan los elementos | `tree_table`, fila/celda | `Topic.structure` |
| Estilo visual | Cómo se presenta un elemento | `legal.article` | Catálogo, estilo referenciado |
| Regla | Cuándo aplicar un estilo | Rol artículo | Catálogo |
| Herencia | Qué propiedades se toman de un hermano de referencia | primer hijo | Política del catálogo |
| Anotación | Indicador funcional/editorial | marcador, etiqueta | Anotaciones IR; no estilo |

Los IDs de rol y estilo son espacios de nombres distintos aunque compartan un nombre parecido. Los roles describen semántica; los estilos agrupan propiedades visuales. No se inferirá un rol desde el color, la forma, el nivel de encabezado o el texto literal si no hay evidencia.

## 3. Contrato de catálogo 1.0.0

El archivo canónico de referencia es [`catalog/style-catalog.json`](../catalog/style-catalog.json), validable contra [`style-catalog.schema.json`](style-catalog.schema.json).

Campos obligatorios:

- `catalog_version`: versión del contrato del catálogo, independiente de IR.
- `catalog_id`: identificador estable del catálogo.
- `roles`: vocabulario semántico abierto, con descripción, destinatarios, criterios positivos/negativos y estilo recomendado.
- `styles`: estilos visuales reutilizables, con ID, descripción, elementos destinatarios y propiedades neutrales.
- `rules`: reglas semánticas o estructurales que vinculan contexto y estilo.
- `defaults`: valores base visuales para elementos sin regla más específica.
- `inheritance`: política explícita de herencia por primer hijo.

Los identificadores usan minúsculas ASCII y namespaces con punto, por ejemplo `legal.article`, `table.header_cell`, `legal.article` (rol) y `legal.article` (estilo) solo se pueden reutilizar si el contexto tipado deja inequívoco cuál es cuál; se recomienda usar IDs diferenciados cuando mejore la legibilidad. Los IDs publicados no se renombran: se deprecian y se añade un sustituto con alias/migración documentada en una versión posterior.

### 3.1 Metadatos de rol

Cada rol documenta:
- significado y alcance;
- entidades destinatarias;
- cuándo usar y cuándo no usar;
- ejemplos positivos y negativos;
- estilo recomendado;
- restricciones adicionales si las hay.

El vocabulario es abierto: un documento puede contener un rol externo no incluido en este catálogo. Un validador en modo estricto podrá advertirlo o rechazarlo según la política del proyecto; no debe reinterpretarlo silenciosamente como otro rol. La Fase 3 define el catálogo de referencia, no el modo de validación del parser PMD.

### 3.2 Definiciones de estilo

Cada estilo declara `applies_to` y `properties`. Las propiedades son neutrales y agrupadas por elemento. Un estilo no asigna roles ni altera la estructura. Las propiedades ausentes no se materializan en la definición y quedan disponibles para las capas inferiores/superiores de la cascada según la regla aplicable.

### 3.3 Reglas

Una regla tiene ID estable, tipo (`semantic` o `structural`), predicado de coincidencia, estilo de destino, prioridad entera y descripción. La semántica tiene precedencia de familia sobre la estructura; la prioridad solo desempata reglas dentro de una misma familia. Si dos reglas de igual familia y prioridad producen valores distintos para una misma propiedad y no existe una regla de especificidad inequívoca, el catálogo es ambiguo y debe fallar la validación. No se usa el orden del array ni el orden alfabético como desempate.

## 4. Vocabulario semántico inicial

El catálogo de referencia propone roles jurídicos y de tabla (ver JSON). No es un enum cerrado de IR. Los IDs principales son:

- Jerarquía normativa: `legal.document_title`, `legal.book`, `legal.part`, `legal.title`, `legal.chapter`, `legal.section`, `legal.article`, `legal.paragraph`.
- Función normativa: `legal.definition`, `legal.exception`, `legal.obligation`, `legal.prohibition`, `legal.deadline`, `legal.reference`.
- Tablas: `table.header_cell`, `table.body_cell`.
- Material editorial: `study.note`.

No se debe asignar `legal.exception` por la mera presencia de palabras como «salvo», «excepto» o «sin perjuicio»: el contexto debe confirmar que la unidad tiene función de excepción. Una obligación, prohibición o plazo se marca solo si la fuente expresa esa función. Un contenido editorial no se clasifica como norma.

## 5. Propiedades visuales neutrales

El contrato 1.0.0 del catálogo admite inicialmente:

| Ruta | Tipo | Unidad/valores |
|---|---|---|
| `topic.text.font_family` | string | nombre de familia |
| `topic.text.font_size` | number | puntos; > 0 |
| `topic.text.font_weight` | enum/entero | normal, bold o 100–900 |
| `topic.text.font_style` | enum | normal, italic |
| `topic.text.color` | color | `#RRGGBB` o `#RRGGBBAA` |
| `topic.text.text_transform` | enum | none, uppercase, lowercase, capitalize |
| `topic.text.decoration` | enum | none, underline, line_through |
| `topic.text.align` | enum | left, center, right, justify |
| `topic.fill.color` | color | hexadecimal |
| `topic.fill.opacity` | number | 0–1 |
| `topic.border.color` | color | hexadecimal |
| `topic.border.width` | number | puntos; >= 0 |
| `topic.border.pattern` | enum | solid, dashed, dotted, dash_dot |
| `topic.shape.type` | enum | rectangle, rounded_rectangle, ellipse, underline, double_underline, none |

El esquema reserva otros tipos de elemento, pero sus propiedades quedan fuera del primer perfil de catálogo hasta definir semántica y mapeo. No se incluyen coordenadas absolutas, plegado, orden, estructura, marcadores ni propiedades internas XMind dentro del estilo visual.

Los tokens neutrales de catálogo no se deben confundir con la estructura del YAML runtime actual. La migración de propiedades hacia el resolutor será una tarea posterior con compatibilidad y pruebas; esta fase no reescribe `config/styles.yaml`.

## 6. Reglas semánticas y estructurales

Orden de familia:

1. Las reglas semánticas son prioritarias: un rol conocido selecciona su estilo.
2. Las reglas estructurales complementan la semántica y sirven de fallback cuando falta un rol aplicable o no hay regla semántica coincidente.
3. Una regla estructural no puede sustituir una regla semántica coincidente por tener mayor prioridad numérica.
4. Si varias reglas de una misma familia coinciden, se aplica la de mayor prioridad. En empate, solo se permite combinar si no hay conflictos de propiedad; si hay conflicto, error.
5. Una regla desconocida o un estilo referenciado inexistente es error de catálogo, no fallback silencioso.

Ejemplo: una celda de `tree_table` sin rol recibe el estilo estructural `table.body-cell`. Si su rol es `table.header_cell`, prevalece la regla semántica de cabecera. Así la estructura no anula el significado.

## 7. Herencia por referencia al primer hijo

La herencia se define como una regla PMD de autoría, no como comportamiento nativo demostrado de XMind y no como herencia de `style_set`.

### 7.1 Ámbitos

- Árbol ordinario: grupos de hijos directos del mismo padre.
- `tree_table`: las celdas de cada fila forman un grupo independiente; el primer `topic_id` de la fila es su referencia. No se mezclan celdas de filas distintas.
- No se propaga entre relaciones, anotaciones, límites u otras entidades no incluidas en el grupo.

### 7.2 Fuente y recursividad

La fuente es el **estilo visual efectivo** del primer hijo del grupo después de resolver sus propios defaults, contexto estructural, regla semántica y referencias explícitas, pero antes de aplicar la herencia de sus hermanos. Los hermanos siguientes reciben una copia de sus propiedades visuales como capa de herencia. La copia es por valor y no muta el primer hijo ni los catálogos.

La resolución se hace en recorrido top-down:
1. Resolver el tema raíz con defaults, reglas y referencias explícitas.
2. Para cada grupo de hijos, resolver el primer hijo sin herencia de ese grupo.
3. Tomar su estilo efectivo como fuente.
4. Resolver los demás hijos con esa fuente como capa de herencia.
5. Aplicar el mismo procedimiento recursivamente a los hijos de cada tema.

No hay dependencia circular: el primer hijo nunca hereda de sus hermanos.

### 7.3 Fusión por propiedad y excepciones

La herencia solo rellena propiedades ausentes. No sobrescribe una propiedad aportada por una regla semántica coincidente, un estilo explícito o un override local del propio hijo. Por ello, una celda `table.body_cell` puede heredar tipografía y bordes de la primera celda y, a la vez, conservar el relleno/color de su propio estilo semántico.

Una excepción se declara explícitamente en el propio hijo mediante estilo referenciado o override local; esa propiedad prevalece sobre la herencia. Una excepción parcial solo sustituye las propiedades declaradas, no todo el estilo. Una excepción total requerirá una futura sintaxis explícita; no se introduce aquí.

### 7.4 Primer hijo sin estilo explícito

La ausencia de estilo escrito no equivale a ausencia de estilo efectivo. El primer hijo se resuelve normalmente con defaults y reglas. Ese resultado efectivo será la fuente. Si tampoco hay regla aplicable, se heredan únicamente los defaults aplicables que el primer hijo haya resuelto. Si el primer hijo no tiene ninguna propiedad efectiva para una ruta, no se inventa un valor para los hermanos.

## 8. Precedencia completa por propiedad

De menor a mayor prioridad:

1. Defaults generales del catálogo.
2. Regla estructural aplicable.
3. Herencia desde el primer hijo del grupo (solo para propiedades aún ausentes).
4. Regla semántica aplicable.
5. Estilo explícito referenciado por el elemento.
6. Overrides locales explícitos del elemento.

La herencia de `style_set` IR 1.x es un contexto separado y no se reinterpreta como herencia visual. Durante la transición, el runtime IR 1.x conserva su cascada actual (defaults del sistema → `metadata.style_defaults` → conjunto → estilo nombrado → overrides). La precedencia anterior pertenece al motor PMD objetivo y se aplicará solo cuando el catálogo y el PMD se implementen y versionen.

### 8.1 Ausencia, null e inherited

- Ausencia: no aporta valor; permite aplicar capas inferiores.
- Valor explícito: aporta valor en su capa.
- `null`: reinicia la propiedad al default general del catálogo y bloquea valores de capas inferiores; una capa posterior de mayor prioridad aún puede reemplazarlo.
- Cadena literal `"inherited"`: no es una instrucción PMD. Se conserva literalmente solo en importaciones/compatibilidad del formato de origen; no es un valor permitido por este catálogo.
- Herencia de primer hijo: se representa mediante la política `inheritance`, nunca con el literal `inherited`.

## 9. Conflictos, diagnósticos y determinismo

El motor debe:
- validar que cada `style_ref` exista y sea compatible con `applies_to`;
- detectar IDs duplicados, roles/estilos no declarados, propiedades desconocidas, tipos/rangos inválidos y reglas contradictorias;
- producir error ante conflictos irresolubles, sin elegir por orden accidental;
- conservar el valor ganador y su procedencia por propiedad;
- informar de propiedades que el adaptador destino no soporte, sin eliminarlas silenciosamente;
- producir el mismo resultado para el mismo documento, catálogo, versión y perfil de adaptador.

La procedencia mínima por propiedad deberá distinguir: default, regla estructural, herencia de primer hijo (incluyendo ID de origen), regla semántica, estilo explícito y override local. La trazabilidad es parte del resultado de diseño aunque el IR/runtime actual todavía no la almacene.

## 10. Relación con el YAML runtime existente

`config/styles.yaml` continúa siendo la configuración consumida por `resolve_ir_styles()`. Su esquema y precedencia no cambian en Fase 3. El nuevo catálogo JSON es una especificación semántica de autoría y no se carga desde el runtime actual. No se debe presentar como reemplazo ni mezclar sus claves con `style_sets`/ `styles`.

Una fase posterior definirá un adaptador/migración del catálogo PMD a la representación de estilos del IR. Hasta entonces, las pruebas conceptuales de esta fase validan el diseño, no la ejecución Python.

## 11. Casos de resolución de referencia

Los casos deterministas y sus resultados esperados están en [`style-resolution-cases.md`](style-resolution-cases.md). Cubren prioridad semántica, fallback estructural, herencia por grupo, excepción parcial, ausencia de estilo explícito, conflictos y procedencia.

## 12. Criterios de cierre de Fase 3

- [x] Contrato versionado y esquema legible por máquina.
- [x] Vocabulario semántico inicial orientado a legislación/tablas.
- [x] Estilos visuales separados de roles y reglas.
- [x] Propiedades neutrales iniciales y restricciones.
- [x] Prioridad semántica sobre reglas estructurales.
- [x] Precedencia por propiedad, defaults, fallback y excepciones.
- [x] Herencia por primer hijo con alcance, fuente, recursividad y grupos de tabla.
- [x] Ausencia, `null` y literal `inherited` diferenciados.
- [x] Procedencia y diagnósticos definidos.
- [x] Compatibilidad conceptual con el YAML runtime actual preservada.
- [x] Casos de resolución de referencia documentados.

**Fuera de alcance:** implementación del loader/runtime, parser PMD, cambios en IR, conversión IA, adaptador XMind y publicación de release.
