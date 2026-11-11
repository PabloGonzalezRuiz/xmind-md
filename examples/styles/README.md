# Laboratorio de estilos personalizados

Este laboratorio contiene cuatro temas visuales independientes para aprender a construir catálogos YAML y aplicarlos a documentos Markdown.

## Ejemplos

| Tema | Catálogo | Documento |
|---|---|---|
| Académico | [academico.yaml](academico.yaml) | [academico.md](academico.md) |
| Legislación | [legislacion.yaml](legislacion.yaml) | [legislacion.md](legislacion.md) |
| Minimalista | [minimalista.yaml](minimalista.yaml) | [minimalista.md](minimalista.md) |
| Alto contraste | [alto-contraste.yaml](alto-contraste.yaml) | [alto-contraste.md](alto-contraste.md) |

## Cómo probarlos

Desde la raíz del repositorio, ejecuta:

```bash
xmind-md examples/styles/academico.md --styles examples/styles/academico.yaml --output academico.xmind
xmind-md examples/styles/legislacion.md --styles examples/styles/legislacion.yaml --output legislacion.xmind
xmind-md examples/styles/minimalista.md --styles examples/styles/minimalista.yaml --output minimalista.xmind
xmind-md examples/styles/alto-contraste.md --styles examples/styles/alto-contraste.yaml --output alto-contraste.xmind
```

Abre cada archivo generado con XMind y compara el resultado. Los archivos `.xmind` se generan localmente: el repositorio contiene los fuentes Markdown y YAML para que puedas modificarlos y repetir la exportación.

## Qué estudiar en cada ejemplo

1. **Académico:** jerarquía visual sobria, tipografía y estilos semánticos reutilizables.
2. **Legislación:** diferenciación de normas, artículos y conceptos clave.
3. **Minimalista:** uso deliberado de pocos atributos y ausencia de decoración innecesaria.
4. **Alto contraste:** contraste marcado entre texto, fondo y bordes.

## Personalizar un ejemplo

1. Duplica el par `.md` + `.yaml`.
2. Cambia primero los valores de `topic.text` y, si lo necesitas, `topic.background` y `topic.border`.
3. Añade estilos bajo `style_sets.<NOMBRE>.styles`.
4. Asigna el estilo con una directiva `:::xmind` inmediatamente antes del encabezado correspondiente.
5. Exporta y comprueba el resultado en XMind.

Los catálogos utilizan únicamente propiedades de tema contempladas por el perfil de exportación documentado en [la guía de estilos](../../docs/user-guide/styles-and-themes.md). La apariencia final puede variar según la versión de XMind.
