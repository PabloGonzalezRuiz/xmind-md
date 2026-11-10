# Pruebas de integración XMind

## Objetivo

Contrastar el paquete generado por XMind MD con un archivo `.xmind` externo
real, además de comprobar la estructura moderna ZIP + JSON y los campos
obligatorios de las relaciones.

## Fixture de referencia

- Proyecto de origen: [sc0tfree/xmind-mcp](https://github.com/sc0tfree/xmind-mcp).
- Archivo: `tests/fixture.xmind`.
- Revisión fijada: `6225cbcd3e8fc565bc18e80346699a6e118dd0f7`.
- Licencia declarada por el proyecto: MIT.
- SHA del blob del archivo en GitHub: `3bde1da15010a8736ccbf0af3c630b3fd4d4fd6a`.

El fixture se descarga en CI en vez de almacenarse como binario dentro de este
repositorio. La prueba de origen del proyecto externo espera una hoja titulada
`Mind Map`, tema raíz `Central Topic` y cuatro temas principales. También
comprueba que el paquete conserva `Thumbnails/thumbnail.png` y `content.xml`. En la revisión fijada, el fixture no incluye una entrada `mimetype`; por ello la prueba no la exige en el archivo externo. El adaptador de XMind MD sí la incluye y sus pruebas unitarias comprueban su valor y su compresión.

La procedencia exacta de creación del fixture no está acreditada como una
exportación directa de XMind Desktop. Por tanto, es una referencia de
interoperabilidad de terceros, no una muestra oficial ni una certificación de
la aplicación.

## Qué verifican las pruebas

1. El fixture externo es un ZIP legible y contiene `content.json`,
   `metadata.json`, `manifest.json`, miniatura y `content.xml`.
2. El contenido del fixture tiene la estructura moderna de hoja, raíz e hijos
   adjuntos.
3. El archivo generado por XMind MD utiliza la misma estructura esencial de
   hoja, tema raíz e hijos adjuntos.
4. Las relaciones generadas contienen `end1Id`, `end2Id` y los dos puntos de
   control que declara el modelo oficial.

## Ejecución local

Si se desea ejecutar la prueba del fixture fuera de CI, descargar el archivo
en `tests/fixtures/reference.xmind` desde la revisión indicada en este
documento. Sin el fixture, las pruebas que dependen de él se omiten; las
pruebas unitarias y la prueba estructural de relaciones siguen ejecutándose.

## Ejecución en GitHub Actions

El workflow `.github/workflows/ci.yml` descarga el fixture desde una URL
inmutable de GitHub antes de ejecutar `pytest`. La prueba no necesita instalar
el SDK externo ni añade dependencias de ejecución al proyecto.

## Cobertura del perfil ampliado del adaptador

Las pruebas unitarias de `tests/test_xmind_adapter.py` incluyen además:

- Temas `detached` y `callout` agrupados bajo las claves correspondientes de `children`.
- Requisito de posición numérica para temas `detached`.
- Conversión de `position`, `structure_class`, `branch=folded` y `width` a los campos XMind correspondientes.
- Enlaces internos entre temas, traducidos a `href` con esquema `xmind:#` y UUID del tema destino.
- Enlaces a archivo limitados a URI `file://`.
- Rechazo de clases de tema, layouts, enlaces y destinos no admitidos.
- Comprobación de que el tema raíz debe ser `attached`.

Estas pruebas verifican la estructura JSON generada. No sustituyen la apertura y comprobación visual en XMind Desktop.

## Lo que todavía no demuestra

- Que XMind Desktop abra el archivo generado.
- Que el trazado visual de las relaciones sea correcto.
- Que todos los estilos se representen igual en todas las versiones de XMind.
- Que el paquete generado preserve los elementos auxiliares opcionales del
  fixture de referencia.

La validación visual requiere abrir el archivo generado y guardarlo desde una
versión identificada de XMind Desktop. Esa comprobación manual queda pendiente.

## Archivo para comprobación manual en XMind Desktop

El workflow también ejecuta scripts/create_xmind_smoke.py y publica el
resultado como artefacto xmind-desktop-smoke-test. El archivo se construye
a partir de examples/xmind-smoke-test.md y contiene dos ramas, una nota,
una etiqueta, un marcador y una relación.

Para realizar la comprobación:

1. Abre la última ejecución correcta de CI.
2. Descarga el artefacto xmind-desktop-smoke-test.
3. Extrae xmind-md-smoke-test.xmind.
4. Ábrelo con XMind Desktop.
5. Comprueba que aparecen la raíz, las dos ramas, el detalle, la nota, la
   etiqueta, el marcador y la relación.
6. Guarda una copia desde XMind Desktop y, si es posible, vuelve a abrirla.

La compatibilidad visual solo podrá darse por verificada cuando se conozca la
versión de XMind Desktop y se confirme el resultado de esa comprobación.
