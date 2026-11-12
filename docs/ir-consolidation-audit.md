# Auditoría de consolidación del modelo

**Fecha:** 2026-11-12  
**Base de código:** `05efc482c333b266bf1a2bd5fbf2f3fdee129de7`  
**Rama de trabajo:** `architecture/pmd-ir-roadmap`  
**Alcance:** Fase 1.1 — inventario inicial y caracterización del contrato IR actual. No se ha modificado el parser ni se ha retirado código legacy.

## 1. Hallazgo principal

La ruta CLI ya parte del IR, pero el parser no lo construye directamente:

```text
Markdown
  → parser.parse_markdown()
  → model.MindMap / model.Topic (modelo legacy)
  → ir_parser._convert() / _topic()
  → ir.MindMap / ir.Topic (IR 1.0.0)
  → CLI / resolutor IR / adaptadores
```

Esto significa que la duplicidad no está en los adaptadores, sino en la representación que construye el parser y en la conversión puente. La documentación debe distinguir entre "los adaptadores están migrados" y "el parsing construye IR directamente".

## 2. Inventario por módulo

| Componente | Estado observado | Acción objetivo |
|---|---|---|
| `parser.py` | Analiza Markdown y crea `model.MindMap`/`model.Topic`; conserva API `parse_markdown()` y `parse_file()`. | Separar sintaxis temporal de construcción de dominio y proporcionar una ruta de salida IR directa. |
| `model.py` | Dataclasses legacy `MindMap` y `Topic`, con listas de temas raíz y campos antiguos/duplicados. | Mantener temporalmente como compatibilidad; retirar cuando los consumidores estén migrados. |
| `ir_parser.py` | Contiene conversión de bloques, temas, assets, relaciones, límites, resúmenes y funciones `parse_*_ir`; llama al parser legacy. | Absorber la construcción IR en el parser/capa de construcción y eliminar el puente una vez cubierto por pruebas. |
| `ir/entities.py` | Entidades canónicas neutrales IR 1.0.0. | Conservar como contrato canónico; ampliar solo mediante decisión de versionado. |
| `ir/validation.py` | Validación semántica del IR. | Conservar y reforzar al ampliar IR. |
| `styles.py` | Importa `model.Topic`; mantiene resolución legacy y resolución IR. | Migrar consumidores a IR y retirar la ruta legacy tras pruebas de compatibilidad. |
| `cli.py` | Utiliza `parse_file_ir()`; los adaptadores reciben IR. | Conservar la orquestación y la API CLI. |
| `adapters/json_adapter.py` | Consume IR. | Conservar; no necesita conocer el modelo legacy. |
| `adapters/xmind_adapter.py` | Consume IR. | Conservar; evolución estructural en fase posterior. |

## 3. Consumidores y pruebas localizados

- `tests/test_parser.py` importa y prueba `parse_markdown()` y `parse_file()`; protege la API legacy y detalles del parser.
- `tests/test_ir_parser.py` prueba `parse_markdown_ir()` y `parse_file_ir()`; cubre temas, contenido, recursos, directivas, relaciones y errores.
- `tests/test_styles.py` instancia `model.Topic`/`model.MindMap` y prueba la resolución legacy.
- `tests/test_ir_styles.py` prueba la resolución sobre entidades IR.
- `tests/test_cli.py` cubre la interfaz CLI; la implementación de CLI usa `parse_file_ir()`.
- Los adaptadores y sus pruebas se apoyan en IR; no se ha observado una dependencia directa de `model.py` en los adaptadores.

Este inventario corresponde a los archivos versionados inspeccionados. No demuestra que no existan consumidores externos de las funciones públicas legacy.

## 4. Riesgos de migración

1. Cambiar directamente `parse_markdown()` para que devuelva IR rompería el contrato observado en `tests/test_parser.py` y posiblemente consumidores externos.
2. Mantener dos árboles de dominio tras la migración perpetuaría la duplicidad que queremos eliminar.
3. Los IDs deterministas dependen de `source_path`, título, IDs de origen y reglas internas; deben conservarse mediante pruebas.
4. La conversión de imágenes/recursos debe evitar IDs duplicados y preservar referencias.
5. Relaciones, límites y resúmenes globales se validan hoy en el parser legacy y se convierten después; su validación no debe perderse.
6. La ruta legacy de estilos tiene pruebas propias. Debe deprecarse con aviso y compatibilidad explícita o migrarse con un adaptador.
7. No debe confundirse una salida JSON válida con equivalencia semántica del documento.

## 5. Trabajo necesario para cerrar Fase 1.1

- [x] Inspección de módulos de parsing, IR, estilos, CLI y adaptadores.
- [x] Inventario de consumidores internos y suites de prueba localizados.
- [x] Revisar exportaciones públicas del paquete: `xmind_md.__init__` solo publica `__version__`; las funciones de parsing son importables desde sus módulos. No es posible inferir consumidores externos a partir del repositorio.
- [x] Crear `tests/fixtures/ir-characterization.md` y una prueba de caracterización que fija IDs, metadatos, estilos, estructura, contenido, anotaciones, enlaces, recursos y entidades globales.
- [x] Añadir prueba comparativa legacy/IR para identidad, jerarquía, tipos de bloque, estilos, anotaciones, enlaces, recursos y entidades globales.
- [x] CI de referencia de caracterización: [run 43221440866](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43221440866), commit `cef9359486b438abf50b750dffa03b5fd6c843c4`; 163 pruebas correctas en Python 3.10, 3.11 y 3.12 y build/install correcto.

## 6. Resultado de la caracterización

Se añadió el fixture `tests/fixtures/ir-characterization.md` y la prueba `test_characterization_fixture_preserves_the_complete_ir_contract`. El caso cubre:
- IDs deterministas del mapa/hoja/tema y serialización reproducible para una entrada y ruta iguales.
- Metadatos, estilos, conjuntos de estilos y extensiones.
- Procedencia de encabezados y rangos de contenido.
- Párrafos con formato y enlaces internos, listas anidadas, tablas, citas, divisores, imágenes y código.
- Etiquetas, marcadores, tareas, notas y enlaces externos.
- Inventario de assets y referencias de recursos.
- Relaciones, límites y resúmenes.

**Observación de contrato:** el parser actual asigna a los temas `source.file`, `line_start` y `line_end`; no rellena `source.markdown_heading`, aunque la especificación IR lo contempla como campo opcional y algunos ejemplos JSON lo muestran. La caracterización fija el comportamiento real sin introducir una modificación funcional no aprobada.

La prueba comparativa adicional verifica que el parser legacy y el IR conservan las mismas identidades, jerarquía, procedencia, referencias de estilo, anotaciones, enlaces, recursos y entidades globales en el fixture. La suite CI [43221440866](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43221440866) terminó correctamente: 163 pruebas por cada versión Python (3.10, 3.11 y 3.12) y distribución construida/instalada con éxito.

## 7. Próximo paso técnico

La caracterización inicial está completada. El siguiente trabajo es diseñar un AST sintáctico mínimo que preserve toda la información necesaria para construir IR directamente, sin convertir un modelo de dominio legacy. La API legacy podrá delegar en la ruta canónica y adaptar su resultado solo mientras exista una necesidad de compatibilidad.

## 8. Límites de esta auditoría

Esta tarea comenzó como inspección estática y se amplió con dos pruebas de caracterización en CI. No se ha ejecutado pytest localmente, no se ha cambiado el parser ni se ha retirado el modelo legacy. La CI de la rama ha validado las pruebas en Python 3.10, 3.11 y 3.12 y la construcción/instalación de distribuciones. La migración del parser solo se considerará completada cuando la ruta canónica construya IR directamente y las pruebas de regresión sigan verdes.
