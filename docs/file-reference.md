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
| `model.py` | Modelo legacy conservado por compatibilidad. No es el contrato de los adaptadores. |
| `parser.py` | Analiza el subconjunto Markdown enriquecido y conserva la API/modelo legacy. |
| `ir_parser.py` | Puente de parsing al modelo canónico IR 1.0.0; expone `parse_markdown_ir()` y `parse_file_ir()`. |
| `styles.py` | Carga YAML y resuelve estilos en modelos IR y legacy. |
| `cli.py` | Coordina parsing, resolución de estilos y exportación JSON/XMind. |
| `ir/` | Entidades, serialización y validación del contrato neutral IR 1.0.0. |
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
| `development-status.md` | Registro operativo, auditoría, hoja de ruta y evidencias. |
| `architecture.md` | Capas, flujo de datos e invariantes vigentes. |
| `development.md` | Instalación, CLI, pruebas y ciclo de contribución. |
| `file-reference.md` | Este catálogo. |
| `grammar.md` | Sintaxis Markdown y matriz real de implementación. |
| `ir-specification.md` | Contrato neutral IR 1.0.0. |
| `ir-schema.json` | JSON Schema Draft 2020-12 del IR. |
| `ir-migration-plan.md` | Registro/plan histórico de migración al IR. |
| `style-system.md` | Modelo de estilos, precedencia y capacidades implementadas. |
| `xmind-adapter.md` | Mapeo IR→XMind y matriz de soporte/rechazo/pérdidas. |
| `xmind-engine-evaluation.md` | Evaluación de motores y decisión de serialización Python nativa. |
| `xmind-integration-tests.md` | Fixture de referencia, CI y prueba manual XMind Desktop. |

## Ejemplos

| Ruta | Función |
|---|---|
| `examples/constitucion.md` | Ejemplo de entrada Markdown enriquecida. |
| `examples/xmind-smoke-test.md` | Fuente del libro mínimo para prueba manual XMind Desktop. |
| `examples/assets/escudo.svg` | Recurso SVG ilustrativo original utilizado por el ejemplo de Constitución. |
| `examples/ir/constitucion.json` | Ejemplo de documento IR serializado. |

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
