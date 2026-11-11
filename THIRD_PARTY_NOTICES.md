# Avisos de terceros y procedencia de materiales

Este documento registra componentes y materiales de terceros identificados en el repositorio y en el flujo de CI. La licencia MIT de XMind MD no sustituye las licencias de estos componentes ni implica que sus titulares hayan cedido derechos sobre ellos.

## Dependencias y herramientas Python

Las licencias se han contrastado con los archivos de licencia o metadatos públicos de los proyectos originales. Estos paquetes se instalan mediante pip; no se ha encontrado código fuente de estas dependencias copiado o incluido directamente en el árbol de XMind MD.

| Componente | Uso | Alcance | Licencia | Fuente |
|---|---|---|---|---|
| PyYAML | Parseo YAML | Ejecución: PyYAML>=6.0 | MIT | https://github.com/yaml/pyyaml/blob/main/LICENSE |
| pytest | Pruebas | Desarrollo: pytest>=8.0 | MIT | https://github.com/pytest-dev/pytest/blob/main/LICENSE |
| Ruff | Lint y formato | Desarrollo: ruff>=0.5 | MIT | https://github.com/astral-sh/ruff/blob/main/LICENSE |
| jsonschema | Validación de esquemas | Desarrollo: jsonschema[format]>=4.22,<5 | MIT | https://github.com/python-jsonschema/jsonschema/blob/main/COPYING |
| setuptools | Backend de construcción | Build: setuptools>=77.0.3 | MIT | https://github.com/pypa/setuptools/blob/main/LICENSE |
| wheel | Soporte de construcción | Build: wheel | MIT | https://github.com/pypa/wheel/blob/main/LICENSE.txt |
| build | Frontend de construcción CI | Instalado explícitamente en workflow; no es dependencia de ejecución | MIT | https://github.com/pypa/build/blob/main/LICENSE |

**Alcance:** refleja dependencias directas declaradas y herramientas de construcción explícitas, no un SBOM exhaustivo de dependencias transitivas. El repositorio no contiene un lockfile que fije la resolución completa. El extra format de jsonschema, pytest y las herramientas de build pueden instalar dependencias transitivas adicionales; sus versiones y licencias deben inventariarse a partir de una resolución concreta antes de redistribuirlas agrupadas.

Las dependencias no se incorporan como código fuente al wheel/sdist de XMind MD. Los instaladores resuelven e instalan PyYAML como dependencia declarada; las herramientas de desarrollo y build se usan en CI.

## Fixture XMind externo descargado por CI

El workflow .github/workflows/ci.yml descarga temporalmente:

- Repositorio: https://github.com/sc0tfree/xmind-mcp
- Archivo: tests/fixture.xmind
- Revisión fijada: 6225cbcd3e8fc565bc18e80346699a6e118dd0f7
- URL exacta: https://raw.githubusercontent.com/sc0tfree/xmind-mcp/6225cbcd3e8fc565bc18e80346699a6e118dd0f7/tests/fixture.xmind
- Licencia declarada por el repositorio en esa revisión: MIT
- Aviso de copyright del LICENSE de esa revisión: Copyright (c) 2026 Henry Prince.

El fixture se descarga en el workspace de GitHub Actions para pruebas de integración. No está versionado en XMind MD ni se incluye en los wheel/sdist verificados. La licencia declarada por el repositorio de origen no constituye una afirmación independiente sobre posibles derechos de terceros incorporados dentro del contenido binario del fixture.

### Aviso MIT del repositorio de origen

The MIT License (MIT)

Copyright (c) 2026 Henry Prince

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the Software), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Fixture XMind propio

tests/fixtures/xmind/xmind-md-smoke-test.xmind está documentado como artefacto generado por la propia CI del proyecto (run histórico #209). Su README registra SHA-256 y contenido de prueba. No se ha identificado en el árbol una atribución o recurso gráfico externo. La apertura manual se realizó en XMind Desktop 26.05.01107. La conclusión de autoría se basa en el registro de generación del proyecto; conviene conservarlo y no añadir contenido de terceros sin documentarlo.

## Ejemplos y recursos

- examples/xmind-smoke-test.md: contenido de prueba redactado para el proyecto; no se han identificado citas o recursos externos.
- examples/constitucion.md: contiene texto de ejemplo relacionado con la Constitución Española y un enlace a BOE. El artículo 13 del texto refundido de la Ley de Propiedad Intelectual excluye de su objeto las disposiciones legales y reglamentarias y determinados actos públicos. Fuente oficial: https://www.boe.es/eli/es/rdlg/1996/04/12/1/con/20200708. Esta observación se limita al texto normativo; no cubre imágenes, comentarios, selecciones, anotaciones o materiales editoriales añadidos.
- La referencia histórica a `assets/escudo.png` se corrigió en la auditoría funcional: `examples/constitucion.md` y `examples/ir/constitucion.json` apuntan ahora a `examples/assets/escudo.svg`, un recurso ilustrativo original versionado y comprobado por tests. No se ha incluido ni identificado un escudo gráfico de terceros.
- examples/ir/constitucion.json es un ejemplo de datos IR y no contiene un archivo de imagen binario; la ruta de recurso indicada es solo una referencia.

No se han encontrado directorios de dependencias vendorizadas, fuentes de iconos, tipografías, imágenes o bibliotecas de terceros en el árbol actual. Esta comprobación es una inspección del contenido versionado y no una certificación legal de titularidad.

## Acciones de GitHub

El workflow usa actions/checkout@v5, actions/setup-python@v6 y actions/upload-artifact@v6. Se verificó el campo runs.using de los tres action.yml en esas referencias: todos declaran node24. Los repositorios oficiales de las tres acciones publican licencia MIT:

- https://github.com/actions/checkout/blob/main/LICENSE
- https://github.com/actions/setup-python/blob/main/LICENSE
- https://github.com/actions/upload-artifact/blob/main/LICENSE

Se ejecutan en GitHub Actions y no se incorporan como código al paquete Python. Las versiones están referenciadas mediante tags mayores, no SHA inmutable; fijar SHA es una mejora de reproducibilidad y cadena de suministro, no una condición de copyright detectada. La migración de Node.js 20 a Node.js 24 se validó en GitHub Actions run [42996452355](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42996452355).

## Conclusión de auditoría

1. No se ha detectado una incompatibilidad evidente entre la licencia MIT del código propio y las licencias declaradas de las dependencias directas/herramientas inventariadas.
2. El fixture externo de CI declara MIT en el repositorio de origen; se ha añadido atribución explícita y el fixture no forma parte de las distribuciones Python.
3. El fixture manual del proyecto aparece generado por la CI propia, según su documentación.
4. El ejemplo constitucional se apoya en texto normativo sujeto a la exclusión del artículo 13 LPI; su recurso gráfico actual es un SVG ilustrativo original versionado.
5. El inventario de dependencias transitivas no está cerrado porque no hay lockfile ni SBOM de resolución. No debe describirse como inventario exhaustivo.
6. Antes de publicar, mantener este aviso dentro del repositorio y resolver la referencia rota al recurso assets/escudo.png. Si se incorporan imágenes o fixtures externos, registrar origen, licencia, atribución y checksum.

Este documento es un inventario técnico de procedencia, no asesoramiento jurídico ni una garantía sobre la titularidad de todos los elementos.