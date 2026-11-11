# Auditoría integral y preparación de Release

- **Fecha de auditoría:** 2026-11-11
- **Rama:** `main`
- **Commit base de auditoría de código:** `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`
- **Última validación funcional y de distribuciones:** [43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888)
- **Última revisión documental:** sincronización de tarea 7 completada el 2026-11-11; ver sección 12 y `documentation-audit.md`
- **Alcance:** árbol del repositorio, arquitectura, parser/IR/estilos/adaptadores/CLI, pruebas, workflow, metadatos de distribución, licencia y documentación.
- **Entorno:** inspección de GitHub y GitHub Actions; no se ejecutó código en el equipo del usuario.

## 1. Dictamen ejecutivo

El proyecto dispone de una cadena funcional Markdown → IR 1.0.0 → JSON/XMind, CLI instalada, CI Ubuntu con Ruff y pytest, fixture histórico validado manualmente en XMind Desktop y construcción de wheel/sdist desde entornos limpios. Las tareas 1–7 de la hoja de ruta están cerradas, incluida la sincronización documental final (sección 12). **La publicación todavía no se ha ejecutado**: queda preparar changelog, decidir versión/tag, realizar la comprobación final del artefacto candidato y publicar una Release reproducible (tarea 8). La existencia de pruebas estructurales no sustituye la inspección manual del nuevo smoke con estilos en XMind Desktop.

La evidencia funcional más reciente previa a la auditoría documental es el run #43006735888 (161 pruebas por versión, Python 3.10/3.11/3.12); la validación de los cambios documentales se registra en la sección 12 una vez concluya la CI correspondiente al commit final.

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
- Wheel: instalación en virtualenv limpio y conversión Markdown → JSON y XMind: success.
- Sdist: instalación en virtualenv limpio y conversión Markdown → JSON y XMind: success.
- Run de revalidación [42990429514](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990429514), commit `a270b1b911d8ccbc36e0e9d8613c409f1e22d074`: ambos jobs success, Ruff success, 131 passed in 0.54s; wheel/sdist generaron XMind y pasaron verificación ZIP/MIME/JSON.
- Artefacto `python-distributions`: ID `13839594760`, 72.878 bytes, SHA-256 del ZIP del artefacto `9b4a1960284e323fb00e4edaae19e12e00ec69377022a48730b8dd8ffe43ec59`, retención hasta 2026-12-11.
- Artefacto `xmind-desktop-smoke-test`: ID `13840690878`, 1.331 bytes, SHA-256 del ZIP del artefacto `e4596bf69bac18c669d709089f4b8eabb0f9daec63e171856cc1e447510b618c`, retención hasta 2026-11-25.

Los hashes anteriores identifican los ZIP de artefactos de GitHub Actions, no los hashes individuales de los ficheros wheel/sdist contenidos en ellos.

### 3.2 Alcance y límites de la evidencia

La instalación de wheel y sdist ejecutó conversiones CLI a JSON y XMind en entornos limpios separados. La salida XMind se verificó como ZIP íntegro, con `mimetype` en primera posición y sin compresión, valor MIME correcto y `content.json` con el tema raíz esperado. El fixture histórico se abrió/guardó/reabrió manualmente en XMind Desktop 26.05.01107. Esa prueba manual sigue limitada a los elementos comprobados y no certifica todas las capacidades.

La CI solo ejecuta Python 3.12 en Ubuntu aunque el paquete declara Python `>=3.10`. La compatibilidad de ejecución en Python 3.10/3.11 y Windows no queda acreditada por este pipeline.

En ejecuciones históricas aparecía un aviso de deprecación para `checkout@v4`, `setup-python@v5` y `upload-artifact@v4`. **Resuelto el 2026-11-11:** el workflow usa ahora checkout@v5, setup-python@v6 y upload-artifact@v6, cuyas definiciones action.yml declaran node24. La ejecución posterior #42996452355 terminó success y sus cuatro logs no contienen el aviso Node.js 20.

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
| CI | Ubuntu/Python 3.10, 3.11 y 3.12; Ruff, pytest, smoke y build | Matriz y runtime Node.js 24 validados; run #42996452355 |
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
3. **Acciones CI:** completado; runtime Node.js 24 validado en run #42996452355.
4. **Versionado:** `0.1.0` duplicada en TOML, paquete y verificador.
5. **Terceros:** fixture externo y fixture binario propio requieren inventario de procedencia/licencia.
6. **Parser y especificación:** la especificación general incluye capacidades previstas; la sección de estado real debe seguir prevaleciendo. Auditar cada afirmación contra código y tests antes de Release.
7. **Cobertura funcional XMind:** el perfil rechaza recursos/imágenes, tareas, boundaries, summaries, extensiones y otras propiedades; no anunciar soporte general.
8. **Distribución de recursos:** no hay declaración de package-data; confirmar que no se necesitan recursos externos para la CLI instalada.

## 7. Hoja de ruta pendiente

| Orden | Tarea | Criterio de cierre |
|---:|---|---|
| 1 | Smoke XMind desde wheel y sdist instalados | **Completada** en CI #42990025087 y revalidada en #42990429514 |
| 2 | Auditoría de procedencia/licencias de terceros | **Inventario técnico completado** en THIRD_PARTY_NOTICES.md; queda pendiente el cierre de la inconsistencia del recurso de ejemplo y un SBOM de transitivas si se decide redistribuirlas agrupadas |
| 3 | Reforzar matriz de compatibilidad Python | **Completada**: CI verde en Python 3.10/3.11/3.12, run #42995180722; 131 pruebas por versión |
| 4 | Actualizar acciones GitHub Actions y eliminar aviso Node 20 | **Completada**: checkout@v5, setup-python@v6 y upload-artifact@v6; node24 verificado y CI verde (#42996452355) |
| 5 | Resolver versionado y metadatos de publicación | Fuente de versión consistente, verificador no desincronizable, metadatos públicos coherentes |
| 6 | Auditoría funcional final de parser/IR/estilos/CLI/XMind | Matriz de capacidades basada en código/tests; defectos críticos corregidos o limitaciones explícitas |
| 7 | Sincronización final de toda la documentación | **Revisión completada**; CI final del commit documental pendiente de registrar |
| 8 | Preparar changelog, tag y GitHub Release estable | Artefactos identificados y comprobados; notas de versión; tag y Release reproducibles |

El usuario ha autorizado la auditoría de procedencia/licencias (tarea 2). El inventario técnico está documentado; la limitación de dependencias transitivas y la referencia rota del recurso se mantienen como hallazgos pendientes para las tareas correspondientes.

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
- [Avisos de terceros](../THIRD_PARTY_NOTICES.md)
- [Arquitectura](architecture.md)
- [Gramática](grammar.md)
- [Matriz del adaptador XMind](xmind-adapter.md)
- [Guía de desarrollo](development.md)


### Cierre de tarea 1 — smoke XMind de distribuciones

La tarea 1 quedó completada en run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087), commit `9831ae89da6e331219e1edbce71f6415752e2f22`. Los dos jobs terminaron success. Pytest: **131 passed in 0.48s**; Ruff lint/format success. Wheel y sdist se instalaron en entornos limpios, generaron JSON y XMind, y cada archivo XMind pasó las comprobaciones ZIP, `mimetype`, `content.json` y `testzip()`. Artefacto de distribución ID `13840773838`, 73.210 bytes, SHA-256 del ZIP `eb6a4f8235544b66106615734791605eed540ad0eb98f39d6af0ebf3fb5d6c3a`. Artefacto smoke ID `13841725579`, 1.331 bytes, SHA-256 del ZIP `ee794ec21589f37d59d85c4f25f519d2f45c547ba7f8dcb5eee1aa5f733f7c65`.

Esta verificación acredita generación estructural desde ambas distribuciones instaladas; no sustituye una nueva apertura manual de ese artefacto en XMind Desktop.


### Cierre de tarea 2 — inventario de licencias y procedencia

La tarea 2 se ha ejecutado y documentado en THIRD_PARTY_NOTICES.md. Se inspeccionaron el árbol versionado, pyproject.toml, workflow CI, ejemplos y README del fixture propio; se contrastaron los avisos de licencia en los repositorios originales de dependencias y acciones.

Hallazgos principales:
- Dependencia de ejecución: PyYAML (MIT).
- Dependencias/herramientas de desarrollo: pytest, Ruff y jsonschema (MIT).
- Build: setuptools, wheel y build (MIT).
- Acciones CI: checkout, setup-python y upload-artifact (MIT).
- Fixture XMind externo: se descarga desde sc0tfree/xmind-mcp en commit fijo 6225cbcd3e8fc565bc18e80346699a6e118dd0f7; el repositorio declara MIT y su aviso indica Copyright (c) 2026 Henry Prince. No se incluye en wheel/sdist.
- Fixture de interoperabilidad del proyecto: README registra que fue generado por la CI propia.
- Ejemplo constitucional: contiene referencia a texto normativo y enlace BOE. El artículo 13 LPI excluye disposiciones legales y reglamentarias; no se extiende esta conclusión a otros materiales.
- Hallazgo pendiente: examples/constitucion.md referencia assets/escudo.png, archivo que no existe en el árbol. No se ha incorporado una imagen.

**Límite importante:** el inventario cubre dependencias directas y herramientas explícitas, no todas las dependencias transitivas. No hay lockfile ni SBOM con la resolución concreta. No se afirma que sea un análisis jurídico ni certificación completa de titularidad.

La documentación de terceros es descriptiva; no se ha cambiado el código de ejecución en esta tarea.


### Validación de la auditoría de terceros y documentación

El inventario THIRD_PARTY_NOTICES.md y los documentos actualizados quedaron validados en run [42993499900](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42993499900), commit `d31a389a3066ec17d581629b7aa3078c32fcb80e`. Ambos jobs success; Ruff lint/format success; 131 pruebas superadas; wheel/sdist construidos y verificados; instalación y generación CLI JSON/XMind desde ambas distribuciones success.

Artefactos: `python-distributions` ID 13842766711 (73.605 bytes; SHA-256 ZIP `e6490d4d8e80a94f7fbd97afe56e534a4f98d256107e503cc9d27bf97726b41b`) y `xmind-desktop-smoke-test` ID 13843490530 (1.333 bytes; SHA-256 ZIP `d1fc50796fd95e350b2d2869a0a5281c0f8c3c5eb416c84490ca36522966f9ba`).

### Cierre de tarea 3 — matriz Python

La matriz se incorporó a `.github/workflows/ci.yml` en commit `db241f04b489de23c429d4189c589859aaffc8fb`. Run [42995180722](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42995180722) finalizó completed/success:

- Python 3.10: Ruff lint/format y 131 pruebas success.
- Python 3.11: Ruff lint/format y 131 pruebas success.
- Python 3.12: Ruff lint/format y 131 pruebas success.
- Cada versión generó su artefacto XMind independiente.
- El job de distribuciones construyó wheel/sdist, verificó licencia/contenido, instaló ambos en entornos limpios y generó JSON/XMind correctamente.

La matriz prueba compatibilidad de la suite con las versiones declaradas. Python 3.10 está fuera de soporte de seguridad desde 2026-10-01; la decisión de elevar `requires-python` se reserva para la tarea de versionado/metadatos. No afirmar que wheel/sdist se probaron en cada versión de matriz: su instalación funcional se ejecutó en Python 3.12.

La migración de acciones a Node.js 24 está completada y validada. La siguiente tarea pendiente es revisar versionado y metadatos de publicación; requiere autorización del usuario.
### Cierre de tarea 4 — actualización de runtimes de GitHub Actions

**Completada.** GitHub retiró Node.js 20 de sus runners el 23-09-2026; las acciones JavaScript deben migrarse a releases que declaren Node.js 24.

En .github/workflows/ci.yml: checkout v4 → v5; setup-python v5 → v6; upload-artifact v4 → v6.

Se comprobó directamente en los ficheros action.yml oficiales que las tres versiones seleccionadas declaran runs.using: node24.

Run [42996452355](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42996452355), commit e42f0db5fdc943ce060a358293335573eeb28902, completed/success. Los tres jobs de matriz pasaron Ruff y 131 pruebas cada uno; wheel/sdist se construyeron, verificaron e instalaron correctamente y produjeron JSON/XMind. Los cuatro logs fueron revisados y no contienen avisos Node.js 20/node20. Artefactos: smoke 3.10 ID 13843574011; smoke 3.11 ID 13843124343; smoke 3.12 ID 13843997547; distribuciones ID 13843737659.

La mejora de fijar acciones por SHA inmutable no se incluyó en esta tarea y permanece como mejora independiente de cadena de suministro.

## 10. Actualización de versionado y metadatos — tarea 5 (2026-11-11)

**Estado: COMPLETADA.** Esta sección prevalece sobre los hallazgos históricos de duplicidad de versión y falta de metadatos que aparecen en las secciones anteriores, redactadas antes de la tarea 5.

- Fuente única de versión: `src/xmind_md/__init__.py::__version__`.
- `pyproject.toml` usa versión dinámica de setuptools; no mantiene una copia estática de la versión.
- Metadatos PEP 621 completados: autor, descripción, README, `requires-python >=3.10`, licencia MIT PEP 639, licencia empaquetada, classifiers de estado Alpha/plataforma/versiones y enlaces de proyecto.
- Se conserva 0.1.0; no se ha preparado changelog ni creado tag/Release en esta tarea.
- `xmind-md --version` expone la versión importada de la fuente única.
- `scripts/verify_distributions.py` compara esa versión con METADATA del wheel y PKG-INFO canónico del sdist.
- Python 3.10 se mantiene por compatibilidad técnica demostrada; está fuera de soporte upstream desde 2026-10-01. La matriz no equivale a mantenimiento de seguridad de Python upstream.

### Validación

Run [43002869927](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43002869927), commit `635d8d5bfa42d5b84401f661b7bce3858140dd16`: completed/success. Los tres jobs de pruebas terminaron success con 132 pruebas por versión y Ruff lint/format correcto. El job de distribución construyó wheel/sdist, verificó metadatos y licencia, instaló ambos en entornos limpios y generó JSON/XMind desde ambos paquetes; validación estructural XMind correcta.

Artefacto de distribución: `python-distributions`, ID `13846567777`, 74.823 bytes, digest SHA-256 del ZIP `d3a4997bb167c40f5e63811d52bb990f31cd9d10f9467385a5c8b27df22c6c40`.

### Siguiente tarea

La tarea 6 es la auditoría funcional final de parser, IR, estilos, CLI y adaptador XMind. La tarea 5 está cerrada; no iniciar la tarea 6 sin autorización expresa. La Release sigue pendiente de completar también las tareas 6, 7 y 8.


## 11. Actualización tras auditoría funcional — tarea 6 (2026-11-11)

Esta sección prevalece sobre el dictamen y los hallazgos históricos anteriores que se redactaron antes de las tareas 4, 5 y 6. Consultar también [functional-audit.md](functional-audit.md).

**Tarea 6: COMPLETADA Y VALIDADA.**

Se corrigieron defectos de parser/IR, resolución de estilos externos, configuración YAML de estilos, serialización XMind/JSON y referencias de ejemplo. Entre las correcciones más relevantes:
- Preservación de extensiones de mapa y entidades globales; rechazo de campos desconocidos.
- Soporte Markdown para temas `detached`; validación de kinds/links/markers y YAML JSON-compatible.
- Resolución de referencias de estilos tras cargar fuentes embebidas y externas.
- Migración de `config/styles.yaml` al formato real del resolutor y mapeo de propiedades de línea.
- Rechazo explícito de imágenes inline no soportadas, en vez de aplanarlas silenciosamente.
- Asset de ejemplo ausente sustituido por un SVG ilustrativo original y actualización de los dos ejemplos Constitución.

### Evidencia final

Run [43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888), commit `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`: completed/success.

- Python 3.10/3.11/3.12: **161 pruebas superadas por versión**, Ruff lint y format correctos.
- XMind smoke generado en cada job.
- Wheel y sdist construidos, verificados, instalados en entornos limpios separados y probados con conversiones JSON/XMind; validación ZIP/MIME/JSON correcta.
- Artefacto `python-distributions`: ID `13849240803`, 77.807 bytes, digest SHA-256 del ZIP de Actions `0d638d960a62909f2c21a1c60687baf4f99e6529f7926eaf7d8e2a4348a048bf`.

### Riesgos/condiciones que permanecen

- El perfil XMind sigue sin exportar recursos/imágenes, tareas, boundaries, summaries ni extensiones. `summary` como tipo de tema tampoco está soportado. El contenido se aplana a notas.
- El smoke actualizado con estilos pasó CI, pero no ha sido inspeccionado manualmente de nuevo en XMind Desktop. La comprobación manual histórica sigue siendo la del fixture versionado con XMind Desktop 26.05.01107.
- CI solo valida Ubuntu, no Windows. Python 3.10 se conserva por compatibilidad técnica, pero upstream dejó de soportarlo el 2026-10-01.
- La sincronización documental de tarea 7 se ha completado; consultar la sección 12 y `documentation-audit.md`.
- No se ha creado changelog, tag ni GitHub Release. La versión sigue en 0.1.0.

**Siguiente paso:** tarea 7, sincronización documental final. No comenzar sin autorización expresa. Después quedará tarea 8, preparación de changelog/tag/Release.


## 12. Cierre de sincronización documental — tarea 7 (2026-11-11)

**Estado: COMPLETADA Y VALIDADA.**

Se han corregido las discrepancias detectadas en README, gramática, especificación IR, sistema de estilos, adaptador XMind y guía de desarrollo. El detalle de cambios, contraste con código y limitaciones es [documentation-audit.md](documentation-audit.md).

La configuración YAML ejecutable se documenta como `style_sets` + `styles`, sin `extends/elements/applies_to/properties`. La cascada de estilos corresponde a la implementación actual. La gramática diferencia tipos representables en IR de tipos exportables a XMind. La matriz XMind identifica attached/detached/callout como soportados, detached con coordenadas, y summary como no soportado. README y guía usan el ejemplo smoke para exportar XMind y reportan 161 pruebas por versión.

Run [43009183421](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009183421), commit `6cd1c937ee090bc36483be49e7d1f5c740e0926a`, finalizó `completed / success`. Python 3.10/3.11/3.12: Ruff lint/format correctos y **161 pruebas superadas por versión**. Los tres jobs generaron sus XMind smoke. El job de distribuciones construyó wheel/sdist, verificó contenido/licencia, instaló ambos en entornos limpios separados y ejecutó conversiones CLI JSON/XMind; validación ZIP/MIME/JSON correcta.

Artefactos: `python-distributions` ID `13850260351` (78.103 bytes; SHA-256 del ZIP de Actions `c8109d8d722befe2a5ed1bc953af15711b0caaf9d0f2bf9928bc050796b38a0f`); smoke Python 3.10 ID `13849418602`, Python 3.11 ID `13848884276`, Python 3.12 ID `13849314179`.

Los límites de publicación siguen vigentes: no hay inspección manual del nuevo smoke con estilos en XMind Desktop; CI solo Ubuntu; Python 3.10 fuera de soporte upstream; adaptador XMind parcial; no existe changelog, tag ni Release. La versión se mantiene en 0.1.0.

**Siguiente paso propuesto:** tarea 8, preparación de changelog, tag y GitHub Release. No iniciar hasta recibir autorización expresa del usuario. La autorización previa para publicar queda condicionada a los criterios de esta auditoría y a la validación del commit candidato.
