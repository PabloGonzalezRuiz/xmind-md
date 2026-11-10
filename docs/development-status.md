# Estado de desarrollo

> **Documento de seguimiento operativo del proyecto.** Debe actualizarse al terminar cada tarea de desarrollo autorizada y cuando cambie una decisión técnica relevante.

- **Última actualización:** 2026-11-10
- **Rama de referencia:** `main`
- **Último commit revisado antes de esta actualización:** `9df7ee3e1dbe6c78bb045d325495ed613d093042`
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

**Estado: pendiente de migración.**

La especificación IR 1.0.0 está documentada, pero `src/xmind_md/model.py` todavía representa el modelo transitorio:

- `MindMap.topics` contiene una lista de temas raíz, en vez de `MindMap.sheet.root_topic`.
- `MindMap.assets` es una lista, no un inventario indexado por ID.
- `Topic.content` contiene texto heredado; los bloques estructurados están separados en `content_blocks`.
- El estilo se distribuye entre `style_ref`, `style_overrides` y `resolved_style`.
- Los recursos se almacenan como lista en `Topic.resources`.
- Relaciones, límites y resúmenes están en `MindMap`, no dentro de `Sheet`.
- No existe todavía una entidad `Sheet` en el modelo Python.

El parser, los resolutores, los adaptadores y las pruebas consumen partes de esta estructura antigua. La migración debe ser coordinada para no dejar consumidores rotos.

### 3.2 Parser Markdown

**Estado: implementación parcial existente.**

El parser ya reconoce parte de la sintaxis descrita en la documentación: encabezados, metadatos/directivas, contenido textual y varios bloques estructurados, además de elementos como relaciones, límites y resúmenes. No debe considerarse completa toda la gramática hasta contrastar cada construcción con `docs/grammar.md` y sus pruebas.

### 3.3 Estilos

**Estado: implementación parcial existente.**

Existe carga de estilos YAML y resolución inicial de referencias, conjuntos y modificaciones locales. Debe alinearse con la estructura `style.ref`, `style.overrides` y `style.resolved` del IR 1.0.0 y con la precedencia definida en la especificación.

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
- En esta revisión no se ha confirmado una ejecución CI satisfactoria reciente.
- Ruff y la ejecución local en Windows deben verificarse expresamente; la existencia de configuración o documentación no demuestra que hayan pasado.

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
| 2 | Implementar el modelo Python conforme al IR | **Pendiente de autorización/ejecución** | Entidades canónicas, invariantes y pruebas del modelo |
| 3 | Adaptar el parser al nuevo modelo | Pendiente | Parser construye el IR canónico y conserva la sintaxis probada |
| 4 | Adaptar el resolutor de estilos | Pendiente | Cascada conforme a IR y pruebas de precedencia |
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

## 6. Registro de tareas terminadas

### Tarea 1 — Contrato IR y plan de migración

- **Estado:** completada.
- **Resultado:** contrato IR 1.0.0 especificado; esquema JSON y ejemplo creados; plan de migración documentado.
- **Archivos principales:** `docs/ir-specification.md`, `docs/ir-schema.json`, `examples/ir/constitucion.json`, `docs/ir-migration-plan.md`.
- **Commit del plan de migración:** `9df7ee3e1dbe6c78bb045d325495ed613d093042`.
- **Limitación pendiente:** la existencia del esquema no equivale a haberlo validado todavía con un validador Draft 2020-12.

## 7. Próxima tarea

### Tarea 2 — Implementar el modelo Python conforme al IR 1.0.0

**Situación:** pendiente de inicio. El usuario ha autorizado continuar con esta fase una vez creado este documento de seguimiento.

**Alcance previsto:**

- Definir las entidades canónicas, incluida `Sheet`.
- Representar una única raíz mediante `MindMap.sheet.root_topic`.
- Estructurar bloques de contenido, estilos, recursos y entidades de hoja según el contrato.
- Añadir validación de invariantes e IDs.
- Añadir pruebas unitarias específicas del modelo.
- Mantener una estrategia de transición explícita para los consumidores legacy; no afirmar que parser y adaptadores están migrados hasta completar sus tareas.

**Fuera de alcance:** completar la gramática, cambiar el parser de forma integral, terminar la resolución de estilos o ampliar la compatibilidad XMind. Esas tareas conservan sus propios pasos en la hoja de ruta.

**Criterios de aceptación:** el modelo puede representar y serializar el contrato canónico; se validan árbol, IDs y referencias cubiertas por el modelo; las pruebas nuevas pasan; las incompatibilidades pendientes quedan identificadas sin ocultarlas.

## 8. Protocolo obligatorio de actualización

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

## 9. Reglas para retomar el trabajo

Antes de modificar el repositorio:

1. Consultar la rama y el último commit de `main`.
2. Leer este documento y el plan de migración.
3. Inspeccionar los archivos afectados y sus consumidores directos.
4. Comprobar si el estado descrito sigue vigente.
5. Respetar el alcance de la tarea autorizada y solicitar autorización antes de pasar a la siguiente.

Este documento es una fotografía mantenida del estado de desarrollo, no una garantía automática de que el repositorio no haya cambiado desde su última actualización.
