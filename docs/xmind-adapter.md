# Adaptador XMind: alcance de la primera versión

**Módulo:** `src/xmind_md/adapters/xmind_adapter.py`  
**Formato objetivo:** XMind moderno, contenedor ZIP con JSON  
**Estado:** adaptador IR 1.x integrado en CLI; fixture manual comprobado en XMind Desktop 26.05.01107; perfil de exportación parcial

## 1. Responsabilidad y contrato

El adaptador recibe un `xmind_md.ir.MindMap` IR 1.0.0/1.1.0 y genera un paquete `.xmind`. Para IR 1.1.0 rechaza explícitamente `Topic.semantic_role` y `Topic.structure` hasta que exista el mapeo correspondiente en la Fase 7. No analiza Markdown, no resuelve estilos y no modifica el IR. El parser admite `summary` en el IR, pero el adaptador exporta únicamente temas `attached`, `detached` y `callout`; un tema `detached` necesita coordenadas `layout.position.x/y`.

- `build_xmind_content(mind_map)`: construye el contenido JSON en memoria.
- `write_xmind(mind_map, destination)`: genera el contenedor ZIP.

El adaptador no importa ni consume `xmind_md.model`, que es el modelo legacy. Los estilos deben llegar resueltos en `StyleState.resolved`; el adaptador no ejecuta la cascada.

Antes de serializar, valida el perfil de capacidades. Si encuentra una característica no implementada, lanza `XMindAdapterError`; no debe descartarla silenciosamente.

## 2. Estructura del paquete

La primera versión escribe las siguientes entradas, en este orden:

1. `mimetype`, sin compresión y como primera entrada.
2. `content.json`, con una hoja y su árbol de temas.
3. `metadata.json`, con versiones de estructura y hoja activa.
4. `manifest.json`, con el registro de los recursos incluidos.
5. `Thumbnails/thumbnail.png`, miniatura PNG transparente de 1 × 1 píxel.

El contenedor se genera con `zipfile` y los documentos JSON con `json`, sin añadir dependencias de ejecución.

## 3. Mapeo IR → XMind

| Entidad/capacidad IR | Traducción |
|---|---|
| `MindMap.sheet` | Hoja XMind única |
| `Sheet.id` | Base para UUID determinista de la hoja |
| `Sheet.title` | `sheet.title` |
| `Sheet.root_topic` | `rootTopic` |
| Temas `attached` | `class: topic` y `children.attached` recursivo |
| Temas `detached` | `class: topic` y `children.detached` recursivo | Requieren `layout.position` con coordenadas numéricas `x` e `y` |
| Temas `callout` | `class: topic` y `children.callout` recursivo | Soportados por el perfil actual |
| IDs de temas | UUID deterministas derivados mediante UUID5 |
| `Relationship` | `end1Id`, `end2Id`, título, ID determinista y dos `controlPoints` neutrales |
| `Annotation.notes` | `notes.plain.content` |
| Párrafos, listas, tablas, código, citas y separadores | Texto plano/Markdown dentro de la nota |
| `Label.text` | Elementos de `labels` |
| `Marker.group/value` | `markers[].markerId`, compuesto como `grupo-valor` |
| Enlaces `kind=web` y `kind=topic` | `href` web o `xmind:#` con UUID de destino |
| Enlaces `kind=file` | `href` cuando el destino comienza por `file://` |
| `Topic.style.resolved` | Objeto `style` con propiedades traducidas |
| `Relationship.style.resolved` | Estilo de relación; se admiten `line.color`, `line.width` y `line.pattern` |
| `MindMap.metadata.author` | `metadata.json.modifier` |

Los IDs propios de notas, etiquetas y marcadores no se conservan como IDs XMind: el perfil del formato utilizado no ofrece un campo equivalente en la estructura generada. Los nombres de estilos y las definiciones de conjuntos se materializan en propiedades resueltas; no se exportan como catálogos reutilizables.

### Propiedades de estilo admitidas

| Propiedad neutral | Propiedad XMind |
|---|---|
| `shape` | `shape-class` |
| `text.font_family` | `fo:font-family` |
| `text.font_size` | `fo:font-size` |
| `text.font_weight` | `fo:font-weight` |
| `text.bold` | `fo:font-weight` (`bold` / `normal`) |
| `text.italic` | `fo:font-style` (`italic` / `normal`) |
| `text.color` | `fo:color` |
| `text.decoration` | `fo:text-decoration` |
| `background.color` / `background.fill` | `svg:fill` |
| `border.color` | `line-color` |
| `border.width` | `line-width` |
| `border.pattern` | `line-pattern` |

Los valores de propiedades se serializan como texto. Se admiten las claves de la tabla de estilos, incluidas `line.color`, `line.width` y `line.pattern` en relaciones. Los valores `null`, las propiedades desconocidas y los estilos sin resolver se rechazan.

## 4. Limitaciones explícitas

No se exportan todavía:

- Assets, imágenes, adjuntos, audio ni referencias de recursos.
- Bloques de contenido `image` y `raw`, ni imágenes en línea.
- `boundaries` y `summaries`.
- Temas `summary` y otras clases de tema distintas de `attached`, `detached` y `callout`.
- Anotaciones de tarea.
- Estilos visuales de notas.
- Extensiones de temas o relaciones.
- Layouts distintos del perfil predeterminado `mind_map/balanced`.
- Metadatos específicos de hoja.
- Metadatos de mapa distintos de `author`, `style_set`, `style_defaults` y `source_file`.
- Más de un enlace por tema o enlaces cuyo tipo no sea `web`, `topic` o `file://`.
- Propiedades visuales fuera de la tabla anterior.
- Notas enriquecidas HTML; el contenido se aplana a texto.

Los metadatos no admitidos y las entidades no exportables producen un error explícito. La procedencia del tema (`source`) y los metadatos de origen/selección de estilo se consideran información de autoría y no se incorporan al documento XMind.

Las relaciones se serializan con dos puntos de control neutrales. La estructura queda cubierta por pruebas, pero su trazado visual requiere comprobación manual en XMind Desktop.

## 5. Identificadores y referencias

Los IDs de temas, hojas, relaciones y estilos de salida se generan como UUID5 deterministas a partir del ID del mapa y del ID de origen. Las relaciones se traducen mediante la tabla de correspondencia de IDs de temas. Una referencia inexistente provoca un error.

## 6. Pruebas y criterio de compatibilidad

Las pruebas unitarias y de integración comprueban:

- Estructura JSON de hoja, raíz, hijos y relaciones.
- Estabilidad de IDs.
- Conversión de notas, etiquetas, marcadores, enlaces y estilos resueltos.
- Orden y contenido del ZIP, MIME, manifiesto y miniatura.
- Rechazo de características no soportadas.
- Que la exportación no modifica el documento IR original.

Estas pruebas demuestran consistencia interna del generador, no compatibilidad completa con la aplicación. La compatibilidad con XMind Desktop solo podrá declararse después de abrir y volver a guardar un archivo generado con una versión concreta de XMind, y comparar su estructura.

## 7. Referencias de formato

- Modelo oficial: https://github.com/xmindltd/xmind-model
- SDK oficial: https://github.com/xmindltd/xmind-sdk-js
- Implementación Python de contraste: https://github.com/innotools/xmindpy
- Decisión de arquitectura: [xmind-engine-evaluation.md](xmind-engine-evaluation.md)


## 8. Matriz de capacidades IR 1.x

La clasificación distingue entre representación exportada, conversión con pérdida explícita y rechazo. «Soportado» significa que existe una conversión estructural probada; no certifica todavía la apertura visual en XMind Desktop.

| Entidad o propiedad IR | Estado | Comportamiento del adaptador |
|---|---|---|
| `MindMap.id` | Soportado | Sirve de base para UUID5 deterministas |
| `MindMap.title` | No representado en el paquete de una sola hoja | Se utiliza `Sheet.title` como título visible; el título del mapa no se exporta |
| `MindMap.metadata.author` | Soportado con mapeo | Se convierte en `metadata.json.modifier` |
| `MindMap.metadata.style_set`, `style_defaults`, `source_file` | Aceptado como metadato de autoría | No se materializa como catálogo de estilos ni se exporta como campo XMind |
| Otros metadatos del mapa | No soportado | Error explícito |
| `MindMap.styles`, `style_sets` | Soportado con pérdida controlada | Se exportan las propiedades finales resueltas, no los catálogos reutilizables |
| `MindMap.assets` | No soportado | Error explícito; no se incluyen archivos en `resources/` |
| `Sheet` única, ID y título | Soportado | Se crea una hoja XMind |
| `Sheet.metadata` | No soportado | Error explícito |
| `Sheet.layout` | Parcial | Solo `mind_map` con dirección `balanced` y sin propiedades adicionales |
| `Topic.kind=attached` | Soportado | `children.attached`; obligatorio para la raíz |
| `Topic.kind=detached` | Soportado con requisito | `children.detached`; requiere `layout.position` con coordenadas numéricas `x/y` |
| `Topic.kind=callout` | Soportado | `children.callout` |
| `Topic.kind=summary` y otros tipos | No soportado | Error explícito |
| `Topic.layout` en IR 1.0.0 | Parcial | `position`, `structure_class`, `branch=folded`, `width`; resto rechazado |
| `Topic.layout.structure_class` en IR 1.1.0 | No soportado | Campo heredado no neutral; migración lo preserva en `extensions.xmind.legacy_structure_class` |
| `Topic.semantic_role` en IR 1.1.0 | No soportado todavía | Error explícito; no se descarta el rol |
| `Topic.structure=tree_table` en IR 1.1.0 | No soportado todavía | Error explícito; el mapeo se implementará en Fase 7 |
| `Topic.content` paragraph/list/table/code/quote/divider | Soportado con pérdida de formato | Se aplana a texto dentro de `notes.plain.content`; se pierden estilos inline, los destinos de enlaces inline (queda su texto visible) y la estructura original de los bloques |
| `Topic.content` equation/image/raw | No soportado | Error explícito |
| Notas sin estilo visual | Soportado con pérdida de formato | Se concatenan con el contenido del tema en `notes.plain.content`; los IDs de nota y la estructura de bloques no se conservan |
| Notas con estilo visual resuelto | No soportado | Error explícito |
| Etiquetas y marcadores | Soportado con mapeo | Se convierten a `labels` y `markers[].markerId`; los IDs IR no se conservan |
| `Topic.links` web | Soportado | `href` |
| `Topic.links` topic | Soportado | `href` con esquema `xmind:#` y UUID de destino |
| `Topic.links` file | Parcial | Solo URI `file://` |
| Enlaces `internal`, múltiples o con título adicional | No soportado | Error explícito |
| Recursos de tema: imágenes, adjuntos y audio | No soportado | Error explícito |
| `Annotation.task` | No soportado | Error explícito |
| `Relationship` | Soportado | Extremos traducidos mediante el mapa de IDs; puntos de control neutrales |
| Estilo de relación | Parcial | Solo propiedades de estilo incluidas en la tabla de mapeo |
| `Boundary` y `Summary` | No soportado | Error explícito |
| Extensiones de tema o relación | No soportado | Error explícito |
| `Topic.source` y procedencia de bloques | No representado | Los rangos de origen no tienen campo equivalente en el perfil generado |
| Propiedades de estilo desconocidas, valores `null` o estilos sin resolver | No soportado | Error explícito |

Las pérdidas intencionadas (aplanamiento de bloques, IDs auxiliares, catálogos de estilos) se describen en esta tabla y no deben confundirse con soporte de ida y vuelta. Los casos no soportados deben continuar fallando de forma explícita.


## 9. Evidencia de interoperabilidad manual

La validación manual ya no está pendiente para el fixture de smoke test. El archivo `tests/fixtures/xmind/xmind-md-smoke-test.xmind` se descargó, abrió, inspeccionó, guardó, cerró y volvió a abrir en XMind Desktop 26.05.01107 para Windows.

Se comprobaron: tema central, dos ramas, un subtema, una nota desplegable, una etiqueta, un marcador de prioridad y una relación. El usuario confirmó que el archivo funcionaba correctamente después de guardarlo y reabrirlo.

Esta evidencia confirma exclusivamente el fixture y las características inspeccionadas en esa versión. No certifica todas las capacidades del adaptador ni compatibilidad universal con versiones futuras de XMind. La matriz de la sección 8 continúa siendo la referencia para saber qué se exporta, qué se aplana y qué se rechaza.
