# Prompt maestro de reconstrucción y continuidad — XMind MD

> **Documento autónomo para iniciar el trabajo desde cero con otra IA.** Está redactado como instrucciones de proyecto, no presupone acceso a conversaciones anteriores. Antes de ejecutar cualquier cambio, la IA debe verificar el estado real del repositorio y reconciliar este documento con el código, las pruebas y `docs/development-status.md`.

## PROMPT

Actúa como arquitecto de software y desarrollador Python senior. Vas a auditar, reconstruir, mantener y ampliar **XMind MD**:

- Repositorio: https://github.com/PabloGonzalezRuiz/xmind-md
- Rama de referencia: `main`
- Objetivo: convertir Markdown enriquecido en mapas mentales mediante un modelo intermedio neutral (IR), con exportación JSON y XMind moderno.
- Entorno objetivo: Python >= 3.10; Windows y Linux; GitHub Actions.
- Idioma de código y documentación: español, manteniendo nombres técnicos/API en inglés cuando corresponda.

Este prompt debe bastar para comprender el propósito, la arquitectura, las decisiones, el estado, las pruebas, los riesgos y el trabajo pendiente sin consultar el historial de chat. No presupongas que el contenido de este prompt sigue vigente: compruébalo contra GitHub.

---

## 1. Objetivo funcional

El usuario escribe documentos Markdown enriquecidos que representan mapas mentales. Debe poder controlar:

- Jerarquía y orden de temas.
- Metadatos del mapa y de la hoja.
- Estilos globales, conjuntos reutilizables, herencia y overrides.
- Contenido de temas: párrafos, listas, tablas, código, citas y otros bloques definidos por el IR.
- Anotaciones: notas, etiquetas y marcadores.
- Enlaces, relaciones y, progresivamente, recursos, imágenes, límites, resúmenes y otras capacidades.
- Exportación a JSON IR para inspección y a archivos `.xmind`.

El objetivo a largo plazo es cubrir de forma explícita las capacidades útiles de XMind, pero **no se debe confundir el objetivo final con la cobertura ya implementada**. La gramática Markdown no debe acoplarse a XMind ni a una biblioteca de exportación.

## 2. Protocolo de trabajo obligatorio

El usuario requiere un desarrollo por tareas autorizadas:

1. Auditar el estado real antes de modificar.
2. Mantener una hoja de ruta numerada y verificable.
3. Ejecutar solo la tarea autorizada.
4. Añadir pruebas adecuadas y actualizar la documentación afectada.
5. Registrar archivos, decisiones, commits, entorno, pruebas y limitaciones en `docs/development-status.md`.
6. No declarar una prueba superada sin consultar una ejecución real.
7. No marcar una tarea como completada mientras algún criterio de aceptación siga pendiente.
8. Al terminar una tarea, presentar evidencias y pedir autorización antes de iniciar la siguiente.
9. No avanzar en tareas futuras sin autorización expresa.
10. Si un trabajo depende de una acción del usuario (por ejemplo abrir XMind Desktop en su equipo), preparar el material, indicar los pasos y esperar el resultado; no simular acceso a su escritorio.

No reescribas módulos completos si basta un cambio localizado. No alteres áreas ajenas al alcance autorizado. Si aparecen defectos fuera del alcance, documenta el hallazgo y propón una tarea.

## 3. Arquitectura obligatoria

Flujo principal:

~~~text
Markdown enriquecido
       |
       v
src/xmind_md/parser.py
       |
       v
src/xmind_md/ir_parser.py
       |
       v
Modelo canónico IR 1.0.0
       |
       +------> src/xmind_md/styles.py (resolución de estilos)
       |
       +------> adapters/json_adapter.py
       |
       +------> adapters/xmind_adapter.py
       |
       v
CLI / scripts / GitHub Actions
~~~

Capas y responsabilidades:

1. **Fuente:** Markdown y configuración YAML.
2. **Parser:** reconoce la gramática y produce el modelo de parsing legacy/transitorio.
3. **Puente IR:** transforma el resultado en entidades canónicas IR y ejecuta validación semántica.
4. **IR:** contrato independiente del parser y de los motores de salida.
5. **Resolutor:** carga configuración y materializa estilos en `StyleState.resolved`.
6. **Adaptadores:** serializan el IR sin interpretar Markdown ni resolver estilos.
7. **CLI/automatización:** orquestan las capas y gestionan códigos de salida.

Invariantes:
- El parser no genera archivos XMind ni importa el adaptador.
- El IR no importa PyYAML ni bibliotecas de exportación.
- El adaptador no analiza Markdown ni resuelve estilos.
- Los adaptadores reciben IR canónico.
- El adaptador no modifica el IR.
- Una capacidad no soportada debe rechazarse con diagnóstico; nunca descartarse silenciosamente.
- Un ZIP estructuralmente válido no acredita compatibilidad con XMind Desktop.
- Una misma entrada/configuración debe producir estructura estable; los metadatos de creación pueden depender del instante.

## 4. Contrato IR 1.0.0

Fuentes:
- `docs/ir-specification.md`
- `docs/ir-schema.json` (JSON Schema Draft 2020-12)
- `examples/ir/constitucion.json`
- `src/xmind_md/ir/entities.py`
- `src/xmind_md/ir/validation.py`

Estructura conceptual:

~~~text
MindMap
├── id, title, metadata
├── styles, style_sets, assets
└── sheet
    ├── id, title, metadata, layout
    ├── root_topic
    │   ├── content[]
    │   ├── annotations (notes, labels, markers)
    │   ├── resources, links
    │   ├── style, layout, kind, source
    │   └── children[]
    ├── relationships[]
    ├── boundaries[]
    └── summaries[]
~~~

El modelo Python contiene entidades tipadas para MindMap, Sheet, Topic, ContentBlock, anotaciones (Note, Label, Marker), recursos, Asset, Relationship, Boundary, Summary, SheetLayout y StyleState. Cada entidad relevante implementa serialización `to_dict()`.

La validación semántica comprueba, entre otros aspectos, IDs, estructura del árbol, referencias, tipos, estilos y relaciones. El JSON Schema valida la forma estructural y formatos declarados; no sustituye la validación semántica Python.

Decisiones:
- Un Markdown produce una única hoja y un único tema raíz.
- Todos los temas pertenecen al árbol.
- No hay temas flotantes como raíz independiente del árbol.
- El IR preserva identidad, orden, referencias y procedencia cuando el parser puede determinarla.
- IR 1.0.0 es el contrato canónico; cualquier cambio incompatible exige versionado y migración.

El modelo anterior `src/xmind_md/model.py` se conserva como API legacy. No lo elimines hasta auditar consumidores, compatibilidad y estrategia de retirada.

## 5. Parser y gramática Markdown

Archivos:
- `src/xmind_md/parser.py`
- `src/xmind_md/ir_parser.py`
- `docs/grammar.md`
- `tests/test_parser.py`
- `tests/test_ir_parser.py`

API canónica:
- `parse_markdown_ir(text, source_path=None)`
- `parse_file_ir(path)`

API legacy conservada:
- `parse_markdown()`
- `parse_file()`

La gramática implementada incluye encabezados de nivel 1–6 para jerarquía, front matter YAML y directivas documentadas, bloques de contenido, listas anidadas, tablas, código cercado, citas, separadores, formato inline (negrita, cursiva, tachado y código), enlaces internos `topic:ID`, IDs explícitos y procedencia/rangos de origen para los bloques cubiertos. Los detalles exactos y las restricciones están en `docs/grammar.md`; **ese documento es la referencia normativa para sintaxis**, no este resumen.

No afirmar compatibilidad completa con CommonMark/GFM. No añadir sintaxis nueva sin definir semántica, escapes, errores, casos límite y pruebas.

## 6. Sistema de estilos

Archivos:
- `src/xmind_md/styles.py`
- `config/styles.yaml`
- `docs/style-system.md`
- `tests/test_styles.py`
- `tests/test_ir_styles.py`

El resolutor admite carga YAML segura, conjuntos, herencia por rama, sustitución de conjunto en descendientes, estilos nombrados, overrides locales y fusión recursiva. La cascada IR aplicada por propiedad es:

1. Valores predeterminados del sistema.
2. `metadata.style_defaults`.
3. Conjunto de estilos aplicable.
4. Estilo nombrado.
5. Overrides locales.

La selección global se realiza mediante `metadata.style_set`; el tema puede seleccionar/sustituir con `Topic.style.style_set`. El resultado se escribe en `style.resolved`, sin mutar las definiciones originales. La ruta legacy sigue existiendo por compatibilidad.

El estado vigente de la resolución de estilos se describe en `docs/style-system.md`: la ruta IR 1.0.0 está implementada y probada; la ruta legacy se conserva por compatibilidad y el catálogo de propiedades exportables XMind es parcial.

## 7. Adaptadores y CLI actuales

### JSON

`src/xmind_md/adapters/json_adapter.py` serializa exclusivamente `MindMap.to_dict()` del IR canónico.

### XMind

`src/xmind_md/adapters/xmind_adapter.py` genera un contenedor ZIP moderno con:
- `mimetype` (primera entrada, sin compresión).
- `content.json`.
- `metadata.json`.
- `manifest.json`.
- `Thumbnails/thumbnail.png`.

API:
- `build_xmind_content(mind_map)`
- `write_xmind(mind_map, destination)`

Consume estilos resueltos; crea IDs de salida UUID5 deterministas y traduce las relaciones a referencias de temas. La matriz completa y autoritativa de capacidades está en `docs/xmind-adapter.md`. En términos generales, el perfil actual contempla temas attached/detached/callout, un subconjunto de layout y estilos, notas aplanadas, etiquetas, marcadores, enlaces web/topic/file bajo restricciones y relaciones estructurales. Rechaza expresamente, entre otros, assets/recursos, imágenes/raw/equaciones, boundaries, summaries, tareas, extensiones, estilos no reconocidos y otras estructuras fuera del perfil.

No declares interoperabilidad visual hasta superar la prueba manual con XMind Desktop.

### CLI

`src/xmind_md/cli.py` y `src/xmind_md/__main__.py` permiten:
- Deducir formato por extensión `.json` o `.xmind`.
- Seleccionar `--format json|xmind`.
- Exigir coincidencia entre formato explícito y extensión conocida.
- Usar `--styles` para configuración YAML.
- Generar JSON manteniendo la resolución legacy de estilos solo cuando se proporciona `--styles`.
- Resolver estilos antes de exportar XMind.
- Devolver código 2 y mensaje en stderr ante errores de formato, lectura, configuración o capacidades no exportables.

Ejemplos:

~~~bash
xmind-md examples/constitucion.md --output output/constitucion.json
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.xmind
python -m xmind_md examples/constitucion.md --output output/constitucion.xmind --format xmind
~~~

La ayuda de CLI y las pruebas de `tests/test_cli.py` son la referencia de comportamiento.

## 8. Estructura actual del repositorio

Árbol funcional (verificar siempre el árbol real antes de modificar):

- `.github/workflows/ci.yml`: CI (instalación, fixture externo fijado, pytest, smoke XMind y publicación de artefacto).
- `config/styles.yaml`: estilos de ejemplo.
- `docs/`: arquitectura, catálogo, gramática, estilos, especificación/schema IR, migración, evaluación de motor, adaptador, pruebas de integración, guía de desarrollo, estado y este prompt.
- `examples/constitucion.md`: ejemplo de usuario.
- `examples/ir/constitucion.json`: ejemplo IR validado.
- `examples/xmind-smoke-test.md`: entrada de prueba manual XMind.
- `scripts/create_xmind_smoke.py`: genera el archivo de comprobación.
- `src/xmind_md/parser.py`, `ir_parser.py`, `styles.py`, `cli.py`, `model.py`, `__main__.py`.
- `src/xmind_md/ir/`: entidades y validación.
- `src/xmind_md/adapters/`: adaptadores JSON y XMind.
- `tests/`: pruebas de CLI, parser legacy/IR, esquema, estilos legacy/IR, adaptadores y fixture de integración.
- `pyproject.toml`: paquete, dependencias, entry point y configuración pytest/Ruff.
- `README.md`: presentación, instalación y uso.

Consulta `docs/file-reference.md` para responsabilidades por archivo, teniendo presente que también contiene descripciones legacy que deben sincronizarse.

## 9. Instalación, ejecución y pruebas

Requisitos declarados:
- Python >= 3.10.
- Dependencia de ejecución: PyYAML >= 6.0.
- Dependencias dev: pytest >= 8, Ruff >= 0.5, jsonschema[format] >= 4.22 y < 5.
- Entry point: `xmind-md = xmind_md.cli:main`.

Instalación:

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
~~~

Lint/format:

~~~bash
ruff check src tests
ruff format --check src tests
~~~

CI en `.github/workflows/ci.yml` utiliza exclusivamente `ubuntu-latest`, Python 3.12, Ruff lint y formato, pytest, descarga del fixture XMind, generación del smoke y publicación de un artefacto. La configuración Ubuntu-only se publicó en el commit `41983b75ce45626327d2484e5ddc9b55b9d90929`; no afirmes que ha pasado hasta consultar el run real.

## 10. Estado comprobado a 2026-11-11

La hoja de ruta operativa está en `docs/development-status.md`. Las tareas 1–11 están registradas como completadas:

1. Contrato IR 1.0.0 y plan de migración.
2. Entidades Python y validación semántica IR.
3. Puente parser → IR.
4. Resolutor de estilos IR.
5. Adaptadores JSON/XMind migrados al IR.
6. Validación Draft 2020-12 del esquema y del ejemplo.
7. Auditoría/ampliación/pruebas de la gramática implementada.
8. Ampliación de capacidades del adaptador XMind.
9. Integración XMind en CLI.
10. Prueba manual XMind Desktop: el usuario abrió, inspeccionó, guardó y reabrió el fixture con XMind Desktop Windows 26.05.01107.
11. Auditoría y verificación del workflow histórico de GitHub Actions.

### Evidencia histórica

- CI #209, run `42843815047`, commit `1fd131cc16786093dba00e09fd551f299a439761`: 131 pruebas superadas en 0,37 s; workflow Linux/Python 3.12.16 y artefacto smoke publicado.
- Prueba manual: fixture XMind abierto y guardado en XMind Desktop 26.05.01107; el usuario confirmó que se visualizaban tema central, ramas, subtema, nota, etiqueta, marcador y relación, y que el archivo reabrió correctamente.
- Esta evidencia histórica no acredita la matriz CI nueva.

### Estado de la tarea 12 — CI y Ruff (en curso)

- Commit de workflow: `509fd41869429526c6a903e3a3bdc2f2507a2be9`.
- Commit de registro de implementación: `a6bd54423f5d79d18207e65be809d4be5f5900fe`.
- Workflow: matriz Ubuntu/Windows, Python 3.12, `ruff check src tests`, `ruff format --check src tests`, pytest, generación del smoke XMind y publicación de artefactos diferenciados por sistema.
- Run inicial `42977948292`: ambos jobs fallaron en Ruff con nueve incidencias. Se corrigieron y publicaron.
- Run siguiente `42981097378`: ambos jobs volvieron a fallar en Ruff lint con tres incidencias I001 en `src/xmind_md/adapters/xmind_adapter.py`, `src/xmind_md/ir/validation.py` y `tests/test_xmind_integration.py`. Los pasos posteriores (Ruff format, fixture, pytest, generación XMind y artefactos) quedaron omitidos.
- Se corrigieron esos tres bloques de imports en commits `c03293b31f18fda69a274259a86b1225265fce48`, `80b781ed8a1fcde254d1cfac0d1d80b757c5496b` y `d3f545fcecc0f98d1031f37b1aadcfad6b3f7dda`.
- La ejecución CI posterior a estas correcciones está pendiente de localizar y revisar. No afirmar que lint, formato, pytest ni artefactos han pasado.
- El usuario ha indicado que no quiere instalar Python ni ejecutar comandos localmente por ahora. La validación se hará en GitHub Actions.

### Hoja de ruta pendiente

12. **CI y Ruff (en curso):** run 42981647696 volvió a fallar con tres errores Ruff I001 en ambos runners. Se ha corregido la separación requerida después de from __future__ import annotations en los tres archivos; commits 6a3313c, aa67bf2, 0f3c8fe. Revisar la siguiente ejecución hasta que lint, formato, pytest, generación XMind y artefactos pasen en Linux y Windows.
13. **Sincronización documental:** README, arquitectura, migración IR, estilos, evaluación del motor, adaptador XMind, catálogo de archivos y guía de desarrollo.
14. **Auditoría final y publicación estable:** revisar requisitos, seguridad de entradas, errores, dependencias, licencia, ejemplos, reproducibilidad, documentación y compatibilidad. No publicar como estable hasta satisfacer criterios definidos.

## 11. Auditoría documental conocida

La auditoría del 2026-11-11 confirma estas discrepancias que deben resolverse en la tarea 13:

- `docs/architecture.md`: revisar afirmaciones antiguas sobre la CLI y la exportación XMind.
- `docs/ir-migration-plan.md`: presenta integración CLI y fases de migración como pendientes.
- `docs/style-system.md`: el encabezado declara pendiente la resolución completa, aunque el resolutor IR está implementado y probado.
- `docs/xmind-engine-evaluation.md`: conserva el estado inicial y afirma que faltan capacidades que el adaptador actual ya implementa, además de indicar que CLI y compatibilidad manual están pendientes.
- `docs/xmind-adapter.md`: la sección de limitaciones contradice la matriz sobre temas detached/callout y otras capacidades.
- `docs/file-reference.md`: describe `model.py` como modelo principal y no refleja suficientemente IR, puente, CLI y pruebas actuales.
- `README.md`: estado «prototipo inicial» y advertencias que no distinguen la prueba manual superada de la cobertura parcial del adaptador.
- `docs/development.md`: no refleja todavía la matriz de CI Ubuntu/Windows ni el flujo de validación sin instalación local.
- `docs/development-status.md`: actualizado en esta auditoría; conserva el historial y diferencia CI histórica de la nueva matriz aún no verificada.

La tarea 13 debe corregir estas discrepancias sin borrar el historial. Toda documentación debe diferenciar: implementado, probado estructuralmente, generado en CI, inspeccionado manualmente en aplicación y pendiente.
## 12. Criterios para nuevas capacidades

Antes de implementar una nueva capacidad:
1. Identifica su semántica en Markdown.
2. Define o confirma las entidades/campos IR y su versión.
3. Añade validación estructural y semántica.
4. Implementa conversión desde parser.
5. Implementa resolución si afecta a estilos.
6. Implementa cada adaptador de forma independiente.
7. Define pérdidas/rechazos y errores.
8. Añade pruebas positivas, negativas y de regresión.
9. Actualiza esquema, ejemplos y documentación.
10. Verifica el resultado real en el motor destino cuando sea necesario.

No añadas dependencias de ejecución sin evaluar alternativas, mantenimiento, licencia y beneficio.

## 13. Fuentes de verdad y cómo retomar

Orden para resolver contradicciones:
1. Código actual y pruebas ejecutadas en el commit inspeccionado.
2. Especificación IR y JSON Schema aprobados para el contrato.
3. Documentación técnica específica de la característica.
4. `docs/development-status.md` para secuencia, tareas y evidencias.
5. Este prompt para intención, arquitectura y contexto.
6. Suposiciones: nunca presentarlas como hechos.

Al comenzar una sesión:
1. Consulta rama, SHA actual y estado del repositorio.
2. Lee `docs/development-status.md` y este prompt.
3. Inspecciona el árbol del repositorio.
4. Consulta los documentos específicos de la tarea.
5. Verifica las últimas ejecuciones CI y sus jobs/logs.
6. Comprueba que la autorización del usuario cubre la siguiente tarea.
7. Actualiza este prompt y el estado si descubres discrepancias sustanciales.
8. Continúa solo dentro del alcance autorizado.

Al finalizar una tarea:
- Actualiza `docs/development-status.md`.
- Actualiza este prompt si cambia el estado, la arquitectura o la hoja de ruta.
- Sincroniza los documentos técnicos directamente afectados.
- Registra commits, URLs CI, recuentos, entorno y resultados manuales.
- Deja una siguiente tarea inequívoca y espera autorización.

## FIN DEL PROMPT



## 11.1 Incidencia CI del 2026-11-11: runs 42981647696 y 42982298488

Los runs https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42981647696 y https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42982298488 fallaron en Ubuntu y Windows durante Ruff lint, con tres errores I001 persistentes en `src/xmind_md/adapters/xmind_adapter.py`, `src/xmind_md/ir/validation.py` y `tests/test_xmind_integration.py`.

La inspección de los archivos completos de `main` corrige la interpretación anterior: la línea en blanco después de `from __future__ import annotations` ya era correcta. La causa era una línea vacía adicional entre el último import y la primera asignación de nivel superior (había dos en lugar de una). La corrección mínima publicada elimina solo esa línea sobrante en cada archivo:
- Adaptador: `41aa8b573490b055b2bab96153023dea6aa79940`
- Validación: `2e05cf5aa5478b9e1bd87e87e5ffa54ba6d53cea`
- Test de integración: `ae81408334b7b17678e25b43f5d2cf4fae3625a2`

El run 42982298488 instaló correctamente las dependencias en ambos runners, pero Ruff lint volvió a fallar. Ruff format, pytest, fixture, generación XMind y artefactos no se ejecutaron. La tarea 12 sigue abierta hasta revisar el nuevo run generado por los tres commits más recientes y comprobar todos los pasos en ambos sistemas.


## 14. Decisión CI actualizada — 2026-11-11: solo Ubuntu

Esta sección prevalece sobre las referencias históricas anteriores a una matriz Ubuntu/Windows.

El usuario autorizó simplificar la CI para que GitHub Actions ejecute todas las comprobaciones exclusivamente en Linux. El cambio está publicado en `.github/workflows/ci.yml`, commit `41983b75ce45626327d2484e5ddc9b55b9d90929`.

Configuración vigente:
- `runs-on: ubuntu-latest`; ya no existe matriz de sistemas operativos.
- Un job denominado `Tests (Ubuntu)`.
- Python 3.12.
- Instalación editable con dependencias dev.
- `ruff check src tests`.
- `ruff format --check src tests`.
- Descarga del fixture XMind de referencia.
- `python -m pytest`.
- Generación mediante `python scripts/create_xmind_smoke.py`.
- Publicación de un único artefacto `xmind-desktop-smoke-test`.

Motivo: el archivo `.xmind` generado no depende del sistema operativo que lo crea. La compatibilidad del artefacto con XMind Desktop para Windows se verifica mediante la prueba manual de apertura, inspección, guardado y reapertura que el usuario ya completó. La CI no necesita un runner Windows adicional para ese objetivo.

**No confundir**:
- CI en Ubuntu valida instalación, lint, formato, tests y generación/publicación del archivo.
- La prueba manual en XMind Desktop para Windows valida la interoperabilidad del artefacto con esa aplicación.
- La decisión de quitar Windows de CI no demuestra que el paquete Python funcione nativamente en Windows; simplemente deja de ser un objetivo de la matriz automática actual.

La tarea 12 sigue abierta hasta inspeccionar el run disparado por el commit `41983b75ce45626327d2484e5ddc9b55b9d90929` y comprobar todos los pasos del job Ubuntu. El usuario no desea instalar Python ni ejecutar comandos localmente.

La siguiente acción es consultar el run nuevo cuando esté disponible; no iniciar la tarea 13 hasta que la tarea 12 esté cerrada y el usuario autorice el siguiente punto.


## 15. Consulta automática de ejecuciones GitHub Actions — regla obligatoria

No pedir al usuario que proporcione la URL del run como paso habitual. El endpoint de listado de GitHub REST está disponible a través de la acción genérica de lectura:

`GET https://api.github.com/repos/PabloGonzalezRuiz/xmind-md/actions/runs?branch=main&per_page=10`

Al retomar el proyecto, consultar el listado, seleccionar la ejecución más reciente de `.github/workflows/ci.yml` en `main`, y extraer su `id` y `html_url`. Después consultar jobs, pasos, logs y artefactos con las acciones específicas del conector. Solicitar URL manual únicamente si el endpoint de listado falla o no devuelve la ejecución que se necesita.

### Última ejecución comprobada: 42983466610

- URL: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42983466610
- Commit: `88a62c94d01bbb6d2b90228d6f175ac8bf444cfc`.
- Ubuntu 26.04, Python 3.12.16.
- Install y Ruff lint: success.
- Ruff format: failure; 17 archivos requieren formato, 7 ya estaban formateados.
- Fixture, pytest, generación y artefacto: skipped.
- No hay artefactos.
- Próximo paso dentro de la tarea 12: aplicar formato Ruff a los 17 archivos identificados y repetir CI.

Esta ejecución demuestra que el lint I001 ya pasa en la CI Ubuntu-only. No demuestra todavía que las pruebas ni la generación XMind pasen.


## 16. Requisito obligatorio de Release estable

El usuario ha solicitado expresamente que publiques una Release completa y estable tan pronto como el proyecto esté preparado. Esta publicación forma parte de la tarea final de auditoría y publicación; no debe adelantarse por presión de calendario.

No crear la Release hasta que se cumplan todos estos criterios:
- CI verde en el commit candidato: instalación, Ruff lint, Ruff format, pytest, descarga del fixture, generación del XMind smoke test y subida del artefacto.
- Interoperabilidad comprobada en XMind Desktop mediante apertura, inspección, guardado y reapertura; documentar exactamente qué capacidades se han comprobado.
- Auditoría de funcionalidades y limitaciones reales de parser, IR, estilos, CLI y adaptador; no prometer compatibilidad completa no demostrada.
- README y documentación técnica sincronizados con instalación, uso, sintaxis de entrada, capacidades, limitaciones, dependencias y licencia.
- Revisar el versionado y el empaquetado actuales antes de decidir número de versión. Preparar notas de versión/changelog, etiqueta Git y pasos de instalación reproducibles.
- Publicar GitHub Release con código fuente y solo los paquetes/artefactos de distribución que hayan sido construidos y verificados. No presentar el artefacto de smoke test como paquete de distribución.

La instrucción del usuario autoriza crear la Release cuando estos criterios se cumplan. No hace falta volver a pedir autorización para la publicación final, pero sí hay que informar antes de cualquier decisión técnica irreversible no cubierta por esa autorización. No inventar número de versión ni declarar estabilidad antes de la auditoría.

Estado de partida 2026-11-11: no apto para Release. Run 42983767866, commit `34c0274f5a5f6e80bf65d6c4b55ff895471b5437`: Install y Ruff lint success; Ruff format failure (17 archivos); fixture, pytest, generación y artefacto skipped. La tarea CI permanece abierta.


## Actualización de estado — 2026-11-11: tarea 12 completada

Esta sección es la referencia vigente y prevalece sobre cualquier estado anterior de la tarea 12 en este prompt.

La tarea 12 (CI, Ruff y comprobaciones automáticas) está **COMPLETADA**. El usuario no tuvo que instalar Python ni ejecutar comandos en su equipo: el formateo se realizó en un runner Ubuntu de GitHub Actions.

- Los 17 archivos que requerían formato se corrigieron mediante python -m ruff format src tests.
- Los cambios se integraron en main mediante PR [#1](https://github.com/PabloGonzalezRuiz/xmind-md/pull/1).
- Commit integrado y verificado: 23c3a9b4bcae7159f7c46d217cd489265516588c.
- Se retiró el workflow temporal de autoformateo; no forma parte de la automatización permanente.
- Run CI verde: [42985048305](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985048305).
- Entorno: Ubuntu, Python 3.12.16.
- Ruff lint: success.
- Ruff format: success; el formateador informó que los 24 archivos ya estaban formateados después de aplicar los cambios.
- Descarga del fixture de referencia: success.
- Pytest: **131 passed in 0.53s**.
- Generación del archivo smoke XMind: success.
- Publicación del artefacto xmind-desktop-smoke-test: success (ID 13839211520, 1.332 bytes; SHA-256 7c338dfa36bd345e539eaf9d1dde3e17c31f16db7105ffefce5b6b133271383d).

El job Tests (Ubuntu) y todos sus pasos finalizaron con success. Esto acredita CI y generación del artefacto en ese commit; no amplía por sí solo la cobertura manual de XMind Desktop más allá de los elementos que el usuario ya comprobó.

### Hoja de ruta vigente

12. **CI y Ruff — COMPLETADA.**
13. **Sincronización del README y documentación técnica — PENDIENTE.**
14. **Auditoría final y publicación estable — PENDIENTE.**

Al retomar, consultar primero docs/development-status.md, verificar que main sigue en el commit esperado o en un descendiente y revisar el último run CI. La siguiente tarea a proponer es la 13; esperar autorización explícita antes de empezarla.


## Actualización vigente — 2026-11-11: tarea 13 completada

Esta sección prevalece sobre cualquier estado anterior del prompt que diga que la CLI no exporta XMind, que la interoperabilidad manual está pendiente, que la tarea 12 sigue abierta o que la tarea 13 está pendiente.

La tarea 13 (sincronizar README y documentación técnica) está **COMPLETADA**. Se contrastó la documentación con el código actual y se actualizaron:

- `README.md`: descripción, estado, instalación, CLI JSON/XMind, ejemplo, capacidades, limitaciones, prueba manual y enlaces.
- `docs/architecture.md`: flujo real Markdown → parser → IR → estilos/adaptadores → CLI.
- `docs/development.md`: comandos actuales, CLI y pipeline CI.
- `docs/file-reference.md`: catálogo actualizado de rutas y responsabilidades reales.
- `docs/grammar.md`: estado de subconjunto implementado; no es CommonMark/GFM completo.
- `docs/ir-specification.md`: estado implementado del IR y separación entre IR, parser y adaptador.
- `docs/style-system.md`: resolución implementada, precedencia, herencia y límites de exportación.
- `docs/xmind-adapter.md`: prueba manual completada en XMind Desktop 26.05.01107 y alcance exacto.
- `docs/xmind-engine-evaluation.md`: decisión Python nativa y estado real de implementación.

Código de referencia contrastado: `src/xmind_md/cli.py`, `src/xmind_md/ir_parser.py`, `src/xmind_md/styles.py`, `src/xmind_md/ir/` y `src/xmind_md/adapters/xmind_adapter.py`.

### Estado técnico vigente

- La CLI admite salida JSON y XMind; infiere por extensión o recibe `--format`.
- El IR 1.0.0 es el contrato canónico de los adaptadores.
- El parser implementa un subconjunto de Markdown enriquecido, no CommonMark/GFM completos.
- La resolución de estilos IR implementa defaults, style_defaults, conjunto, estilo nombrado y overrides.
- El adaptador XMind genera ZIP + JSON moderno y rechaza explícitamente capacidades no soportadas; no es un exportador completo de todas las entidades IR.
- El fixture manual se abrió, inspeccionó, guardó y reabrió en XMind Desktop 26.05.01107 para Windows. Solo están acreditados los elementos enumerados en `docs/xmind-integration-tests.md`.
- La CI Ubuntu del commit de tarea 12 pasó: run [42985176851](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985176851), 131 pruebas y artefacto smoke publicado.

El registro de tarea 13 está en `docs/development-status.md`, sección 18. Los cambios documentales posteriores disparan CI; al retomar, verificar el run más reciente del commit vigente.

### Hoja de ruta vigente

12. **CI y Ruff — COMPLETADA.**
13. **Sincronización documental — COMPLETADA.**
14. **Auditoría final y publicación estable — PENDIENTE.**

La siguiente tarea a proponer es la 14. Esperar autorización explícita antes de comenzarla. No publicar la Release hasta auditar versionado, paquete instalable, dependencias, licencia, changelog, artefactos de distribución y CI verde sobre el commit candidato. El usuario ya autorizó la publicación cuando esos criterios se cumplan; no es necesario pedir autorización otra vez para la publicación final, pero sí informar de decisiones irreversibles no cubiertas por ese permiso.


### CI posterior a la sincronización documental

La sincronización documental se validó con GitHub Actions run [42985726802](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985726802), commit `fd2002cac38348162860f8dfc706721febfcf217`: Ubuntu/Python 3.12.16, instalación, Ruff lint, Ruff format, descarga de fixture, pytest (**131 passed in 0.50s**), generación XMind y subida del artefacto, todo success. Artefacto `xmind-desktop-smoke-test`, ID `13838948884`, SHA-256 `7a723811f728e517e0f683a14e5ba514c71caa9c12a75f0d2c842282b59c99a9`.

El resultado confirma que los cambios documentales no han roto la CI. La tarea 13 está cerrada; la siguiente es la tarea 14, pendiente de autorización expresa.


## 14. Continuidad: auditoría de empaquetado/licencia — 2026-11-11

La auditoría inicial de la tarea 14 está registrada en `docs/release-audit.md` y en la sección 19 de `docs/development-status.md`.

Puntos comprobados:
- Paquete Python configurado con setuptools, diseño `src`, metadatos PEP 621, dependencias runtime/dev y entry point CLI.
- Versión `0.1.0` duplicada en `pyproject.toml` y `src/xmind_md/__init__.py`, coincidente en el commit auditado.
- No existe LICENSE/COPYING/NOTICE ni declaración de licencia en metadatos. No elegir ni añadir una licencia sin confirmación expresa del titular.
- Build backend declara `setuptools>=68`; para metadata SPDX PEP 639, PyPA documenta soporte de setuptools desde 77.0.3.
- No hay Releases publicadas.
- La CI #283 está verde, pero instala en editable; no construye wheel/sdist ni prueba instalación desde distribuciones.
- No instalar ni ejecutar Python localmente: validar empaquetado mediante GitHub Actions.

Siguiente paso: obtener la decisión del titular sobre la licencia antes de tocar archivos legales/metadatos. Después, con autorización, añadir build de wheel/sdist y pruebas de instalación limpia en CI. No publicar Release hasta superar esos criterios y cerrar el resto de la auditoría.


## Continuidad — decisión MIT confirmada (2026-11-11)

Esta actualización prevalece sobre las notas históricas que indiquen que la licencia estaba pendiente o no existía.

El titular del proyecto ha elegido MIT y ha indicado el aviso de copyright **Pablo González Ruiz**. Se incorporaron:
- `LICENSE` con MIT y copyright 2026.
- `pyproject.toml`: `license = "MIT"`, `license-files = ["LICENSE"]`, `setuptools>=77.0.3` para soporte PEP 639.
- `docs/license-adoption.md`: decisión y alcance.
- `README.md`: sección de licencia y enlaces.

No cambiar la licencia ni el titular sin instrucción expresa. La licencia MIT no se extiende automáticamente a dependencias, fixtures ni materiales de terceros; auditar sus condiciones antes de distribuir. La versión sigue en 0.1.0 y no hay Release.

Pendiente inmediato: extender GitHub Actions para construir wheel y sdist, inspeccionar que incluyen los metadatos y LICENSE, instalar cada distribución en un entorno limpio y ejecutar una prueba funcional de la CLI. El usuario no desea ejecutar Python localmente. Esperar autorización expresa para iniciar esa siguiente tarea.


### Evidencia CI de la adopción MIT

Run [42986904524](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42986904524), commit `a64921cfdcc49016b5fd8eeb90cb7703ebb5355a`, finalizó success en Ubuntu. Instalación, Ruff lint, Ruff format, fixture, **131 pruebas**, generación XMind y artefacto finalizaron correctamente. El artefacto smoke tiene ID `13840285930` y SHA-256 `24e880172a25dcc52046db2f4978ff8d5dfdc8ebd2548d6890d5ebd551cf6a84`.

La CI solo confirma el flujo de instalación editable actual. Todavía no construye ni instala wheel/sdist.


## 15. Auditoría integral vigente — 2026-11-11

Esta sección prevalece sobre las referencias históricas de este prompt que indiquen que wheel/sdist no se construyen o que su instalación está pendiente.

### Estado comprobado de main

- Commit auditado: `81b514195f1ea9a7bb0225c3353717f29251c615`.
- CI run [42988289597](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42988289597): completed/success.
- Job Tests Ubuntu: Ruff lint/format success; **131 passed in 0.36s**; smoke XMind generado y subido.
- Job Build and install distributions Ubuntu: wheel y sdist construidos; `scripts/verify_distributions.py` confirmó metadatos MIT, LICENSE y módulos esenciales; ambas distribuciones se instalaron en virtualenvs limpios separados y ejecutaron la CLI para producir JSON válido.
- Artefactos: `python-distributions` ID 13839594760 (72.878 bytes; SHA-256 ZIP `9b4a1960284e323fb00e4edaae19e12e00ec69377022a48730b8dd8ffe43ec59`); `xmind-desktop-smoke-test` ID 13840690878 (1.331 bytes; SHA-256 ZIP `e4596bf69bac18c669d709089f4b8eabb0f9daec63e171856cc1e447510b618c`).
- Los hashes identifican ZIPs de artefactos de Actions, no los ficheros individuales wheel/sdist.

### Hallazgos de auditoría

1. El smoke de distribuciones instaladas solo genera JSON; falta probar `.xmind` desde wheel y sdist limpios.
2. El proyecto declara Python >=3.10, pero la CI solo prueba 3.12 en Ubuntu.
3. La versión `0.1.0` está repetida en TOML, paquete y verificador.
4. **Resuelto:** acciones migradas a checkout@v5, setup-python@v6 y upload-artifact@v6; las tres declaran node24.
5. Revisar procedencia/licencias del fixture XMind externo, fixture binario propio, ejemplos y dependencias antes de distribuir.
6. El parser es un subconjunto Markdown propio; el adaptador XMind exporta un perfil parcial y rechaza capacidades no soportadas. La matriz de gramática y adaptador es normativa para las afirmaciones públicas.

### Hoja de ruta de tarea 14

1. **Completada:** smoke XMind desde wheel y sdist instalados; ZIP, MIME, content.json e integridad verificados en CI #42990025087.
2. **Siguiente:** inventariar licencias/procedencia de dependencias, fixtures y ejemplos.
3. **Completada:** matriz CI Python 3.10/3.11/3.12; run #42995180722.
4. **Completada:** migración de acciones CI a Node.js 24; run #42996452355.
5. Unificar/verificar versión y completar metadatos de distribución.
6. Auditar funcionalidad y cobertura; corregir defectos prioritarios.
7. Reconciliar documentación final.
8. Preparar changelog, tag y Release.

### Instrucciones para retomar

1. Leer este prompt, `docs/development-status.md` y `docs/release-audit.md`.
2. Consultar el último run de `main` mediante GitHub REST API, sin pedir URL al usuario salvo que el endpoint falle.
3. Inspeccionar jobs, pasos, logs y artefactos; no inferir resultados.
4. La tarea 1 de la lista anterior está completada y documentada. Presentar resultados y pedir autorización antes de iniciar la tarea 2.
5. Toda comprobación se realiza en GitHub Actions; el usuario no quiere instalar Python localmente.
6. Actualizar status, prompt y documentos afectados al finalizar cada tarea.


### Cierre de la primera tarea

Run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087), commit `9831ae89da6e331219e1edbce71f6415752e2f22`: ambos jobs success; Ruff lint/format success; 131 pruebas superadas; wheel y sdist construidos, verificados e instalados en entornos limpios. Ambos paquetes generaron JSON y XMind; el XMind pasó comprobaciones de ZIP, MIME, orden/compresión, content.json e integridad. Artefactos: `python-distributions` ID 13840773838 y `xmind-desktop-smoke-test` ID 13841725579. No afirmar que se ha repetido la validación visual manual en XMind Desktop.


## 16. Auditoría de licencias/procedencia completada — 2026-11-11

La tarea de inventario de terceros se ejecutó tras autorización del usuario. Leer siempre THIRD_PARTY_NOTICES.md antes de modificar licencias o preparar Release.

Hallazgos registrados:
- PyYAML runtime; pytest/Ruff/jsonschema dev; setuptools/wheel build; build frontend CI: todos con licencia MIT declarada en sus proyectos.
- Acciones actions/checkout, actions/setup-python y actions/upload-artifact: MIT.
- Fixture externo temporal sc0tfree/xmind-mcp/tests/fixture.xmind, commit fijo 6225cbcd3e8fc565bc18e80346699a6e118dd0f7. LICENSE de ese commit declara MIT, Copyright (c) 2026 Henry Prince. No se empaqueta en wheel/sdist.
- Fixture de interoperabilidad propio documentado como generado por CI del proyecto.
- El ejemplo constitucional enlaza BOE y contiene texto normativo. Artículo 13 LPI excluye disposiciones legales y reglamentarias; no inferir que esto cubra otros recursos.
- Hallazgo abierto: examples/constitucion.md referencia assets/escudo.png que no existe en el árbol; el IR JSON de ejemplo también lo describe sin binario.
- No se encontró código fuente vendorizado, imágenes, fuentes tipográficas ni bibliotecas externas en el árbol.
- No hay lockfile ni SBOM; la auditoría no cubre todas las dependencias transitivas y no es asesoramiento jurídico.

La tarea 2 está documentada en THIRD_PARTY_NOTICES.md, docs/license-adoption.md, docs/release-audit.md y docs/development-status.md. La tarea 3 (matriz CI Python 3.10/3.11/3.12) y la tarea 4 (migración de acciones a Node.js 24) están completadas. La siguiente tarea es revisar versionado y metadatos de publicación; pendiente de autorización.


### Evidencia CI posterior a la auditoría de terceros

La documentación consolidada quedó validada en run [42993499900](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42993499900), commit `d31a389a3066ec17d581629b7aa3078c32fcb80e`: ambos jobs success; Ruff lint/format success; 131 pruebas superadas; wheel/sdist construidos, verificados e instalados; generación JSON/XMind desde ambos paquetes correcta. Artefactos: `python-distributions` ID 13842766711 y `xmind-desktop-smoke-test` ID 13843490530.


## Continuidad vigente — matriz de Python autorizada e incorporada (2026-11-11)

El usuario autorizó la siguiente tarea de la auditoría de Release: probar Python 3.10, 3.11 y 3.12. Se modificó `.github/workflows/ci.yml` en commit `db241f04b489de23c429d4189c589859aaffc8fb`.

Configuración:
- El job `tests` ejecuta una matriz `3.10`, `3.11`, `3.12`.
- `fail-fast: false`.
- Nombre del job identifica versión.
- Cada versión publica su propio artefacto smoke con sufijo de versión, evitando colisiones de `upload-artifact@v6`.
- El job de construcción/instalación de wheel y sdist permanece en Python 3.12 y depende del éxito de todos los jobs de test.

**Importante:** Python 3.10 alcanzó EOL el 1 de octubre de 2026. Se prueba porque `pyproject.toml` sigue declarando `requires-python = ">=3.10"`; no significa que reciba ya actualizaciones de seguridad. No cambiar el mínimo de Python en esta tarea. La decisión se tomará durante versionado/metadatos, con evidencia.

Estado al retomar:
- Workflow modificado y commit creado.
- Documentación de estado y prompt de reconstrucción actualizadas con el alcance y criterios.
- La ejecución de GitHub Actions correspondiente al commit de la matriz todavía debe localizarse y validarse.
- Consultar Actions automáticamente por `head_sha = db241f04b489de23c429d4189c589859aaffc8fb`; no pedir URL al usuario.
- Inspeccionar jobs, pasos, logs y artefactos. Si alguna versión falla, diagnosticar y corregir dentro de esta tarea; volver a esperar y comprobar el nuevo run.
- Cerrar la tarea solo cuando pasen las tres versiones y el job de wheel/sdist, documentar evidencia real en `docs/development-status.md` y en este prompt, y validar la actualización documental en CI.
- La migración de acciones de GitHub a Node.js 24 ya está completada y validada; la siguiente tarea propuesta es revisar versionado y metadatos de publicación. No empezarla sin autorización expresa.
- El usuario no quiere instalar Python localmente ni ejecutar comandos en su equipo.

## Cierre de tarea 3 — matriz de compatibilidad Python (2026-11-11)

**Tarea completada y validada.** El usuario autorizó probar Python 3.10, 3.11 y 3.12. Workflow actualizado en commit `db241f04b489de23c429d4189c589859aaffc8fb`.

Run [42995180722](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42995180722): completed/success. Los tres jobs de matriz terminaron success:
- Python 3.10: Ruff lint/format success; **131 passed in 0.54s**; XMind smoke generado y artefacto subido.
- Python 3.11: Ruff lint/format success; **131 passed in 0.39s**; XMind smoke generado y artefacto subido.
- Python 3.12: Ruff lint/format success; **131 passed in 0.37s**; XMind smoke generado y artefacto subido.

El job `Build and install distributions (Ubuntu)` también terminó success: wheel y sdist construidos, verificados, instalados en virtualenvs separados; ambos generaron JSON y XMind; se comprobaron estructura ZIP, MIME, `content.json` e integridad.

Artefactos smoke:
- Python 3.10: ID `13843133705`, digest ZIP `210cb7846d26b3c569ce145fbdcd77223fa3198c342ab642accda4038c54567a`.
- Python 3.11: ID `13843223449`, digest ZIP `4248f5338c3125ae7f2207122ed6469ada1c4600613d2e921373038046edf60c`.
- Python 3.12: ID `13843358216`, digest ZIP `c93c7fb70d11e581035a0222a3ad794b7401b3cb25de63e2d1dc098f6c000054`.
- Distribuciones: ID `13842698603`, digest ZIP `f351a55f4d90b4f98be796caf5e904698f01219028e3fceca93388e0f8ec0b88`.

Los digest corresponden a contenedores ZIP de artefactos Actions, no a los archivos de distribución internos.

**Importante sobre Python 3.10:** está fuera de soporte de seguridad desde 2026-10-01. Se mantiene en matriz porque el proyecto aún declara `requires-python >=3.10`. La matriz acredita compatibilidad técnica observada; no soporte de seguridad. No modificar el mínimo en esta tarea. Evaluarlo durante versionado/metadatos.

La documentación de cierre se ha actualizado en `docs/development-status.md` y `docs/release-audit.md`; este prompt queda sincronizado con la evidencia. Las actualizaciones documentales quedaron validadas en run [42995377488](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42995377488), commit `1e2e6c20fd35bb070c298b80674ef98200f8abf8`: los tres jobs de Python y el job de distribuciones finalizaron success.

**Siguiente tarea propuesta:** revisar versionado y metadatos de publicación. No empezarla hasta recibir autorización expresa.
## Cierre de tarea 4 — migración de acciones a Node.js 24 (2026-11-11)

El usuario autorizó actualizar las acciones de GitHub para eliminar el runtime Node.js 20. En .github/workflows/ci.yml se actualizaron:
- actions/checkout@v4 → @v5.
- actions/setup-python@v5 → @v6.
- actions/upload-artifact@v4 → @v6.

Se inspeccionó el action.yml de cada tag oficial y los tres declaran runs.using: node24.

Run [42996452355](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42996452355), commit e42f0db5fdc943ce060a358293335573eeb28902, completed/success:
- Python 3.10: 131 passed; Ruff correcto.
- Python 3.11: 131 passed; Ruff correcto.
- Python 3.12: 131 passed; Ruff correcto.
- Wheel/sdist construidos, verificados, instalados en entornos limpios y probados generando JSON/XMind.
- Artefactos smoke y distribuciones publicados.
- Los cuatro logs fueron revisados: no aparece el aviso Node.js 20 ni runtime node20.

No se fijaron SHA inmutables; se mantienen tags mayores, y la fijación por SHA queda como mejora separada. El cambio actualiza el runtime interno de las acciones, no la versión de Python instalada para probar el proyecto.

La siguiente tarea de la hoja de ruta es revisar coherencia de versión y metadatos de publicación. Requiere autorización expresa.

## Estado de continuidad actualizado — 2026-11-11, cierre de tarea 5

La tarea 5 de versionado/metadatos está **completada y validada**. No se debe repetir ni volver a proponer como siguiente tarea.

- Versión actual: `0.1.0`; no se ha creado tag ni GitHub Release.
- Fuente única: `src/xmind_md/__init__.py`, constante literal `__version__`.
- `pyproject.toml`: versión dinámica con `[tool.setuptools.dynamic]`, metadatos PEP 621 completos (nombre, descripción, autor, README, Python mínimo, MIT PEP 639, classifiers, URLs, dependencia runtime, extras dev y entry point).
- CLI: `xmind-md --version`.
- Verificador de distribución: obtiene la versión por AST y compara `METADATA` del wheel y `PKG-INFO` canónico del sdist; no debe introducirse otra versión literal en ese script.
- Python mínimo: se conserva `>=3.10`. La matriz de compatibilidad técnica en 3.10/3.11/3.12 está comprobada, pero Python 3.10 está fuera de soporte upstream desde 2026-10-01. No describirlo como versión con mantenimiento de seguridad upstream.
- CI [43002869927](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43002869927), commit `635d8d5bfa42d5b84401f661b7bce3858140dd16`: completed/success; 132 pruebas en cada versión Python; Ruff lint/format; wheel/sdist construidos, verificados, instalados por separado y probados generando JSON/XMind.
- No publicar todavía. Faltan auditoría funcional (tarea 6), sincronización final documental (tarea 7) y changelog/tag/Release (tarea 8).

**Siguiente tarea autorizable en ese momento:** tarea 6 — auditoría funcional final. Se completó posteriormente; consultar el cierre de tarea 6 al final de este documento.


## Estado de continuidad actualizado — cierre de tarea 6 (2026-11-11)

La tarea 6 de auditoría funcional está **completada y validada**. Su informe de hallazgos y limitaciones es `docs/functional-audit.md`; el estado operativo se encuentra en `docs/development-status.md`, sección 27.

### Cambios funcionales realizados

- Parser: `detached` accesible desde Markdown; raíz limitada a `attached`; tipos de `kind` y links validados; markers limitados a escalares; campos globales desconocidos rechazados; extensiones conservadas; texto legacy de listas reparado; barras invertidas en tablas preservadas salvo `\|`; YAML normalizado a tipos JSON y valores no JSON rechazados; author/description validados.
- Puente IR: preserva extensiones de mapa y de relaciones, boundaries y summaries.
- Validación IR: referencias de estilos se resuelven después de cargar los catálogos embebidos/externos en `resolve_styles()`; comprobaciones robustas para títulos, bloques, enlaces y assets.
- Estilos: `config/styles.yaml` migrado al esquema consumido por el resolutor; propiedades de línea de relaciones mapeadas; bold/italic exigen bool.
- XMind/JSON: imágenes inline generan rechazo explícito en vez de pérdida silenciosa; serialización estricta con `allow_nan=False`.
- Ejemplos: añadido asset original `examples/assets/escudo.svg`; Markdown e IR JSON sincronizados; README usa el ejemplo mínimo soportado para exportación XMind; smoke script resuelve el catálogo externo.

### Evidencia

Run [43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888), commit `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`, completed/success:
- Python 3.10, 3.11, 3.12: Ruff lint/format y 161 pruebas por versión.
- XMind smoke generado en los tres jobs.
- Wheel y sdist construidos, verificados e instalados en entornos limpios; CLI genera JSON/XMind desde ambos y la estructura ZIP/MIME/JSON es correcta.
- Artefacto de distribuciones ID `13849240803`, 77.807 bytes, SHA-256 del ZIP de Actions `0d638d960a62909f2c21a1c60687baf4f99e6529f7926eaf7d8e2a4348a048bf`.

### Limitaciones conocidas

El adaptador XMind sigue siendo parcial: no exporta recursos/imágenes, tareas, boundaries, summaries ni extensiones; el tipo de tema `summary` no se exporta; el contenido de bloques se aplana a notas y se pierde parte del formato. El smoke nuevo con estilos pasó CI, pero no se ha inspeccionado manualmente en XMind Desktop. CI solo es Ubuntu. Python 3.10 está fuera de soporte upstream desde 2026-10-01.

No hay tag ni Release; versión actual 0.1.0.

### Siguiente tarea

**Tarea 7 — sincronización documental final.** Revisar y corregir README, grammar.md, ir-specification.md, style-system.md, xmind-adapter.md, development.md, file-reference.md y ejemplos para que reflejen el comportamiento actual. En particular, actualizar esquema de estilos, resolución externa, soporte detached, restricciones YAML/inline images y límites XMind. Esperar autorización expresa antes de iniciarla.


## Estado de continuidad actualizado — cierre de tarea 7 (2026-11-11)

La tarea 7 de sincronización documental está **completada y validada**. El informe de auditoría es `docs/documentation-audit.md`; el estado operativo es la sección 28 de `docs/development-status.md`.

Run [43009183421](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009183421), commit `6cd1c937ee090bc36483be49e7d1f5c740e0926a`, finalizó `completed / success`. Python 3.10/3.11/3.12: Ruff lint/format correctos y **161 pruebas superadas por versión**. Los tres jobs generaron sus XMind smoke. El job de distribuciones construyó wheel/sdist, verificó contenido/licencia, instaló ambos en entornos limpios separados y ejecutó conversiones CLI JSON/XMind; validación ZIP/MIME/JSON correcta.

Artefactos: `python-distributions` ID `13850260351` (78.103 bytes; SHA-256 del ZIP de Actions `c8109d8d722befe2a5ed1bc953af15711b0caaf9d0f2bf9928bc050796b38a0f`); smoke Python 3.10 ID `13849418602`, Python 3.11 ID `13848884276`, Python 3.12 ID `13849314179`.

### Documentación sincronizada

- README: 161 pruebas por versión y matriz Python 3.10/3.11/3.12; ejemplo de exportación XMind correcto.
- Gramática: kinds attached/detached/callout/summary; raíz attached; YAML normalizado a JSON; subconjunto real de Markdown delimitado.
- IR: contrato neutral separado de capacidades parser/exportador; referencias a estilos externos se resuelven tras cargar ambos catálogos.
- Estilos: esquema ejecutable real `style_sets` + `styles`; no utilizar `extends`, `elements`, `applies_to` ni `properties` en la configuración actual; precedencia real documentada.
- XMind: attached/detached/callout soportados; detached exige posición; summary no exportable; enlaces, estilos, pérdidas y rechazos explicitados.
- Desarrollo: CLI de XMind usa el smoke fixture; CI matriz Ubuntu Python 3.10/3.11/3.12; build/install wheel/sdist en Python 3.12.

### Límites que no deben ocultarse

No CommonMark/GFM completo. El adaptador XMind rechaza recursos/imágenes, tareas, boundaries, summaries, extensiones, Topic.kind=summary y propiedades no soportadas; aplana bloques a notas y pierde parte del formato inline. El smoke con estilos aún no se ha inspeccionado manualmente de nuevo en XMind Desktop. CI solo Ubuntu; Python 3.10 está fuera de soporte upstream desde 2026-10-01.

### Siguiente tarea

**Tarea 8 — preparar changelog, fijar la versión final, crear tag y GitHub Release reproducible.** Antes de publicar, ejecutar CI sobre el commit candidato, comprobar artefactos y respetar los criterios de `docs/release-audit.md`. La versión actual sigue siendo 0.1.0 y no existe tag/Release. No iniciar tarea 8 sin autorización expresa del usuario.
