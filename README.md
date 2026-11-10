# XMind MD

**XMind MD** es un proyecto para describir mapas mentales mediante Markdown enriquecido y convertir esa descripción en un modelo intermedio independiente del formato de salida.

La idea central es separar cuatro capas:

1. **Documento fuente:** Markdown legible y editable.
2. **Parser:** interpreta encabezados y metadatos.
3. **Modelo intermedio:** representa el mapa sin depender de XMind ni de una biblioteca concreta.
4. **Adaptadores:** transforman el modelo al formato de destino (JSON de inspección y XMind moderno).

## Documentación del proyecto

La documentación está organizada para que una persona o una IA pueda entender, reconstruir y continuar el proyecto:

- **[Prompt maestro para reconstruir el proyecto](docs/ai-reconstruction-prompt.md):** contexto autónomo, objetivos, arquitectura, reglas de diseño, estado real y protocolo de trabajo para otra IA.
- **[Estado de desarrollo](docs/development-status.md):** seguimiento operativo actualizado tras cada tarea, hoja de ruta, decisiones vigentes, evidencias y próximo paso.
- [Arquitectura](docs/architecture.md): capas, flujo de datos, contratos e invariantes.
- [Catálogo de archivos](docs/file-reference.md): función de cada archivo y dónde deben realizarse los cambios.
- [Gramática Markdown](docs/grammar.md): sintaxis reconocida y limitaciones actuales.
- [Guía de desarrollo](docs/development.md): instalación, ejecución, pruebas y ciclo de contribución.
- [Evaluación del motor XMind](docs/xmind-engine-evaluation.md): alternativas estudiadas y decisión técnica para generar `.xmind`.
- [Adaptador XMind](docs/xmind-adapter.md): formato generado, mapeos implementados y limitaciones actuales.
- [Pruebas de integración XMind](docs/xmind-integration-tests.md): fixture externo, validaciones automatizadas y pasos para abrir el artefacto de prueba en XMind Desktop.

## Estado actual

**Estado:** prototipo inicial

Esta primera versión implementa:

- Jerarquía de temas a partir de encabezados Markdown (`#` a `######`).
- Metadatos `@conjunto(...)` y `@estilo(...)` asociados al siguiente encabezado.
- Modelo intermedio IR 1.0.0 y exportación JSON para inspección.
- Resolución de estilos definidos en YAML.
- CLI para generar JSON o libros XMind modernos (`.xmind`) a partir del IR canónico.
- Adaptador XMind experimental (ZIP + JSON), con temas jerárquicos, IDs estables, relaciones, notas, etiquetas, marcadores y estilos básicos.
- Pruebas automatizadas del adaptador y de integración con un fixture `.xmind` externo descargado por GitHub Actions.
- Generación en CI de un archivo `.xmind` descargable para la comprobación manual en XMind Desktop.

**El adaptador XMind es todavía experimental.** La generación automatizada y las pruebas estructurales no acreditan por sí solas la apertura, inspección y guardado en XMind Desktop. Las limitaciones están detalladas en [xmind-adapter.md](docs/xmind-adapter.md).

## Instalación local

Python 3.10 o superior:

~~~bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install -e ".[dev]"
~~~

## Uso

El formato se deduce de la extensión del archivo de salida:

~~~bash
# JSON del modelo intermedio
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json

# Libro XMind
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.xmind
~~~

También puede indicarse explícitamente con `--format json` o `--format xmind`. Si se utiliza una extensión conocida (`.json` o `.xmind`), debe coincidir con el formato solicitado. Para otra extensión es obligatorio indicar `--format`.

La misma interfaz está disponible como módulo:

~~~bash
python -m xmind_md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.xmind
~~~

La exportación XMind resuelve los estilos antes de llamar al adaptador. Las construcciones IR que el perfil XMind actual no puede representar se rechazan con un error; consulta la [matriz de capacidades](docs/xmind-adapter.md).

## Ejemplo de Markdown

~~~md
@conjunto(TAI_LEGISLACION)
# Constitución Española

## Título preliminar

@estilo(concepto_importante)
### Artículo 1
- España se constituye en un Estado social y democrático de Derecho.
~~~

Los metadatos deben aparecer antes del encabezado al que se aplican. Los elementos de lista se conservan como contenido textual del tema en esta fase inicial.

## Estructura

- `src/xmind_md/`: parser, modelo, estilos y adaptadores JSON/XMind.
- `config/`: conjuntos de estilos.
- `examples/`: documentos de ejemplo.
- `tests/`: pruebas.
- `docs/`: documentación técnica y prompt de reconstrucción.
- `.github/workflows/`: integración continua.

## Desarrollo

~~~bash
python -m pytest
~~~

El código incluye docstrings y comentarios en español para explicar responsabilidades, decisiones y limitaciones. La norma para futuros cambios está descrita en [development.md](docs/development.md).
