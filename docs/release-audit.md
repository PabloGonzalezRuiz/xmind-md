# Auditoría de empaquetado y licencia

- **Fecha:** 2026-11-11
- **Rama auditada:** `main`
- **Commit auditado:** `dd16f626353b36cf3a9b1f15a4001d3c3ad93601`
- **Alcance:** metadatos de distribución Python, configuración de build, descubrimiento de paquetes, entry point, licencia y estado de publicaciones.
- **Entorno:** revisión del repositorio y GitHub Actions; no se ha instalado ni ejecutado Python localmente.

## 1. Resultado ejecutivo

La configuración actual permite preparar un paquete Python mediante `setuptools`, pero **todavía no hay evidencia de que se haya construido, instalado y probado una distribución wheel y sdist**. La CI actual instala el proyecto en modo editable (`pip install -e ".[dev]"`), ejecuta pruebas y genera un libro XMind; no construye los archivos de distribución.

**Bloqueo principal para una publicación abierta:** no existe un archivo de licencia en la raíz ni metadatos `project.license` en `pyproject.toml`. La elección de licencia queda pendiente de confirmación expresa del titular del proyecto. No se ha añadido una licencia ni se ha inferido una a partir de la visibilidad pública del repositorio.

La API de GitHub devuelve una lista vacía de Releases. No hay, por tanto, una Release publicada en el momento de esta auditoría.

## 2. Configuración comprobada

| Elemento | Estado observado | Evaluación |
|---|---|---|
| Backend | `setuptools.build_meta` | Adecuado para el proyecto |
| Requisitos de build | `setuptools>=68`, `wheel` | Funciona como configuración base; actualizar el mínimo si se adopta metadata SPDX PEP 639 |
| Diseño de paquetes | `src/` | Correcto |
| Descubrimiento | `[tool.setuptools.packages.find]`, `where = ["src"]` | Configurado |
| Nombre | `xmind-md` | Declarado |
| Versión | `0.1.0` | Declarada en TOML y duplicada en `src/xmind_md/__init__.py` |
| Python | `>=3.10` | Declarado; la CI de referencia usa Python 3.12 |
| README | `README.md` | Incluido como descripción larga |
| Dependencia de ejecución | `PyYAML>=6.0` | Declarada |
| Dependencias de desarrollo | pytest, Ruff y jsonschema | Separadas en el extra `dev` |
| Comando instalado | `xmind-md = xmind_md.cli:main` | Entry point declarado |
| Licencia | Ausente | Bloqueo de publicación abierta hasta decisión |
| Autor/mantenedor | No declarado | Metadatos opcionales que conviene decidir antes de publicar |
| URLs de proyecto | No declaradas | Recomendable añadir repositorio y documentación |
| Clasificadores | No declarados | Recomendable añadir Python y estado de desarrollo, con cuidado de no anunciar compatibilidad no probada |
| Prueba de wheel/sdist | No existe en CI | Pendiente |
| Release | No hay Releases publicadas | Pendiente |

## 3. Hallazgos de licencia

Se comprobó que no existen en la raíz `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING`, `NOTICE` ni `AUTHORS.md`. Tampoco se declara `license` ni `license-files` en `pyproject.toml`.

La ausencia de una licencia explícita significa que no debe presentarse el proyecto como software de código abierto con permisos de reutilización definidos. La decisión no se puede deducir del hecho de que el repositorio sea público.

Opciones habituales que el titular puede valorar:

- **MIT:** licencia permisiva, breve y sencilla; exige conservar avisos de copyright y licencia.
- **Apache-2.0:** permisiva, con términos explícitos sobre patentes y condiciones más extensas.
- **GPL-3.0-or-later:** copyleft; impone condiciones de distribución de obras derivadas.
- **Sin licencia abierta / licencia propietaria:** no añadir una licencia de código abierto.

La selección debe hacerla el titular del proyecto. Esta auditoría no constituye asesoramiento jurídico.

Si se elige una licencia SPDX estándar, la guía actual de empaquetado Python recomienda declarar `[project].license` como expresión SPDX y `license-files` con los archivos que se distribuirán. La guía indica que setuptools incorporó soporte PEP 639 desde la versión 77.0.3; en ese caso conviene elevar el mínimo de build de `setuptools>=68` a `setuptools>=77.0.3`.

Referencias oficiales:
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files
- https://packaging.python.org/en/latest/specifications/pyproject-toml/

## 4. Hallazgos de empaquetado

Aspectos ya resueltos:
- `pyproject.toml` contiene `[build-system]` y `[project]`.
- `setuptools.build_meta` y el diseño `src` están declarados.
- El paquete se descubre desde `src`.
- El README está configurado como descripción larga.
- La versión del paquete y `xmind_md.__version__` coinciden actualmente en `0.1.0`.
- El entry point de consola coincide con la función `main` de la CLI.
- Las dependencias de runtime están separadas de las de desarrollo.

Aspectos que todavía no están demostrados:
- Construcción de `.whl` y `.tar.gz` (sdist).
- Inclusión de metadatos y archivos legales dentro de ambas distribuciones.
- Instalación desde wheel en un entorno limpio no editable.
- Instalación desde sdist.
- Ejecución del comando `xmind-md` instalado y de `python -m xmind_md` desde una instalación no editable.
- Conversión de un ejemplo real usando únicamente la distribución instalada.
- Compatibilidad declarada con versiones Python distintas de la usada en CI.

La configuración actual no declara archivos de datos del paquete. La aplicación obtiene sus ejemplos y configuración del repositorio/argumentos del usuario; antes de publicar debe confirmarse si esa separación es intencionada y si algún recurso del paquete necesita incluirse en la distribución.

La versión está duplicada en dos archivos. No es un error actual porque ambas declaran `0.1.0`, pero es un riesgo de divergencia en futuras versiones. Se debe decidir si se mantiene una comprobación automatizada de igualdad o si se adopta una única fuente de versión.

## 5. Evidencia CI consultada

Ejecución más reciente al auditar:
- Run #283: https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42985816448
- Commit: `dd16f626353b36cf3a9b1f15a4001d3c3ad93601`
- Job `Tests (Ubuntu)`: completed / success.
- Pasos Install, Ruff lint, Ruff format, descarga del fixture, Tests, generación XMind y Upload XMind smoke test: todos success.
- Artefacto `xmind-desktop-smoke-test`: 1.331 bytes; SHA-256 `6d4a3ee6533744496d6693e1f9b9668478684e97ad67a0aafa9da58b5ecffcb0`.

**Límite de esta evidencia:** la CI instala en editable y no ejecuta `python -m build`; por tanto, no valida wheel ni sdist.

## 6. Decisiones pendientes y siguiente trabajo

1. Confirmar la licencia que desea aplicar el titular. No añadir un archivo LICENSE ni declarar una expresión SPDX hasta recibir esa decisión.
2. Incorporar la licencia elegida y los metadatos correspondientes, incluyendo la versión mínima de setuptools que soporte el formato elegido.
3. Ampliar GitHub Actions para construir wheel y sdist, comprobar su contenido e instalarlos en entornos limpios.
4. Ejecutar una prueba funcional con la CLI instalada desde wheel y desde sdist, no desde una instalación editable.
5. Revisar metadatos públicos (autoría, URLs, clasificadores) y coherencia de versión.
6. Solo después de cerrar estas comprobaciones, continuar con la auditoría funcional, dependencias, seguridad, documentación y preparación de la Release.

**Estado:** auditoría inicial de empaquetado y licencia completada; cambios de licencia y construcción de distribuciones pendientes de decisión y autorización específica.


## 7. Decisión posterior: licencia MIT adoptada — 2026-11-11

La incertidumbre sobre la selección de licencia quedó resuelta por instrucción expresa del titular. Se adopta **MIT**, con el aviso `Copyright (c) 2026 Pablo González Ruiz`.

Cambios realizados:
- `LICENSE`: texto íntegro de MIT.
- `pyproject.toml`: `license = "MIT"` y `license-files = ["LICENSE"]`.
- Requisito de build elevado a `setuptools>=77.0.3` para soporte de metadatos SPDX PEP 639.
- `README.md` actualizado y decisión documentada en `docs/license-adoption.md`.

La licencia está incorporada en el repositorio, pero su inclusión en wheel/sdist aún no está verificada. Tampoco se han construido ni instalado distribuciones. La CI debe validar la compatibilidad de setuptools, metadatos, inclusión del fichero legal e instalación funcional desde ambos formatos.

La selección MIT facilita la reutilización del código propio, pero no cambia las licencias de dependencias, fixtures ni otros materiales de terceros. Se debe comprobar su procedencia y condiciones antes de publicar paquetes.

No se ha cambiado la versión 0.1.0 ni se ha creado una Release.

## 8. Siguiente fase de empaquetado

1. Añadir a GitHub Actions un job que construya wheel y sdist desde el árbol limpio.
2. Inspeccionar los archivos para confirmar metadatos y presencia de LICENSE.
3. Crear entornos virtuales separados e instalar cada distribución, sin instalación editable.
4. Ejecutar `xmind-md --help` y una conversión de ejemplo con el paquete instalado.
5. Repetir CI con Ruff y la suite completa.
6. Solo con evidencia verde, continuar la auditoría de dependencias, licencias de terceros, metadatos y publicación.

El usuario ha autorizado adoptar MIT y usar su nombre como titular. La siguiente fase de empaquetado debe esperar autorización expresa antes de iniciarse.
