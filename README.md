# XMind MD

**XMind MD** es un proyecto para describir mapas mentales mediante Markdown enriquecido y convertir esa descripción en un modelo intermedio independiente del formato de salida.

La idea central es separar cuatro capas:

1. **Documento fuente:** Markdown legible y editable.
2. **Parser:** interpreta encabezados y metadatos.
3. **Modelo intermedio:** representa el mapa sin depender de XMind ni de una biblioteca concreta.
4. **Adaptadores:** transforman el modelo al formato de destino (el primer objetivo es `.xmind`).

## Estado actual

<badge>Prototipo inicial</badge>

Esta primera versión implementa:

- Jerarquía de temas a partir de encabezados Markdown (`#` a `######`).
- Metadatos `@conjunto(...)` y `@estilo(...)` asociados al siguiente encabezado.
- Modelo intermedio JSON.
- Resolución inicial de estilos definidos en YAML.
- CLI para validar y generar el JSON intermedio.
- Pruebas automatizadas y workflow de GitHub Actions.

**Todavía no exporta archivos `.xmind`.** El adaptador actual escribe JSON para poder validar primero la gramática y el modelo. La exportación real se incorporará cuando esté verificada contra el formato y la versión objetivo de XMind.

## Instalación local

Python 3.10 o superior:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

python -m pip install -e ".[dev]"
```

## Uso

```bash
xmind-md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json
```

También puede ejecutarse como módulo:

```bash
python -m xmind_md examples/constitucion.md --styles config/styles.yaml --output output/constitucion.json
```

## Ejemplo de Markdown

```md
@conjunto(TAI_LEGISLACION)
# Constitución Española

## Título preliminar

@estilo(concepto_importante)
### Artículo 1
- España se constituye en un Estado social y democrático de Derecho.
```

Los metadatos deben aparecer antes del encabezado al que se aplican. Los elementos de lista se conservan como contenido textual del tema en esta fase inicial.

Consulta [docs/grammar.md](docs/grammar.md) para la gramática prevista.

## Estructura

- `src/xmind_md/`: parser, modelo, estilos y adaptadores.
- `config/`: conjuntos de estilos.
- `examples/`: documentos de ejemplo.
- `tests/`: pruebas.
- `.github/workflows/`: integración continua.

## Desarrollo

```bash
pytest
```

Las decisiones de diseño y las limitaciones conocidas se documentarán en `docs/`.
