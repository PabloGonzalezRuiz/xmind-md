# Auditoría integral y preparación de Release

- **Fecha de auditoría:** 2026-11-11
- **Rama:** `main`
- **Commit de código auditado:** `81b514195f1ea9a7bb0225c3353717f29251c615`
- **Ejecución CI:** [42988289597](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42988289597)
- **Alcance:** árbol del repositorio, arquitectura, parser/IR/estilos/adaptadores/CLI, pruebas, workflow, metadatos de distribución, licencia y documentación.
- **Entorno:** inspección de GitHub y GitHub Actions; no se ejecutó código en el equipo del usuario.

## 1. Dictamen ejecutivo

El proyecto ya dispone de una cadena funcional Markdown → IR 1.0.0 → JSON/XMind, CLI instalada, CI Ubuntu con Ruff y pytest, fixture validado manualmente en XMind Desktop y construcción de wheel/sdist. **La publicación estable todavía no está autorizada por la evidencia técnica disponible**: quedan auditorías de terceros, compatibilidad de Python, cobertura del paquete instalado para salida XMind, calidad de release y revisión final de documentación/versionado.

La ejecución #42988289597 finalizó con conclusión `success`. No es solo una prueba de instalación editable: construyó las dos distribuciones, verificó sus contenidos y licencia, instaló cada una en un entorno virtual limpio separado y ejecutó una conversión CLI a JSON.

## 2. Estado del repositorio auditado

La estructura real contiene:
- `.github/workflows/ci.yml`: dos jobs, pruebas/calidad y construcción/instalación de distribuciones.
- `src/xmind_md/`: parser legacy, puente IR, entidades/validación IR, estilos, CLI y adaptadores JSON/XMind.
- `tests/`: pruebas de parser, IR, esquema, estilos, adaptadores, CLI e integración.
- `scripts/create_xmind_smoke.py`: generación del fixture de comprobación XMind.
- `scripts/verify_distributions.py`: inspección de wheel/sdist.
- `docs/`: especificaciones, matrices, continuidad, auditoría y guía.
- `examples/`, `config/` y `tests/fixtures/xmind/`: ejemplos/configuración y fixture manual.

La versión declarada es `0.1.0` tanto en `pyproject.toml` como en `src/xmind_md/__init__.py`. La coincidencia está comprobada en el commit auditado, pero la duplicidad sigue siendo un riesgo de divergencia. El verificador de distribución también contiene literalmente la versión `0.1.0`; habrá que parametrizarlo o comprobar expresamente los tres puntos al preparar el siguiente versionado.

## 3. Evidencia CI y distribución

### 3.1 Run #42988289597

- Commit: `81b514195f1ea9a7bb0225c3353717f29251c615`.
- Estado: `completed / success`.
- Job `Tests (Ubuntu)`: success.
- Job `Build and install distributions (Ubuntu)`: success.
- Entorno: Ubuntu, Python 3.12.

Job de pruebas:
- Instalación editable con dependencias de desarrollo: success.
- Ruff lint: success (`All checks passed!`).
- Ruff format: success.
- Descarga del fixture XMind externo: success.
- Pytest: **131 passed in 0.36s**.
- Generación del smoke XMind y subida: success.

Job de distribución:
- Build: `xmind_md-0.1.0.tar.gz` y `xmind_md-0.1.0-py3-none-any.whl`.
- Verificador: ambos formatos aceptados; comprueba nombre/versión, expresión MIT, LICENSE y módulos/archivos esenciales.
- Wheel: instalación en virtualenv limpio y conversión Markdown → JSON: success.
- Sdist: instalación en virtualenv limpio y conversión Markdown → JSON: success.
- Artefacto `python-distributions`: ID `13839594760`, 72.878 bytes, SHA-256 del ZIP del artefacto `9b4a1960284e323fb00e4edaae19e12e00ec69377022a48730b8dd8ffe43ec59`, retención hasta 2026-12-11.
- Artefacto `xmind-desktop-smoke-test`: ID `13840690878`, 1.331 bytes, SHA-256 del ZIP del artefacto `e4596bf69bac18c669d709089f4b8eabb0f9daec63e171856cc1e447510b618c`, retención hasta 2026-11-25.

Los hashes anteriores identifican los ZIP de artefactos de GitHub Actions, no los hashes individuales de los ficheros wheel/sdist contenidos en ellos.

### 3.2 Alcance y límites de la evidencia

La instalación de wheel y sdist ejecutó conversiones CLI a JSON y XMind en entornos limpios separados. La salida XMind se verificó como ZIP íntegro, con `mimetype` en primera posición y sin compresión, valor MIME correcto y `content.json` con el tema raíz esperado. El fixture histórico se abrió/guardó/reabrió manualmente en XMind Desktop 26.05.01107. Esa prueba manual sigue limitada a los elementos comprobados y no certifica todas las capacidades.

La CI solo ejecuta Python 3.12 en Ubuntu aunque el paquete declara Python `>=3.10`. La compatibilidad de ejecución en Python 3.10/3.11 y Windows no queda acreditada por este pipeline.

El log muestra además un aviso de deprecación: las acciones `checkout@v4`, `setup-python@v5` y `upload-artifact@v4` están usando Node.js 20 y GitHub indica migración forzada a Node.js 24. No ha fallado el run, pero conviene actualizar/verificar versiones de acciones antes de publicar.

## 4. Auditoría técnica por capas

| Área | Estado observado | Pendiente / riesgo |
|---|---|---|
| Parser | Subconjunto Markdown enriquecido implementado; API legacy | No es CommonMark/GFM completo; revisar discrepancias entre gramática normativa y parser |
| Puente IR | `parse_markdown_ir()` / `parse_file_ir()` construyen IR 1.0.0 | Modelo legacy `model.py` sigue presente; evaluar retirada sin romper API |
| IR | Entidades, serialización, validación y JSON Schema | Verificar exhaustividad de invariantes entre schema y validación semántica |
| Estilos | Cascada IR con herencia y overrides | Cobertura de propiedades y coherencia de precedencia frente a ejemplos |
| Adaptador JSON | Serialización IR | Revisar contrato de estabilidad y errores |
| Adaptador XMind | Perfil parcial; rechaza capacidades no soportadas | Salida de wheel/sdist aún no probada en formato XMind; compatibilidad visual limitada a fixture manual |
| CLI | JSON/XMind, formato por extensión o explícito, errores con código 2 | Añadir prueba instalada de XMind; revisar diagnósticos y opciones públicas |
| CI | Ubuntu/Python 3.12, Ruff, pytest, smoke y build | Matriz Python ausente; avisos Node 20 deprecado |
| Packaging | Wheel/sdist construidos, inspeccionados, instalados y CLI JSON probada | Fijar versión única o comprobación; ampliar smoke XMind y metadatos |
| Licencia | MIT declarada y empaquetada | Revisar procedencia/licencia de materiales de terceros |
| Release | No hay Release estable documentada en esta auditoría | Changelog, versión, tag, assets y notas pendientes |

## 5. Licencia y procedencia de materiales

El proyecto declara MIT con `Copyright (c) 2026 Pablo González Ruiz`; el wheel contiene `License-Expression: MIT` y un fichero bajo `.dist-info/licenses/`; el sdist contiene `LICENSE`. Esto valida el empaquetado del aviso, no la titularidad jurídica de cada fichero.

Antes de distribuir:
- Identificar procedencia y licencia del fixture de referencia descargado desde `sc0tfree/xmind-mcp` en un commit fijado.
- Revisar el fixture XMind propio y los elementos incluidos; el hecho de que el usuario lo haya guardado en XMind Desktop no demuestra titularidad de todo contenido embebido.
- Revisar dependencias runtime y de desarrollo, incluyendo PyYAML, pytest, Ruff, jsonschema y dependencias transitivas relevantes.
- Separar claramente código propio, fixtures de terceros, ejemplos y archivos generados; conservar avisos/atribuciones cuando proceda.
- No asumir que la licencia MIT del repositorio se aplica a obras de terceros.

## 6. Riesgos y mejoras detectadas

1. **Compatibilidad Python:** `requires-python >=3.10` sin matriz automatizada en 3.10/3.11.
2. **Salida XMind desde distribuciones:** el smoke instalado actualmente prueba JSON, no `.xmind`.
3. **Acciones CI:** aviso de deprecación Node.js 20 en acciones actuales.
4. **Versionado:** `0.1.0` duplicada en TOML, paquete y verificador.
5. **Terceros:** fixture externo y fixture binario propio requieren inventario de procedencia/licencia.
6. **Parser y especificación:** la especificación general incluye capacidades previstas; la sección de estado real debe seguir prevaleciendo. Auditar cada afirmación contra código y tests antes de Release.
7. **Cobertura funcional XMind:** el perfil rechaza recursos/imágenes, tareas, boundaries, summaries, extensiones y otras propiedades; no anunciar soporte general.
8. **Distribución de recursos:** no hay declaración de package-data; confirmar que no se necesitan recursos externos para la CLI instalada.

## 7. Hoja de ruta pendiente

| Orden | Tarea | Criterio de cierre |
|---:|---|---|
| 1 | Completar smoke de distribuciones: probar salida XMind desde wheel y sdist instalados | Ambos paquetes producen ZIP XMind válido; validar contenido.json, mimetype y estructura; CI verde |
| 2 | Auditoría de procedencia/licencias de terceros | Inventario de dependencias/fixtures/ejemplos con licencia, origen y acción necesaria; avisos conservados |
| 3 | Reforzar matriz de compatibilidad Python | CI en versiones soportadas seleccionadas (mínimo 3.10, 3.11, 3.12) o reducir/documentar alcance |
| 4 | Actualizar acciones GitHub Actions y eliminar aviso Node 20 | Workflow vigente sin advertencia de runtime obsoleto y CI verde |
| 5 | Resolver versionado y metadatos de publicación | Fuente de versión consistente, verificador no desincronizable, metadatos públicos coherentes |
| 6 | Auditoría funcional final de parser/IR/estilos/CLI/XMind | Matriz de capacidades basada en código/tests; defectos críticos corregidos o limitaciones explícitas |
| 7 | Sincronización final de toda la documentación | README y documentos técnicos/operativos sin contradicciones; CI verde |
| 8 | Preparar changelog, tag y GitHub Release estable | Artefactos identificados y comprobados; notas de versión; tag y Release reproducibles |

El usuario ha solicitado enumerar tareas y ejecutar la primera; la tarea 1 queda como siguiente trabajo autorizado. No iniciar la tarea 2 hasta presentar resultados y solicitar autorización.

## 8. Criterios de publicación

No publicar hasta que:
- CI verde en el commit candidato con pruebas, lint, formato, matriz de Python acordada y build/install de wheel/sdist.
- La CLI instalada desde wheel y sdist genere JSON y XMind correctamente.
- El perfil XMind, las pérdidas y los rechazos estén descritos con precisión.
- Se haya comprobado manualmente en XMind Desktop el artefacto candidato o una muestra generada desde el mismo commit.
- Se haya completado la auditoría de terceros y avisos de licencia.
- Versionado, metadatos, changelog y documentación estén sincronizados.
- Se construyan artefactos de Release y se publiquen con tag y notas verificables.

La instrucción previa del usuario autoriza crear la Release cuando se cumplan estos criterios. No inventar la versión ni declarar estabilidad antes de cerrar la auditoría. La decisión final de versión debe basarse en el alcance real, no en el número de pruebas.

## 9. Referencias internas

- [Estado de desarrollo](development-status.md)
- [Prompt maestro de reconstrucción](ai-reconstruction-prompt.md)
- [Adopción MIT](license-adoption.md)
- [Arquitectura](architecture.md)
- [Gramática](grammar.md)
- [Matriz del adaptador XMind](xmind-adapter.md)
- [Guía de desarrollo](development.md)


### Cierre de tarea 1 — smoke XMind de distribuciones

La tarea 1 quedó completada en run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087), commit `9831ae89da6e331219e1edbce71f6415752e2f22`. Los dos jobs terminaron success. Pytest: **131 passed in 0.48s**; Ruff lint/format success. Wheel y sdist se instalaron en entornos limpios, generaron JSON y XMind, y cada archivo XMind pasó las comprobaciones ZIP, `mimetype`, `content.json` y `testzip()`. Artefacto de distribución ID `13840773838`, 73.210 bytes, SHA-256 del ZIP `eb6a4f8235544b66106615734791605eed540ad0eb98f39d6af0ebf3fb5d6c3a`. Artefacto smoke ID `13841725579`, 1.331 bytes, SHA-256 del ZIP `ee794ec21589f37d59d85c4f25f519d2f45c547ba7f8dcb5eee1aa5f733f7c65`.

Esta verificación acredita generación estructural desde ambas distribuciones instaladas; no sustituye una nueva apertura manual de ese artefacto en XMind Desktop.
