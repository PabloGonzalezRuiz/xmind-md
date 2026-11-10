# Estado de desarrollo

> **Documento de seguimiento operativo del proyecto.** Debe actualizarse al terminar cada tarea de desarrollo autorizada y cuando cambie una decisión técnica relevante.

- **Última actualización:** 2026-11-10
- **Rama de referencia:** `main`
- **Último commit de implementación:** `c81121bc0536841cc638e3169c0c505d2a6b5645`
- **Contrato objetivo:** IR 1.0.0
- **Estado global:** prototipo en migración hacia el IR 1.0.0; todavía no declarar compatibilidad completa.

## 1. Para qué sirve este documento

Este archivo es el punto de entrada para que una persona o una IA pueda retomar el desarrollo sin reconstruir el estado únicamente a partir del historial de conversación.

Registra:

1. Qué existe realmente en el repositorio.
2. Qué está implementado, qué está parcialmente implementado y qué no está verificado.
3. Las decisiones técnicas vigentes.
4. Las tareas terminadas y pendientes.
5. El siguiente paso autorizado y sus criterios de aceptación.
6. La evidencia disponible para afirmar que algo funciona.

No sustituye a las especificaciones. Cuando haya discrepancias, consultar los documentos técnicos enlazados y resolverlas explícitamente; no asumir que el código cumple una especificación por el mero hecho de que esta exista.

## 2. Fuentes de verdad

| Área | Documento o ubicación |
|---|---|
| Contrato del modelo intermedio | [Especificación IR 1.0.0](ir-specification.md) |
| Validación estructural del IR | [JSON Schema](ir-schema.json) |
| Ejemplo del IR | [Constitución en IR](../examples/ir/constitucion.json) |
| Migración del modelo | [Plan de migración](ir-migration-plan.md) |
| Arquitectura | [architecture.md](architecture.md) |
| Gramática Markdown | [grammar.md](grammar.md) |
| Adaptador XMind | [xmind-adapter.md](xmind-adapter.md) |
| Pruebas de integración XMind | [xmind-integration-tests.md](xmind-integration-tests.md) |
| Instalación y desarrollo | [development.md](development.md) |
| Prompt de reconstrucción | [ai-reconstruction-prompt.md](ai-reconstruction-prompt.md) |

Prioridad: contrato IR aprobado para la estructura objetivo; código y pruebas para el comportamiento realmente disponible; este documento para el estado y la secuencia de trabajo.

## 3. Estado técnico comprobado

### 3.1 Modelo intermedio

**Estado: modelo canónico creado; integración y verificación pendientes.**

Se ha añadido `src/xmind_md/ir/` con entidades canónicas IR 1.0.0, serialización y validación semántica. El módulo `src/xmind_md/model.py` se conserva temporalmente para que parser, estilos y adaptadores actuales sigan funcionando mientras se migran en las tareas siguientes. Por tanto, la aplicación todavía no produce IR 1.0.0 de extremo a extremo.

El modelo legacy `src/xmind_md/model.py` todavía presenta estas diferencias:

- `MindMap.topics` contiene una lista de temas raíz, en vez de `MindMap.sheet.root_topic`.
- `MindMap.assets` es una lista, no un inventario indexado por ID.
- `Topic.content` contiene texto heredado; los bloques estructurados están separados en `content_blocks`.
- El estilo se distribuye entre `style_ref`, `style_overrides` y `resolved_style`.
- Los recursos se almacenan como lista en `Topic.resources`.
- Relaciones, límites y resúmenes están en `MindMap`, no dentro de `Sheet`.
- No existe todavía una entidad `Sheet` en el modelo Python.

El parser, los resolutores, los adaptadores y las pruebas consumen partes de esta estructura antigua. La migración debe ser coordinada para no dejar consumidores rotos.

### 3.2 Parser Markdown

**Estado: puente de conversión a IR 1.0.0 implementado y probado; API legacy conservada temporalmente.**

`src/xmind_md/ir_parser.py` expone `parse_markdown_ir()` y `parse_file_ir()`. Estas funciones convierten el resultado del parser actual a entidades canónicas, estructuran la hoja y validan el documento resultante. `parse_markdown()` y `parse_file()` continúan devolviendo el modelo legacy para no romper el resolutor de estilos, la CLI y los adaptadores aún no migrados. La gramática completa sigue pendiente de la tarea 7.

### 3.3 Estilos

**Estado: resolutor IR 1.0.0 implementado y probado; ruta legacy conservada.**

`resolve_styles()` despacha el modelo canónico a `resolve_ir_styles()` y mantiene el comportamiento anterior para el modelo legacy. La cascada IR aplica valores predeterminados del sistema, `metadata.style_defaults`, conjunto aplicable, estilo nombrado y overrides locales, mediante fusión recursiva por propiedad. Los conjuntos se seleccionan globalmente con `metadata.style_set` o por tema con `Topic.style.style_set`; se heredan por rama y pueden sustituirse en descendientes. Se resuelven temas, notas, relaciones, límites y resúmenes. Las definiciones originales no se mutan.

### 3.4 Adaptadores y exportación

**Estado: adaptadores existentes; exportación XMind experimental.**

- Existe un adaptador JSON de inspección.
- Existe un adaptador XMind basado en ZIP y JSON.
- La exportación XMind cubre solo una parte de las entidades y propiedades del contrato.
- La exportación XMind todavía no está integrada en la CLI.
- No se ha acreditado aquí una apertura y posterior guardado satisfactorios del archivo generado en XMind Desktop.

No anunciar compatibilidad completa con XMind Desktop hasta realizar y registrar esa comprobación.

### 3.5 CLI, pruebas y automatización

**Estado: funcionalidad parcial documentada; ejecución global pendiente de evidencia.**

- La CLI permite generar el JSON intermedio.
- Hay pruebas unitarias y de integración en `tests/`.
- GitHub Actions contiene un flujo de CI y una generación de artefacto XMind de prueba.
- La ejecución CI #123 finalizó correctamente: 65 pruebas superadas y artefacto XMind de comprobación generado.
- Ruff no forma parte todavía de los pasos del workflow y debe verificarse expresamente.
- La ejecución local en Windows sigue pendiente; la existencia de configuración o documentación no demuestra que haya pasado.

## 4. Decisiones técnicas vigentes

1. Un archivo Markdown produce un mapa con una única hoja.
2. La hoja contiene exactamente un tema raíz.
3. Todos los temas pertenecen al árbol; no se permiten temas flotantes.
4. El contenido se representa mediante bloques estructurados.
5. Los estilos se pueden definir en YAML y en Markdown, con precedencia explícita.
6. El IR es neutral respecto a XMind y a las bibliotecas de exportación.
7. El parser interpreta Markdown; el modelo define entidades; el resolutor calcula estilos; los adaptadores convierten el IR.
8. Las características no soportadas por un adaptador deben notificarse, no descartarse silenciosamente.
9. No se debe declarar implementada una capacidad solo porque aparezca en el esquema o la documentación.
10. La migración debe mantener una sola fuente de verdad por dato y retirar la compatibilidad legacy cuando todos los consumidores estén migrados.

## 5. Hoja de ruta y estado

| N.º | Tarea | Estado | Criterio de cierre |
|---:|---|---|---|
| 1 | Consolidar el contrato IR 1.0.0 y preparar la migración | **Completada** | Especificación, esquema, ejemplo y plan de migración disponibles |
| 2 | Implementar el modelo Python conforme al IR | **Completada** | Entidades canónicas, invariantes y pruebas del modelo ejecutadas con éxito |
| 3 | Adaptar el parser al nuevo modelo | **Completada** | Parser construye el IR canónico y conserva la sintaxis probada |
| 4 | Adaptar el resolutor de estilos | **Completada** | Cascada conforme a IR y pruebas de precedencia |
| 5 | Adaptar los exportadores JSON y XMind | Pendiente | Consumen el modelo canónico y notifican pérdidas |
| 6 | Validar el esquema JSON y los ejemplos | Pendiente | Draft 2020-12 validado por herramienta y ejemplos conformes |
| 7 | Completar y probar la gramática Markdown | Pendiente | Gramática y pruebas cubren las construcciones declaradas |
| 8 | Ampliar y probar las capacidades del adaptador XMind | Pendiente | Matriz de capacidades y pruebas por entidad/propiedad |
| 9 | Integrar la exportación XMind en la CLI | Pendiente | Comando/opción documentado y probado |
| 10 | Completar las pruebas con XMind Desktop | Pendiente | Apertura, inspección y guardado comprobados y registrados |
| 11 | Verificar ejecución local en Windows | Pendiente | Instalación, CLI y pruebas ejecutadas en entorno Windows |
| 12 | Completar CI, Ruff y comprobaciones automáticas | Pendiente | Workflow verde con pruebas y lint |
| 13 | Sincronizar README y documentación técnica | Pendiente | Documentación coherente con el comportamiento real |
| 14 | Auditoría final y publicación estable | Pendiente | Criterios de aceptación globales cumplidos |

Los estados se refieren a evidencia en el repositorio, no a intenciones ni a tareas descritas en documentos futuros.

## 6. Registro de tareas terminadas y actividad

### Tarea 4 — Resolutor de estilos IR 1.0.0

- **Estado:** completada y verificada mediante GitHub Actions.
- **Archivos de implementación:** `src/xmind_md/styles.py`, `src/xmind_md/ir/entities.py`, `src/xmind_md/ir/validation.py`, `src/xmind_md/ir_parser.py`.
- **Contrato:** se añadió `StyleState.style_set` opcional y su serialización/esquema, para no perder la selección de conjuntos por tema que ya permite Markdown. Se documentó la herencia y sustitución por rama en `docs/ir-specification.md`.
- **Resolución:** `resolve_ir_styles()` implementa la cascada por propiedad: valores predeterminados del sistema, `metadata.style_defaults`, conjunto aplicable, estilo nombrado y overrides locales. La fusión es recursiva; los valores explícitos `null` se conservan. El conjunto se hereda del padre, puede sustituirse por tema y admite selección global mediante `metadata.style_set`.
- **Cobertura:** temas, notas, relaciones, límites y resúmenes. Las definiciones externas se combinan con las del documento, prevaleciendo estas últimas. El resultado se escribe en `style.resolved`; las definiciones originales no se modifican.
- **Compatibilidad:** `resolve_styles()` despacha automáticamente los documentos IR a `resolve_ir_styles()`; mantiene la implementación legacy para los consumidores aún no migrados. El puente `ir_parser.py` conserva ahora tanto el conjunto global como el conjunto específico de cada tema.
- **Validación:** se comprueba la existencia de conjuntos y estilos referenciados. Los formatos incorrectos de definiciones y overrides generan `StyleError`.
- **Pruebas:** CI #144 (`42826026792`), commit `c81121bc0536841cc638e3169c0c505d2a6b5645`: **77 pruebas superadas**. Pasaron `Tests`, `Build XMind Desktop smoke test` y `Upload XMind smoke test`. Entorno: GitHub Actions, Python 3.12.16.
- **Commits principales:** `6070bbaced6ff0621653a9067e9035f22768bdd` (entidad StyleState); `be916113bf1faa269b83c7215f0a08289c4001a3` (esquema); `4789a55675b9ad165a743b31cd299df477d6927a` (especificación); `37e82304081438ef3bfc5dbe76e3f557610f6c3c` y `380dfdcfcdc9e41f1cd6732c736c5538e6a1a505` (preservación de conjuntos en parser); `ace1bcd63492d068dfa8d594a77bbe8ad6e6117d` (validación); `d1e93c4a139dd4e4f1a32019f0cf8f04fe066d26` y `6cf5cca4147ba7ecab5f65eceaf0777b58c0e061` (resolutor y despacho).
- **Pruebas nuevas:** `tests/test_ir_styles.py` cubre cascada, fusión recursiva, herencia, sustitución de conjunto, precedencia de definiciones, errores, no mutación y estilos de entidades de hoja; se ampliaron `tests/test_ir_model.py` y `tests/test_ir_parser.py`.
- **Documentación:** actualizadas `docs/ir-specification.md` y `docs/architecture.md`. La validación formal del esquema JSON completo y Ruff siguen en las tareas correspondientes; no se afirman como ejecutadas en esta fase.


### Tarea 3 — Puente del parser al IR 1.0.0

- **Estado:** completada y verificada mediante GitHub Actions.
- **Archivos:** `src/xmind_md/ir_parser.py`, `tests/test_ir_parser.py`.
- **API canónica:** `parse_markdown_ir(text, source_path)` y `parse_file_ir(path)`.
- **Resultado:** convierte la salida del parser existente a `MindMap.sheet.root_topic`, bloques estructurados, anotaciones, estilos, enlaces, assets, relaciones, límites y resúmenes; valida el resultado con `validate_mind_map()`.
- **Compatibilidad:** se mantienen `parse_markdown()` y `parse_file()` como API legacy hasta que estilos, CLI y adaptadores se migren. No se ha cambiado aún el flujo predeterminado de la aplicación.
- **Pruebas:** CI #123 (`42824785297`), commit `d6e3152670696060e09eabe8ac1b2262c2476718`: **65 pruebas superadas**. Pasaron los pasos `Tests`, `Build XMind Desktop smoke test` y `Upload XMind smoke test`. Entorno: GitHub Actions, Python 3.12.16.
- **Correcciones durante la fase:** #120 detectó una referencia a estilo inexistente; #121 detectó una aserción que inspeccionaba la raíz en lugar del tema hijo. Ambos problemas se corrigieron y la ejecución #123 quedó verde.
- **Limitaciones:** no se ha migrado el resolutor de estilos, la CLI ni los adaptadores. La gramática completa sigue pendiente. La generación del artefacto XMind no acredita apertura manual en XMind Desktop.


### Tarea 2 — Modelo canónico IR 1.0.0

- **Estado:** completada y verificada mediante GitHub Actions.
- **Archivos:** `src/xmind_md/ir/entities.py`, `src/xmind_md/ir/validation.py`, `src/xmind_md/ir/__init__.py`, `tests/test_ir_model.py`.
- **Resultado:** entidades tipadas para mapa, hoja, tema, contenido, anotaciones, estilos, recursos, relaciones, límites y resúmenes; serialización con forma canónica; validación de IDs, árbol, estilos y referencias.
- **Compatibilidad:** `src/xmind_md/model.py` no se ha sustituido todavía. Los consumidores actuales siguen usando el modelo legacy hasta las tareas de migración del parser, estilos y adaptadores.
- **Fallo inicial:** CI #114 (`42823184882`, commit `1676f4594c941a0625f4c73fc098d862e29b156a`): 58 pasadas y 1 fallida. El test inspeccionaba el tema raíz aunque el contenido, etiqueta y recurso se habían asignado al tema hijo.
- **Corrección:** `tests/test_ir_model.py` ahora inspecciona `root_topic.children[0]`. Commit: `a94c0c93c0ba542c4c7bde85e60351c31d20a446`.
- **Verificación:** CI #115 (`42823555030`), sobre el commit de corrección: **59 pruebas superadas**. Los pasos `Tests`, `Build XMind Desktop smoke test` y `Upload XMind smoke test` finalizaron correctamente. Entorno: GitHub Actions, Ubuntu runner, Python 3.12.16.
- **Artefacto:** generado y publicado con el nombre `xmind-desktop-smoke-test` en esa ejecución; esto acredita la generación, no la apertura manual en XMind Desktop.
- **Advertencias de runner:** Node.js 20 de las acciones y la futura migración de `ubuntu-latest` son independientes del fallo inicial de pytest.

### Tarea 1 — Contrato IR y plan de migración

- **Estado:** completada.
- **Resultado:** contrato IR 1.0.0 especificado; esquema JSON y ejemplo creados; plan de migración documentado.
- **Archivos principales:** `docs/ir-specification.md`, `docs/ir-schema.json`, `examples/ir/constitucion.json`, `docs/ir-migration-plan.md`.
- **Commit del plan de migración:** `9df7ee3e1dbe6c78bb045d325495ed613d093042`.
- **Limitación pendiente:** la existencia del esquema no equivale a haberlo validado todavía con un validador Draft 2020-12.

## 7. Próxima tarea

### Tarea 5 — Adaptar los exportadores JSON y XMind al IR 1.0.0

**Estado:** pendiente de autorización expresa.

**Alcance propuesto:**
- Hacer que el adaptador JSON serialice directamente el modelo canónico.
- Migrar el adaptador XMind para leer `MindMap.sheet.root_topic` y las entidades de hoja.
- Consumir `style.resolved` sin volver a interpretar ni resolver estilos.
- Mantener los límites de capacidad explícitos y notificar cualquier pérdida o propiedad no soportada.
- Evitar dependencias del modelo legacy una vez migrados ambos adaptadores.

**Criterios de aceptación:**
- Pruebas de exportación JSON y XMind basadas en objetos IR.
- Pruebas positivas y negativas para estilos, recursos y entidades de hoja.
- La suite completa sigue pasando y el IR original no se modifica.
- No se declara compatibilidad completa con XMind Desktop sin validación manual.
- Actualización de esta documentación al cerrar la tarea.

No iniciar esta tarea hasta recibir autorización expresa.

## 9. Protocolo obligatorio de actualización

Al terminar cada tarea autorizada:

1. Actualizar el estado de la tarea en la tabla de la sección 5.
2. Añadir una entrada en el registro de tareas terminadas con archivos modificados, decisiones y commit.
3. Actualizar la descripción del estado técnico afectado.
4. Anotar pruebas ejecutadas con comando, resultado y entorno. Diferenciar claramente pruebas locales, CI y verificaciones manuales.
5. Actualizar la sección «Próxima tarea» con el siguiente paso y sus criterios.
6. Registrar bloqueos o limitaciones que sigan abiertos.
7. Hacer commit de esta actualización junto con la tarea o en un commit documental asociado.
8. No marcar una tarea como completada si alguno de sus criterios de aceptación sigue pendiente.

Si no se puede ejecutar una prueba, anotarlo como **no ejecutada**; si falla, registrar el fallo. Nunca inferir un resultado.

## 10. Reglas para retomar el trabajo

Antes de modificar el repositorio:

1. Consultar la rama y el último commit de `main`.
2. Leer este documento y el plan de migración.
3. Inspeccionar los archivos afectados y sus consumidores directos.
4. Comprobar si el estado descrito sigue vigente.
5. Respetar el alcance de la tarea autorizada y solicitar autorización antes de pasar a la siguiente.

Este documento es una fotografía mantenida del estado de desarrollo, no una garantía automática de que el repositorio no haya cambiado desde su última actualización.
