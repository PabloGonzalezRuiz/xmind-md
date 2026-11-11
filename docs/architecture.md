# Arquitectura de XMind MD

## 1. Propósito y estado

XMind MD convierte Markdown enriquecido en un modelo intermedio neutral (IR 1.0.0) y exporta ese modelo a JSON o a un libro XMind moderno (`.xmind`). La implementación principal es Python (>=3.10).

La arquitectura separa parsing, representación semántica, resolución de estilos y serialización. El adaptador XMind implementa un perfil parcial y validado; las capacidades no soportadas se rechazan explícitamente.

## 2. Flujo de datos real

```text
Markdown + front matter/directivas YAML
                  |
                  v
      parser.py (sintaxis/AST legacy)
                  |
                  v
       ir_parser.py (puente canónico)
                  |
                  v
             IR 1.0.0
              /      \
             v        v
     resolve_styles   json_adapter
             |        |
             v        v
       xmind_adapter  JSON IR
             |
             v
       libro .xmind
```

La CLI usa `parse_file_ir()`. La salida JSON serializa el IR. La salida XMind resuelve estilos y luego llama a `write_xmind()`. La selección del formato se realiza mediante `.json`, `.xmind` o `--format`.

## 3. Capas y responsabilidades

### 3.1 Entrada y parser

- `src/xmind_md/parser.py`: analiza el subconjunto documentado de Markdown enriquecido y conserva una API/modelo legacy.
- `src/xmind_md/ir_parser.py`: convierte el resultado al contrato IR 1.0.0, incluyendo temas, bloques, anotaciones, recursos, estilos, enlaces y entidades de hoja.
- La gramática implementada no equivale a CommonMark ni GFM completos. Su matriz y restricciones están en [grammar.md](grammar.md).

El parser no genera archivos XMind ni conoce estructuras privadas del formato de salida.

### 3.2 Modelo intermedio (IR)

Directorio: `src/xmind_md/ir/`.

El contrato neutral incluye `MindMap`, `Sheet`, `Topic`, `ContentBlock`, anotaciones, recursos, relaciones, límites, resúmenes y estados de estilo. El esquema JSON Draft 2020-12 y el ejemplo canónico están en `docs/ir-schema.json` y `examples/ir/constitucion.json`.

`src/xmind_md/model.py` mantiene el modelo legacy requerido por el parser y consumidores anteriores. No es el contrato que reciben los adaptadores.

### 3.3 Resolución de estilos

Archivo: `src/xmind_md/styles.py`.

`resolve_styles()` detecta el tipo de modelo y delega los documentos IR a `resolve_ir_styles()`; conserva también una ruta legacy. Para IR, la precedencia por propiedad es:

1. Defaults del sistema.
2. `metadata.style_defaults` del documento.
3. Conjunto efectivo.
4. Estilo nombrado.
5. Overrides locales.

El conjunto se hereda por descendencia y puede sustituirse en un tema. Las definiciones del documento prevalecen sobre las externas con el mismo nombre. La fusión es recursiva y no muta las definiciones originales; escribe el resultado en `style.resolved`. Se resuelven estilos de temas, notas, relaciones, límites y resúmenes.

La resolución neutral no implica que el adaptador XMind pueda traducir todas las propiedades. El adaptador mantiene su propio catálogo de propiedades admitidas y falla ante propiedades desconocidas.

### 3.4 Adaptadores

Directorio: `src/xmind_md/adapters/`.

- `json_adapter.py`: serializa el documento IR mediante su representación neutral.
- `xmind_adapter.py`: crea `content.json`, metadatos, manifiesto, miniatura y contenedor ZIP del formato XMind moderno.

El adaptador XMind recibe únicamente IR 1.0.0. No analiza Markdown, no resuelve estilos y no modifica el IR. Valida el perfil soportado y lanza `XMindAdapterError` ante construcciones no exportables. La matriz detallada está en [xmind-adapter.md](xmind-adapter.md).

### 3.5 CLI

Archivo: `src/xmind_md/cli.py`.

La CLI:
- recibe un Markdown de entrada y una ruta de salida obligatoria;
- acepta `--styles` para configuración YAML externa;
- admite `--format json|xmind`, o infiere el formato por extensión;
- analiza a IR mediante `parse_file_ir()`;
- resuelve estilos antes de exportar XMind;
- serializa JSON y, si se proporciona configuración externa, puede resolver estilos antes de serializar;
- comunica errores de E/S, formato y estilos por stderr y devuelve código 2.

El comando instalado es `xmind-md`; también está disponible `python -m xmind_md`.

### 3.6 Automatización y pruebas

- `tests/`: pruebas unitarias y de integración de parser, IR, estilos, adaptadores y CLI.
- `.github/workflows/ci.yml`: dos jobs Ubuntu/Python 3.12; el primero ejecuta instalación editable, Ruff, fixture, pytest y generación XMind; el segundo construye wheel/sdist, inspecciona metadatos/licencia, instala cada distribución en un entorno limpio y ejecuta una conversión CLI a JSON.
- `scripts/create_xmind_smoke.py`: genera un libro de comprobación para interoperabilidad manual.
- `scripts/verify_distributions.py`: comprueba que wheel/sdist contienen metadatos, LICENSE y módulos esenciales.
- `pyproject.toml`: metadatos de paquete, dependencias, entry point y configuración de herramientas.

La CI [42988289597](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/42988289597) completó ambos jobs: Ruff, 131 pruebas, generación XMind, build wheel/sdist, verificación de contenido/licencia e instalación limpia de ambas distribuciones con prueba CLI JSON. La CLI XMind desde los paquetes instalados sigue siendo una comprobación pendiente. La evidencia vigente se mantiene en [development-status.md](development-status.md) y [release-audit.md](release-audit.md).

## 4. Contratos e invariantes

1. El parser produce una representación neutral, no un archivo XMind.
2. El IR no importa librerías de exportación.
3. Los adaptadores consumen IR 1.0.0, no el modelo legacy.
4. El orden de temas, bloques y colecciones significativas se conserva.
5. Las referencias de estilo son simbólicas; las propiedades resueltas se almacenan separadamente.
6. El adaptador no interpreta Markdown ni resuelve estilos.
7. Las capacidades no implementadas se rechazan explícitamente; no se descartan silenciosamente.
8. La generación de un ZIP válido y las pruebas JSON no equivalen a compatibilidad completa con XMind Desktop.
9. La compatibilidad se declara por característica y evidencia de versión, no como promesa genérica.

## 5. Decisiones técnicas vigentes

- Python >= 3.10; CI actual en Python 3.12 sobre Ubuntu.
- Paquete con diseño `src/`.
- PyYAML como dependencia de ejecución.
- pytest, Ruff y jsonschema como dependencias de desarrollo.
- IR 1.0.0 como contrato canónico.
- JSON como formato de inspección.
- XMind moderno ZIP + JSON como formato de salida.
- Serialización XMind mediante biblioteca estándar de Python; los SDK externos son referencias técnicas, no dependencias obligatorias.
- Sin generación de temas flotantes en el modelo neutral.
- CI Linux/Ubuntu; la interoperabilidad Windows se verifica con XMind Desktop, no mediante un runner Windows.

## 6. Verificación de interoperabilidad

El fixture `tests/fixtures/xmind/xmind-md-smoke-test.xmind` fue abierto, inspeccionado, guardado, cerrado y reabierto por el usuario en XMind Desktop 26.05.01107 para Windows. Se comprobaron tema central, ramas, subtema, nota, etiqueta, marcador y relación.

Esta comprobación acredita esos elementos del fixture en esa versión. No demuestra que todos los elementos del IR, todos los estilos o todas las capacidades del formato XMind estén soportados.

## 7. Extensiones y limitaciones

Las capacidades del parser, del IR y del adaptador son distintas. Que el IR pueda representar una entidad no significa que el parser pueda crearla desde Markdown ni que el adaptador XMind pueda exportarla. Consultar:

- [Gramática Markdown](grammar.md).
- [Especificación IR](ir-specification.md).
- [Sistema de estilos](style-system.md).
- [Matriz del adaptador XMind](xmind-adapter.md).

## 8. Criterios para aceptar cambios

Cada cambio debe incluir:
- responsabilidad y capa afectada;
- cambios del IR si se introduce un concepto neutral nuevo;
- pruebas positivas y negativas;
- actualización de documentación y ejemplos;
- actualización de la matriz de capacidades;
- ejecución satisfactoria de CI antes de declarar el cambio validado.
