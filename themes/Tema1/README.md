# Tema1

Directorio reservado para el primer tema XMind de PMD.

## Estado

- [ ] Recibir y analizar `Tema1.xmind`.
- [ ] Documentar la jerarquía y las etiquetas con sus rutas completas.
- [ ] Analizar estilos explícitos y comportamiento de herencia.
- [ ] Identificar la representación de tablas de árbol y sus celdas.
- [ ] Generar y validar los artefactos derivados cuando estén implementados los conversores.

## Archivos previstos

| Archivo | Función | Estado |
|---|---|---|
| `Tema1.xmind` | Fuente editable del tema | Pendiente de recibir |
| `Tema1.md` | Markdown de origen, si procede | Pendiente |
| `Tema1.pmd` | Representación PMD generada | No generado |
| `Tema1.yaml` | Configuración de etiquetas y estilos generada | No generado |
| `Tema1.svg` | Vista previa del árbol de etiquetas | No generado |

El archivo XMind será la fuente editable de verdad. Los archivos derivados se generarán de forma coherente desde una representación intermedia común; no deben editarse manualmente.

## Convenciones acordadas para PMD

- La raíz identifica el tema y no es una etiqueta.
- Cada etiqueta se identifica mediante su ruta jerárquica completa.
- El separador canónico de rutas es el punto (`.`).
- Los identificadores de etiqueta deben ser únicos en toda la estructura.
- Los nombres individuales de etiqueta no pueden contener el separador `.`.
- La resolución de formatos por defecto seguirá una herencia recursiva descendente, con fallback ascendente al padre y prioridad para los valores explícitos. La resolución se aplicará propiedad por propiedad.

Estas convenciones describen el diseño acordado; su correspondencia exacta con los datos internos de XMind se comprobará al analizar el archivo.
