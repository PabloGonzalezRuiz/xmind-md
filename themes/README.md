# Temas y referencias XMind

Este directorio reúne referencias visuales y estructurales para diseñar PMD y comprobar la reconstrucción de mapas XMind reales.

Cada subdirectorio puede contener exportaciones procedentes de XMind (`content.json`, SVG), Markdown producido por la importación nativa y documentación del análisis. No se presupone que el archivo `.xmind` original esté versionado ni que las exportaciones sean derivados generados por XMind MD.

## Estructura actual

```text
themes/
└── Tema1/
    ├── content.json   # Datos exportados desde XMind
    ├── Tema1.svg      # Exportación visual de XMind
    ├── Tema1.md       # Markdown de referencia
    └── README.md      # Análisis y tareas pendientes
```

## Uso de las referencias

- `content.json` permite estudiar jerarquía, estructura, estilos y marcadores.
- `Tema1.svg` sirve como referencia visual. El futuro SVG generado debe ser lo más fiel posible a la apariencia original de XMind, sin obligación de reproducir literalmente su XML.
- `Tema1.md` permite identificar qué información conserva y qué pierde la ruta nativa de Markdown.
- Los análisis deben distinguir los datos explícitos de XMind de las inferencias semánticas que PMD o la IA puedan añadir.

El archivo XMind original puede añadirse cuando esté disponible. No debe describirse como fuente versionada mientras no exista en el repositorio.
