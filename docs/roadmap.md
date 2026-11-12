# Hoja de ruta XMind MD / PMD

**Actualizada:** 2026-11-12. **Rama de trabajo:** `architecture/pmd-ir-roadmap`. **ADR:** [ADR-001](decisions/ADR-001-pmd-ir-architecture.md).

Esta hoja de ruta sustituye la secuencia anterior de fases PMD, que colocaba la biblioteca de estilos antes de resolver la duplicidad del modelo y las carencias estructurales del IR. La secuencia nueva prioriza los contratos de ejecución: no diseñaremos sintaxis para compensar limitaciones del IR.

## Estado de partida verificado

- Repositorio: `PabloGonzalezRuiz/xmind-md`.
- Base de trabajo: `05efc482c333b266bf1a2bd5fbf2f3fdee129de7`.
- Rama creada para este trabajo: `architecture/pmd-ir-roadmap`.
- Release `v0.1.0` publicada como Alpha/prerelease.
- El flujo CLI es Markdown → `parse_file_ir()` → IR 1.0.0 → resolución de estilos (para XMind) → adaptador JSON/XMind.
- `parser.py` construye actualmente el modelo `MindMap`/`Topic` de `model.py`; `ir_parser.py` lo convierte al IR. Por tanto, la duplicidad del modelo sigue existiendo en la ruta de parsing.
- `styles.py` conserva una ruta legacy y otra IR. El modelo legacy sigue siendo importado por el parser y por la ruta legacy del resolutor.
- Los adaptadores consumen IR; no se propone reescribirlos desde cero.
- El IR actual distingue `Topic.kind` de entidades, pero no dispone todavía de un rol semántico explícito ni de una estructura neutral `tree_table`.
- La tabla Markdown actual no sustituye a una tabla de árbol.
- La referencia Tema1 y la investigación de implementaciones oficiales XMind están documentadas en `reference-analysis-tema1.md` y `xmind-official-sdk-research.md`.
- El CI verde de la base histórica no se considerará evidencia de esta rama; cada cambio deberá verificarse con una ejecución nueva.

## Fases

### Fase 0 — Decisiones y plan de migración

**Estado: COMPLETADA en esta rama.**

- [x] Crear ADR de arquitectura objetivo.
- [x] Establecer orden de dependencias entre IR, catálogo, PMD y adaptador.
- [x] Registrar la situación real del puente legacy y evitar declarar retirada la duplicidad.
- [x] Definir compatibilidad, versionado, criterios de prueba y política SVG.

**Criterio de cierre:** ADR aprobado y hoja de ruta coherente con el código observado.

### Fase 1 — Consolidación del modelo de ejecución

**Estado: EN CURSO.** Las tareas 1.1 (inventario/caracterización) y 1.2 (parsing directo a IR) están implementadas. La tarea 1.3 (resolutor/API legacy) sigue pendiente. El AST es temporal; la ruta IR ya no construye el modelo legacy. Las API antiguas se mantienen aisladas mediante un adaptador AST → legacy.

#### 1.1 Caracterización y mapa de consumidores
- [x] Inventariar las llamadas internas a `parse_markdown()`, `parse_file()`, `parse_markdown_ir()` y `parse_file_ir()`.
- [x] Inventariar importaciones y consumidores internos de `model.py`, `Topic`, `MindMap` y la ruta legacy de `styles.py`.
- [x] Registrar contratos observables mediante suites existentes y fixture de caracterización: IDs, procedencia, errores, directivas, contenido, anotaciones, recursos, relaciones, límites y resúmenes.
- [x] Añadir fixture Markdown, prueba de caracterización IR y comparación de identidad/estructura entre parser legacy e IR; CI [43221440866](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43221440866), 163 pruebas por Python 3.10–3.12 y build/install correctos.

#### 1.2 Parser con salida IR directa
- [x] Separar la gramática del modelo legacy mediante DocumentSyntax y TopicSyntax temporales.
- [x] Construir entidades canónicas en ir_builder.py directamente desde el AST.
- [x] Retirar la conversión legacy → IR; ir_parser.py es ahora una fachada fina.
- [x] Mantener parse_markdown() y parse_file() mediante legacy_adapter.py (AST → legacy), fuera de la ruta canónica.
- [x] Añadir pruebas de AST, preservación de la API legacy y no instanciación del modelo legacy en parse_markdown_ir().
- [ ] Confirmar la revisión final de CI del builder separado y actualizar la evidencia.

#### 1.3 Resolutor y API
- [ ] Migrar consumidores restantes de estilos a IR.
- [ ] Retirar la detección y resolución legacy de `styles.py` cuando ya no sea necesaria.
- [ ] Decidir deprecación y retirada de `model.py` según la compatibilidad pública documentada.
- [ ] Mantener la CLI y los adaptadores funcionando sin cambios de comportamiento no intencionados.

**Criterios de cierre de Fase 1**
- La ruta canónica de parsing construye IR directamente.
- Ningún componente interno de ejecución depende del modelo legacy.
- Las API legacy, si se mantienen, delegan en la ruta canónica o están deprecadas explícitamente.
- Pruebas de caracterización y suite completa verdes en Python 3.10, 3.11 y 3.12.
- CLI JSON/XMind y fixture de smoke siguen funcionando.
- Documentación y matriz de compatibilidad actualizadas.

### Fase 2 — Evolución semántica y estructural del IR

- [ ] Definir el vocabulario y ubicación de roles semánticos, separado de `Topic.kind`.
- [ ] Definir estructuras compuestas neutrales, empezando por `tree_table`.
- [ ] Especificar filas, celdas, roles de celda, orden, anidamiento y contenido.
- [ ] Separar estructura neutral de las claves privadas de XMind.
- [ ] Revisar el tratamiento de propiedades ausentes, explícitas y el literal `inherited`.
- [ ] Actualizar entidades, esquema, validación, ejemplos y documentación.
- [ ] Definir política de versión IR y migración de documentos 1.0.0.

**Criterio de cierre:** esquema y validación aprobados, fixtures positivos/negativos, migración documentada y ninguna filtración de clases internas XMind al IR.

### Fase 3 — Catálogo semántico y visual de estilos

- [ ] Diseñar esquema de catálogo legible por máquina y documentación legible por IA/personas.
- [ ] Definir estilos semánticos (significado, destinatarios, cuándo usar/no usar, ejemplos y restricciones).
- [ ] Definir tokens/propiedades visuales neutrales y mapeo por adaptador.
- [ ] Definir reglas semánticas prioritarias y reglas estructurales complementarias.
- [ ] Definir precedencia, defaults, fallback, overrides y conflictos.
- [ ] Definir procedencia/auditoría por propiedad resuelta.
- [ ] Formalizar herencia por primer hijo, recursividad, estilos parciales y excepciones.
- [ ] Distinguirla de herencia de style_set y de herencia nativa XMind.
- [ ] Mantener el YAML runtime actual compatible durante la transición.

**Criterio de cierre:** catálogo versionado, especificación del motor, ejemplos y casos de prueba conceptuales deterministas.

### Fase 4 — Especificación del lenguaje PMD

- [ ] Definir el modelo de documento, front matter y relación con Markdown ordinario.
- [ ] Definir sintaxis compacta para roles, estructuras, estilos y excepciones.
- [ ] Resolver explícitamente semántica de encabezados y listas.
- [ ] Definir referencias/IDs, escapes, errores y compatibilidad.
- [ ] Diseñar ejemplos legislativos y tablas de árbol con anotación mínima.
- [ ] Verificar que la sintaxis puede representar el IR aprobado sin detalles XMind.

**Criterio de cierre:** gramática inequívoca, ejemplos de referencia y especificación validada antes de programar parser.

### Fase 5 — Parser, validador y conversión PMD → IR

- [ ] Implementar parser PMD separado del parser Markdown existente.
- [ ] Validar roles, estructuras, referencias y estilos.
- [ ] Convertir PMD al IR de forma determinista.
- [ ] Añadir pruebas negativas y fixtures de referencia.
- [ ] Preservar el flujo Markdown → IR durante la introducción de PMD.

**Criterio de cierre:** documentos PMD de referencia parsean a IR válido y reproducible.

### Fase 6 — Conversión asistida por IA Markdown → PMD

- [ ] Crear prompt/protocolo de transformación basado en catálogo y reglas.
- [ ] Construir corpus de Markdown fuente y PMD esperado, especialmente legislación.
- [ ] Definir cómo señalar ambigüedades y evitar invención.
- [ ] Medir precisión semántica, validez PMD y cantidad de anotación manual.
- [ ] Incorporar el catálogo y ejemplos en el contexto de la IA.

**Criterio de cierre:** evaluación reproducible y reducción demostrable del formateo manual.

### Fase 7 — Adaptador XMind y fidelidad visual

- [ ] Implementar mapeo de `tree_table` y roles de celda.
- [ ] Ampliar estilos, marcadores y recursos según prioridades reales.
- [ ] Mantener rechazo explícito de características no soportadas.
- [ ] Crear fixtures generados y guardados desde la versión objetivo de XMind Desktop.
- [ ] Validar archivos abiertos/guardados/reabiertos en XMind Desktop.
- [ ] Comparar SVG por fidelidad visual, no por identidad XML.

**Criterio de cierre:** estructuras prioritarias reproducidas con fidelidad visual suficiente y matriz de compatibilidad sustentada en pruebas.

### Fase 8 — Integración, documentación y publicación

- [ ] Integrar CLI y comandos de validación/inspección PMD.
- [ ] Completar guías de autoría, catálogo y reglas para IA.
- [ ] Actualizar ejemplos, changelog y notas de migración.
- [ ] Ejecutar CI completa y pruebas manuales Desktop.
- [ ] Publicar versión cuando se cumplan los criterios de release.

**Criterio de cierre:** flujo reproducible Markdown → IA → PMD → IR → XMind, documentación y distribución verificadas.

## Orden y reglas de ejecución

1. Las fases 1 y 2 preceden al cierre de sintaxis PMD.
2. El catálogo semántico se especifica tras acordar el vocabulario/estructura del IR; puede prepararse conceptualmente en paralelo, pero no se implementa antes de estabilizar sus destinatarios.
3. Cada tarea se trabaja en commits pequeños y preferiblemente en ramas de trabajo.
4. Antes de editar se consulta HEAD y los archivos afectados.
5. Cada cambio de código requiere pruebas locales cuando haya entorno disponible y CI nueva; no se declara validado solo por haber enviado el cambio.
6. No se cambia el contrato IR 1.0.0 silenciosamente.
7. Se actualizan `development-status.md`, `architecture.md`, `file-reference.md` y el prompt de continuidad cuando una decisión o implementación afecte a su contenido.
8. Se distinguen siempre: observado, implementado, decidido y pendiente.
9. No se copia una implementación o serializador oficial XMind sin verificar compatibilidad con Desktop.

## Ejecución activa

La Fase 0 queda documentada en ADR-001. La Fase 1 está iniciada: el mapa inicial de consumidores está en [ir-consolidation-audit.md](ir-consolidation-audit.md). Caracterización inicial y comparación legacy/IR completadas; CI [43221440866](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43221440866) verde con 163 pruebas por Python 3.10–3.12 y build/install correctos. El repositorio no permite conocer consumidores externos; por prudencia se conservarán las funciones legacy como wrappers/adaptadores durante la migración. Siguiente tarea: implementar por pasos el diseño de [ir-parser-design.md](ir-parser-design.md), comenzando por AST sintáctico y builder IR.
