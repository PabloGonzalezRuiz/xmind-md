# Catálogo de archivos

Este documento explica la finalidad de cada archivo versionado y qué tipo de cambios deben realizarse en él.

## Raíz del repositorio

| Archivo | Función | Cuándo modificarlo |
|---|---|---|
| README.md | Presentación, estado, instalación y uso rápido. | Cuando cambie el estado funcional, la instalación o el flujo básico. |
| pyproject.toml | Construcción del paquete, dependencias, comando CLI y configuración de pruebas/lint. | Al añadir dependencias, comandos o herramientas. |
| .gitignore | Evita versionar cachés, entornos virtuales y artefactos locales. | Al introducir nuevos artefactos generados. |

## Código fuente: src/xmind_md/

| Archivo | Responsabilidad | No debe hacer |
|---|---|---|
| __init__.py | Identidad del paquete y versión pública. | Ejecutar el programa o importar adaptadores innecesariamente. |
| __main__.py | Permite python -m xmind_md. | Duplicar la lógica de la CLI. |
| model.py | Define MindMap y Topic, el modelo intermedio. | Conocer XMind, Markdown o detalles de serialización externos. |
| parser.py | Convierte la gramática Markdown enriquecida en el modelo. | Escribir archivos ni resolver propiedades visuales específicas de XMind. |
| styles.py | Lee YAML y resuelve conjuntos/estilos. | Convertir propiedades a XML/JSON interno de XMind. |
| cli.py | Coordina las operaciones y gestiona argumentos/errores. | Acumular reglas de parsing o exportación. |

### Adaptadores: src/xmind_md/adapters/

| Archivo | Responsabilidad |
|---|---|
| __init__.py | Declara el paquete de adaptadores y su contrato general. |
| json_adapter.py | Escribe una representación JSON del modelo intermedio. |

El futuro adaptador XMind debe añadirse como módulo separado, por ejemplo xmind_adapter.py, sin reemplazar el modelo neutral.

## Configuración: config/

| Archivo | Función |
|---|---|
| styles.yaml | Define conjuntos de estilos reutilizables y sus propiedades neutrales. |

No incluir aquí identificadores ni estructuras privadas de una biblioteca de exportación.

## Documentación: docs/

| Archivo | Función |
|---|---|
| architecture.md | Explica capas, flujo de datos, contratos e invariantes. |
| file-reference.md | Catálogo de archivos y responsabilidades. |
| grammar.md | Sintaxis de los documentos fuente y límites del parser actual. |
| ai-reconstruction-prompt.md | Prompt autónomo para que otra IA reconstruya y continúe el proyecto. |
| development.md | Instalación, ejecución, pruebas y ciclo de contribución. |

## Ejemplos: examples/

| Archivo | Función |
|---|---|
| constitucion.md | Documento de muestra para probar encabezados, contenido y directivas de estilo. |

Los ejemplos también actúan como fixtures legibles: al cambiar la gramática, deben actualizarse y añadirse pruebas.

## Pruebas: tests/

| Archivo | Función |
|---|---|
| test_parser.py | Comprueba parsing, jerarquía, metadatos y errores de sintaxis. |
| test_styles.py | Comprueba la resolución de estilos desde un conjunto heredado. |

Toda funcionalidad nueva debe tener pruebas. No basta con modificar un ejemplo o comprobar visualmente el JSON.

## Automatización: .github/workflows/

| Archivo | Función |
|---|---|
| ci.yml | Ejecuta la instalación y las pruebas en GitHub Actions. |

## Salida: output/

El directorio está reservado para resultados locales. .gitkeep conserva el directorio en Git y .gitignore excluye los resultados generados.
