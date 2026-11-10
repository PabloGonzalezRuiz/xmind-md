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

- Que todos los estilos se representen igual en todas las versiones de XMind.
- Que el paquete generado preserve los elementos auxiliares opcionales del
  fixture de referencia.
- Que todas las capacidades del formato XMind estén implementadas por el adaptador.

La validación manual del fixture de integración sí se ha completado; su alcance y versión se registran a continuación.

## Fixture utilizado en la comprobación manual

El workflow también ejecuta scripts/create_xmind_smoke.py y publica el
resultado como artefacto xmind-desktop-smoke-test. El archivo se construye
a partir de examples/xmind-smoke-test.md y contiene dos ramas, una nota,
una etiqueta, un marcador y una relación.

El fixture permanente se encuentra en `tests/fixtures/xmind/xmind-md-smoke-test.xmind`; su README registra procedencia y hash. La comprobación manual de este archivo se completó el 2026-11-10 en XMind Desktop 26.05.01107 para Windows, según el resultado detallado más abajo.


## Resultado de la prueba manual — 2026-11-10

- **Estado:** superada por confirmación del usuario.
- **Sistema operativo:** Windows.
- **Aplicación:** XMind Desktop **26.05.01107**.
- **Archivo:** `tests/fixtures/xmind/xmind-md-smoke-test.xmind`.
- **Descarga:** realizada correctamente desde el repositorio.
- **Apertura:** realizada sin errores; el usuario confirmó que el mapa se visualizaba correctamente.
- **Elementos inspeccionados:**
  - Tema central: `XMind MD · Prueba de apertura`.
  - Ramas principales: `Rama A` y `Rama B`.
  - Subtema: `Detalle de rama A`, hijo de Rama A.
  - Nota desplegable de Rama A: `Nota de prueba asociada a la rama A.`.
  - Etiqueta de Rama A: `IMPORTANTE`.
  - Marcador de prioridad de Rama A: icono con número `1`.
  - Relación entre las ramas: `Relación de prueba`.
- **Persistencia:** el usuario guardó el archivo, lo cerró y volvió a abrirlo; confirmó que funcionaba correctamente y que se conservaba el contenido.
- **Conclusión:** el fixture y las capacidades enumeradas quedan comprobados visualmente en XMind Desktop 26.05.01107 para Windows. Esta evidencia no debe extrapolarse a otras versiones ni a capacidades no incluidas en el fixture.

La prueba manual se considera cerrada para este fixture. La ejecución local de la aplicación/CLI y de la suite de pruebas en Windows sigue siendo una tarea independiente.
