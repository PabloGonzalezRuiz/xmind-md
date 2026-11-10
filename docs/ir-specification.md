# Especificación del modelo intermedio (IR)

**Proyecto:** XMind MD  
**Versión del contrato:** 1.0.0  
**Estado:** especificación aprobada; esquema Draft 2020-12 validado y ejemplo conforme  
**Esquema asociado:** [ir-schema.json](ir-schema.json)  
**Ejemplo:** [constitucion.json](../examples/ir/constitucion.json)

## 1. Propósito

El modelo intermedio (Intermediate Representation, IR) es el contrato neutral entre el documento Markdown enriquecido, el parser, el sistema de estilos y los adaptadores de salida.

El IR describe el significado y la presentación de un mapa mental sin depender de una biblioteca concreta ni del formato interno de XMind. Su objetivo de cobertura es representar las capacidades documentales y visuales de XMind, conservando también propiedades específicas mediante extensiones.

El IR no modela funciones de servicio de la aplicación —cuentas, colaboración en tiempo real, sincronización o funciones de IA— salvo que en el futuro se defina un módulo separado para ello.

## 2. Decisiones de diseño

1. Un archivo Markdown produce un mapa con una única hoja.
2. Cada hoja tiene exactamente un tema raíz.
3. Todos los temas pertenecen al árbol jerárquico; no existen temas flotantes.
4. El contenido de los temas se representa mediante bloques estructurados.
5. Los estilos pueden definirse en YAML y en Markdown.
6. Las propiedades visuales se resuelven por propiedad, no sustituyendo objetos completos.
7. El núcleo es neutral y extensible; las particularidades de XMind se conservan en extensiones.
8. Las relaciones visuales no modifican la jerarquía.
9. El orden de temas, bloques, listas, etiquetas y marcadores es significativo y debe conservarse.
10. La serialización debe ser determinista para una misma entrada y configuración.

## 3. Estructura de alto nivel

Un documento IR contiene:

- `ir_version`: versión del contrato.
- `id`: identificador del mapa.
- `title`: título.
- `metadata`: metadatos descriptivos y de procedencia.
- `styles`: definiciones de estilos individuales.
- `style_sets`: conjuntos de estilos reutilizables.
- `assets`: inventario de recursos.
- `sheet`: única hoja del mapa.

La hoja contiene su propia identidad, título, estructura visual, tema raíz, relaciones, límites y resúmenes.

## 4. Entidades

### 4.1 MindMap

Es el contenedor de todo el documento. No contiene directamente una lista de temas raíz: contiene una única hoja.

### 4.2 Sheet

Representa la hoja del mapa. Incluye:

- `id`, `title` y `metadata`.
- `layout.structure`: tipo de estructura visual, por ejemplo `mind_map`, `org_chart`, `logic_chart`, `tree`, `timeline`, `fishbone`, `matrix` o `brace_map`.
- `layout.direction`: orientación o distribución, definida mediante valores neutrales y extensibles.
- `root_topic`: único tema raíz.
- `relationships`, `boundaries` y `summaries`.

La estructura visual no debe confundirse con la jerarquía: la primera determina la disposición gráfica; la segunda determina la relación padre-hijo.

### 4.3 Topic

Es el nodo jerárquico principal. Sus campos son:

- `id`: identificador único dentro del mapa, independiente del título.
- `title`: texto principal visible.
- `kind`: clase semántica, por ejemplo `attached`, `callout` o `summary`. Los tipos especiales también deben respetar la pertenencia a una rama.
- `content`: lista ordenada de bloques estructurados.
- `annotations`: notas, etiquetas, marcadores y tarea.
- `resources`: referencias a imágenes, adjuntos y audio.
- `links`: enlaces externos, internos, a temas o archivos.
- `style`: referencia, modificaciones particulares y propiedades resueltas.
- `layout`: propiedades locales de disposición, como plegado o anchura.
- `extensions`: propiedades específicas de un motor o futuras capacidades.
- `source`: procedencia en el documento fuente.
- `children`: lista ordenada de temas subordinados.

No se permite una colección de temas flotantes. Todo tema debe ser descendiente del único `root_topic`.

### 4.4 ContentBlock

El contenido es una secuencia de bloques tipados. Los tipos previstos son:

| Tipo | Uso |
|---|---|
| `paragraph` | Párrafo de texto con fragmentos enriquecidos (`runs`) |
| `list` | Lista ordenada o no ordenada, con elementos anidados |
| `table` | Tabla con filas, celdas y encabezados |
| `code` | Código con lenguaje y opciones de presentación |
| `quote` | Cita y atribución opcional |
| `equation` | Expresión matemática, preferentemente LaTeX |
| `image` | Imagen referenciada desde `assets` |
| `divider` | Separador visual |
| `raw` | Contenido no interpretado con formato o MIME declarado |

Los fragmentos de texto (`runs`) permiten aplicar negrita, cursiva, subrayado, tachado, color, enlaces y otros atributos a partes del texto. No deben convertirse en temas.

Las listas contienen elementos con contenido y sublistas. Las tablas tienen estructura explícita de filas y celdas; no se almacenan como texto tabulado.

### 4.5 Annotations

Agrupa información complementaria:

- `notes`: notas con contenido estructurado.
- `labels`: etiquetas textuales.
- `markers`: marcadores con identificador, grupo y valor.
- `task`: estado, progreso, fechas y asignación opcional.

Los identificadores de marcadores deben poder representar tanto marcadores estándar como personalizados.

### 4.6 Resources y Assets

Los temas referencian recursos mediante IDs. El inventario `assets` del mapa almacena los metadatos comunes del recurso: ubicación, nombre, MIME, tamaño y datos de integridad cuando estén disponibles.

Los tipos previstos incluyen `image`, `attachment` y `audio`. Las rutas relativas se resuelven respecto al documento fuente o a la raíz de recursos definida por el proyecto; el parser no debe inventar rutas absolutas.

### 4.7 Links

Un enlace declara su tipo:

- `web`: URL externa.
- `topic`: referencia a otro tema mediante ID.
- `file`: archivo del proyecto.
- `internal`: destino interno del documento o del formato de salida.

Las referencias a temas deben validarse después de construir el árbol.

### 4.8 Relationship

Conecta dos temas existentes sin cambiar su relación jerárquica. Incluye IDs de origen y destino, título opcional, estilo y extensiones. Puede incluir dirección, extremos de línea y otros atributos visuales.

### 4.9 Boundary

Agrupa visualmente un conjunto de temas. Declara su ID, los IDs de temas incluidos, título opcional, estilo y extensiones.

### 4.10 Summary

Representa un resumen visual asociado a uno o varios temas. Declara su ID, los temas incluidos, título, estilo y extensiones.

Los límites y resúmenes no deben simularse insertando texto artificial en los títulos de los temas.

## 5. Sistema de estilos

### 5.1 Fuentes

Los estilos pueden proceder de dos fuentes:

- YAML externo: estilos y conjuntos reutilizables.
- Markdown: selección de conjunto, selección de estilo y modificaciones locales.

El parser extrae las referencias y modificaciones declaradas en Markdown. El módulo de estilos carga YAML y resuelve la cascada. El adaptador recibe las propiedades ya resueltas, pero puede consultar las referencias originales para diagnóstico.

### 5.2 Niveles de precedencia

De menor a mayor prioridad:

1. Valores predeterminados del sistema.
2. Tema visual global o configuración general del mapa.
3. Conjunto de estilos aplicable.
4. Estilo concreto referenciado.
5. Modificaciones particulares del elemento (`overrides`).

La propiedad más específica prevalece. Las propiedades no declaradas en un nivel inferior se conservan. La fusión es recursiva por propiedad.

### 5.3 Ausencia y restablecimiento

- Propiedad ausente: hereda el valor anterior.
- Propiedad con valor explícito: sustituye el valor anterior.
- `null`: solicita restablecer la propiedad a su valor predeterminado definido por el sistema o por el adaptador, según el contrato de esa propiedad. No significa lo mismo que propiedad ausente.

### 5.4 Categorías neutrales

El vocabulario inicial incluye:

- `typography`: familia, tamaño, peso, cursiva y alineación.
- `text`: color y decoración.
- `background`: color, imagen y transparencia.
- `shape`: forma, radio y dimensiones.
- `border`: color, grosor y patrón.
- `spacing`: márgenes, relleno y separación.
- `line`: color, grosor, patrón y extremos.
- `layout`: dirección, distribución, posición y anchura.
- `effects`: sombra y efectos.
- `visibility`: visibilidad y plegado.

El vocabulario podrá ampliarse sin cambiar la semántica de las propiedades existentes. Las propiedades propias de un motor se almacenarán en `extensions`.

### 5.5 Estilo de un elemento

Cada elemento estilizable utiliza:

- `ref`: nombre simbólico del estilo concreto.
- `style_set`: nombre del conjunto de estilos aplicable, opcional. Si no se declara, hereda el conjunto del tema padre; en la raíz se utiliza el conjunto global indicado en `metadata.style_set`, si existe.
- `overrides`: modificaciones locales.
- `resolved`: resultado calculado de la cascada.

La referencia `style_set` forma parte de `StyleState` para conservar en el IR la selección de conjunto que permite la sintaxis Markdown. Un tema puede sustituir el conjunto heredado declarando otro; los descendientes heredan el conjunto efectivo salvo que lo sustituyan a su vez.

Los valores generales del mapa pueden declararse en `metadata.style_defaults`, organizados por tipo de elemento (`topic`, `relationship`, `boundary`, `summary` y `notes`). Los valores predeterminados del sistema se suministran al resolutor como configuración, sin incorporarlos a las definiciones del documento.

La procedencia de los valores resueltos debe poder recuperarse en diagnóstico, aunque no sea necesario duplicarla en cada exportación.

## 6. Extensiones específicas de motores

Las propiedades neutrales se almacenan en campos normalizados. Las características no normalizadas se guardan en un espacio de nombres:

```json
{
  "extensions": {
    "xmind": {
      "property_name": "value"
    }
  }
}
```

Las extensiones deben conservarse en operaciones de lectura, validación y escritura. No deben sobrescribir silenciosamente propiedades neutrales.

La presencia de una propiedad en el IR no garantiza que todos los adaptadores puedan exportarla. Cada adaptador debe declarar sus capacidades y advertir sobre conversiones, aproximaciones o pérdidas.

## 7. Identificadores y referencias

1. Todos los IDs de entidades deben ser únicos dentro del mapa.
2. Los IDs no deben derivarse exclusivamente del título.
3. Se recomienda generación determinista basada en la procedencia y posición semántica, con mecanismo para resolver colisiones.
4. Las referencias internas deben apuntar a entidades existentes.
5. El árbol no puede contener ciclos.
6. Cada tema, excepto la raíz, tiene exactamente un padre.
7. Las relaciones no crean parentesco.
8. El orden de las listas es significativo.

## 8. Procedencia

El campo `source` permite localizar el origen de una entidad:

- `file`: archivo fuente.
- `line_start` y `line_end`: intervalo de líneas, cuando exista.
- `markdown_heading`: encabezado de origen, si procede.
- `source_id`: identificador opcional de la directiva o elemento fuente.

La procedencia sirve para diagnóstico y trazabilidad; no determina la identidad semántica del tema.

## 9. Validación

El validador debe comprobar:

- Versión IR reconocida.
- Una sola hoja y un solo tema raíz.
- IDs únicos.
- Tipos de bloque reconocidos o preservados como `raw`.
- Árbol sin ciclos y con un único padre por tema.
- Referencias de temas, recursos y estilos existentes.
- Valores y tipos de propiedades válidos.
- Estructura de listas y tablas coherente.
- Conservación de extensiones desconocidas.

Los errores deben identificar la ruta del elemento en el IR y, cuando exista, su ubicación en el Markdown.

### 9.1 Validación estructural automatizada

El contrato se publica en `docs/ir-schema.json`, declarado como JSON Schema Draft 2020-12. Las pruebas automatizadas usan `jsonschema` y `Draft202012Validator` para comprobar la validez del propio esquema y validar todos los documentos `*.json` situados bajo `examples/ir/`. Se activa `FormatChecker` para los formatos declarados, incluidos `date` y `date-time`.

Esta validación estructural no reemplaza la validación semántica del modelo Python: unicidad global de IDs, referencias entre temas/recursos/estilos, ciclos y pertenencia de cada tema al árbol se comprueban mediante `validate_mind_map()`.

## 10. Adaptadores y pérdidas de información

Un adaptador:

1. Recibe un IR validado.
2. No interpreta Markdown.
3. No modifica el IR original.
4. Traduce propiedades neutrales al formato destino.
5. Informa de características no soportadas.
6. Aplica únicamente conversiones documentadas.
7. No descarta contenido silenciosamente.

El adaptador JSON es una representación de inspección. El futuro adaptador XMind deberá fijar una versión/formato objetivo y verificarse con archivos abiertos en la aplicación real.

## 11. Versionado y compatibilidad

La versión del contrato utiliza SemVer:

- MAJOR: cambios incompatibles en estructura o semántica.
- MINOR: campos o capacidades opcionales compatibles.
- PATCH: correcciones de documentación o restricciones que no cambien la interpretación válida.

Los documentos deben declarar `ir_version`. Las herramientas deben rechazar versiones mayores desconocidas o activar una migración explícita; no deben reinterpretarlas silenciosamente.

## 12. Separación de responsabilidades

| Componente | Responsabilidad |
|---|---|
| Parser Markdown | Convierte sintaxis fuente en entidades IR |
| Modelo | Define entidades y serialización neutral |
| Resolutor de estilos | Carga YAML, aplica precedencia y valida estilos |
| Validador | Comprueba estructura y referencias |
| Adaptador JSON | Serializa el IR |
| Adaptador XMind | Traduce el IR al formato XMind |
| CLI | Coordina las fases y comunica errores |

El modelo no importa bibliotecas XMind ni conoce la gramática Markdown. El adaptador no interpreta etiquetas Markdown. El parser no escribe archivos de salida.

## 13. Estado de implementación

Esta especificación define el objetivo del contrato 1.0.0. No significa que todas las entidades estén implementadas en Python ni que el exportador XMind exista.

La implementación se realizará por fases, con pruebas para cada capacidad. Las diferencias entre especificación, código y capacidades del adaptador deberán quedar documentadas.

## 14. Criterios de aceptación del contrato

- El esquema JSON Draft 2020-12 es válido y las pruebas automatizadas validan todos los ejemplos incluidos.
- El ejemplo contiene una hoja y una única raíz.
- La jerarquía, el contenido estructurado y las referencias son válidos.
- Se representan estilos, anotaciones, recursos, relaciones, límites y resúmenes.
- Las extensiones se conservan.
- Se documenta la política de pérdidas de los adaptadores.
- La serialización es determinista.
