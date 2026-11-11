# Decisión y adopción de licencia MIT

- **Fecha:** 2026-11-11
- **Titular indicado por el usuario:** Pablo González Ruiz
- **Licencia elegida:** MIT
- **Archivos:** `LICENSE` y metadatos de `pyproject.toml`
- **Estado:** incorporada en `main`; inclusión en wheel/sdist verificada en GitHub Actions run 42988289597.

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

## Validación de distribuciones

GitHub Actions run [42988289597](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42988289597), commit `81b514195f1ea9a7bb0225c3353717f29251c615`, construyó wheel y sdist. El verificador confirmó `License-Expression: MIT` y la presencia de `LICENSE` dentro del wheel y del sdist. Ambos paquetes se instalaron en entornos virtuales limpios separados y ejecutaron la CLI para convertir Markdown a JSON. Los dos jobs finalizaron success; pytest registró 131 pruebas superadas.

Esto acredita el procesamiento de metadatos y la inclusión del texto MIT en las distribuciones generadas. No sustituye la auditoría de titularidad/procedencia de fixtures y dependencias de terceros descrita en `release-audit.md`.


La ampliación de prueba se validó en el run [42990025087](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42990025087), commit `9831ae89da6e331219e1edbce71f6415752e2f22`, con ambos jobs success. Esto valida el uso de MIT en wheel/sdist y el empaquetado funcional; no determina la titularidad de materiales de terceros.