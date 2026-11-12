# Parser PMD 1.0.0

**Estado:** implementado y validado en la Fase 5. **Salida:** IR 1.1.0.  
**API:** `xmind_md.ir_parser.parse_pmd_markdown()` y `parse_pmd_file()`.

## 1. Uso desde Python

Analizar un archivo:

```python
from xmind_md.ir_parser import parse_pmd_file

mind_map = parse_pmd_file("examples/pmd/constitucion-estructura.pmd.md")
assert mind_map.ir_version == "1.1.0"
```

Analizar texto:

```python
from xmind_md.ir_parser import parse_pmd_markdown

source = """---
pmd_version: "1.0.0"
title: Mapa de estudio
catalog:
  id: xmind-md.study
  version: "1.0.0"
---

# Mapa de estudio
"""
mind_map = parse_pmd_markdown(source, source_path="estudio.pmd.md")
```

Ambas funciones devuelven un objeto `MindMap` del IR canónico, validado. Los errores de sintaxis, referencias o semántica PMD se notifican como `PMDParseError`, subclase de `ValueError`.

`source_path` participa en la generación determinista de IDs de temas que no declaran `id`. Si no se especifica, se usa `<memory>`. Al analizar archivos, `parse_pmd_file()` utiliza la ruta del archivo.

Se puede proporcionar un catálogo alternativo como mapping Python:

```python
mind_map = parse_pmd_markdown(source, catalog=catalog_data)
```

El catálogo suministrado debe coincidir exactamente con el `id` y la `version` del front matter. Si no se proporciona uno y el documento declara `catalog: xmind-md.study@1.0.0`, se utiliza el catálogo de referencia incluido en el paquete.

## 2. Qué valida

- Front matter obligatorio, versión PMD exacta, mappings cerrados y metadatos.
- YAML seguro: claves duplicadas, alias, fechas implícitas, tags no admitidos y valores no representables no se aceptan.
- Encabezados ATX H1–H6, directiva `:::pmd` asociada al encabezado siguiente y directivas PMD globales/notas.
- IDs explícitos únicos y generación determinista SHA-256 para temas sin ID.
- Referencias `parent`, incluidas referencias adelantadas; árbol conectado, sin ciclos y con un único padre.
- Existencia de roles y estilos en el catálogo versionado; referencias visuales y valores de overrides.
- Rutas y tipos de `style_overrides` contra las propiedades presentes en defaults y estilos del catálogo. `null` se conserva como reinicio explícito; `inherited` se rechaza.
- `tree_table`: filas/celdas no vacías, IDs explícitos, referencias a hijos directos, sin duplicados y cobertura exacta de los hijos.
- Anotaciones, marcadores (incluidos IDs explícitos), notas, enlaces y entidades globales mediante los contratos IR existentes.
- Validación final del documento IR 1.1.0.

La sintaxis abreviada de `structure.rows[].cells` (lista de IDs) se normaliza a `TreeTableCell(topic_id=...)`. El contenido de las celdas permanece en los temas hijos; no se duplica.

## 3. Separación respecto al parser Markdown existente

`parse_markdown_ir()` y `parse_file_ir()` mantienen su contrato actual y siguen produciendo IR 1.0.0. El parser PMD es una API independiente. Reutiliza el analizador de bloques Markdown para el contenido común, pero procesa front matter, directivas, roles, referencias y estructuras PMD en una capa separada.

No se reinterpretan las directivas legacy `:::xmind` dentro de PMD 1.0.0. La gramática PMD normativa sigue siendo [pmd-language-spec.md](pmd-language-spec.md).

## 4. Qué no hace todavía

- No hay comando CLI para PMD.
- No convierte Markdown convencional a PMD mediante IA; corresponde a la Fase 6.
- No ejecuta la cascada completa del catálogo (defaults, reglas semánticas/estructurales, herencia por primer hijo y resolución de estilos). El parser valida y conserva roles, referencias y overrides; la política de herencia se registra como metadato PMD.
- No transforma el catálogo PMD en los `style_sets/styles` del resolutor IR 1.x.
- El adaptador XMind no exporta todavía roles/estructuras IR 1.1.0; su ampliación corresponde a la Fase 7.
- No se ha añadido una dependencia runtime para validar JSON Schema; el parser valida los contratos necesarios directamente y la CI comprueba los fixtures.

Por tanto, que un documento PMD se convierta en IR 1.1.0 válido no significa que ya pueda exportarse a XMind ni que se hayan resuelto visualmente sus estilos PMD.

## 5. Pruebas

Las pruebas están en `tests/test_pmd_parser.py` e incluyen ambos ejemplos de referencia, árbol de tabla, roles, estilos, referencias adelantadas, IDs deterministas, notas, marcadores, errores, YAML estricto, overrides y compatibilidad con el parser Markdown.

La evidencia de CI de cierre de Fase 5 está registrada en [development-status.md](development-status.md).
