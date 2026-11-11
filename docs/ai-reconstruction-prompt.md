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

**Atención:** `docs/style-system.md` contiene un encabezado de estado antiguo («resolución completa pendiente»). El código y las pruebas actuales demuestran que el resolutor IR ya está implementado. No tomar ese encabezado como estado actual; sincronizarlo en la tarea de documentación.

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

CI en `.github/workflows/ci.yml` configura actualmente una matriz `ubuntu-latest` y `windows-latest`, Python 3.12, Ruff lint y formato, pytest, descarga del fixture XMind, generación del smoke y artefactos separados por sistema. Esta configuración está publicada en el commit `509fd41869429526c6a903e3a3bdc2f2507a2be9`; no afirmes que ha pasado hasta consultar los runs reales.

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
- Run inicial aportado por el usuario: `42977948292`; ambos jobs fallaron en Ruff y no llegaron a pytest ni a la generación de artefactos.
- Se corrigieron las nueve incidencias detectadas: imports desordenados, SIM102, F821 (Any), UP037, FURB188 y F401. Commits: `a7225b5`, `ab05615`, `c2aff0d`, `2b005f9`, `ec18113`, `c66d92a`, `40e875a`, `98c360b`, `2e16371`.
- Las correcciones ya están publicadas y han disparado nuevas ejecuciones por push. No se ha podido recuperar desde el conector el ID ni los resultados de esos runs recientes. El resultado de la nueva configuración está **pendiente de verificación**; no declarar pasos superados.
- El usuario ha indicado que no quiere instalar Python ni ejecutar comandos localmente por ahora. La validación se hará en GitHub Actions.

### Hoja de ruta pendiente

12. **CI y Ruff (en curso):** obtener y revisar la ejecución real de ambos runners; corregir fallos hasta que lint, formato, pytest y artefactos pasen en Linux y Windows.
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
