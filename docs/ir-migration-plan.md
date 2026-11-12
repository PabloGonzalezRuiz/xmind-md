# Plan de consolidación del modelo intermedio (IR)

**Versión base histórica:** IR 1.0.0  
**Versión vigente:** IR 1.1.0  
**Estado:** consolidación del runtime completada; evolución semántica IR 1.1.0 en curso. Este documento conserva el historial de la migración 1.0.0; el estado operativo está en `roadmap.md` y `development-status.md`.  
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

El modelo legacy `src/xmind_md/model.py` conserva la estructura transitoria descrita en las primeras fases de este plan. El nuevo modelo canónico está en `src/xmind_md/ir/`; los consumidores se están migrando por etapas para no romper la API anterior.

## 2. Contrato canónico

Las clases Python representan las entidades del esquema: `MindMap`, `Sheet`, `Topic`, `ContentBlock`, anotaciones, recursos, `Asset`, `Relationship`, `Boundary`, `Summary` y `StyleState`. IR 1.1.0 añade `Topic.semantic_role`, `Topic.structure`, `TopicStructure`, `TreeTableRow` y `TreeTableCell`.

El modelo no importa parser, PyYAML ni bibliotecas de exportación. Las entidades se convierten a diccionarios JSON con la estructura contractual.

## 3. Política de compatibilidad

1. La API legacy se mantiene temporalmente para consumidores aún no migrados.
2. Los adaptadores deben consumir el contrato canónico, no depender de alias legacy.
3. Los campos nuevos `semantic_role` y `structure` solo se serializan cuando están declarados; IR 1.0.0 conserva su forma original.
4. La compatibilidad legacy se mantiene aislada; su retirada requiere conocer consumidores externos.
5. No se permite que un mismo dato tenga dos representaciones divergentes.

## 4. Secuencia y estado de migración

### Fase A — Modelo canónico

**Estado: completada.** Entidades, serialización y validación semántica están implementadas en `src/xmind_md/ir/` y cubiertas por pruebas. Esto solo acredita la existencia del modelo IR; no significa que el parser lo construya directamente.

### Fase B — Parser y resolutor de estilos

**Estado: implementada parcialmente y probada.**

- `parser.py` produce `DocumentSyntax` / `TopicSyntax`, sin construir entidades legacy.
- `ir_builder.py` construye una única hoja y coloca la raíz en `sheet.root_topic` directamente desde el AST.
- Convierte bloques actuales a formas estructuradas del IR y crea assets indexados por ID.
- Conserva trazabilidad de origen.
- El resolutor IR aplica la cascada de estilos y almacena el resultado en `style.resolved`.
- `StyleState.style_set` conserva la selección de conjunto por tema y permite herencia/sustitución por rama.
- El subconjunto de gramática Markdown implementado está auditado y documentado en `docs/grammar.md`; la compatibilidad CommonMark/GFM completa queda fuera de alcance y sus limitaciones están enumeradas.

### Fase C — Adaptadores

**Estado: migrada, ampliada y verificada en CI.**

- El adaptador JSON serializa exclusivamente `MindMap.to_dict()` del IR 1.0.0.
- El adaptador XMind consume `MindMap.sheet.root_topic`, entidades de anotación y relaciones canónicas, y `StyleState.resolved`.
- Los adaptadores no importan el modelo legacy.
- La CLI JSON y el script de smoke test utilizan `parse_file_ir()`.
- Los formatos y capacidades XMind no soportados se rechazan explícitamente.
- La exportación no modifica el IR original.
- Tarea 8: matriz de capacidades IR/XMind documentada; temas `detached` y `callout`, propiedades locales de layout seleccionadas y enlaces internos/a archivo implementados con pruebas. Los `boundaries`, `summaries`, assets, tareas y extensiones siguen rechazados.

### Fase D — Validación y documentación

**Estado: COMPLETADA.** El esquema y ejemplos se validan automáticamente; la gramática implementada está delimitada en `grammar.md`; la CI actual valida parser, IR, estilos, adaptadores, CLI y distribuciones.

- `docs/ir-schema.json` comprobado con `Draft202012Validator.check_schema()`.
- Todos los archivos JSON bajo `examples/ir/` validados con `FormatChecker`.
- Pruebas negativas para versión, propiedad obligatoria, tipo de enlace y formato date-time.
- Evidencia histórica: CI #165, 90 pruebas superadas; la suite actual tiene 161 pruebas por versión en Python 3.10/3.11/3.12.
- Pruebas de ida y vuelta y validación ampliada del contrato.
- Gramática implementada delimitada mediante matriz de capacidades, pruebas positivas/negativas y limitaciones explícitas.
- Ejecución de Ruff.
- Sincronización documental y auditoría funcional/documental completadas en tareas 6 y 7.

## 5. Criterios de aceptación

La migración de consumidores se considera completada cuando:

- Los adaptadores consumen el modelo canónico.
- La serialización JSON refleja la estructura IR 1.0.0.
- El adaptador XMind consume las entidades ubicadas dentro de Sheet.
- Los estilos exportados proceden de `style.resolved`.
- Las características no soportadas se rechazan explícitamente.
- Las pruebas de exportación positivas y negativas pasan.
- La suite completa no presenta regresiones.
- Se comprueba que la exportación no muta el documento IR.

La migración de adaptadores y CLI al IR está completada. En la rama de trabajo `architecture/pmd-ir-roadmap`, el parsing se ha migrado también: `parser.py` produce AST sintáctico, `ir_builder.py` construye directamente el IR e `ir_parser.py` es una fachada. `legacy_adapter.py` proyecta el AST al modelo antiguo únicamente para las funciones `parse_markdown()` / `parse_file()`. La consolidación del modelo de ejecución se completó en `architecture/pmd-ir-roadmap`: `styles.py` no importa `model.py` y deriva las API antiguas a `legacy_styles.py`. `model.py` se conserva como compatibilidad externa aislada. CI final [43227325673](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43227325673) valida 166 pruebas por Python 3.10–3.12 y build/install de wheel/sdist. La exportación XMind permanece deliberadamente parcial; sus límites se describen en `xmind-adapter.md`. Para evitar pérdida silenciosa, el adaptador rechaza explícitamente `semantic_role` y `Topic.structure` hasta la Fase 7. El modelo IR puede representar entidades que el parser no genera o que el adaptador no exporta.

## 6. Fuera de alcance de esta migración

- Compatibilidad completa con CommonMark/GFM y extensiones Markdown avanzadas.
- Implementar todas las propiedades visuales de XMind.
- Garantizar compatibilidad total con XMind Desktop.
- Ampliar el perfil XMind más allá de las capacidades documentadas, si se autoriza como tarea futura.
- Retirar toda la API legacy antes de migrar sus últimos consumidores.

## 7. Regla de versionado

El modelo Python, el esquema JSON y la validación semántica soportan IR 1.0.0 y 1.1.0. La versión 1.1.0 añade campos opcionales y una migración explícita desde 1.0.0. Esto no significa que el parser genere todas las entidades ni que los adaptadores puedan exportarlas. Los cambios incompatibles deberán reflejarse en el versionado del IR y en sus pruebas.


## 8. Evolución IR 1.1.0

La Fase 2 añade roles semánticos y estructuras compuestas. CI final [43247569102](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43247569102): 189 pruebas por Python 3.10–3.12, Ruff y build/install wheel/sdist correctos. La especificación vigente está en [ir-specification.md](ir-specification.md), el diseño detallado en [ir-1.1-design.md](ir-1.1-design.md) y la decisión en [ADR-002](decisions/ADR-002-ir-semantic-structures.md).

- `Topic.kind` conserva el tipo de representación del tema.
- `Topic.semantic_role` describe su significado documental o funcional.
- `Topic.structure` representa `tree_table` con filas y celdas ordenadas que referencian hijos directos.
- El contenido sigue residiendo en el Topic referenciado.
- `migrate_ir_1_0_to_1_1()` devuelve una copia y preserva `layout.structure_class` histórica bajo `extensions.xmind.legacy_structure_class`; avisa y no inventa roles.
- El adaptador XMind rechaza las nuevas semánticas hasta la Fase 7.
