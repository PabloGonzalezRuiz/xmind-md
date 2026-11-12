# Intercambio Markdown ↔ XMind: comportamiento observado y límites

**Estado:** documentación de ingeniería inversa; 2026-11-12.  
**Ámbito:** exportación Markdown desde XMind Desktop y capacidades que necesitamos considerar al convertir Markdown de entrada.  
**Importante:** este documento separa observaciones verificadas en los archivos del repositorio de conclusiones generales aún no verificadas en distintas versiones de XMind.

## 1. Propósito

La importación Markdown de XMind es útil como transporte de texto y jerarquía, pero no constituye un formato de autoría completo para mapas con estructuras especiales y estilos elaborados. PMD debe cerrar esa brecha sin obligar a escribir anotaciones visuales extensas en Markdown.

Hay dos operaciones distintas que no deben confundirse:

- **XMind → Markdown:** exportación que realiza XMind. El archivo de referencia disponible es `themes/Tema1/Tema1.md`.
- **Markdown → XMind:** importación que realiza XMind, o conversión propia del proyecto. No se dispone en el repositorio de una matriz exhaustiva de importación nativa de XMind. Las capacidades del parser de XMind MD están documentadas en [grammar.md](grammar.md) y no son las capacidades de importación nativa de XMind.

## 2. Evidencia directa: exportación Tema1

El archivo `themes/Tema1/Tema1.md` exportado desde XMind contiene:

```md
# **Tema1**

- ListaBloque

- BloqueLey
    - Nombre
        - **RESUMEN**
            - **Titulo**
                - **Capitulo**
                    - **Articulo**
                        - **Cabecera**
                        - **cuerpo**
```

El ejemplo conserva:

- Los textos de los diez temas.
- Una representación aproximada de la jerarquía mediante un encabezado para la raíz y listas anidadas.
- Algunos énfasis Markdown, como negrita en determinados títulos.
- Separaciones en blanco y saltos de línea que forman parte de la exportación.

No conserva de forma recuperable en el Markdown:

- Los IDs originales de los temas.
- La diferencia entre estructura de árbol ordinaria y tabla de árbol.
- El rol de título superior de tabla y los roles de sus celdas.
- Los estilos visuales por tema ni los valores de la hoja.
- Los marcadores XMind.
- Posiciones, anchuras, formas, rellenos, bordes, conexiones y propiedades tipográficas.
- La correspondencia entre cada título y su objeto JSON/SVG.

La negrita no permite reconstruir por sí sola un estilo XMind. Es únicamente una pista de formato inline que puede ser deliberada o derivada de la presentación.

## 3. Consecuencia: pérdida de información

La conversión XMind → Markdown de esta referencia es **con pérdida**. Distintos mapas XMind pueden producir Markdown indistinguibles si solo difieren en color, forma, marcador o estructura visual. Por tanto, no es posible reconstruir el original de forma fiable a partir de ese Markdown únicamente.

Ejemplo de ambigüedad:

- Un nodo con negrita puede ser un título, un concepto importante o una celda de tabla.
- Dos hermanos en una lista pueden ser ramas de árbol o celdas de una tabla de árbol.
- La profundidad de indentación expresa relación textual/jerárquica, no necesariamente el tipo de estructura visual XMind.

No debemos intentar deducir detalles que la exportación no transporta. La IA puede inferir una representación probable a partir del contenido, pero debe marcar como inferidos los roles y estilos que no estén expresados en la fuente.

## 4. Jerarquía y listas: interpretación prudente

En Tema1, el primer encabezado Markdown representa el tema raíz y las listas representan los temas subordinados. Sin embargo, no debe suponerse que cualquier lista exportada por XMind equivale siempre a un árbol completo en todos los casos: el archivo de referencia es una muestra concreta, no una especificación de todas las versiones y opciones de exportación.

Para nuestro parser Markdown actual:

- Los encabezados ATX crean temas.
- Las listas ordenadas y no ordenadas crean bloques de contenido con elementos anidados; no crean temas.
- Por tanto, el Markdown de Tema1 no se puede importar con nuestro parser como el mismo árbol sin una transformación previa o un modo de conversión específico.
- La gramática implementada no es CommonMark/GFM completa.

Este último punto es especialmente importante para el conversor IA: deberá transformar la jerarquía expresada mediante listas en la estructura PMD de temas, si ese es el objetivo, en vez de enviar el Markdown exportado sin cambios al parser actual.

## 5. Markdown enriquecido de XMind MD no es el Markdown nativo de XMind

El proyecto ya implementa un subconjunto propio de Markdown enriquecido:

- Front matter YAML para metadatos y estilos.
- Encabezados ATX para crear temas.
- Directivas `:::xmind` asociadas al siguiente encabezado.
- Directivas para notas, relaciones, límites y resúmenes.
- Listas, tablas, código, citas, enlaces, imágenes y otros bloques dentro del contenido según la gramática documentada.
- Referencias a estilos y overrides.

Es una gramática de XMind MD, no una afirmación sobre la gramática que entiende el importador nativo de XMind Desktop. No debemos usar expresiones como “XMind soporta `:::xmind`” salvo que se esté hablando de nuestro parser.

## 6. Implicaciones para la conversión asistida por IA

La IA debería trabajar en dos pasadas conceptuales:

1. **Análisis de contenido:** identificar títulos, apartados, enumeraciones, definiciones, excepciones, referencias, tablas y relaciones.
2. **Construcción de intención PMD:** crear temas, bloques, estructuras especiales, roles semánticos y referencias a estilos del catálogo.

Reglas recomendadas:

- Mantener el texto original y el orden salvo que el usuario solicite normalización.
- No convertir automáticamente toda lista en ramas del mapa: distinguir listas de contenido de jerarquías de temas.
- No inferir una tabla de árbol únicamente porque existan dos o más elementos hermanos.
- Si la estructura visual no es explícita, usar reglas semánticas del perfil seleccionado y registrar la inferencia.
- Mantener separados el rol semántico (`article`, `section`, `exception`, `table_header`) y el estilo visual (`article_heading`, `cell_header`, etc.).
- Usar estilos del tema/catalogo, no escribir colores y propiedades de bajo nivel en cada nodo.
- Cuando la confianza sea baja o existan interpretaciones estructurales alternativas, producir PMD conservador o pedir una aclaración concreta.

## 7. Pruebas de conversión que faltan

Para convertir observaciones en una especificación fiable, se necesitan muestras de XMind Desktop adicionales:

- Exportar a Markdown un mapa sencillo de árbol con varios niveles.
- Exportar un mapa con listas como contenido interno de un tema.
- Exportar un mapa con tabla de árbol y varias celdas/filas.
- Exportar mapas con marcadores, etiquetas, notas y enlaces.
- Importar Markdown de control con encabezados, listas, tablas y énfasis y registrar el resultado en XMind.
- Repetir las pruebas en la versión de XMind Desktop que se vaya a soportar.

Registrar para cada prueba versión de XMind, opciones de exportación/importación, archivo fuente, archivo resultante y diferencias observadas.

## 8. Referencias internas

- [Tema1.md](../themes/Tema1/Tema1.md): Markdown real exportado por XMind.
- [Análisis de referencia Tema1](reference-analysis-tema1.md): comparación con JSON y SVG.
- [Gramática implementada de XMind MD](grammar.md): parser propio del proyecto.
- [Arquitectura](architecture.md): flujo actual Markdown → IR → adaptador.
- [Diseño PMD](pmd-design.md): dirección futura de conversión asistida por IA.

## 9. Estado de conocimiento

| Afirmación | Estado |
|---|---|
| Tema1.md conserva los títulos y una jerarquía aproximada | Observado directamente |
| Tema1.md no expresa tabla de árbol ni estilos/IDs/marcadores | Observado directamente |
| Las listas de nuestro parser actual son bloques de contenido, no temas | Verificado en gramática/código |
| Todo Markdown exportado por XMind se comporta igual que Tema1 | No demostrado |
| Importación nativa de XMind conserva o descarta cada construcción Markdown en todas las versiones | Pendiente de pruebas controladas |
| PMD debe representar semántica y estructuras sin depender de la sintaxis Markdown nativa | Decisión de diseño |

No presentar como comportamiento universal de XMind lo que solo se ha observado en una exportación concreta.
