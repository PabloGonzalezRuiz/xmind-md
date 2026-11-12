# Temas XMind

Este directorio contiene un subdirectorio por cada tema visual de PMD.

Cada tema tendrá su propio directorio y utilizará el archivo `.xmind` como fuente editable de verdad. Las representaciones derivadas (PMD, YAML y SVG) se generarán a partir de una representación intermedia común una vez definida e implementada esa conversión.

## Estructura prevista

```text
themes/
└── Tema1/
    ├── Tema1.xmind   # Fuente editable del tema
    ├── Tema1.md      # Markdown de origen, cuando proceda
    ├── Tema1.pmd     # Representación PMD generada
    ├── Tema1.yaml    # Esquema de estilos generado
    ├── Tema1.svg     # Vista previa del árbol de etiquetas
    └── README.md     # Documentación del tema
```

Los archivos derivados no deben editarse manualmente. No se crearán archivos derivados hasta que exista una fuente XMind analizada y una conversión validada.
