# Estado de desarrollo

> **Documento de seguimiento operativo del proyecto.** Debe actualizarse al terminar cada tarea de desarrollo autorizada y cuando cambie una decisión técnica relevante.

- **Última actualización:** 2026-11-11 (remediación Ruff)
- **Rama de referencia:** `main`
- **Última prueba manual XMind Desktop:** superada en Windows, XMind 26.05.01107.
- **Commit de incorporación del fixture XMind permanente:** `a1cf99861c819d9f148a7c7a3d779df6a95fc394`.
- **Contrato objetivo:** IR 1.0.0
- **Estado global:** IR 1.0.0 integrado en parser, estilos, adaptadores y CLI; fixture comprobado manualmente en XMind Desktop 26.05.01107; CI histórica Linux/Python 3.12 con 131 pruebas superadas. El workflow actual ya incorpora matriz Ubuntu/Windows y Ruff, pero las ejecuciones de esa nueva configuración aún no están verificadas. El usuario ha decidido no instalar ni ejecutar herramientas localmente por ahora.

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

**Estado: modelo IR, parser, resolutor y adaptadores canónicos integrados; validación formal del esquema completada.**

`src/xmind_md/ir/` contiene las entidades canónicas IR 1.0.0, serialización y validación semántica. `src/xmind_md/model.py` se conserva como API legacy por compatibilidad; los adaptadores JSON/XMind y el flujo actual de CLI/smoke consumen el IR canónico.

El modelo legacy `src/xmind_md/model.py` todavía presenta estas diferencias:

- `MindMap.topics` contiene una lista de temas raíz, en vez de `MindMap.sheet.root_topic`.
- `MindMap.assets` es una lista, no un inventario indexado por ID.
- `Topic.content` contiene texto heredado; los bloques estructurados están separados en `content_blocks`.
- El estilo se distribuye entre `style_ref`, `style_overrides` y `resolved_style`.
- Los recursos se almacenan como lista en `Topic.resources`.
- Relaciones, límites y resúmenes están en `MindMap`, no dentro de `Sheet`.
- No existe todavía una entidad `Sheet` en el modelo Python.

El puente del parser y el resolutor disponen de rutas canónicas IR. Los adaptadores y los consumidores directos migrados no dependen del modelo legacy.

### 3.2 Parser Markdown

**Estado: puente de conversión a IR 1.0.0 implementado y probado; API legacy conservada temporalmente.**

`src/xmind_md/ir_parser.py` expone `parse_markdown_ir()` y `parse_file_ir()`. Estas funciones convierten el resultado del parser actual a entidades canónicas, estructuran la hoja y validan el documento resultante. `parse_markdown()` y `parse_file()` conservan la API legacy; `parse_markdown_ir()` y `parse_file_ir()` proporcionan la ruta canónica. La CLI JSON y el generador smoke usan la ruta IR. La tarea 7 ha auditado y probado el subconjunto implementado; `docs/grammar.md` delimita expresamente las funciones no compatibles con CommonMark/GFM completo.

### 3.3 Estilos

**Estado: resolutor IR 1.0.0 implementado y probado; ruta legacy conservada.**

`resolve_styles()` despacha el modelo canónico a `resolve_ir_styles()` y mantiene el comportamiento anterior para el modelo legacy. La cascada IR aplica valores predeterminados del sistema, `metadata.style_defaults`, conjunto aplicable, estilo nombrado y overrides locales, mediante fusión recursiva por propiedad. Los conjuntos se seleccionan globalmente con `metadata.style_set` o por tema con `Topic.style.style_set`; se heredan por rama y pueden sustituirse en descendientes. Se resuelven temas, notas, relaciones, límites y resúmenes. Las definiciones originales no se mutan.

### 3.4 Adaptadores y exportación

**Estado: adaptadores migrados al IR 1.0.0 y verificados en CI.**

- `json_adapter.py` serializa exclusivamente `MindMap.to_dict()` del IR 1.0.0.
- `xmind_adapter.py` consume `MindMap.sheet`, entidades `Topic`, `Relationship`, `Annotation` y `StyleState` canónicas; no importa el modelo legacy.
- La exportación XMind mantiene un perfil parcial y rechaza recursos, imágenes, boundaries, summaries, layouts no predeterminados y extensiones no soportadas.
- La CLI JSON y el script de smoke test construyen IR mediante `parse_file_ir()`.
- La apertura, inspección visual, guardado y reapertura manual del fixture se confirmaron en XMind Desktop para Windows 26.05.01107. La comprobación cubre los elementos incluidos en el fixture, no todas las capacidades del formato.

La prueba manual acredita el fixture y los elementos comprobados, no compatibilidad universal ni cobertura de todas las capacidades XMind.

### 3.5 CLI, pruebas y automatización

**Estado: suite y generación de artefacto verificadas históricamente; prueba manual del fixture superada; matriz CI actualizada a Ubuntu/Windows y correcciones Ruff publicadas, pendientes de nueva verificación.**

- La CLI genera JSON (`.json`) o libros XMind (`.xmind`) a partir de `parse_file_ir()`; admite `--format` explícito y deducción por extensión.
- La exportación XMind resuelve estilos antes de invocar el adaptador; la salida JSON conserva el comportamiento anterior y solo resuelve estilos si se proporciona `--styles`.
- Los errores de entrada, configuración, formato y capacidades XMind no exportables se muestran en stderr y devuelven código 2.
- Hay pruebas unitarias, de integración y de CLI en `tests/`.
- GitHub Actions contiene un flujo de CI y una generación de artefacto XMind de prueba.
- CI #165, commit `2250dbf06d86680cbfcf9c5c4c4d208e62a4f53b`: **90 pruebas superadas**, incluyendo validación formal Draft 2020-12, ejemplos y casos negativos; generación y publicación del artefacto XMind correctas.
- CI #178, commit `f2f491cd52e668a53d31c1dddbf321c30f262882`: **97 pruebas superadas**; generación y publicación del artefacto XMind correctas tras los cambios de gramática.
- CI #203, run `42842555229`, commit `1995076eee2e5108c37320c7a9df9be21745f5de`: **131 pruebas superadas en 0,45 s**; Tests, generación del smoke XMind y publicación del artefacto correctos. Entorno: GitHub Actions, Ubuntu, Python 3.12.16. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42842555229
- CI #205, run `42842726726`, commit `f99273d3f93a95648457aa183bb4ec55bb99fda8`: workflow completo correcto tras la actualización del documento de estado. Los cinco pasos Install, Download XMind reference fixture, Tests, Build XMind Desktop smoke test y Upload XMind smoke test finalizaron correctamente. El log registra **131 pruebas superadas en 0,52 s**. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42842726726
- CI #209, run `42843815047`, commit `1fd131cc16786093dba00e09fd551f299a439761`: job tests completado con success; Install, descarga del fixture de referencia, Tests, generación y publicación del smoke test finalizaron correctamente. Log: **131 passed in 0.37s**, GitHub-hosted Linux, Python 3.12.16. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42843815047
- Auditoría detallada del run #209 (workflow anterior): job `tests` y sus pasos completados con `success`; artefacto `xmind-desktop-smoke-test` publicado (ID `13776583547`, 1.333 bytes, SHA-256 `a0706df6bc41f5cd1ba04c85bffb04faeb8d93e0422cc454c75895d83d2ae69a`), con expiración `2026-11-24T15:23:39Z`. Esta evidencia no valida la matriz nueva ni Ruff.
- Validador: `jsonschema 4.26.0` con extra `format`; se comprueban los formatos de fecha/fecha-hora.
- Commit `509fd41869429526c6a903e3a3bdc2f2507a2be9`: `.github/workflows/ci.yml` incorpora matriz `ubuntu-latest`/`windows-latest`, Python 3.12, `ruff check src tests`, `ruff format --check src tests`, pytest, generación del smoke XMind y artefactos separados por sistema operativo.
- Commit `a6bd54423f5d79d18207e65be809d4be5f5900fe`: registra la implementación en curso.
- A fecha de esta auditoría no se ha obtenido evidencia verificable de los runs disparados por esos commits. No afirmar que Ruff, Windows, pytest en ambos runners ni los dos artefactos han pasado.
- El usuario no quiere instalar ni ejecutar Python localmente; la validación debe realizarse en GitHub Actions.

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
| 5 | Adaptar los exportadores JSON y XMind | **Completada** | Consumen el modelo canónico y notifican pérdidas |
| 6 | Validar el esquema JSON y los ejemplos | **Completada** | Draft 2020-12 validado por herramienta y ejemplos conformes |
| 7 | Completar y probar la gramática Markdown | **Completada** | Subconjunto implementado auditado, limitaciones explícitas y suite CI verde |
| 8 | Ampliar y probar las capacidades del adaptador XMind | **Completada** | Matriz de capacidades, conversiones adicionales y suite CI verde |
| 9 | Integrar la exportación XMind en la CLI | **Completada** | CLI XMind y JSON probadas, errores controlados y documentación actualizada |
| 10 | Completar las pruebas con XMind Desktop | **Completada** | Apertura, inspección, guardado y reapertura confirmados; versión y resultados registrados |
| 11 | Auditar y verificar la ejecución en GitHub Actions | **Completada** | Workflow y último run inspeccionados; 131 pruebas y artefacto generados correctamente |
| 12 | Completar CI, Ruff y comprobaciones automáticas | **En curso** | Workflow verde con pruebas y lint en Linux y Windows |
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


### Tarea 5 — Adaptadores JSON y XMind para IR 1.0.0

- **Estado:** completada.
- **Implementación:** `src/xmind_md/adapters/json_adapter.py` serializa exclusivamente `MindMap.to_dict()`; `src/xmind_md/adapters/xmind_adapter.py` consume `MindMap.sheet`, temas, anotaciones, relaciones y `StyleState.resolved` canónicos. Ninguno importa el modelo legacy.
- **Consumidores directos:** `src/xmind_md/cli.py` y `scripts/create_xmind_smoke.py` utilizan `parse_file_ir()`. Las pruebas unitarias y de integración XMind construyen objetos IR.
- **Seguridad ante pérdidas:** el adaptador XMind rechaza assets, recursos, imágenes, bloques raw, boundaries, summaries, tareas, extensiones, layouts no predeterminados, metadatos de mapa/hoja no soportados, enlaces no web o múltiples y estilos sin resolver/no reconocidos.
- **No mutación:** se añadió prueba que compara la serialización IR antes y después de exportar.
- **Pruebas:** CI #157, commit `a179b38197f5e59d40a08b3efd26460e1093c735`: **84 pruebas superadas**. CI #160, commit documental final `dee63dbd9c1caa0dc1f82ccaec047b0154bb1014`: **84 pruebas superadas** y pasos `Build XMind Desktop smoke test` y `Upload XMind smoke test` correctos. Run #160: `42830369404`.
- **Correcciones verificadas:** CI #151 detectó dos pruebas de integración que seguían construyendo el modelo legacy; CI #152 detectó que el script smoke aún usaba el parser legacy. Se migraron ambas rutas y las ejecuciones posteriores quedaron verdes.
- **Artefacto:** `xmind-desktop-smoke-test` generado y subido en CI #160. Esto acredita la generación del paquete, no su apertura manual en XMind Desktop.
- **Commits:** implementación `5a52a84b4a36b5e029fdfb26252e811ff637f592`; pruebas IR de integración `638cf3392947841332a06099a95e09807a359553`; script smoke `5dc36fa038fc9bb78ecbffa746461e240a7660c9`; validación de metadatos y prueba `275f230cd9741b6d7faa59f3c076a76f31df980e` / `a179b38197f5e59d40a08b3efd26460e1093c735`; documentación `3039d0fa6ed9864c218eda2d1621beadadd225b9`, `718a5d9ab564d49570fb508d0cc9af80c2e009af`, `dee63dbd9c1caa0dc1f82ccaec047b0154bb1014`.
- **Entorno:** GitHub Actions, Ubuntu runner, Python 3.12.16. Ruff no se ejecutó; permanece en la tarea 12.
- **Documentación:** actualizadas `docs/xmind-adapter.md`, `docs/architecture.md` y `docs/ir-migration-plan.md`.

### Tarea 6 — Validación formal del esquema JSON y los ejemplos

- **Estado:** completada y verificada en GitHub Actions.
- **Dependencia de desarrollo:** añadido \`jsonschema[format]>=4.22,<5\` a \`pyproject.toml\`; CI resolvió \`jsonschema 4.26.0\` y el extra de validadores de formato.
- **Pruebas:** nuevo \`tests/test_ir_schema.py\`.
  - Comprueba que \`docs/ir-schema.json\` es un esquema válido Draft 2020-12 mediante \`Draft202012Validator.check_schema()\`.
  - Valida todos los JSON encontrados recursivamente en \`examples/ir/\` con \`FormatChecker\`.
  - Comprueba rechazos para versión IR incorrecta, propiedad obligatoria ausente, tipo de enlace no permitido y fecha-hora inválida.
- **Resultado CI #165:** commit \`2250dbf06d86680cbfcf9c5c4c4d208e62a4f53b\`; **90 pruebas superadas en 0,30 s**. Pasaron también la descarga del fixture XMind, generación del archivo smoke y publicación del artefacto. Run: \`42833000666\`.
- **Commits:** dependencia inicial \`de32ff87b54573be595eff26e304730dea73b166\`; pruebas \`367940776aadad58b971185a06a9180c3b1d393a\`; extra de formatos \`3937ddfd04c16488b16d40fde6f3c1c7e4e9c29d\`; prueba de fecha-hora \`2250dbf06d86680cbfcf9c5c4c4d208e62a4f53b\`.
- **Alcance:** validación estructural y de formatos declarados por JSON Schema; no sustituye \`validate_mind_map()\`, que comprueba invariantes semánticas y referencias cruzadas.
- **Limitaciones restantes:** solo existe actualmente un ejemplo JSON en \`examples/ir/\`; no se afirma validación de ejemplos que no existen. Ruff y ejecución local Windows permanecen pendientes.

### Tarea 7 — Auditoría, ampliación y pruebas de la gramática Markdown

- **Estado:** completada y verificada en GitHub Actions.
- **Archivos:** src/xmind_md/parser.py, src/xmind_md/ir_parser.py, src/xmind_md/ir/validation.py, tests/test_parser.py, tests/test_ir_parser.py, docs/grammar.md, docs/ir-migration-plan.md.
- **Auditoría:** contrastadas las reglas documentadas con el parser legacy y la conversión al IR. Se sustituyeron afirmaciones genéricas por una matriz de construcciones implementadas y limitaciones explícitas. No se anuncia compatibilidad completa con CommonMark/GFM.
- **Cambios de parser:** formato inline para negrita, cursiva, tachado y código; enlaces internos [texto](topic:ID); pipes escapados en tablas; comprobación de colisiones entre IDs de entidades globales y temas; procedencia inclusiva por archivo y rango de líneas en párrafos, listas, tablas, código cercado, citas, separadores e imágenes.
- **Conversión IR:** se conservan los rangos de origen de los bloques; las notas mantienen formato inline; los enlaces a temas se representan como kind: topic. validate_mind_map() comprueba los destinos de enlaces internos tanto en los enlaces del tema como en los runs de contenido y notas.
- **Pruebas nuevas:** 7 pruebas de regresión para pipes escapados, colisión de IDs, enlaces internos válidos/inexistentes, tachado y formato de notas, procedencia y rangos de todos los bloques principales. La salida pasa por validación semántica IR.
- **CI final:** #178, run 42836154415, commit f2f491cd52e668a53d31c1dddbf321c30f262882: **97 pruebas superadas en 0,46 s**; pasos Tests, Build XMind Desktop smoke test y Upload XMind smoke test correctos. Entorno: GitHub Actions, Ubuntu, Python 3.12.16. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42836154415
- **Correcciones detectadas por CI:** una ejecución intermedia detectó que la validación no recorría enlaces internos dentro de runs; otra detectó que los bloques de código cercado no tenían source. Ambos defectos se corrigieron y se cubrieron antes de la ejecución final #178.
- **Commits relevantes:** parser inline/tablas/procedencia eaa0f5f5f8e0ea92c178c17d85261a7067e7ae02, corrección de tokens/tabla 714d60177e7e219c1329df71b82215c3fe1b1b73, conversión IR 315ed13a3dc9efb1cb8943ae02f28332a904b417, validación de enlaces 33b654f89e5af669c27bd12919be7038ee44eff2, cobertura de rangos 3107aaf3f25b9c51633c813b005965c48ec9ea25 y corrección de procedencia de código f2f491cd52e668a53d31c1dddbf321c30f262882.
- **Limitaciones deliberadas:** no se implementan CommonMark/GFM completos, fórmulas, HTML, enlaces de referencia, listas laxas, imágenes inline con inventario de assets, ni notas con bloques estructurados. Están enumeradas en docs/grammar.md.
- **No ejecutado:** Ruff, ejecución local Windows y apertura/guardado manual del artefacto en XMind Desktop siguen pendientes en sus tareas correspondientes.

### Tarea 8 — Ampliación y auditoría de capacidades del adaptador XMind

- **Estado:** completada y verificada en GitHub Actions.
- **Archivos:** `src/xmind_md/adapters/xmind_adapter.py`, `tests/test_xmind_adapter.py`, `docs/xmind-adapter.md`, `docs/xmind-integration-tests.md`, `docs/ir-migration-plan.md`.
- **Auditoría:** contrastadas las capacidades IR 1.0.0 con el modelo JSON oficial de XMind. La matriz de `docs/xmind-adapter.md` clasifica cada entidad/capacidad como soportada, parcial o no soportada y describe las pérdidas intencionadas.
- **Temas:** el adaptador exporta hijos `attached`, `detached` y `callout` en las colecciones XMind correspondientes. La raíz debe ser `attached`; los temas `detached` requieren `layout.position` con coordenadas numéricas finitas.
- **Layout de tema:** se mapean `position`, `structure_class`, `branch=folded` y `width` a `position`, `structureClass`, `branch` y `customWidth`. Se rechazan propiedades desconocidas, valores inválidos y números no finitos.
- **Enlaces:** un enlace `topic` se convierte a `href` `xmind:#<UUID>` tras resolver el ID destino; los enlaces `file` se admiten solo con URI `file://`; se conserva el comportamiento `web`. Se rechazan enlaces múltiples, tipo `internal`, títulos adicionales y destinos internos inexistentes.
- **Pérdidas documentadas:** el contenido de bloques se aplana a notas de texto; se pierden los estilos inline y destinos de enlaces inline, los IDs auxiliares y la procedencia; los catálogos de estilos se materializan en propiedades resueltas. Estas pérdidas constan en la matriz.
- **No soportado y rechazado explícitamente:** `kind=summary` y otras clases de tema, `Boundary`, `Summary`, assets y recursos, imágenes, audio, adjuntos, tareas, extensiones, metadatos de hoja, layouts de hoja no predeterminados, estilos visuales de notas y propiedades de estilo no reconocidas.
- **Pruebas nuevas:** casos positivos de temas detached/callout, layout y enlaces topic/file; casos negativos de raíz inválida, clases/layout inválidos, coordenadas/anchuras no finitas, enlaces inválidos o con pérdida, tareas, metadatos, notas con estilo, ecuaciones y enlaces múltiples. La prueba de no mutación IR existente continúa pasando.
- **CI final de código/pruebas:** #192, run `42841141633`, commit `da3c95034e200996a8e7c2a463fdce1796d43de2`: **122 pruebas superadas en 0,35 s**; pasos `Tests`, `Build XMind Desktop smoke test` y `Upload XMind smoke test` correctos. Entorno: GitHub Actions, Ubuntu, Python 3.12.16. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42841141633
- **CI posterior a la actualización documental:** #194, run `42841327165`, commit `844bf4a71a016dc1f85946eca987a2e5810e39bb`: workflow completo correcto, incluidos `Tests`, generación y publicación del artefacto smoke. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42841327165
- **Correcciones durante CI:** #182–#183 detectaron una comprobación residual que seguía rechazando todo `Topic.layout` y una expectativa antigua para la raíz; #191 reveló cuatro defectos en pruebas negativas (mensajes esperados y selección de nota/enlace). Se corrigieron antes de #192.
- **Commits relevantes:** soporte de tipos/layout/enlaces `5731ca68215772129581ef5cc056c69ef58fb322`, `c90c29b26fff7d7bf8cec916d944dca5ba56c98f`; pruebas `403f51743b8bb40115fa3c219e219be0de93f823`, `ff3f1326acd7949fbc94492dba976c6acc1259d3`, `0de66bbfceaa1fee45f7546c16dfe97c4651921f`, `2a473e1c6860744dbb8abeac31b19aa1bf2ecb28`, `da3c95034e200996a8e7c2a463fdce1796d43de2`; documentación `d7418cf996ed7469689aa5650439937c6380014f`, `5840eb67e2c96ddcc6bc47c20fd7a60de1cb06f9`, `fb62dd8d413b71462df8ff0376286c653acd1dae`, `a1f327e2d3b566f0c18625bafe1ca44a28e6970c`.
- **No ejecutado:** Ruff, ejecución local Windows y apertura/guardado manual del artefacto en XMind Desktop. La generación y subida del smoke test CI no acredita compatibilidad visual en la aplicación.

### Tarea 9 — Integración de la exportación XMind en la CLI

- **Estado:** completada y verificada en GitHub Actions.
- **Archivos:** `src/xmind_md/cli.py`, `tests/test_cli.py`, `README.md`, `docs/development.md`.
- **Interfaz:** la extensión `.json` o `.xmind` determina el formato por defecto. Se añade `--format json|xmind` para selección explícita; las extensiones conocidas deben concordar con el formato, y las extensiones no reconocidas requieren `--format`.
- **Flujo canónico:** la CLI lee mediante `parse_file_ir()`. Para XMind resuelve siempre los estilos (con configuración externa opcional) antes de llamar a `write_xmind()`. Para JSON mantiene el comportamiento previo: resuelve estilos solo cuando se proporciona `--styles`, y serializa con `write_json()`. No se altera la API legacy.
- **Errores:** formatos ambiguos o incompatibles, archivos de entrada/configuración ausentes o inválidos, referencias de estilos inexistentes y capacidades IR no exportables producen un mensaje `Error:` en stderr y código de salida 2.
- **Pruebas CLI:** 9 pruebas cubren exportación JSON, generación de un ZIP XMind e inspección de `content.json`, formato explícito, incompatibilidad de extensión, extensión desconocida, entrada inexistente, ayuda, resumen IR no soportado y conjunto de estilos inexistente.
- **Correcciones durante CI:** las ejecuciones #200 y #202 detectaron fixtures de prueba que no activaban realmente las rutas negativas (escapes de nueva línea y construcciones Markdown no adecuadas). Se corrigieron los fixtures y se volvió a ejecutar la suite completa; no se ocultaron esos fallos intermedios.
- **CI final:** #203, run `42842555229`, commit `1995076eee2e5108c37320c7a9df9be21745f5de`: **131 pruebas superadas en 0,45 s**. Pasaron `Tests`, `Build XMind Desktop smoke test` y `Upload XMind smoke test`. Entorno: GitHub Actions, Ubuntu, Python 3.12.16. https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42842555229
- **Commits principales:** CLI `acf87ed9914509e8e81f2bb5d148386c0709d929`; primera batería de pruebas `fd61af356d5df023ce46665221f068baa2f23307`; ampliación y correcciones de pruebas `c062e7d68fc28563fd837bbb0668481e410a56a4`, `456ff64df9a8efd5c554245c8248f27eac6def33`, `36c81c4c2d1d28183ec5431cb3ba432f25770056`, `1995076eee2e5108c37320c7a9df9be21745f5de`; README `9c150d6e6d6eb8156646ad38871ec931c84cff54`; guía de desarrollo `4f189ec5615162f14f58d9f6c12998b069002641`.
- **Limitaciones que permanecen:** el perfil XMind sigue rechazando las capacidades no implementadas en el adaptador. El smoke test acredita generación y estructura automatizada; la comprobación manual posterior en XMind Desktop 26.05.01107 se registra en la tarea 10. Ruff y ejecución local Windows siguen pendientes.

## 7. Auditoría integral y reconstrucción desde cero (2026-11-10)

### Alcance auditado

- Árbol Git completo de `main`: 59 entradas, sin truncamiento.
- Documentación de arquitectura, catálogo de archivos, IR, migración, gramática, estilos, motor XMind, adaptador, integración, CLI y prompt maestro.
- Código fuente de parser, puente IR, entidades/validación, estilos, adaptadores, CLI y script smoke.
- Pruebas de CLI, parser, IR, esquema, estilos, adaptadores e integración.
- `pyproject.toml`, workflow GitHub Actions y ejecuciones CI recientes.

### Resultado técnico

- Las tareas 1–9 están completadas según el código, pruebas y registro histórico.
- El flujo canónico está integrado hasta CLI: Markdown → parser → IR 1.0.0 → resolución de estilos cuando procede → adaptador JSON/XMind.
- El modelo legacy `src/xmind_md/model.py` y las API legacy de parsing/estilos siguen presentes; no eliminarlos sin auditar consumidores y compatibilidad.
- La exportación XMind es un perfil parcial. La matriz de `docs/xmind-adapter.md` debe considerarse junto al código y las pruebas; no equivale a compatibilidad visual completa.
- El workflow #205 (run `42842726726`, commit `f99273d3f93a95648457aa183bb4ec55bb99fda8`) terminó correctamente. El log de Tests registra **131 passed in 0.52s**. Se completaron también descarga del fixture, generación y publicación del artefacto.
- No hay evidencia de ejecución local Windows ni Ruff. La apertura, inspección, guardado y reapertura manual del fixture sí quedaron confirmados por el usuario en XMind Desktop 26.05.01107.

### Discrepancias documentales detectadas (pendientes de tarea 13)

1. `docs/architecture.md`: todavía afirma que CLI no exporta XMind y su lista de extensiones está desfasada.
2. `docs/ir-migration-plan.md`: presenta la integración CLI como pendiente y mantiene criterios de migración antiguos.
3. `docs/style-system.md`: encabezado declara pendiente la resolución completa, aunque el resolutor IR está implementado y probado.
4. `docs/xmind-engine-evaluation.md`: conserva el estado inicial; dice que faltan `controlPoints`, temas detached/callout y CLI.
5. `docs/xmind-adapter.md`: su sección de limitaciones contradice la matriz posterior sobre detached/callout; hay que reconciliar texto y código.
6. `docs/file-reference.md`: describe `model.py` como modelo principal y no refleja adecuadamente los módulos IR, puente y nuevas pruebas.
7. `docs/development-status.md`: había un literal `\\n` en el bloque de CI, y la cabecera no recogía el último commit/documentación ni CI #205. Esta auditoría corrige el registro operativo, pero no pretende cerrar toda la tarea 13.
8. El prompt anterior contenía afirmaciones obsoletas sobre CLI, adaptador y fases. Se ha reescrito como prompt autónomo con estado actual, arquitectura, pruebas, limitaciones, ruta de trabajo y discrepancias pendientes.

### Prompt maestro actualizado

- Archivo: `docs/ai-reconstruction-prompt.md`.
- Commit inicial de reconstrucción: `30f9a690ebe631d3d5ddbbd353fd488df29a6384`.
- Commit de sincronización tras auditar el artefacto y la tarea 10: `ab968fc1078512713f149cade4d415e03efb154c`.
- Contenido: propósito, protocolo de trabajo, arquitectura, contrato IR, parser/gramática, estilos, adaptadores, CLI, estructura de repositorio, instalación/pruebas, estado al 2026-11-10, hoja de ruta, discrepancias conocidas y reglas para retomar desde cero.

### Tarea 10 — Prueba manual en XMind Desktop

- **Estado: completada**, tras confirmación del usuario el 2026-11-10.
- **Entorno:** Windows, XMind Desktop versión `26.05.01107`.
- **Resultado:** el usuario descargó el fixture permanente, lo abrió y confirmó que se visualizaba correctamente; comprobó el tema central `XMind MD · Prueba de apertura`, ramas `Rama A` y `Rama B`, subtema `Detalle de rama A`, nota desplegable `Nota de prueba asociada a la rama A.`, etiqueta `IMPORTANTE`, marcador de prioridad `1` y relación `Relación de prueba`.
- **Persistencia:** el usuario confirmó que guardó el archivo, lo cerró y volvió a abrirlo sin problemas; indicó que «va perfecto».
- **Alcance:** esta prueba acredita el fixture y los elementos enumerados en esta versión de XMind; no certifica compatibilidad universal ni todas las capacidades de XMind.

### Artefacto y fixture de la tarea 10

- Artefacto obtenido de CI #205: `xmind-desktop-smoke-test`, artifact ID `13775958163`, expiración GitHub `2026-11-24T15:17:14Z`.
- Archivo interno: `xmind-md-smoke-test.xmind`.
- Tamaño: 3.299 bytes.
- SHA-256: `9caa73f02ecd6e082202663ada77bd4079ef8bde7da835509d00c314c045acd3`.
- Verificación automatizada local del artefacto original: `unzip -t` correcto; entradas `mimetype`, `content.json`, `metadata.json`, `manifest.json` y `Thumbnails/thumbnail.png` legibles.
- Para evitar depender de la caducidad de Actions, se añadió una copia permanente y equivalente del libro en `tests/fixtures/xmind/xmind-md-smoke-test.xmind`, junto con `tests/fixtures/xmind/README.md`. El ZIP se recomprimió; conserva los archivos internos del libro.
- Commit de incorporación: `a1cf99861c819d9f148a7c7a3d779df6a95fc394`.
- Tamaño del fixture versionado: 1.852 bytes. SHA-256: `bc7a3a79f055ee9d9afe3ad976adb303ec04ee117a9f92d9137c2f5018cf2c33`.
- Enlace directo al archivo: https://raw.githubusercontent.com/PabloGonzalezRuiz/xmind-md/main/tests/fixtures/xmind/xmind-md-smoke-test.xmind
- Esta verificación **no** sustituye XMind Desktop. La tarea permanece en curso hasta que el usuario abra el archivo, inspeccione los elementos, guarde una copia y confirme el resultado.

## 8. Estado de la tarea 11 y próxima tarea

### Tarea 11 — Auditoría y verificación de GitHub Actions

**Estado: completada el 2026-11-10.** El usuario decidió aplazar cualquier instalación o ejecución local en Windows hasta que el proyecto funcione desde GitHub. No se ha instalado ni modificado software en su equipo.

**Auditoría del workflow vigente** (.github/workflows/ci.yml):

- Disparadores: push, pull_request y workflow_dispatch.
- Único entorno: ubuntu-latest; no hay matriz Windows/Linux.
- Versión fijada: Python 3.12.
- Instalación: python -m pip install -e ".[dev]".
- Dependencias de desarrollo instaladas: pytest, Ruff y jsonschema.
- Comprobaciones ejecutadas: descarga de fixture XMind de referencia, pytest, generación del XMind smoke test y subida del artefacto.
- No se ejecutan ruff check ni ruff format --check.
- No se verifica todavía el comportamiento del paquete en un runner Windows.

**Evidencia consultada:**

- CI #209, run 42843815047, commit 1fd131cc16786093dba00e09fd551f299a439761.
- Job tests: estado completed, conclusión success.
- Pasos Install, Download XMind reference fixture, Tests, Build XMind Desktop smoke test y Upload XMind smoke test: todos correctos.
- Log de pytest: **131 passed in 0.37s**.
- Entorno: GitHub-hosted Linux, Python 3.12.16.
- URL: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42843815047

**Conclusión:** la ruta de instalación, pruebas y generación del artefacto funciona en el runner Linux de GitHub. Esto no acredita compatibilidad con Windows ni calidad de lint; esas comprobaciones aún no se ejecutan. Las advertencias deprecatorias de Node.js 20 corresponden a las versiones de las acciones GitHub utilizadas, no a fallos de pytest.

**Decisión del usuario:** aplazar la instalación local y las pruebas en su ordenador Windows hasta que el flujo de GitHub esté suficientemente completo. No solicitar comandos locales en las siguientes fases.

### Tarea 12 — Completar CI, Ruff y comprobaciones automáticas

**Estado: en curso; primera modificación del workflow publicada.**

- Autorización del usuario recibida el 2026-11-10.
- Commit de implementación inicial: `509fd41869429526c6a903e3a3bdc2f2507a2be9` (`ci: add Ruff and Windows/Linux test matrix`).
- Archivo modificado: `.github/workflows/ci.yml`.
- Se añadió una matriz `ubuntu-latest` y `windows-latest`, ambos con Python 3.12.
- Se añadieron `python -m ruff check src tests` y `python -m ruff format --check src tests`.
- Se sustituyó el paso de descarga basado en `mkdir`/`curl` por una descarga con `urllib` desde Python, para evitar diferencias entre shells de Linux y PowerShell.
- Los artefactos usan nombres diferenciados por sistema operativo para evitar colisiones entre los jobs de matriz.
- **Validación pendiente:** no se dispone aún de una lectura verificable del run generado por este commit; por tanto, no se afirma que Ruff, pytest ni Windows hayan pasado. Hay que inspeccionar el workflow y corregir cualquier fallo antes de cerrar la tarea.



Alcance propuesto:

1. Incorporar ruff check src tests al workflow.
2. Incorporar ruff format --check src tests.
3. Ejecutar CI, corregir los problemas reales de lint/formato con cambios acotados y repetir el workflow.
4. Evaluar e incorporar una matriz de runners Linux y Windows, manteniendo Python 3.12, para comprobar la compatibilidad multiplataforma directamente en GitHub Actions.
5. Revisar que la descarga del fixture y la generación del artefacto funcionen en ambos sistemas; adaptar pasos de shell si fuera necesario.
6. Registrar resultados exactos, versiones y posibles limitaciones.

**Criterio de cierre:** workflow verde en Linux y Windows con pruebas, lint y comprobación de formato; artefacto XMind generado y publicado correctamente en el entorno previsto. No se considerará verificada la ejecución Windows hasta que un runner Windows termine correctamente.

**Tarea 13 — Sincronizar README y documentación técnica.** Resolver las discrepancias de la auditoría enumeradas en esta misma documentación.

**Tarea 14 — Auditoría final y publicación estable.** Revisar código, contratos, pruebas, dependencias/licencias, seguridad de entradas, reproducibilidad, empaquetado, versionado y documentación antes de decidir si procede publicar una versión estable.

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


## 7. Auditoría de continuidad — 2026-11-11

### 7.1 Revisión del repositorio

- Rama de referencia: `main`.
- Último commit observado tras la remediación documental: `a9f6ee85da395b6176d43cd8578c9cc74441d6c2` (`docs: update reconstruction prompt with Ruff remediation`).
- Cambio de workflow: `509fd41869429526c6a903e3a3bdc2f2507a2be9` (`ci: add Ruff and Windows/Linux test matrix`).
- El workflow actual define runners Ubuntu y Windows con Python 3.12; instala `.[dev]`; ejecuta Ruff lint, Ruff format, descarga el fixture XMind, pytest, generación del smoke y subida de artefactos con nombres por sistema operativo.
- Los commits de workflow y estado se han localizado en GitHub. El conector disponible no permite listar ejecuciones push recientes; `fetch_commit_workflow_runs` solo devuelve ejecuciones asociadas a pull requests y devolvió listas vacías para los commits examinados. Por tanto, el resultado de la nueva matriz queda **sin verificar**, no fallido ni superado.
- Run inicial aportado por el usuario: `42977948292` (https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42977948292). Los dos jobs fallaron en Ruff antes de pytest.
- Diagnóstico exacto de Ruff: 9 incidencias en total, repartidas en importaciones sin ordenar, `SIM102`, `F821` (`Any` no definido), `UP037`, `FURB188` y `F401`.
- Correcciones publicadas: `a7225b5` (import Any), `ab05615` (anotación recursiva), `c2aff0d` (removeprefix), `2b005f9` (import no usado), `ec18113` (imports test parser), `c66d92a` (condición de layout), `40e875a`, `98c360b` y `2e16371` (separación docstring/imports para reglas I001).
- Los commits de corrección disparan CI por push. Aún no se ha inspeccionado el resultado de la nueva ejecución; lint, formato, pytest y artefactos siguen pendientes de evidencia.

### 7.2 Diferencia entre evidencia histórica y actual

- Evidencia histórica: CI #209, run `42843815047`, commit `1fd131cc16786093dba00e09fd551f299a439761`, 131 pruebas superadas en Linux/Python 3.12.16 y artefacto generado.
- Esa ejecución es anterior a la matriz Windows/Ruff. No sirve como prueba de los nuevos pasos.
- Prueba manual de XMind Desktop: superada por el usuario en Windows con XMind 26.05.01107; el fixture se abrió, inspeccionó, guardó y reabrió.

### 7.3 Documentación pendiente de sincronización

Se mantienen para la tarea 13, sin confundirlos con defectos de ejecución:

1. `README.md`: califica el estado como «prototipo inicial» y presenta advertencias anteriores a la prueba manual ya superada; debe distinguir la validación manual del fixture de la cobertura parcial del adaptador.
2. `docs/architecture.md`: revisar afirmaciones antiguas sobre la CLI y la exportación.
3. `docs/ir-migration-plan.md`: actualizar fases ya terminadas, especialmente integración CLI.
4. `docs/style-system.md`: corregir el encabezado obsoleto que declara pendiente la resolución de estilos.
5. `docs/xmind-engine-evaluation.md`: actualizar estado, capacidades y criterios de verificación a la implementación actual.
6. `docs/xmind-adapter.md`: reconciliar la sección de limitaciones con la matriz (detached/callout y demás capacidades).
7. `docs/file-reference.md`: reflejar IR, puente, CLI y pruebas actuales en lugar de describir `model.py` como modelo principal.
8. `docs/development.md`: documentar la CI actual multiplataforma y dejar claro que la ejecución local es opcional en este flujo.

### 7.4 Hoja de ruta después de esta auditoría

| Orden | Punto | Estado |
|---:|---|---|
| 1 | Verificar la nueva matriz CI/Ruff en GitHub Actions; corregir fallos hasta obtener evidencia verde en Ubuntu y Windows | **En curso** |
| 2 | Sincronizar README y documentación técnica con código, pruebas y estado real | Pendiente |
| 3 | Auditoría final de requisitos, seguridad, dependencias, licencia, reproducibilidad y publicación | Pendiente |

### 7.5 Registro de esta actualización documental

- Estado de desarrollo y auditoría inicial: commit `4911815f7f6251ee5524833d980b9bb66016b262`; remediación y diagnóstico Ruff añadidos en `5f40a1440563d6bae1a6c7054b4f29238c576031`.
- Prompt maestro sincronizado inicialmente: `5b500eb3fb7e5bd647184ef43017a5671cca544f`; actualizado con remediación Ruff en `a9f6ee85da395b6176d43cd8578c9cc74441d6c2`.
- La documentación técnica restante se mantiene como tarea 13 y no se considera sincronizada todavía.

### 7.6 Regla de continuidad inmediata

El siguiente trabajo sigue siendo la tarea 12. Antes de cerrarla hay que obtener el resultado real de ambos jobs, revisar cada paso (Ruff lint, Ruff format, pytest, generación y artefacto) y corregir los fallos encontrados. Si no se puede acceder a los runs desde el conector, solicitar al usuario el enlace o una captura del resultado de GitHub Actions; no pedir ejecución local. Tras cerrar la tarea 12, presentar la evidencia y pedir autorización para la tarea 13.
