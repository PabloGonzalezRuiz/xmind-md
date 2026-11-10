# Adaptador XMind: alcance de la primera versión

**Módulo:** `src/xmind_md/adapters/xmind_adapter.py`  
**Formato objetivo:** XMind moderno, contenedor ZIP con JSON  
**Estado:** implementación inicial; compatibilidad con XMind Desktop pendiente de prueba

## 1. Responsabilidad

El adaptador recibe un objeto `MindMap` del IR y genera un paquete `.xmind`. No analiza Markdown, no resuelve referencias simbólicas y no modifica el IR.

La función pública `build_xmind_content(mind_map)` construye el contenido JSON en memoria. La función `write_xmind(mind_map, destination)` genera el contenedor ZIP.

Antes de serializar, el adaptador valida el subconjunto de características admitido. Si encuentra una característica no implementada, lanza `XMindAdapterError`; no debe descartarla silenciosamente.

## 2. Estructura del paquete

La primera versión escribe las siguientes entradas, en este orden:

1. `mimetype`, sin compresión y como primera entrada.
2. `content.json`, con una hoja y su árbol de temas.
3. `metadata.json`, con versiones de estructura y hoja activa.
4. `manifest.json`, con el registro de los recursos incluidos.
5. `Thumbnails/thumbnail.png`, miniatura PNG transparente de 1 × 1 píxel.

El contenedor se genera con `zipfile` y los documentos JSON con `json`, sin añadir dependencias de ejecución.

## 3. Características implementadas en el adaptador

| Característica del IR | Traducción inicial |
|---|---|
| Un mapa con una raíz | Una hoja XMind (`class: sheet`) y `rootTopic` |
| Temas `attached` | `class: topic` y `children.attached` recursivo |
| IDs del IR | UUID deterministas derivados mediante UUID5 |
| Relaciones (provisional) | `end1Id`, `end2Id`, título e ID determinista; falta completar `controlPoints` |
| Notas | `notes.plain.content` |
| Párrafos, listas, tablas, código y citas | Texto plano/Markdown dentro de la nota |
| Etiquetas | `labels` |
| Marcadores | `markers[].markerId`, construidos como `grupo-valor` |
| Un enlace por tema | `href` |
| Estilos básicos de tema | Objeto `style` con ID y `properties` traducidas |

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

Los valores de propiedades se serializan como texto, de acuerdo con el tipo declarado en el esquema JSON oficial.

Los estilos con nombre o conjuntos deben haberse resuelto previamente mediante `resolve_styles`. Las propiedades no incluidas en la tabla y los reinicios `null` se rechazan.

## 4. Limitaciones explícitas

No se consideran implementados todavía:

- Integración del adaptador en la CLI.
- Empaquetado de imágenes y otros recursos en `resources/`.
- Límites (`boundaries`) y resúmenes (`summaries`).
- Temas flotantes/detached y callouts.
- Extensiones específicas de XMind y datos de tarea.
- Varias direcciones/enlaces por tema.
- Relaciones completas: el mapeo de extremos está implementado, pero aún no se generan los `controlPoints` exigidos por el esquema oficial; por tanto, no se debe considerar validada la representación visual de relaciones.
- Estilos de relaciones y estilos avanzados de límites/resúmenes.
- Posicionamiento, estructura de mapa y propiedades avanzadas de layout.
- Formato de notas enriquecidas HTML; el contenido se aplana a texto.
- Compatibilidad completa con CommonMark o con todas las propiedades visuales de XMind.

Si el IR contiene una característica estructural aún no soportada, la exportación debe fallar con un mensaje explícito.

## 5. Identificadores

Los IDs de temas, hojas, relaciones y estilos de salida se generan como UUID5 deterministas a partir del ID del mapa y del ID de origen. Así se conserva la estabilidad entre ejecuciones para el mismo IR, sin exponer los IDs simbólicos del IR como identificadores internos de XMind.

Las relaciones se traducen usando la tabla de correspondencia de IDs de temas. Una referencia inexistente provoca un error.

## 6. Verificación y criterio de compatibilidad

Las pruebas unitarias deben comprobar:

- Estructura JSON de hoja, raíz, hijos y relaciones.
- Estabilidad de IDs.
- Conversión de notas, etiquetas, marcadores, enlaces y estilos básicos.
- Orden y contenido del ZIP, MIME, manifiesto y miniatura.
- Rechazo de características no soportadas.

Estas pruebas demuestran consistencia interna del generador, no compatibilidad completa con la aplicación. La compatibilidad con XMind Desktop solo podrá declararse después de abrir y volver a guardar un archivo generado con una versión concreta de XMind, y comparar su estructura.

## 7. Referencias de formato

- Modelo oficial: https://github.com/xmindltd/xmind-model
- SDK oficial: https://github.com/xmindltd/xmind-sdk-js
- Implementación Python de contraste: https://github.com/innotools/xmindpy
- Decisión de arquitectura: [xmind-engine-evaluation.md](xmind-engine-evaluation.md)
