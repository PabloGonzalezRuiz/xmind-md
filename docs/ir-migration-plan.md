# Plan de consolidación del modelo intermedio (IR)

**Versión objetivo:** IR 1.0.0  
**Estado:** plan de migración aprobado como primera tarea de implementación  
**Alcance:** alinear el modelo Python y sus consumidores con `docs/ir-specification.md`, `docs/ir-schema.json` y `examples/ir/constitucion.json`.

## 1. Diagnóstico confirmado

La especificación 1.0.0 define un documento con una única hoja:

```text
MindMap
├── metadata
├── styles
├── style_sets
├── assets
└── sheet
    ├── layout
    ├── root_topic
    ├── relationships
    ├── boundaries
    └── summaries
```

La implementación Python actual todavía expone un modelo transitorio:

- `MindMap.topics` contiene una lista de raíces, aunque el contrato exige una única `sheet.root_topic`.
- `MindMap.assets` es una lista; el contrato define un objeto indexado por ID.
- `Topic.content` se utiliza como lista de texto heredada; el contrato define una lista de bloques estructurados.
- `Topic.content_blocks` no coincide con el nombre contractual `content`.
- El estilo está distribuido entre `style_ref`, `style_overrides` y `resolved_style`; el contrato lo agrupa en `style.ref`, `style.overrides` y `style.resolved`.
- `Topic.resources` es una lista, mientras que el contrato define grupos `images`, `attachments` y `audio`.
- Relaciones, límites y resúmenes están actualmente en el nivel de MindMap; el contrato los sitúa dentro de Sheet.
- La hoja no existe como entidad Python.

El parser, los adaptadores y algunas pruebas consumen los nombres transitorios. No se debe cambiar el modelo sin migrar esos consumidores de forma coordinada.

## 2. Contrato canónico

Las clases Python deberán representar directamente las entidades del esquema:

- `MindMap`
- `Sheet`
- `Topic`
- `ContentBlock` y tipos especializados o estructuras tipadas equivalentes
- `Annotation` / estructuras de notas, etiquetas, marcadores y tareas
- `Resource` / `Asset`
- `Relationship`
- `Boundary`
- `Summary`
- `StyleState`
- `StyleDefinition` y `StyleSet`

El modelo no importará parser, PyYAML ni bibliotecas de exportación. Las entidades deberán poder convertirse a diccionarios JSON sin introducir decisiones de formato XMind.

## 3. Política de compatibilidad

La compatibilidad con el modelo transitorio será temporal y explícita:

1. El parser podrá seguir construyendo el modelo mediante una fábrica o constructor de compatibilidad durante la migración.
2. Los adaptadores deberán consumir el contrato canónico, no depender indefinidamente de alias legacy.
3. Los campos legacy no formarán parte de la serialización IR 1.0.0.
4. La compatibilidad se eliminará cuando parser, estilos, adaptadores y pruebas hayan migrado.
5. No se permitirá que un mismo dato tenga dos representaciones divergentes.

No se mantendrán propiedades legacy silenciosamente si pueden producir dos fuentes de verdad.

## 4. Secuencia de migración

### Fase A — Modelo canónico

- Crear las entidades `Sheet`, `StyleState` y estructuras de recursos.
- Hacer que `MindMap` contenga una única `sheet`.
- Hacer que `Sheet` contenga `root_topic`, relaciones, límites y resúmenes.
- Hacer que `Topic.content` contenga bloques tipados.
- Normalizar estilo y recursos conforme al esquema.
- Añadir validación de invariantes del árbol e IDs.

### Fase B — Parser y resolutor de estilos

- Adaptar el parser para construir el modelo canónico.
- Mantener una única raíz y convertirla en `sheet.root_topic`.
- Convertir bloques actuales a las formas del esquema.
- Construir assets indexados por ID y referencias desde los temas.
- Producir `style.ref`, `style.overrides` y `style.resolved`.
- Mantener trazabilidad de origen.

### Fase C — Adaptadores

- Actualizar el adaptador JSON para serializar únicamente IR 1.0.0.
- Actualizar el adaptador XMind para leer `sheet.root_topic` y entidades dentro de Sheet.
- Rechazar características no soportadas con errores claros; nunca descartarlas silenciosamente.

### Fase D — Pruebas y documentación

- Validar el ejemplo de referencia con JSON Schema Draft 2020-12.
- Añadir pruebas de ida y vuelta de serialización.
- Añadir pruebas de validación de referencias e IDs.
- Ejecutar toda la suite y Ruff.
- Actualizar README, arquitectura, gramática y documentación de adaptadores para que no describan estructuras contradictorias.

## 5. Criterios de aceptación

La consolidación se considerará terminada únicamente cuando:

- La serialización Python tenga la misma estructura que el esquema IR 1.0.0.
- El ejemplo JSON valide con un validador JSON Schema Draft 2020-12.
- El parser produzca un `MindMap` con una única `Sheet` y un `root_topic`.
- Los bloques de contenido, estilos y assets sigan las formas contractuales.
- Las relaciones, boundaries y summaries estén dentro de Sheet.
- Los adaptadores y pruebas consuman el modelo canónico.
- No haya regresiones en las funciones ya implementadas.
- Las limitaciones del adaptador XMind sigan documentadas con precisión.

## 6. Fuera de alcance de esta primera tarea

Esta consolidación no implica todavía:

- Completar toda la gramática Markdown.
- Implementar todas las propiedades visuales de XMind.
- Garantizar compatibilidad total con XMind Desktop.
- Añadir nuevas funciones a la CLI.
- Cambiar el formato fuente Markdown.

Estas tareas se abordarán después de estabilizar el contrato IR y migrar sus consumidores.

## 7. Regla de versionado

Mientras el modelo Python no cumpla íntegramente este documento y el JSON Schema, la implementación no se anunciará como compatible con IR 1.0.0. Los cambios incompatibles deberán reflejarse en el versionado del IR y en sus pruebas.
