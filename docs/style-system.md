# Sistema de estilos de XMind MD

**Versión de diseño:** 1.0-draft  
**Contrato IR objetivo:** 1.0.0  
**Estado:** diseño propuesto; resolución completa pendiente de implementación.

## 1. Objetivo

El sistema de estilos debe permitir describir la apariencia del mapa mediante propiedades neutrales, reutilizar configuraciones completas y sobrescribir solo las propiedades necesarias.

Debe cubrir los elementos visuales que XMind permite estilizar y mantener el núcleo independiente de su formato interno:

- Mapa y hoja.
- Temas.
- Texto enriquecido dentro de los temas.
- Ramas y conectores jerárquicos.
- Relaciones.
- Límites (boundaries).
- Resúmenes (summaries).
- Callouts.
- Texto y anotaciones cuando el adaptador de destino permita darles estilo.

El diseño distingue tres conceptos:

1. **Catálogo:** propiedades normalizadas, tipos, unidades y valores permitidos.
2. **Definiciones:** estilos y conjuntos reutilizables declarados en YAML.
3. **Resolución:** cálculo de propiedades efectivas por elemento antes de exportar.

El sistema no debe confundir estilos con estructura. Por ejemplo, el plegado de una rama, el orden de los temas y la estructura del mapa son datos de disposición o comportamiento, no colores ni tipografía.

## 2. Principios

1. Las claves del catálogo son neutrales y estables.
2. Ninguna clave del núcleo debe ser un nombre XML, JSON o atributo privado de XMind.
3. Las propiedades se agrupan por elemento y categoría.
4. Se combinan propiedades individualmente mediante fusión recursiva.
5. La ausencia de una propiedad significa heredar.
6. Un valor explícito sustituye el anterior.
7. `null` solicita restablecer la propiedad a su valor predeterminado.
8. Las listas y valores escalares se sustituyen completos; no se concatenan implícitamente.
9. La selección de un conjunto se hereda por la rama de temas, pero los valores visuales de un tema no se copian automáticamente a sus hijos.
10. Cada adaptador declara qué propiedades representa, aproxima o no admite.
11. Las propiedades desconocidas producen un diagnóstico; no se descartan silenciosamente.
12. La resolución debe ser determinista.

## 3. Modelo de datos del sistema de estilos

### 3.1 Estructura de configuración

La configuración externa utiliza estas secciones:

| Sección | Función |
|---|---|
| `version` | Versión del contrato de configuración de estilos |
| `defaults` | Valores generales para el mapa y los elementos |
| `styles` | Catálogo global de estilos con nombre |
| `style_sets` | Conjuntos reutilizables, con perfiles y estilos propios |
| `extensions` | Propiedades específicas de adaptadores |

Estructura de referencia:

~~~yaml
version: 1

defaults:
  elements:
    map: {}
    topic: {}
    branch: {}
    relationship: {}
    boundary: {}
    summary: {}
    summary_topic: {}
    callout: {}

styles: {}

style_sets: {}

extensions: {}
~~~

### 3.2 Elementos estilizados

| Tipo | Qué representa |
|---|---|
| `map` | Fondo y presentación global de la hoja |
| `topic` | Forma, relleno, borde y texto del tema |
| `branch` | Línea de conexión jerárquica entre padre e hijo |
| `relationship` | Línea independiente entre dos temas y su etiqueta |
| `boundary` | Marco que agrupa visualmente temas |
| `summary` | Trazo o llave que resume uno o varios temas |
| `summary_topic` | Apariencia del tema que contiene el texto del resumen |
| `callout` | Elemento de llamada asociado a un tema |

Un tema puede tener un perfil de rol: `root`, `main` o `subtopic`. El rol es una clasificación semántica neutral; no debe confundirse con el nivel de encabezado Markdown. El usuario podrá sobrescribirlo explícitamente cuando la inferencia no sea adecuada.

Los estilos de `notes` y de bloques de contenido se consideran una extensión del catálogo. No se asumirá que XMind los representa visualmente de la misma manera que los temas.

## 4. Catálogo de propiedades neutrales

Las siguientes propiedades constituyen el catálogo inicial recomendado. No todas tienen garantía de representación idéntica en todos los formatos de salida.

### 4.1 Tipografía y texto

| Propiedad | Tipo | Significado |
|---|---|---|
| `typography.font_family` | string | Familia tipográfica |
| `typography.font_size` | number | Tamaño en puntos |
| `typography.font_weight` | enum/number | `normal`, `bold` o peso numérico |
| `typography.font_style` | enum | `normal` o `italic` |
| `typography.text_align` | enum | `left`, `center`, `right`, `justify` |
| `typography.vertical_align` | enum | `top`, `middle`, `bottom` |
| `text.color` | color | Color del texto |
| `text.decoration` | enum/list | `none`, `underline`, `line_through`, combinaciones admitidas |
| `text.wrap` | boolean | Permitir ajuste de línea |
| `text.line_height` | number | Factor de interlineado |

Los fragmentos enriquecidos (`runs`) pueden sobrescribir tipografía, color, decoración y enlace en un tramo concreto. Una propiedad de un fragmento afecta solo a ese tramo.

### 4.2 Forma y relleno

| Propiedad | Tipo | Significado |
|---|---|---|
| `shape.type` | string/enum | Forma del elemento |
| `shape.fill.color` | color | Color de relleno |
| `shape.fill.opacity` | number | Opacidad entre 0 y 1 |
| `shape.fill.image` | asset reference | Imagen de fondo, si el destino la admite |
| `shape.corner_radius` | number | Radio de esquina, cuando proceda |

El catálogo neutral no debe enumerar como universales las 31 formas de una versión concreta de XMind. Utiliza nombres semánticos estables y permite extensiones para formas propietarias.

### 4.3 Borde

| Propiedad | Tipo | Significado |
|---|---|---|
| `border.color` | color | Color del borde |
| `border.width` | number | Grosor en puntos |
| `border.pattern` | enum | `solid`, `dash`, `dot`, `dash_dot` |
| `border.opacity` | number | Opacidad entre 0 y 1 |

### 4.4 Ramas y líneas

| Propiedad | Tipo | Significado |
|---|---|---|
| `line.shape` | enum/string | Geometría de línea o conexión |
| `line.color` | color | Color |
| `line.width` | number | Grosor en puntos |
| `line.pattern` | enum | Patrón continuo o discontinuo |
| `line.start_arrow` | string/enum | Terminación inicial |
| `line.end_arrow` | string/enum | Terminación final |
| `line.taper` | enum/boolean | Variación de grosor, si se admite |
| `line.color_source` | enum | `explicit`, `source_topic`, `target_topic`, `theme` |

Las propiedades de flechas se aplican a relaciones; no se supondrá que las ramas jerárquicas admiten las mismas terminaciones.

### 4.5 Espaciado y dimensiones

| Propiedad | Tipo | Significado |
|---|---|---|
| `spacing.padding` | number/object | Relleno interior en puntos |
| `spacing.margin` | number/object | Separación exterior en puntos |
| `spacing.gap` | number | Separación entre elementos |
| `dimensions.width` | number | Anchura explícita |
| `dimensions.min_width` | number | Anchura mínima |
| `dimensions.max_width` | number | Anchura máxima |
| `dimensions.height` | number | Altura explícita |

Estas propiedades pueden depender de la estructura de mapa y de las capacidades del adaptador. No se debe prometer posicionamiento absoluto cuando el formato de salida lo calcule automáticamente.

### 4.6 Fondo y efectos

| Propiedad | Tipo | Significado |
|---|---|---|
| `background.color` | color | Fondo del mapa o superficie |
| `background.image` | asset reference | Imagen de fondo |
| `background.opacity` | number | Opacidad |
| `effects.shadow` | object/boolean | Sombra, si está soportada |

Los efectos se consideran capacidades opcionales. Si un adaptador no los admite, debe emitir una advertencia de pérdida.

### 4.7 Propiedades de presentación no estilísticas

Se mantienen fuera del catálogo visual:

- Plegado de ramas.
- Orden de temas.
- Orientación y estructura de la hoja.
- Anchura personalizada cuando sea un atributo estructural del tema.
- Numeración automática y su alcance.
- Posición manual.
- Visibilidad funcional.

Pueden pertenecer a `layout`, `numbering` o a otras entidades del IR. El sistema de estilos no debe apropiarse de ellas por comodidad.

## 5. Unidades y formatos

Para evitar ambigüedades:

- Colores: hexadecimal `#RRGGBB` o `#RRGGBBAA`; el formato canónico de serialización será hexadecimal.
- Opacidad: número entre 0 y 1.
- Tamaños de fuente y grosores de línea: puntos (pt), expresados como número sin sufijo.
- Márgenes y rellenos: puntos.
- Anchuras y alturas: puntos cuando sean dimensiones físicas; la semántica concreta se documenta en la propiedad.
- Porcentajes: números entre 0 y 100 solo en propiedades declaradas como porcentaje.
- Fechas y referencias a assets no forman parte del catálogo visual.

No se aceptarán cadenas como `"14px"` para una propiedad que ya tiene unidad definida. La validación debe detectar tipos y rangos incorrectos.

## 6. Conjuntos de estilos y perfiles

Un conjunto reúne una apariencia coherente y puede extender un único conjunto base.

Ejemplo conceptual:

~~~yaml
style_sets:
  BASE_ACADEMICO:
    description: Estilo base para documentación de estudio.
    elements:
      map:
        background:
          color: "#FFFFFF"
      topic:
        roles:
          root:
            typography:
              font_size: 20
              font_weight: bold
          main:
            typography:
              font_size: 16
              font_weight: bold
          subtopic:
            typography:
              font_size: 13
              font_weight: normal
      branch:
        line:
          width: 1.5
          color: "#78909C"

  TAI_LEGISLACION:
    description: Estilos para el temario TAI.
    extends: BASE_ACADEMICO
    elements:
      topic:
        roles:
          root:
            shape:
              type: rounded_rectangle
              fill:
                color: "#263B5A"
            text:
              color: "#FFFFFF"
          main:
            shape:
              type: rounded_rectangle
              fill:
                color: "#DCE6F1"
            text:
              color: "#172B4D"
~~~

Reglas:

- Un conjunto puede extender como máximo un conjunto padre.
- La herencia de conjuntos se resuelve desde el ancestro hasta el conjunto seleccionado.
- Los ciclos de herencia son errores.
- El conjunto seleccionado para un tema se hereda por sus descendientes.
- Un descendiente puede seleccionar otro conjunto para su propia rama.
- El cambio de conjunto no modifica a los hermanos.
- Las propiedades de los perfiles se fusionan por propiedad.

## 7. Estilos con nombre

Un estilo con nombre aplica un grupo de propiedades a un tipo de elemento.

~~~yaml
styles:
  concepto_importante:
    applies_to: topic
    properties:
      shape:
        fill:
          color: "#FCE4D6"
      border:
        color: "#C00000"
        width: 1.5
      text:
        color: "#9C0006"
      typography:
        font_weight: bold
~~~

Puede definirse en el catálogo global o dentro de un conjunto. Si un nombre aparece en varios niveles, la definición más específica prevalece mediante fusión recursiva.

`applies_to` es obligatorio y evita aplicar por error un estilo de relación a un tema. Valores iniciales: `map`, `topic`, `branch`, `relationship`, `boundary`, `summary`, `summary_topic` y `callout`.

## 8. Cascada y precedencia

La resolución se ejecuta para cada elemento estilizable. De menor a mayor prioridad:

1. Valores predeterminados del sistema.
2. Valores generales del mapa (`defaults.elements`).
3. Propiedades base heredadas del conjunto seleccionado.
4. Perfil del rol dentro del conjunto efectivo (solo cuando corresponda).
5. Estilo con nombre, fusionando catálogo global y definiciones de conjuntos desde el ancestro hasta el conjunto actual.
6. Modificaciones locales del elemento (`overrides`).
7. Formato de fragmento de texto (`runs`), solo para el tramo de texto correspondiente.

El tema padre no transmite sus valores visuales a los hijos. Lo que se hereda por el árbol es el contexto del conjunto de estilos, no el color, la forma o la tipografía del padre.

### 8.1 Reglas de fusión

- Mapping + mapping: fusión recursiva por clave.
- Escalar + escalar: el valor más específico reemplaza al anterior.
- Lista + lista: la lista más específica reemplaza a la anterior.
- Propiedad ausente: conserva el valor anterior.
- `null`: restablece al valor predeterminado del sistema para esa propiedad.
- Tipo incompatible: error de validación.

La resolución debe conservar, para diagnóstico, la procedencia de cada valor: predeterminado, mapa, conjunto, perfil, estilo o modificación local.

## 9. Sintaxis en Markdown e IR

La gramática definida en `docs/grammar.md` utiliza:

~~~md
:::xmind
style_set: TAI_LEGISLACION
style: concepto_importante
style_overrides:
  text:
    color: "#9C0006"
  typography:
    font_weight: bold
:::
### Concepto clave
~~~

Correspondencia con el IR:

| Fuente | IR |
|---|---|
| `style_set` | Contexto de conjunto seleccionado |
| `style` | `style.ref` |
| `style_overrides` | `style.overrides` |
| Resultado de la cascada | `style.resolved` |

El parser conserva referencias y modificaciones locales. El módulo de estilos realiza la resolución. El adaptador recibe las propiedades efectivas y los datos de procedencia necesarios para advertir de pérdidas.

## 10. Nombres técnicos y etiquetas en español

Las claves canónicas del catálogo se mantienen en inglés técnico y en `snake_case` para ofrecer estabilidad a Python, JSON y futuros adaptadores.

La interfaz de autoría y la documentación pueden mostrar etiquetas en español. Se recomienda mantener un diccionario independiente de alias y etiquetas:

| Etiqueta española | Clave canónica |
|---|---|
| Color del texto | `text.color` |
| Familia tipográfica | `typography.font_family` |
| Tamaño de fuente | `typography.font_size` |
| Grosor de fuente | `typography.font_weight` |
| Color de relleno | `shape.fill.color` |
| Tipo de forma | `shape.type` |
| Color del borde | `border.color` |
| Grosor del borde | `border.width` |
| Color de línea | `line.color` |
| Grosor de línea | `line.width` |
| Relleno interior | `spacing.padding` |
| Sombra | `effects.shadow` |

Los alias españoles no deben crear propiedades duplicadas en el IR. Se traducen a la clave canónica antes de la validación y resolución. Las colisiones entre alias deben ser errores.

## 11. Capacidades y adaptadores

Cada adaptador debe publicar un catálogo de capacidades por elemento y propiedad, con uno de estos estados:

| Estado | Significado |
|---|---|
| `native` | Representación directa |
| `mapped` | Conversión documentada a una propiedad equivalente |
| `approximate` | Representación aproximada |
| `unsupported` | No se puede representar |

El adaptador XMind debe validar estas capacidades contra la versión de XMind y el formato de archivo elegidos. No se debe deducir compatibilidad únicamente porque una propiedad exista en el IR o en un ejemplo de tema del SDK.

La documentación oficial de XMind describe controles visuales para Topic, Relationship, Boundary, Summary y Callout. También documenta opciones específicas de líneas, extremos de flecha, formas, texto y numeración. Véanse las fuentes al final.

## 12. Validación

La validación del sistema debe comprobar:

- Que el archivo de configuración es un mapping YAML.
- Que `version` es reconocida.
- Que los conjuntos y estilos tienen nombres únicos en su ámbito.
- Que los conjuntos referenciados existen.
- Que la herencia no contiene ciclos.
- Que `applies_to` coincide con el elemento destinatario.
- Que las propiedades pertenecen al catálogo o a `extensions`.
- Que los colores, números, enums y rangos son válidos.
- Que `null` solo se usa según la semántica definida.
- Que los estilos referenciados existen.
- Que los alias localizados no son ambiguos.
- Que las propiedades no soportadas por un adaptador generan advertencias o errores según el modo de validación.

Se recomiendan dos modos:

- **strict:** una propiedad desconocida o un tipo incorrecto impide generar la salida.
- **compatible:** conserva extensiones desconocidas y genera advertencias explícitas.

## 13. Pruebas de aceptación

El sistema de estilos estará listo cuando disponga de pruebas que demuestren:

1. Fusión recursiva de mappings.
2. Sustitución completa de listas.
3. Restablecimiento mediante `null`.
4. Herencia de un conjunto por descendientes.
5. Sustitución de conjunto en una rama sin afectar a hermanos.
6. Herencia de conjuntos mediante `extends`.
7. Detección de ciclos.
8. Aplicación de perfiles `root`, `main` y `subtopic`.
9. Resolución de estilos globales y locales con el mismo nombre.
10. Precedencia de modificaciones locales.
11. Aislamiento de estilos de fragmentos enriquecidos.
12. Validación de tipo de elemento (`applies_to`).
13. Validación de unidades, colores y rangos.
14. Diagnóstico de propiedades no soportadas por el adaptador.
15. Resultado determinista para la misma entrada.

## 14. Fuentes técnicas

- Guía oficial de estilos de XMind: https://xmind.com/user-guide/style-new
- Guía oficial de relaciones: https://xmind.com/user-guide/relationship-new
- Guía oficial de límites: https://xmind.com/user-guide/boundary-new
- Modelo público de XMind: https://github.com/xmindltd/xmind-model
- SDK JavaScript y temas de ejemplo: https://github.com/xmindltd/xmind-sdk-js

Estas fuentes permiten inventariar capacidades y vocabulario, pero no sustituyen las pruebas de exportación y apertura en la versión de XMind que se elija como objetivo.
