# Auditoría de consolidación del modelo

**Fecha:** 2026-11-12  
**Base de código:** `05efc482c333b266bf1a2bd5fbf2f3fdee129de7`  
**Rama de trabajo:** `architecture/pmd-ir-roadmap`  
**Alcance:** Fase 1.1 — inventario inicial de responsabilidades y consumidores conocidos. No se han modificado módulos Python.

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
- [ ] Confirmar exportaciones públicas documentadas y posibles consumidores externos.
- [ ] Crear fixtures de caracterización con salidas IR esperadas para los casos críticos del parser.
- [ ] Añadir pruebas de equivalencia para IDs, procedencia, recursos y entidades globales.
- [ ] Ejecutar suite completa y guardar la ejecución CI de referencia de esta rama.

## 6. Próximo paso técnico

Antes de cambiar el parser, añadir pruebas de caracterización independientes de la implementación que validen la salida IR actual. Después, diseñar un AST sintáctico mínimo que preserve la información necesaria para construir IR sin convertir un modelo de dominio legacy. La API legacy podrá delegar en esa ruta y adaptar la salida solo mientras exista una necesidad de compatibilidad.

## 7. Límites de esta auditoría

Esta tarea es una inspección documental/código estática sobre la base indicada. No se ha ejecutado pytest localmente, no se han añadido pruebas, no se ha cambiado el parser ni se ha retirado el modelo legacy. La CI nueva de la rama deberá verificar los commits documentales; la migración de código solo se considerará completada con pruebas específicas y CI verde.
