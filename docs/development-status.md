# Estado de desarrollo

> **Documento de seguimiento operativo del proyecto.** Debe actualizarse al terminar cada tarea de desarrollo autorizada y cuando cambie una decisión técnica relevante.

- **Última actualización:** 2026-11-11 (tarea 8, preparación de Release Alpha 0.1.0; publicación bloqueada por inspección manual del smoke candidato)
- **Rama de referencia:** `main`
- **Última prueba manual XMind Desktop:** superada en Windows, XMind 26.05.01107.
- **Commit de incorporación del fixture XMind permanente:** `a1cf99861c819d9f148a7c7a3d779df6a95fc394`.
- **Contrato objetivo:** IR 1.0.0
- **Estado global:** IR 1.0.0 integrado en parser, estilos, adaptadores y CLI; exportación JSON/XMind disponible; fixture anterior comprobado manualmente en XMind Desktop 26.05.01107; wheel y sdist construidos, verificados e instalados en CI. Versionado centralizado en `src/xmind_md/__init__.py`, metadatos PEP 621 dinámicos y CLI `--version`; acciones CI usan Node.js 24. La auditoría funcional corrigió validación/preservación de datos, referencias de estilos externos, configuración de estilos, conversión XMind de imágenes inline, serialización JSON estricta y el asset faltante del ejemplo. CI #43006735888 validó 161 pruebas por versión (Python 3.10/3.11/3.12), Ruff, smoke XMind y wheel/sdist instalados y probados. La tarea 7 está completada; consultar `docs/documentation-audit.md`. Tarea 8 en curso: changelog, notas y workflow de publicación preparados para `0.1.0` Alpha. Tag/Release aún no creados; falta inspección manual del smoke candidato en XMind Desktop y CI verde del commit definitivo.

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
| Auditoría funcional | [functional-audit.md](functional-audit.md) |
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

### 3.5 CLI, pruebas, CI y distribuciones

**Estado: CLI JSON/XMind integrada; CI Ubuntu con Ruff y 131 pruebas; wheel/sdist construidos, inspeccionados, instalados y probados con salidas JSON y XMind.**

- La CLI genera JSON (`.json`) o libros XMind (`.xmind`) desde `parse_file_ir()`; admite `--format` explícito y deducción por extensión.
- La exportación XMind resuelve estilos antes de invocar el adaptador. La salida JSON solo resuelve estilos si se proporciona `--styles`.
- Los errores de entrada, configuración, formato y capacidades XMind no exportables se muestran en stderr y devuelven código 2.
- La CI actual está en `.github/workflows/ci.yml`, solo Ubuntu/Python 3.12. El job Tests instala en editable, ejecuta Ruff, descarga el fixture de referencia, pytest y genera el smoke XMind.
- El job dependiente Build and install distributions construye wheel/sdist, verifica metadatos MIT/archivos esenciales, instala cada distribución en un virtualenv limpio separado y ejecuta CLI para JSON y XMind.
- Run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087), commit `9831ae89da6e331219e1edbce71f6415752e2f22`: ambos jobs success; Ruff lint/format success; **131 passed in 0.48s**; wheel/sdist y CLI JSON/XMind correctos.
- La documentación reconciliada se volvió a validar en run [42990299861](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990299861), commit `a150ed9db79d6b133f3bf7f18f3a5c1f0fadcded`: ambos jobs success; **131 passed in 0.50s**; build, verificación, instalaciones y CLI JSON/XMind success.
- Artefactos del run #42990299861: `python-distributions` ID `13841446896`, 73.390 bytes, SHA-256 del ZIP `38a138fcae1d115499ff11cf1d0db6cddf13c6a88db0316e732b66933373b912`; `xmind-desktop-smoke-test` ID `13841477803`, 1.331 bytes, SHA-256 del ZIP `5a579a93abc118feb3091a579567b59b65f72dd0dc5a0c04abdbd4c5b5bfffbf`.
- El smoke XMind desde distribuciones valida ZIP, MIME, posición y compresión de `mimetype`, `content.json`, tema raíz e integridad. No sustituye la inspección visual manual en XMind Desktop.
- La CI no prueba todavía Python 3.10/3.11 ni Windows. El log de Actions muestra aviso de deprecación Node.js 20 en las versiones de actions actualmente utilizadas; se mantiene como tarea de mejora.
- El usuario no desea instalar ni ejecutar Python localmente; las validaciones se realizan en GitHub Actions.


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
| 12 | Completar CI, Ruff y comprobaciones automáticas | **Completada** | Workflow Ubuntu verde con Ruff, 131 pruebas y generación/publicación del artefacto XMind |
| 13 | Sincronizar README y documentación técnica | **Completada** | README, arquitectura, gramática, IR, estilos, adaptador, evaluación del motor, guía de desarrollo y catálogo alineados con código y evidencias |
| 14 | Auditoría final y publicación estable | **En curso** | Auditoría de terceros, compatibilidad, empaquetado, documentación, versión y CI candidato cerrados; Release reproducible |

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
- Últimos commits de código observados: `c03293b31f18fda69a274259a86b1225265fce48`, `80b781ed8a1fcde254d1cfac0d1d80b757c5496b` y `d3f545fcecc0f98d1031f37b1aadcfad6b3f7dda` (corrección de imports I001).
- Cambio de workflow: `509fd41869429526c6a903e3a3bdc2f2507a2be9` (`ci: add Ruff and Windows/Linux test matrix`).
- El workflow actual define runners Ubuntu y Windows con Python 3.12; instala `.[dev]`; ejecuta Ruff lint, Ruff format, descarga el fixture XMind, pytest, generación del smoke y subida de artefactos con nombres por sistema operativo.
- Los commits de workflow y estado se han localizado en GitHub. El conector disponible no permite listar ejecuciones push recientes; `fetch_commit_workflow_runs` solo devuelve ejecuciones asociadas a pull requests y devolvió listas vacías para los commits examinados. Por tanto, el resultado de la nueva matriz queda **sin verificar**, no fallido ni superado.
- Run inicial aportado por el usuario: `42977948292` (https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42977948292). Los dos jobs fallaron en Ruff antes de pytest.
- Run `42981097378` (https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42981097378): ambos runners fallaron en Ruff lint; quedaron exactamente tres `I001` en `src/xmind_md/adapters/xmind_adapter.py`, `src/xmind_md/ir/validation.py` y `tests/test_xmind_integration.py`. Ruff format, fixture, pytest, generación y artefactos fueron omitidos.
- Se comprobó que las otras incidencias del run anterior habían desaparecido. Se corrigió la agrupación de imports en esos tres archivos mediante los commits `c03293b31f18fda69a274259a86b1225265fce48`, `80b781ed8a1fcde254d1cfac0d1d80b757c5496b` y `d3f545fcecc0f98d1031f37b1aadcfad6b3f7dda`.
- Run 42981647696 (11-11-2026), posterior a c03293b, 80b781e y d3f545f: ambos jobs fallaron en Ruff lint; se repiten exactamente tres I001 en los mismos archivos. Los pasos Ruff format, descarga del fixture, pytest, generación XMind y upload quedaron omitidos; no se generaron artefactos.
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



### 7.7 Diagnóstico y correcciones de los runs 42981647696 y 42982298488

- Run 42981647696: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42981647696
- Run 42982298488: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42982298488
- En ambos runs, los jobs Ubuntu y Windows fallaron en `Ruff lint` con los mismos tres errores I001:
  - `src/xmind_md/adapters/xmind_adapter.py`
  - `src/xmind_md/ir/validation.py`
  - `tests/test_xmind_integration.py`
- La inspección de los archivos reales de `main` permitió corregir el diagnóstico previo: **no faltaba una línea vacía después de `from __future__ import annotations`**; esa separación ya era correcta. El problema era que había dos líneas vacías entre el último import y la primera asignación de nivel superior en cada archivo. Ruff/isort espera una sola línea vacía antes de esas asignaciones.
- Run 42982298488: instalación correcta en ambos runners; Ruff lint falló; Ruff format, descarga del fixture, pytest, generación XMind y subida de artefactos fueron omitidos. No se generaron artefactos.
- Corrección publicada tras el run 42982298488: se eliminó únicamente una línea vacía sobrante en cada archivo, manteniendo intacto el resto del contenido:
  - Adaptador: `41aa8b573490b055b2bab96153023dea6aa79940`
  - Validación IR: `2e05cf5aa5478b9e1bd87e87e5ffa54ba6d53cea`
  - Pruebas de integración: `ae81408334b7b17678e25b43f5d2cf4fae3625a2`
- **Corrección del diagnóstico anterior:** los commits `6a3313c`, `aa67bf2` y `0f3c8fe` añadieron/restauraron la separación tras el future import, pero no resolvieron el I001 porque la causa real estaba al final del bloque de imports. No presentar esa intervención como solución.
- Estado: tarea 12 sigue abierta. Hay que inspeccionar el run disparado por los tres commits correctivos más recientes y comprobar todos los pasos en Ubuntu y Windows. No afirmar que lint, formato, pruebas o artefactos hayan pasado hasta disponer de logs y artefactos verificables.


## 7. Decisión y actualización CI — 2026-11-11: runner exclusivamente Ubuntu

El usuario ha autorizado eliminar Windows de la matriz de GitHub Actions. La CI no necesita ejecutar el mismo conjunto de pruebas en dos sistemas para generar archivos XMind que después se abrirán en XMind Desktop para Windows. El formato de salida es independiente del sistema operativo que lo genera; la interoperabilidad con XMind Desktop se comprueba por separado mediante el fixture abierto, guardado y reabierto manualmente por el usuario.

### Cambio publicado

- Archivo: `.github/workflows/ci.yml`.
- Commit: `41983b75ce45626327d2484e5ddc9b55b9d90929`.
- Mensaje: `ci: run checks only on Ubuntu`.
- Runner: `runs-on: ubuntu-latest`; eliminada la matriz `ubuntu-latest/windows-latest`.
- Nombre del job: `Tests (Ubuntu)`.
- Se mantienen Python 3.12, instalación editable con dependencias de desarrollo, Ruff lint, Ruff format, descarga del fixture de referencia, pytest, generación del smoke XMind y publicación del artefacto `xmind-desktop-smoke-test`.
- Se elimina la duplicación de artefactos por sistema operativo.

### Evidencia y siguiente verificación

El cambio del workflow está publicado en `main`, pero todavía no se ha inspeccionado la ejecución de Actions disparada por este commit. Por tanto, no se afirma que Ruff, formato, pytest, generación ni publicación del artefacto hayan pasado.

Los fallos previos en Windows y Ubuntu siguen siendo parte del historial de diagnóstico Ruff. La decisión actual reduce el ámbito de CI a Ubuntu; no equivale a demostrar compatibilidad de ejecución nativa en Windows. La prueba manual ya registrada sí acredita que el archivo XMind de fixture se abre y conserva los elementos comprobados en XMind Desktop para Windows.

La tarea 12 permanece **en curso** hasta verificar en el nuevo run Ubuntu todos los pasos: Install, Ruff lint, Ruff format, descarga del fixture, Tests, Build XMind Desktop smoke test y Upload XMind smoke test.

### Decisión técnica vigente

Para este proyecto se utilizará exclusivamente `ubuntu-latest` en GitHub Actions. No se instalará ni ejecutará Python localmente durante esta fase. La compatibilidad del artefacto se comprobará con XMind Desktop en Windows, sin mantener un segundo runner Windows en CI.


## 8. Automatización de consulta CI y resultado Ubuntu — 2026-11-11

### No volver a solicitar manualmente la URL de Actions

Se ha comprobado que el conector GitHub permite consultar directamente el listado REST de ejecuciones recientes del repositorio, aunque no exista una acción especializada para listar los runs push recientes.

Consulta operativa:
`GET https://api.github.com/repos/PabloGonzalezRuiz/xmind-md/actions/runs?branch=main&per_page=10`

Procedimiento obligatorio al retomar:
1. Consultar ese endpoint directamente mediante la acción genérica de lectura GitHub.
2. Seleccionar el run más reciente de la rama `main` cuyo `path` sea `.github/workflows/ci.yml`; revisar `head_sha`, `created_at`, `status`, `conclusion` y `html_url`.
3. Consultar sus jobs con `fetch_workflow_run_jobs`.
4. Consultar logs de los jobs no satisfactorios o relevantes con `fetch_workflow_job_logs`.
5. Consultar artefactos con `fetch_workflow_run_artifacts`.
6. Si el listado no está disponible o no devuelve runs, solo entonces pedir al usuario un enlace.

**Regla:** no volver a pedir al usuario la URL de una ejecución cuando el endpoint de listado esté accesible. El usuario no tiene que hacer de intermediario para localizar ejecuciones de CI.

### Run 42983466610 — primera CI Ubuntu-only

- URL: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42983466610
- Commit: `88a62c94d01bbb6d2b90228d6f175ac8bf444cfc`.
- Runner confirmado: Ubuntu 26.04, Python 3.12.16.
- Instalación: correcta.
- Ruff lint: correcto.
- Ruff format: **fallido**.
- El log indica que **17 archivos** de `src`/ `tests` necesitan formato Ruff; 7 ya estaban formateados.
- Descarga fixture, pytest, generación XMind y publicación de artefacto: omitidos por el fallo anterior.
- Artefactos: ninguno.
- Conclusión: el runner Ubuntu-only está funcionando y el problema I001 de Ruff lint está resuelto; la tarea 12 sigue abierta por formato.

### Siguiente acción

Corregir el formato de los 17 archivos señalados por Ruff y volver a ejecutar CI. No marcar la tarea 12 como completada hasta que Ruff lint, Ruff format, fixture, pytest, generación XMind y subida del artefacto estén todos verificados como satisfactorios.


## 9. Objetivo de publicación: primera Release estable

El usuario ha solicitado que, en cuanto el proyecto alcance condiciones suficientes, se genere y publique una Release completa y estable. Esta publicación queda integrada en la tarea final de auditoría y publicación (tarea 14 de la hoja de ruta), no como una versión provisional mientras la CI siga fallando.

Criterios mínimos de salida:
1. CI verde en el commit candidato: instalación, Ruff lint, Ruff format, suite de pruebas, descarga del fixture, generación XMind y publicación del artefacto.
2. Prueba de interoperabilidad con XMind Desktop: apertura, inspección, guardado y reapertura del fichero generado; distinguir lo comprobado de las capacidades aún no verificadas.
3. Auditoría funcional del alcance y limitaciones del parser, IR, estilos, CLI y adaptador XMind; no anunciar compatibilidad total si no está demostrada.
4. Documentación sincronizada: README, instalación, uso de CLI, formato de entrada, capacidades, limitaciones, dependencias y licencia.
5. Metadatos de distribución coherentes: versión única, changelog/notas, etiqueta Git y procedimiento de instalación reproducible.
6. Publicación de una GitHub Release con código fuente y los artefactos binarios/distribuibles que realmente se hayan construido y probado. No adjuntar artefactos de smoke test como si fueran el paquete de distribución.

La versión se elegirá después de auditar el versionado existente y el estado de empaquetado; no fijar número ni declarar estabilidad por adelantado. La publicación queda autorizada por la instrucción expresa del usuario, pero solo cuando se cumplan los criterios anteriores.

Estado a 2026-11-11: **no apto todavía para Release**. El run CI más reciente inspeccionado es 42983767866 (commit `34c0274f5a5f6e80bf65d6c4b55ff895471b5437`): instalación y Ruff lint pasan, Ruff format falla porque 17 archivos requieren formato; pytest, generación y artefacto quedan omitidos. La tarea 12 sigue abierta.


## 17. Cierre de la tarea 12 — Ruff y CI Ubuntu (2026-11-11)

**Estado: COMPLETADA.** Esta sección prevalece sobre las notas anteriores que describían la tarea 12 como pendiente o en curso.

### Corrección aplicada

- Ruff había identificado 17 archivos que no cumplían el formato configurado.
- Se ejecutó el formateador oficial, python -m ruff format src tests, dentro de GitHub Actions (runner Ubuntu), sin requerir instalación ni ejecución local del usuario.
- Los cambios se integraron en main mediante el pull request [#1](https://github.com/PabloGonzalezRuiz/xmind-md/pull/1).
- Commit integrado: 23c3a9b4bcae7159f7c46d217cd489265516588c.
- La ejecución de Ruff informó: **24 files already formatted** después de aplicar el formato.
- El workflow temporal de autoformateo se eliminó del repositorio; no queda como parte de la CI permanente.

### Evidencia de aceptación

- GitHub Actions run [42985048305](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985048305).
- Commit probado: 23c3a9b4bcae7159f7c46d217cd489265516588c.
- Runner: Ubuntu, Python 3.12.16.
- Install: success.
- Ruff lint: success.
- Ruff format: success.
- Descarga del fixture XMind de referencia: success.
- Pytest: **131 passed in 0.53s**.
- Generación del smoke test XMind: success.
- Publicación del artefacto xmind-desktop-smoke-test: success.
- Artefacto ID: 13839211520; tamaño: 1.332 bytes; SHA-256: 7c338dfa36bd345e539eaf9d1dde3e17c31f16db7105ffefce5b6b133271383d; expiración prevista: 2026-11-25.

Todos los pasos del job Tests (Ubuntu) finalizaron con success. No quedan fallos Ruff pendientes en la ejecución de referencia.

### Hoja de ruta actualizada

12. **CI, Ruff y comprobaciones automáticas — COMPLETADA.**
13. **Sincronizar README y documentación técnica — PENDIENTE.**
14. **Auditoría final y publicación estable — PENDIENTE.**

La siguiente tarea autorizable es la 13. No comenzar la tarea 13 hasta recibir autorización explícita del usuario.


## 18. Cierre de la tarea 13 — sincronización documental (2026-11-11)

**Estado: COMPLETADA.** Esta sección prevalece sobre las discrepancias y listas históricas anteriores que describan la tarea 13 como pendiente o indiquen que la CLI no exporta XMind.

### Auditoría y correcciones realizadas

Se contrastaron los documentos con el código actual, especialmente `cli.py`, `ir_parser.py`, `styles.py`, `ir/` y `adapters/xmind_adapter.py`.

Cambios publicados:

- `README.md`: se reescribió el resumen funcional, instalación, CLI JSON/XMind, ejemplo, limitaciones, validación manual y enlaces a documentación.
- `docs/architecture.md`: se actualizó el flujo real Markdown → parser → IR → estilos/adaptadores → CLI, responsabilidades y decisiones vigentes.
- `docs/development.md`: se documentó la CLI real y el pipeline CI Ubuntu con Ruff, fixture, pytest, smoke test y artefacto.
- `docs/file-reference.md`: se reconstruyó el catálogo para reflejar módulos y rutas reales, incluido el puente IR, el modelo legacy, los adaptadores y fixtures.
- `docs/grammar.md`: se corrigió el estado inicial para dejar claro que existe un subconjunto implementado y probado, no compatibilidad completa CommonMark/GFM.
- `docs/ir-specification.md`: se actualizó el estado de implementación y la distinción entre capacidad del IR, gramática y exportación.
- `docs/style-system.md`: se documentó la resolución ya implementada, su precedencia y la diferencia frente al subconjunto de estilos exportable.
- `docs/xmind-adapter.md`: se registró la prueba manual superada en XMind Desktop 26.05.01107 y su alcance limitado.
- `docs/xmind-engine-evaluation.md`: se sincronizó la decisión de serialización Python nativa con la implementación, CI e interoperabilidad manual.

### Evidencias y límites

- CLI real: `src/xmind_md/cli.py` admite JSON y XMind, con formato inferido por extensión o indicado por `--format`.
- Resolución IR: `resolve_ir_styles()` implementa precedencia por propiedad, herencia y overrides.
- Adaptador: genera ZIP + JSON moderno y rechaza características fuera del perfil implementado.
- Fixture manual: apertura, inspección, guardado y reapertura en XMind Desktop 26.05.01107; solo se acreditan los elementos enumerados en `docs/xmind-integration-tests.md`.
- CI funcional de referencia después de la sincronización documental: run [42985726802](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985726802), commit `fd2002cac38348162860f8dfc706721febfcf217`, conclusión success, 131 pruebas superadas y artefacto smoke publicado.
- Cada cambio documental ha disparado la CI configurada. Debe comprobarse el run correspondiente al último commit de documentación antes de cerrar definitivamente la tarea.

### Hoja de ruta vigente

12. **CI y Ruff — COMPLETADA.**
13. **Sincronización del README y documentación técnica — COMPLETADA.**
14. **Auditoría final y publicación estable — PENDIENTE.**

La siguiente tarea es la 14. No iniciarla hasta recibir autorización expresa del usuario. La Release solo se publicará cuando se cumplan los criterios de la sección 9: CI verde en el commit candidato, auditoría de alcance, packaging y licencia, versión/etiqueta reproducibles y artefactos de distribución reales.


### Verificación CI posterior a la sincronización documental

- Run: [42985726802](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985726802), workflow CI #281.
- Commit probado: `fd2002cac38348162860f8dfc706721febfcf217`.
- Runner: Ubuntu, Python 3.12.16.
- Install, Ruff lint, Ruff format, descarga fixture, pytest, generación XMind y subida de artefacto: todos los pasos success.
- Pytest: **131 passed in 0.50s**.
- Artefacto: `xmind-desktop-smoke-test`, ID `13838948884`, tamaño 1.333 bytes, SHA-256 `7a723811f728e517e0f683a14e5ba514c71caa9c12a75f0d2c842282b59c99a9`.
- Conclusión del run: success.

Esta ejecución valida la documentación sincronizada en ese commit y confirma que los cambios documentales no han roto la CI. La Release sigue pendiente de la tarea 14.


## 19. Tarea 14 — Auditoría inicial de empaquetado y licencia (2026-11-11)

**Estado:** primera auditoría completada; no se ha modificado el código ni se ha publicado una licencia.

- Informe detallado: [docs/release-audit.md](release-audit.md).
- Commit auditado: `dd16f626353b36cf3a9b1f15a4001d3c3ad93601`.
- `pyproject.toml` declara setuptools, diseño `src`, descubrimiento de paquetes, Python `>=3.10`, PyYAML, extras de desarrollo, README y entry point `xmind-md`.
- La versión `0.1.0` coincide entre `pyproject.toml` y `src/xmind_md/__init__.py`.
- No hay archivo LICENSE/COPYING/NOTICE ni metadatos de licencia. La elección queda pendiente de confirmación del titular; no inferir una licencia por la visibilidad pública del repositorio.
- La configuración de build usa `setuptools>=68`. Si se elige una licencia con metadata SPDX PEP 639, la guía actual de PyPA indica soporte de setuptools desde 77.0.3; revisar y elevar el mínimo.
- No hay GitHub Releases publicadas.
- CI #283, run `42985816448`, commit `dd16f626353b36cf3a9b1f15a4001d3c3ad93601`: job Ubuntu success; Install, Ruff lint, Ruff format, descarga de fixture, Tests, generación XMind y Upload artifact success. Artefacto de 1.331 bytes, SHA-256 `6d4a3ee6533744496d6693e1f9b9668478684e97ad67a0aafa9da58b5ecffcb0`.
- La CI instala en modo editable y no construye wheel/sdist. La construcción, instalación limpia y prueba de la distribución son pendientes.
- No se ha instalado ni ejecutado Python en el equipo del usuario.

**Siguiente paso bloqueado por decisión:** confirmar la licencia deseada antes de modificar los metadatos o añadir el texto legal. Después se podrá implementar la prueba de construcción e instalación de wheel/sdist en GitHub Actions, con autorización para ese siguiente punto.


## 20. Adopción de licencia MIT — 2026-11-11

Esta sección prevalece sobre la sección 19 y cualquier referencia anterior que indique que la licencia está pendiente o ausente.

El usuario ha elegido expresamente MIT como opción de menor fricción práctica y ha indicado el titular que debe aparecer: **Pablo González Ruiz**.

Cambios publicados en `main`:
- `LICENSE`: texto estándar MIT con `Copyright (c) 2026 Pablo González Ruiz`. Commit `b2cb8ae2f4bf9a130699fed7cf714d808475e901`.
- `pyproject.toml`: `license = "MIT"`, `license-files = ["LICENSE"]` y build requirement `setuptools>=77.0.3` para metadatos PEP 639. Commit `7a1c7a60aab31d94329f80d5302cee5b53ef6e23`.
- `docs/license-adoption.md`: decisión, alcance, condiciones y cautelas sobre materiales de terceros. Commit `52eda912895cdde8e7838a9a6b58cd262f6cdfcb`.
- `README.md`: sección de licencia y enlaces a la documentación. Commit `c85109dff2ef99f82d5c3749f114eb858f8f0b3b`.

La licencia del repositorio no relicencia automáticamente dependencias, fixtures ni materiales de terceros. Antes de distribuir debe verificarse que el titular puede licenciar bajo MIT todos los materiales propios incluidos.

**Validación pendiente:** CI debe procesar los metadatos PEP 639, construir wheel y sdist, verificar que ambos contienen el archivo de licencia e instalar/probar las distribuciones en entornos limpios. No se ha publicado Release ni cambiado la versión 0.1.0.

**Siguiente punto propuesto:** ampliar GitHub Actions para construir y validar wheel/sdist, sin ejecutar instalaciones locales. Esperar autorización antes de iniciar ese trabajo.


### CI posterior a la adopción MIT

Run [42986904524](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42986904524), commit `a64921cfdcc49016b5fd8eeb90cb7703ebb5355a`: job Ubuntu y todos los pasos success. La instalación con los nuevos metadatos MIT/setuptools, Ruff lint, Ruff format, descarga del fixture, pytest (**131 passed in 0.52s**), generación XMind y subida del artefacto terminaron correctamente. Artefacto `xmind-desktop-smoke-test`, ID `13840285930`, 1.331 bytes, SHA-256 `24e880172a25dcc52046db2f4978ff8d5dfdc8ebd2548d6890d5ebd551cf6a84`.

Esta CI confirma que los metadatos de licencia no rompen la instalación editable ni el pipeline actual. **No** construye ni inspecciona wheel/sdist; esa validación sigue pendiente.


## 21. Auditoría integral y validación de distribuciones — 2026-11-11

Esta sección prevalece sobre los estados anteriores de las secciones históricas que indicaban que wheel/sdist no se construían o que su validación estaba pendiente.

### 21.1 Evidencia CI confirmada

Run [42988289597](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42988289597), commit `81b514195f1ea9a7bb0225c3353717f29251c615`, finalizó `completed / success`.

- `Tests (Ubuntu)`: success; Ruff lint y format success; fixture de referencia descargado; **131 passed in 0.36s**; smoke XMind generado y artefacto subido.
- `Build and install distributions (Ubuntu)`: success.
- Build: `xmind_md-0.1.0-py3-none-any.whl` y `xmind_md-0.1.0.tar.gz`.
- Verificador: comprobó nombre, versión, `License-Expression: MIT`, LICENSE y módulos/archivos esenciales en ambos formatos.
- Wheel y sdist: instalados en entornos virtuales limpios independientes; ambos ejecutaron la CLI y generaron JSON válido.
- Artefacto `python-distributions`: ID `13839594760`, 72.878 bytes, SHA-256 del ZIP `9b4a1960284e323fb00e4edaae19e12e00ec69377022a48730b8dd8ffe43ec59`.
- Artefacto `xmind-desktop-smoke-test`: ID `13840690878`, 1.331 bytes, SHA-256 del ZIP `e4596bf69bac18c669d709089f4b8eabb0f9daec63e171856cc1e447510b618c`.

Los hashes son de los ZIP de artefactos de Actions, no de los paquetes individuales. La prueba CLI de wheel/sdist solo cubre salida JSON; no se ha probado todavía la salida XMind desde esas instalaciones limpias.

### 21.2 Auditoría transversal: hallazgos

1. El parser implementa un subconjunto propio, no CommonMark/GFM completo; la matriz de `docs/grammar.md` debe prevalecer sobre la especificación aspiracional.
2. El modelo legacy `src/xmind_md/model.py` y la API legacy siguen existiendo junto al IR canónico; no retirarlos sin auditoría de compatibilidad.
3. El adaptador XMind es parcial y rechaza recursos/imágenes, tareas, boundaries, summaries y extensiones, entre otros casos.
4. El fixture manual se comprobó en XMind Desktop 26.05.01107, pero esa prueba no valida todas las capacidades ni el artefacto generado por cada commit.
5. `requires-python >=3.10`, pero CI solo ejecuta Python 3.12 sobre Ubuntu.
6. `0.1.0` está duplicada en `pyproject.toml`, `src/xmind_md/__init__.py` y `scripts/verify_distributions.py`.
7. **Resuelto:** el aviso de Node.js 20 se eliminó migrando a `actions/checkout@v5`, `actions/setup-python@v6` y `actions/upload-artifact@v6`, todos con `runs.using: node24`; run #42996452355.
8. El inventario de procedencia y licencias está documentado en THIRD_PARTY_NOTICES.md; no es un SBOM exhaustivo de dependencias transitivas.
9. La MIT está presente en el repositorio y en las distribuciones; no se extiende automáticamente a componentes de terceros.

### 21.3 Hoja de ruta pendiente

1. **Smoke XMind desde wheel y sdist instalados — COMPLETADA.** Run #42990025087 y revalidación #42990429514; ambos paquetes generaron JSON y XMind desde entornos limpios.
2. **Auditoría de terceros — COMPLETADA como inventario técnico.** THIRD_PARTY_NOTICES.md registra licencias/origen; siguen abiertas la referencia de imagen inexistente y el inventario exhaustivo de transitivas.
3. **Completada:** matriz CI Python 3.10, 3.11 y 3.12; run #42995180722.
4. **Completada:** migrar acciones GitHub a Node.js 24; run #42996452355.
5. Resolver fuente única/coherencia de versión y metadatos públicos de distribución.
6. Completar auditoría funcional de parser, IR, estilos, CLI y adaptador; corregir defectos de prioridad de publicación.
7. Revisar de nuevo todos los documentos y ejemplos contra código y evidencias.
8. Preparar changelog, tag, artefactos finales y GitHub Release estable.

### 21.4 Procedimiento y límites

El usuario no desea instalaciones ni ejecuciones Python locales. Toda validación se realizará en GitHub Actions. Se mantiene la regla de no pedir autorización para correcciones o repeticiones dentro de una tarea ya autorizada; detenerse y pedir permiso antes de iniciar la tarea siguiente.

La documentación de continuidad se ha reconciliado con el resultado de empaquetado, la auditoría de terceros, la matriz Python y la migración de acciones a Node.js 24. La siguiente tarea pendiente es revisar versionado y metadatos de publicación.


## 22. Cierre de tarea 1 de la auditoría integral — 2026-11-11

**Tarea completada:** añadir y validar generación XMind desde las distribuciones wheel y sdist instaladas en entornos limpios.

- Workflow modificado: `.github/workflows/ci.yml`; commit `9831ae89da6e331219e1edbce71f6415752e2f22`.
- Run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087): completed/success.
- `Tests (Ubuntu)`: success; Ruff lint/format success; **131 passed in 0.48s**; fixture y smoke XMind publicados.
- `Build and install distributions (Ubuntu)`: success; wheel y sdist construidos y verificados; instalación limpia de ambos; conversión CLI JSON y XMind desde ambos paquetes.
- Comprobaciones XMind: ZIP íntegro, `mimetype` primero y sin compresión, MIME `application/vnd.xmind.workbook`, `content.json` con tema raíz `Package smoke test`, `testzip() is None`.
- Artefacto `python-distributions`: ID `13840773838`, 73.210 bytes, SHA-256 del ZIP `eb6a4f8235544b66106615734791605eed540ad0eb98f39d6af0ebf3fb5d6c3a`.
- Artefacto `xmind-desktop-smoke-test`: ID `13841725579`, 1.331 bytes, SHA-256 del ZIP `ee794ec21589f37d59d85c4f25f519d2f45c547ba7f8dcb5eee1aa5f733f7c65`.

**Límite:** el smoke comprueba la estructura del libro generado desde las distribuciones, no su apertura visual en XMind Desktop. La prueba manual anterior sigue acreditando el fixture y las funciones inspeccionadas en XMind Desktop 26.05.01107.

Siguiente tarea propuesta: auditoría de procedencia/licencias de dependencias, fixtures y ejemplos. No iniciarla sin autorización expresa del usuario.


## 23. Auditoría de licencias y procedencia de terceros — 2026-11-11

**Estado: inventario técnico completado; limitaciones identificadas y documentadas.**

- Nuevo documento: [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
- Dependencia runtime declarada: PyYAML, licencia MIT según el proyecto de origen.
- Dependencias de desarrollo: pytest, Ruff y jsonschema, licencia MIT declarada por sus proyectos.
- Build: setuptools, wheel y build, MIT.
- Acciones CI: actions/checkout, actions/setup-python y actions/upload-artifact, MIT.
- Fixture externo de CI: sc0tfree/xmind-mcp, archivo tests/fixture.xmind en revisión fija 6225cbcd3e8fc565bc18e80346699a6e118dd0f7. El LICENSE de esa revisión declara MIT y Copyright (c) 2026 Henry Prince. El archivo se descarga temporalmente y no está incluido en wheel/sdist.
- Fixture propio: tests/fixtures/xmind/xmind-md-smoke-test.xmind; README documenta generación por CI propia y checksum.
- Ejemplos: examples/xmind-smoke-test.md es contenido de prueba propio según su contenido. examples/constitucion.md referencia texto normativo y BOE; artículo 13 LPI excluye disposiciones legales/reglamentarias y actos públicos. No se extiende esa observación a imágenes o material editorial.
- Hallazgo: examples/constitucion.md referencia assets/escudo.png, pero el archivo no existe en el repositorio. El JSON de ejemplo también describe ese recurso sin incorporar el binario.
- No se han detectado bibliotecas, tipografías, imágenes o directorios de código vendorizado en el árbol actual.
- Limitación: el inventario no es un SBOM exhaustivo. No existe lockfile y no se han resuelto ni enumerado todas las dependencias transitivas del extra jsonschema[format] y de las herramientas.

No se ha detectado una incompatibilidad evidente entre MIT y las dependencias directas/herramientas inventariadas. No se emite certificación jurídica ni garantía de titularidad completa.

La hoja de ruta sigue con: (3) matriz de Python **completada**; (4) actualización de actions, (5) versionado, (6) auditoría funcional, (7) sincronización final y (8) release. El recurso assets/escudo.png deberá corregirse en la auditoría funcional o de ejemplos antes de Release.


**Nota de actualización:** el encabezado y el estado de las secciones históricas 21.x se interpretan a la luz de las secciones 22 y 23, que registran el cierre de las tareas 1 y 2 y prevalecen sobre los estados anteriores.


### 23.1 Validación CI de la documentación de auditoría

La versión documental consolidada quedó validada en run [42993499900](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42993499900), commit `d31a389a3066ec17d581629b7aa3078c32fcb80e`.

- Estado: completed / success.
- Jobs Tests (Ubuntu) y Build and install distributions (Ubuntu): success.
- Ruff lint/format: success.
- Pytest: **131 passed in 0.39s**.
- Build de wheel y sdist: success.
- Verificación de metadatos MIT y contenido: success.
- Instalación limpia de wheel/sdist y conversión CLI JSON/XMind desde ambos: success.
- Artefacto `python-distributions`: ID `13842766711`, 73.605 bytes, SHA-256 ZIP `e6490d4d8e80a94f7fbd97afe56e534a4f98d256107e503cc9d27bf97726b41b`.
- Artefacto `xmind-desktop-smoke-test`: ID `13843490530`, 1.333 bytes, SHA-256 ZIP `d1fc50796fd95e350b2d2869a0a5281c0f8c3c5eb416c84490ca36522966f9ba`.

Esta ejecución valida el commit de documentación del catálogo de archivos, que incluye los documentos de auditoría y el inventario THIRD_PARTY_NOTICES.md.


## 24. Matriz de compatibilidad Python — 2026-11-11

**Estado: configuración incorporada; validación de GitHub Actions pendiente.**

Tras autorización del usuario, se modificó `.github/workflows/ci.yml` para que el job `tests` utilice una matriz de versiones:

- Python 3.10
- Python 3.11
- Python 3.12

La matriz usa `fail-fast: false` para que un fallo en una versión no cancele las otras. El nombre de cada job identifica la versión de Python. El artefacto smoke de cada ejecución se publica con un nombre único (`xmind-desktop-smoke-test-py3.10`, `...py3.11`, `...py3.12`) para evitar colisiones entre ejecuciones paralelas. El job `build-distributions` conserva Python 3.12 y depende de que terminen correctamente todos los jobs de pruebas de la matriz.

### Consideración de ciclo de vida

Python 3.10 alcanzó el fin de soporte el 1 de octubre de 2026. Se conserva en esta matriz porque el proyecto declara actualmente `requires-python = ">=3.10"` y la tarea autorizada consiste en comprobar esa promesa existente. La matriz verifica compatibilidad técnica, pero no implica que 3.10 siga recibiendo actualizaciones de seguridad. La decisión de elevar el mínimo de Python se revisará en la tarea de versionado/metadatos; no modificar `requires-python` dentro de esta tarea sin evidencia y decisión documentada.

### Criterios de cierre

1. Los tres jobs de pruebas (3.10, 3.11 y 3.12) finalizan correctamente.
2. En cada versión pasan instalación, Ruff lint/format, descarga del fixture, pytest y generación del XMind smoke.
3. Se generan tres artefactos con nombres distintos.
4. El job de wheel/sdist sigue construyendo, verificando e instalando ambas distribuciones y probando CLI JSON/XMind.
5. Actualizar esta sección con el ID, commit, resultado, número de pruebas y artefactos reales del run validado.

No iniciar la siguiente tarea de la hoja de ruta hasta cerrar esta validación y obtener autorización del usuario.

### 24.1 Cierre y evidencia CI — tarea completada

**Estado: COMPLETADA.** Run [42995180722](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42995180722), commit `db241f04b489de23c429d4189c589859aaffc8fb`, finalizó `completed / success`.

Jobs:
- `Tests (Ubuntu / Python 3.10)`: success; instalación, Ruff lint, Ruff format, descarga del fixture, pytest (**131 passed in 0.54s**), generación XMind y subida de artefacto.
- `Tests (Ubuntu / Python 3.11)`: success; mismas etapas; **131 passed in 0.39s**.
- `Tests (Ubuntu / Python 3.12)`: success; mismas etapas; **131 passed in 0.37s**.
- `Build and install distributions (Ubuntu)`: success. Construyó wheel y sdist 0.1.0, verificó contenido/licencia, instaló cada distribución en un entorno virtual limpio independiente y generó JSON y XMind desde ambas. Se comprobaron ZIP, MIME, `content.json` e integridad del XMind generado.

Artefactos publicados:
- `xmind-desktop-smoke-test-py3.10`: ID `13843133705`, 1.330 bytes, SHA-256 ZIP `210cb7846d26b3c569ce145fbdcd77223fa3198c342ab642accda4038c54567a`.
- `xmind-desktop-smoke-test-py3.11`: ID `13843223449`, 1.331 bytes, SHA-256 ZIP `4248f5338c3125ae7f2207122ed6469ada1c4600613d2e921373038046edf60c`.
- `xmind-desktop-smoke-test-py3.12`: ID `13843358216`, 1.331 bytes, SHA-256 ZIP `c93c7fb70d11e581035a0222a3ad794b7401b3cb25de63e2d1dc098f6c000054`.
- `python-distributions`: ID `13842698603`, 73.554 bytes, SHA-256 ZIP `f351a55f4d90b4f98be796caf5e904698f01219028e3fceca93388e0f8ec0b88`.

Los hashes son de los ZIP de artefactos de GitHub Actions, no de los archivos wheel/sdist individuales. La prueba funcional de wheel/sdist se ejecutó en Python 3.12; la matriz 3.10/3.11/3.12 valida la instalación editable y la suite de pruebas en esas versiones. No se debe afirmar que wheel/sdist se instalaron en las tres versiones.

**Conclusión:** la promesa técnica actual `requires-python >=3.10` ha pasado la suite en las tres versiones declaradas por la tarea. Python 3.10 está fuera de soporte de seguridad desde el 1 de octubre de 2026; esta matriz confirma compatibilidad observada, no soporte de seguridad. La decisión sobre elevar el mínimo debe abordarse en la tarea de versionado/metadatos.

La migración de acciones de GitHub a Node.js 24 está completada y validada; la siguiente tarea de la auditoría es revisar versionado y metadatos de publicación. No iniciar esa tarea sin autorización expresa del usuario.
## 25. Migración de acciones GitHub Actions a Node.js 24 — 2026-11-11

**Estado: COMPLETADA Y VALIDADA.**

GitHub retiró Node.js 20 de los runners el 23 de septiembre de 2026. La recomendación oficial para quienes usan acciones JavaScript es actualizar a versiones que declaren node24. Se consultaron las referencias oficiales y se verificó el action.yml de cada versión seleccionada.

Cambios en .github/workflows/ci.yml:
- actions/checkout@v4 → actions/checkout@v5.
- actions/setup-python@v5 → actions/setup-python@v6.
- actions/upload-artifact@v4 → actions/upload-artifact@v6.

Verificación previa: las tres versiones seleccionadas declaran runs.using: node24.

Las versiones elegidas mantienen las interfaces usadas por el workflow. No se modificó el Python instalado por setup-python; el cambio afecta al runtime interno de las acciones JavaScript.

### Evidencia de CI

Run [42996452355](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42996452355), commit e42f0db5fdc943ce060a358293335573eeb28902: **completed / success**.

- Python 3.10: Ruff correcto; 131 pruebas superadas.
- Python 3.11: Ruff correcto; 131 pruebas superadas.
- Python 3.12: Ruff correcto; 131 pruebas superadas.
- Build/install de wheel y sdist: correcto; ambas distribuciones generaron JSON y XMind.
- Se publicaron los tres artefactos XMind smoke y python-distributions.
- Inspección de los cuatro logs: no se encontró aviso Node.js 20, node20 ni advertencia de runtime de acciones. Los avisos genéricos de Git/configuración no corresponden al runtime JavaScript.

Artefactos del run:
- xmind-desktop-smoke-test-py3.10: ID 13843574011.
- xmind-desktop-smoke-test-py3.11: ID 13843124343.
- xmind-desktop-smoke-test-py3.12: ID 13843997547.
- python-distributions: ID 13843737659.

No se han fijado SHA inmutables en este cambio; el workflow sigue usando tags mayores. La mejora de reproducibilidad/cadena de suministro queda separada de esta tarea.

**Siguiente tarea propuesta:** resolver la coherencia de versión y metadatos de publicación. Requiere autorización expresa del usuario.

## 26. Tarea 5 — coherencia de versión y metadatos de publicación (2026-11-11)

**Estado: COMPLETADA Y VALIDADA.**

### Decisiones

- Se mantiene la versión actual **0.1.0**. Esta tarea revisó la coherencia del versionado; no era la tarea de preparar el changelog, crear un tag ni publicar la Release. No se ha creado tag ni Release.
- La única fuente de versión es la asignación literal `__version__` en `src/xmind_md/__init__.py`.
- `pyproject.toml` declara `dynamic = ["version"]` y `[tool.setuptools.dynamic].version = { attr = "xmind_md.__version__" }`; setuptools deriva de ahí la versión PEP 621 del wheel y sdist.
- Se mantiene `requires-python = ">=3.10"` porque la suite ha comprobado compatibilidad técnica en Python 3.10, 3.11 y 3.12. Python 3.10 está fuera de soporte upstream desde 2026-10-01; esto se documenta como límite del runtime, no como recomendación de seguridad ni garantía de actualizaciones upstream. No se ha elevado el mínimo en esta tarea.
- Se añadieron metadatos públicos: autor, descripción, README, licencia SPDX MIT, ficheros de licencia, clasificadores de estado Alpha/plataformas/versiones Python y URLs de proyecto/documentación/issues.
- Se añadió `xmind-md --version`, que consulta la misma constante `__version__`.
- `scripts/verify_distributions.py` extrae la versión de la constante mediante AST y la compara con `METADATA` del wheel y el `PKG-INFO` canónico del sdist. Ya no contiene una versión esperada codificada a mano.
- Se añadió una prueba de CLI para `--version`.

### Evidencia CI

Run [43002869927](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43002869927), commit `635d8d5bfa42d5b84401f661b7bce3858140dd16`, finalizó **completed / success**.

- Python 3.10: Ruff lint/format y **132 pruebas superadas**.
- Python 3.11: Ruff lint/format y **132 pruebas superadas**.
- Python 3.12: Ruff lint/format y **132 pruebas superadas**.
- Build de wheel y sdist: success.
- Verificador: comprobó nombre, versión derivada, licencia y contenido en ambos artefactos.
- Wheel y sdist: instalados en entornos limpios separados; cada uno ejecutó CLI Markdown → JSON y Markdown → XMind; los XMind generados pasaron la validación ZIP/MIME/JSON.
- Artefacto `python-distributions`: ID `13846567777`, tamaño 74.823 bytes, SHA-256 del ZIP del artefacto `d3a4997bb167c40f5e63811d52bb990f31cd9d10f9467385a5c8b27df22c6c40`.
- Artefactos XMind smoke: Python 3.10 ID `13846996841`; Python 3.11 ID `13846927390`; Python 3.12 ID `13845764996`.

El hash anterior identifica el ZIP de GitHub Actions que contiene las distribuciones, no el hash de cada wheel/sdist.

### Incidencias durante la validación

Las primeras ejecuciones detectaron, sucesivamente, una sección TOML mal ubicada, un clasificador de licencia obsoleto bajo PEP 639, un orden de imports no conforme con Ruff y la presencia de dos archivos `PKG-INFO` en el sdist (el canónico y el de egg-info). Se corrigieron dentro de esta tarea. El verificador selecciona ahora el `PKG-INFO` canónico; la ejecución final indicada arriba quedó completamente verde.

**Siguiente tarea propuesta en ese momento:** tarea 6, auditoría funcional final. Se completó posteriormente; consultar la sección 27.


## 27. Tarea 6 — auditoría funcional de parser, IR, estilos, CLI y adaptador XMind (2026-11-11)

**Estado: COMPLETADA Y VALIDADA.**

La auditoría funcional detallada, con hallazgos, correcciones, limitaciones y criterios pendientes, se registra en [functional-audit.md](functional-audit.md). Principales correcciones:

- Parser: soporte `detached`, validación segura de kinds/links/markers, rechazo de campos globales desconocidos, preservación de extensiones, reconstrucción del texto legacy de listas, conservación de barras invertidas en tablas y normalización YAML a tipos JSON seguros.
- Puente IR: preservación de extensiones de mapa, relaciones, boundaries y summaries.
- Validación IR: las referencias a estilos externos se resuelven en `resolve_styles()`, después de cargar catálogos; se reforzaron comprobaciones de tipos para títulos, bloques, enlaces y assets.
- Estilos: migrado `config/styles.yaml` al formato realmente soportado; mapeados `line.color/width/pattern` de relaciones; `text.bold/italic` requieren booleanos reales.
- XMind: imágenes inline se rechazan explícitamente en vez de perderse como texto alternativo; serialización JSON estricta con `allow_nan=False`.
- Ejemplos: añadido `examples/assets/escudo.svg`; Markdown e IR JSON actualizados; el comando XMind de README usa el ejemplo de humo compatible; el script de smoke resuelve el catálogo externo.
- Pruebas de regresión añadidas para estos casos y para entradas IR malformadas.

### Evidencia CI

Run [43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888), commit `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`, finalizó **completed / success**.

- Python 3.10, 3.11 y 3.12: Ruff lint/format correcto y **161 pruebas superadas por versión**.
- Los tres jobs generaron el artefacto XMind smoke.
- Wheel y sdist construidos, verificados, instalados en entornos limpios separados y probados con CLI Markdown → JSON/XMind; los XMind pasaron las comprobaciones ZIP/MIME/JSON.
- Artefacto `python-distributions`: ID `13849240803`, tamaño 77.807 bytes, digest SHA-256 del ZIP de Actions `0d638d960a62909f2c21a1c60687baf4f99e6529f7926eaf7d8e2a4348a048bf`.

### Limitaciones y siguiente paso

El adaptador XMind continúa siendo parcial: no exporta imágenes/recursos, tareas, boundaries, summaries ni extensiones; el contenido se aplana a notas y `summary` como tipo de tema no se exporta. El nuevo smoke con estilos pasó CI, pero no se ha vuelto a inspeccionar manualmente en XMind Desktop. La matriz CI es Ubuntu, no Windows.

**Siguiente tarea autorizable: tarea 7 — sincronización documental final.** Revisar README, gramática, IR, estilos, matriz XMind, guía de desarrollo y catálogo frente a la implementación real. No comenzar sin autorización expresa del usuario.


## 28. Tarea 7 — sincronización documental final (2026-11-11)

**Estado: COMPLETADA Y VALIDADA.**

Se han auditado y sincronizado README, gramática, IR, sistema de estilos, adaptador XMind, guía de desarrollo, arquitectura, plan histórico de migración IR, evaluación del motor XMind, guía de integración, adopción de licencia y catálogo de archivos. El informe detallado es [documentation-audit.md](documentation-audit.md).

Cambios relevantes:
- README actualizado a 161 pruebas por versión y matriz Python 3.10/3.11/3.12; comando XMind corregido para usar `examples/xmind-smoke-test.md`.
- Gramática: cuatro kinds IR, raíz attached, detached con posición para exportar; YAML JSON-compatible y limitaciones de Markdown documentadas.
- IR: se distingue representación neutral, subconjunto parser y perfil de salida; referencias de estilos se resuelven tras cargar catálogos embebidos/externos.
- Estilos: ejemplos y esquema YAML actualizados a `style_sets` y `styles`; se retira como formato ejecutable el esquema obsoleto `extends/elements/applies_to/properties`; cascada real documentada.
- Adaptador: contradicción resuelta; attached/detached/callout exportables, detached requiere coordenadas; summary no exportable; se aclaran enlaces, estilos y pérdidas.
- Guía de desarrollo: ejemplos CLI corregidos y workflow actualizado a la matriz real; wheel/sdist se prueban en Python 3.12.
- Se ha creado [documentation-audit.md](documentation-audit.md) como registro reproducible de los cambios y límites que deben mantenerse visibles.

Run [43009183421](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009183421), commit `6cd1c937ee090bc36483be49e7d1f5c740e0926a`, finalizó `completed / success`. Python 3.10/3.11/3.12: Ruff lint/format correctos y **161 pruebas superadas por versión**. Los tres jobs generaron sus XMind smoke. El job de distribuciones construyó wheel/sdist, verificó contenido/licencia, instaló ambos en entornos limpios separados y ejecutó conversiones CLI JSON/XMind; validación ZIP/MIME/JSON correcta.

Artefactos: `python-distributions` ID `13850260351` (78.103 bytes; SHA-256 del ZIP de Actions `c8109d8d722befe2a5ed1bc953af15711b0caaf9d0f2bf9928bc050796b38a0f`); smoke Python 3.10 ID `13849418602`, Python 3.11 ID `13848884276`, Python 3.12 ID `13849314179`.

Se conservan explícitamente las limitaciones: no CommonMark/GFM completo; no recursos/imágenes, tareas, boundaries, summaries, extensiones ni Topic.kind=summary en XMind; bloques aplanados a notas; smoke nuevo no reabierto manualmente en Desktop; CI Ubuntu sin evidencia Windows; Python 3.10 fuera de soporte upstream.

**Siguiente tarea:** tarea 8 — changelog, decisión final de versión, tag y GitHub Release. No iniciarla sin autorización expresa del usuario.


## 29. Tarea 8 — preparación de primera publicación (2026-11-11)

**Estado: PREPARACIÓN COMPLETADA; PUBLICACIÓN BLOQUEADA POR VERIFICACIÓN MANUAL.**

### Decisión de versión

- Se conserva `0.1.0`, ya definida como fuente única en `src/xmind_md/__init__.py` y leída dinámicamente por setuptools.
- Se publica como **Alpha / pre-1.0**, no como estable: el clasificador del paquete es Alpha y el adaptador XMind mantiene limitaciones funcionales documentadas.
- Tag previsto: `v0.1.0`.

### Artefactos documentales y automatización

- `CHANGELOG.md`: entrada 0.1.0 Alpha, capacidades, correcciones, validación y limitaciones.
- `docs/releases/v0.1.0.md`: notas destinadas a GitHub Release.
- `.github/workflows/release.yml`: workflow manual que solo publica desde `main`, exige confirmación de inspección del smoke en XMind Desktop, requiere una CI exitosa para el mismo commit, comprueba versión/tag no existente, construye y verifica wheel/sdist y crea tag/Release con los dos artefactos.
- README, catálogo y `THIRD_PARTY_NOTICES.md` sincronizados; la referencia histórica rota a `escudo.png` queda resuelta. Se conserva el límite de SBOM transitivo no exhaustivo.

La CI de preparación [43011780314](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43011780314), commit `12e876f02a87ffa954292310f089fd9a81345496`, finalizó `completed / success`: 161 pruebas por versión en Python 3.10/3.11/3.12, Ruff lint/format, tres smoke XMind y build/verificación/instalación limpia de wheel y sdist con conversiones CLI JSON/XMind. Artefacto `python-distributions` ID `13851276208`; smoke Python 3.12 ID `13850228137`.

### Puerta pendiente

No ejecutar el workflow de publicación hasta que el usuario abra, guarde y vuelva a abrir en XMind Desktop el smoke generado desde el commit candidato final y confirme que se visualiza correctamente. Después, CI debe estar verde en ese mismo SHA. El workflow exige explícitamente esa confirmación y no permite publicar desde otra rama.

El tag y la Release todavía no existen. No describir `0.1.0` como publicada ni como estable hasta que GitHub confirme la creación de ambos.
