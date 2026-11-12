# Catálogo de archivos

Este documento identifica los principales archivos versionados y la responsabilidad de cada uno. Se mantiene alineado con el árbol real del repositorio; para el estado de tareas y evidencias consultar [development-status.md](development-status.md).

## Raíz

| Archivo | Responsabilidad |
|---|---|
| `README.md` | Presentación, capacidades, instalación y uso de la CLI. |
| `CHANGELOG.md` | Historial de cambios y alcance de las versiones publicadas. |
| `LICENSE` | Licencia MIT del código propio del proyecto. |
| `THIRD_PARTY_NOTICES.md` | Inventario de dependencias, acciones CI, fixtures y procedencia de materiales de terceros. |
| `pyproject.toml` | Metadatos/versión del paquete, dependencias, entry point y configuración de pytest/Ruff. |
| `.gitignore` | Exclusión de entornos, cachés y salidas generadas. |

## Código: `src/xmind_md/`

| Archivo o directorio | Responsabilidad |
|---|---|
| `__init__.py` | Publica `__version__`; debe coincidir con `pyproject.toml`. |
| `__main__.py` | Permite ejecutar el paquete con `python -m xmind_md`. |
| `model.py` | Modelo legacy conservado por compatibilidad; aislado del parsing IR canónico. |
| `parser.py` | Analiza el subconjunto Markdown enriquecido y produce el AST sintáctico temporal. |
| `syntax.py` | Tipos AST temporales `DocumentSyntax` y `TopicSyntax`. |
| `ir_builder.py` | Construye directamente el IR 1.0.0 desde el AST. |
| `ir_parser.py` | Fachada canónica `parse_markdown_ir()` / `parse_file_ir()`; actualmente produce IR 1.0.0. |
| `legacy_adapter.py` | Proyecta el AST al modelo legacy para las API antiguas. |
| `styles.py` | Carga YAML y resuelve estilos IR; fachada de compatibilidad para objetos antiguos. |
| `legacy_styles.py` | Resolución de estilos del modelo legacy, aislada de la ruta IR. |
| `cli.py` | Coordina parsing, resolución de estilos y exportación JSON/XMind. |
| `ir/` | Entidades, serialización y validación de los contratos neutrales IR 1.0.0/1.1.0. |
| `adapters/json_adapter.py` | Serializa el modelo IR a JSON. |
| `adapters/xmind_adapter.py` | Genera libros XMind modernos ZIP + JSON desde IR y valida el perfil soportado. |

### Responsabilidades que no deben mezclarse

- Parser: no genera archivos XMind ni contiene reglas de serialización del motor.
- IR: no importa bibliotecas externas de exportación.
- Resolutor: materializa propiedades neutrales en `style.resolved`.
- Adaptador: no interpreta Markdown ni ejecuta la cascada de estilos.
- CLI: orquesta las capas; no debe duplicar lógica de parser/adaptador.

## Configuración

| Archivo | Función |
|---|---|
| `config/styles.yaml` | Ejemplo de conjuntos y definiciones de estilos neutrales. |

## Documentación: `docs/`

| Archivo | Función |
|---|---|
| `ai-reconstruction-prompt.md` | Prompt autónomo para reconstruir y continuar el proyecto. |
| `functional-audit.md` | Hallazgos, correcciones, evidencia y limitaciones de la auditoría funcional. |
| `documentation-audit.md` | Discrepancias contrastadas y cierre de la sincronización documental de tarea 7. |
| `releases/v0.1.0.md` | Notas de la primera publicación Alpha. |
| `development-status.md` | Registro operativo, estado y evidencias. |
| `roadmap.md` | Hoja de ruta vigente de PMD y conversión asistida por IA. |
| `pmd-design.md` | Dirección de producto, decisiones PMD y diseño objetivo de estilos/IA. |
| `reference-analysis-tema1.md` | Análisis contrastado de estructura JSON, estilos, marcadores, SVG y pérdidas de Markdown en la referencia Tema1. |
| `architecture.md` | Capas, flujo de datos e invariantes vigentes. |
| `development.md` | Instalación, CLI, pruebas y ciclo de contribución. |
| `file-reference.md` | Este catálogo. |
| `grammar.md` | Sintaxis Markdown y matriz real de implementación. |
| `ir-specification.md` | Especificación vigente del contrato neutral IR 1.1.0 y compatibilidad 1.0.0. |
| `ir-schema.json` | JSON Schema Draft 2020-12 del IR. |
| `ir-migration-plan.md` | Registro histórico de consolidación y evolución del contrato IR. |
| `ir-1.1-design.md` | Diseño del contrato IR 1.1.0: roles semánticos y tablas de árbol. |
| `decisions/ADR-002-ir-semantic-structures.md` | Decisión sobre roles semánticos, estructuras compuestas y versionado 1.1.0. |
| `decisions/ADR-001-pmd-ir-architecture.md` | Decisiones arquitectónicas de PMD, IR, estilos y adaptadores. |
| `ir-consolidation-audit.md` | Inventario de módulos, consumidores y riesgos de la consolidación del modelo. |
| `ir-parser-design.md` | Diseño de AST sintáctico, constructor IR, adaptador legacy y estado de migración del parser. |
| `style-system.md` | Modelo de estilos actual y evolución prevista del catálogo semántico y reglas. |
| `xmind-adapter.md` | Mapeo IR→XMind y matriz de soporte/rechazo/pérdidas. |
| `xmind-engine-evaluation.md` | Evaluación de motores y decisión de serialización Python nativa. |
| `xmind-integration-tests.md` | Fixture de referencia, CI y prueba manual XMind Desktop. |

## Ejemplos

| Ruta | Función |
|---|---|
| `examples/constitucion.md` | Ejemplo de entrada Markdown enriquecida. |
| `examples/xmind-smoke-test.md` | Fuente del libro mínimo para prueba manual XMind Desktop. |
| `examples/assets/escudo.svg` | Recurso SVG ilustrativo original utilizado por el ejemplo de Constitución. |
| `examples/ir/constitucion.json` | Ejemplo histórico IR 1.0.0. |
| `examples/ir/tree_table.json` | Ejemplo IR 1.1.0 con roles y estructura tree_table. |

## Pruebas y scripts

| Ruta | Función |
|---|---|
| `tests/test_parser.py` | Gramática, directivas, bloques y errores de parsing. |
| `tests/test_styles.py` | Carga, precedencia, herencia y resolución de estilos. |
| `tests/test_xmind_adapter.py` | Traducción del IR, validación de capacidades y paquete ZIP/JSON. |
| `tests/test_xmind_integration.py` | Contraste estructural con fixture XMind externo. |
| `tests/fixtures/xmind/xmind-md-smoke-test.xmind` | Fixture propio abierto y guardado manualmente en XMind Desktop. |
| `scripts/create_xmind_smoke.py` | Genera el artefacto XMind de smoke test usado en CI. |
| `scripts/verify_distributions.py` | Comprueba nombre/versión, licencia y archivos esenciales de wheel y sdist. |

## Automatización y salida

| Ruta | Función |
|---|---|
| `.github/workflows/ci.yml` | CI Ubuntu: tests/Ruff/XMind y job dependiente de build, verificación e instalación de wheel/sdist. |
| `.github/workflows/release.yml` | Publicación manual protegida: verifica CI/versión, exige confirmación Desktop, construye distribuciones, checksums SHA-256 y crea tag/prerelease. |
| `output/` | Salidas locales; el contenido generado no se versiona salvo fixtures expresamente ubicados en tests. |

El catálogo no sustituye a las pruebas: antes de modificar un módulo, inspecciona su implementación y sus tests actuales.

| `xmind-markdown-behavior.md` | Evidencia y límites de exportación/importación Markdown de XMind; separación frente a la gramática propia del proyecto. |
| `xmind-json-format.md` | Estructura observada de `content.json`, contenedor XMind moderno, estilos, SVG y perfil del adaptador actual. |
| `xmind-official-sdk-research.md` | Investigación de repositorios oficiales TypeScript/MIT (SDK, modelo, generador y XMindMark), esquemas, gramática de mapas, CLI/Skill y serializadores ZIP/JSON. |
