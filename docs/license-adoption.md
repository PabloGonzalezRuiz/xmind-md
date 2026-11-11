# Decisión y adopción de licencia MIT

- **Fecha:** 2026-11-11
- **Titular indicado por el usuario:** Pablo González Ruiz
- **Licencia elegida:** MIT
- **Archivos:** `LICENSE` y metadatos de `pyproject.toml`
- **Estado:** incorporada en `main`; pendiente de validación en GitHub Actions.

## Decisión

El titular del proyecto ha indicado expresamente que se adopte la licencia que menos problemas prácticos pueda ocasionar y ha confirmado el uso de su nombre: **Pablo González Ruiz**. Se ha seleccionado MIT por ser una licencia permisiva, breve y ampliamente reconocida.

MIT permite usar, copiar, modificar, combinar, publicar, distribuir, sublicenciar y vender copias del software. La condición principal es conservar el aviso de copyright y el texto de permiso en las copias o partes sustanciales del software. Incluye una cláusula de exclusión de garantías y responsabilidad.

Esta elección facilita la reutilización, pero no impide que terceros redistribuyan versiones modificadas ni obliga a publicar sus modificaciones. No ofrece una concesión expresa de patentes tan detallada como Apache-2.0.

## Cambios incorporados

- `LICENSE`: texto estándar de MIT con `Copyright (c) 2026 Pablo González Ruiz`.
- `pyproject.toml`: `license = "MIT"` y `license-files = ["LICENSE"]`.
- `pyproject.toml`: mínimo de build actualizado a `setuptools>=77.0.3` para soporte de metadatos PEP 639.
- La versión del paquete sigue siendo `0.1.0`; no se ha creado una Release ni se ha etiquetado una versión.

## Alcance y precauciones

La incorporación refleja la decisión del usuario sobre la titularidad que desea declarar. Antes de distribuir el proyecto, debe comprobarse que el usuario posee o tiene autorización para licenciar bajo MIT todos los derechos incluidos en el repositorio, especialmente contribuciones de terceros, código copiado y recursos/fixtures externos. La licencia MIT del proyecto no relicencia automáticamente materiales de terceros que mantengan sus propias condiciones.

La elección de MIT no constituye asesoramiento jurídico.

## Validación pendiente

La CI debe confirmar que setuptools procesa los metadatos PEP 639, que la licencia se incluye en wheel y sdist y que ambas distribuciones pueden instalarse y ejecutar la CLI. Hasta entonces, la licencia está incorporada en el repositorio, pero no se afirma que los paquetes distribuibles estén validados.

## Evidencia de CI

La adopción quedó validada por GitHub Actions run [42986904524](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42986904524), commit `a64921cfdcc49016b5fd8eeb90cb7703ebb5355a`: instalación, Ruff, 131 pruebas, generación XMind y publicación del artefacto smoke, todo success. Esto comprueba que los metadatos MIT no rompen el pipeline actual. No acredita aún la construcción ni el contenido de wheel/sdist.
