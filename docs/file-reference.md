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
| model.py | Define MindMap y Topic, el modelo intermedio y los bloques de contenido estructurados. | Conocer XMind, Markdown o detalles de serialización externos. |
| parser.py | Convierte front matter, encabezados, directivas y bloques Markdown en el IR; valida jerarquía e IDs. | Escribir archivos ni resolver propiedades visuales específicas de XMind. |
| styles.py | Lee YAML y resuelve conjuntos/estilos. | Convertir propiedades a XML/JSON interno de XMind. |
| cli.py | Coordina las operaciones y gestiona argumentos/errores. | Acumular reglas de parsing o exportación. |

### Adaptadores: src/xmind_md/adapters/

| Archivo | Responsabilidad |
|---|---|
| __init__.py | Declara el paquete de adaptadores y su contrato general. |
| json_adapter.py | Escribe una representación JSON del modelo intermedio. |
| xmind_adapter.py | Genera una primera versión del formato moderno `.xmind` mediante ZIP + JSON nativo Python; valida el subconjunto soportado y rechaza características pendientes. La compatibilidad con XMind Desktop aún no está verificada. |

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
| style-system.md | Catálogo de propiedades visuales, conjuntos, herencia y resolución de estilos. |
| ai-reconstruction-prompt.md | Prompt autónomo para que otra IA reconstruya y continúe el proyecto. |
| development.md | Instalación, ejecución, pruebas y ciclo de contribución. |
| xmind-engine-evaluation.md | Comparación de motores y decisión de arquitectura para el adaptador XMind. |
| xmind-adapter.md | Contrato, mapeos, características soportadas y limitaciones de la primera versión del adaptador. |

## Ejemplos: examples/

| Archivo | Función |
|---|---|
| constitucion.md | Documento de muestra para probar encabezados, contenido y directivas de estilo. |

Los ejemplos también actúan como fixtures legibles: al cambiar la gramática, deben actualizarse y añadirse pruebas.

## Pruebas: tests/

| Archivo | Función |
|---|---|
| test_parser.py | Comprueba gramática enriquecida, bloques estructurados, directivas, referencias y errores. |
| test_styles.py | Comprueba la resolución de estilos desde un conjunto heredado. |
| test_xmind_adapter.py | Comprueba JSON, árbol de temas, IDs, relaciones, estilos básicos y estructura ZIP del adaptador XMind. |

Toda funcionalidad nueva debe tener pruebas. No basta con modificar un ejemplo o comprobar visualmente el JSON.

## Automatización: .github/workflows/

| Archivo | Función |
|---|---|
| ci.yml | Ejecuta la instalación y las pruebas en GitHub Actions. |

## Salida: output/

El directorio está reservado para resultados locales. .gitkeep conserva el directorio en Git y .gitignore excluye los resultados generados.


## Cambios del paso 5 (segunda fase)

- `parser.py`: loader YAML seguro con detección de claves duplicadas, listas anidadas, validación de IDs explícitos, tipos de directivas y referencias globales.
- `styles.py`: carga de estilos globales y conjuntos; fusión recursiva; herencia de conjuntos; precedencia de definiciones del documento frente a las externas; overrides locales.
- `tests/test_parser.py`: casos de listas anidadas, YAML duplicado, IDs inválidos y tipos del front matter.
- `tests/test_styles.py`: precedencia, herencia, fusión y errores de referencias.
