# Plan de consolidación del modelo intermedio (IR)

**Versión objetivo:** IR 1.0.0  
**Estado:** modelo, consumidores y validación formal del esquema implementados; gramática aún pendiente  
**Alcance:** alinear el modelo Python y sus consumidores con \`docs/ir-specification.md\`, \`docs/ir-schema.json\` y \`examples/ir/constitucion.json\`.

## 1. Diagnóstico confirmado

La especificación 1.0.0 define un documento con una única hoja:

\`\`\`text
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
\`\`\`

El modelo legacy \`src/xmind_md/model.py\` conserva la estructura transitoria descrita en las primeras fases de este plan. El nuevo modelo canónico está en \`src/xmind_md/ir/\`; los consumidores se están migrando por etapas para no romper la API anterior.

## 2. Contrato canónico

Las clases Python representan las entidades del esquema: \`MindMap\`, \`Sheet\`, \`Topic\`, \`ContentBlock\`, anotaciones, recursos, \`Asset\`, \`Relationship\`, \`Boundary\`, \`Summary\` y \`StyleState\`.

El modelo no importa parser, PyYAML ni bibliotecas de exportación. Las entidades se convierten a diccionarios JSON con la estructura contractual.

## 3. Política de compatibilidad

1. La API legacy se mantiene temporalmente para consumidores aún no migrados.
2. Los adaptadores deben consumir el contrato canónico, no depender de alias legacy.
3. Los campos legacy no forman parte de la serialización IR 1.0.0.
4. La compatibilidad se retirará cuando parser, estilos, CLI y adaptadores hayan migrado.
5. No se permite que un mismo dato tenga dos representaciones divergentes.

## 4. Secuencia y estado de migración

### Fase A — Modelo canónico

**Estado: completada.** Entidades, serialización y validación semántica están implementadas en \`src/xmind_md/ir/\` y cubiertas por pruebas.

### Fase B — Parser y resolutor de estilos

**Estado: implementada parcialmente y probada.**

- \`parse_markdown_ir()\` / \`parse_file_ir()\` construyen una única hoja y convierten la raíz en \`sheet.root_topic\`.
- Convierte bloques actuales a formas estructuradas del IR y crea assets indexados por ID.
- Conserva trazabilidad de origen.
- El resolutor IR aplica la cascada de estilos y almacena el resultado en \`style.resolved\`.
- \`StyleState.style_set\` conserva la selección de conjunto por tema y permite herencia/sustitución por rama.
- El subconjunto de gramática Markdown implementado está auditado y documentado en `docs/grammar.md`; la compatibilidad CommonMark/GFM completa queda fuera de alcance y sus limitaciones están enumeradas.

### Fase C — Adaptadores

**Estado: migrada y verificada en CI.**

- El adaptador JSON serializa exclusivamente \`MindMap.to_dict()\` del IR 1.0.0.
- El adaptador XMind consume \`MindMap.sheet.root_topic\`, entidades de anotación y relaciones canónicas, y \`StyleState.resolved\`.
- Los adaptadores no importan el modelo legacy.
- La CLI JSON y el script de smoke test utilizan \`parse_file_ir()\`.
- Los formatos y capacidades XMind no soportados se rechazan explícitamente.
- La exportación no modifica el IR original.

### Fase D — Validación y documentación

**Estado: validación formal del esquema y ejemplo, y auditoría de gramática implementadas; otras comprobaciones globales pendientes.**

- `docs/ir-schema.json` comprobado con `Draft202012Validator.check_schema()`.
- Todos los archivos JSON bajo `examples/ir/` validados con `FormatChecker`.
- Pruebas negativas para versión, propiedad obligatoria, tipo de enlace y formato date-time.
- CI #165: 90 pruebas superadas.
- Pruebas de ida y vuelta y validación ampliada del contrato.
- Gramática implementada delimitada mediante matriz de capacidades, pruebas positivas/negativas y limitaciones explícitas.
- Ejecución de Ruff.
- Sincronización documental general y auditoría final.

## 5. Criterios de aceptación

La migración de consumidores se considera completada cuando:

- Los adaptadores consumen el modelo canónico.
- La serialización JSON refleja la estructura IR 1.0.0.
- El adaptador XMind consume las entidades ubicadas dentro de Sheet.
- Los estilos exportados proceden de \`style.resolved\`.
- Las características no soportadas se rechazan explícitamente.
- Las pruebas de exportación positivas y negativas pasan.
- La suite completa no presenta regresiones.
- Se comprueba que la exportación no muta el documento IR.

La validación formal del esquema y el ejemplo ya está automatizada. La consolidación global del contrato IR requiere completar las tareas de gramática y cerrar las comprobaciones restantes.

## 6. Fuera de alcance de esta migración

- Compatibilidad completa con CommonMark/GFM y extensiones Markdown avanzadas.
- Implementar todas las propiedades visuales de XMind.
- Garantizar compatibilidad total con XMind Desktop.
- Integrar una opción de exportación XMind en la CLI.
- Retirar toda la API legacy antes de migrar sus últimos consumidores.

## 7. Regla de versionado

Mientras el modelo Python no cumpla íntegramente el contrato y el JSON Schema, la implementación no se anunciará como compatible globalmente con IR 1.0.0. Los cambios incompatibles deberán reflejarse en el versionado del IR y en sus pruebas.
