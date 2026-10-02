# DMKD: revisión de redacción y correcciones verificables

Fecha: 1 de octubre de 2026. Estado: **borrador de trabajo, no autorizado para envío**.

## Alcance y estilo

El autor solicita el skill «humanizar científico». No está disponible con ese
nombre en el catálogo ni en las carpetas de skills consultadas. Se aplica como
alternativa el skill disponible de adaptación al estilo (`write-like-me`), con
el manuscrito y la respuesta aportados como referencias. No se afirma haber
ejecutado un skill inexistente ni haber evaluado detectores de autoría.

Se conserva el registro académico inglés y la notación. Se acortan frases
formularias, se sustituyen nominalizaciones innecesarias por explicaciones
directas y se distingue habilidad positiva de utilidad real. No se incorporan
datos biográficos, citas nuevas, experimentos inventados ni promesas de
validación futura. La redacción no convierte evidencia pendiente en verificada.

Entrada: `/home/fede/Descargas/Baseline_relative_predictability_horizons.zip`.
SHA-256: `d383ead3ff2b5bafbb23e25467c274e4af7730c3a27eaa9676695bcaddcc302b`.
Los trece archivos originales están intactos en
`revision/overleaf_2026-10-01/original/`. La copia de trabajo está en
`revision/overleaf_2026-10-01/working/`; solo se editan `main.tex` y la carta.
Se preservan los dos autores y la afiliación aportada en el ZIP; su validación
final corresponde a los autores. No se sustituye `paper/paper2_submission.tex`
ni se introduce el estudio de seis dominios en el paper de cuatro dominios.

## Cambios de evidencia, separados de los de estilo

- PM2.5: texto, Tabla 3 e interpretación reconciliados con la curva LightGBM
  ya mostrada: 48/22, intervalo [27,48], positivos [7,11], [13,14] y [27,48],
  cinco cambios de signo. El antiguo 48/13 pertenece a un resultado distinto
  de media móvil. No se presenta esa diferencia como efecto de soporte.
- Load: se describe el entrenamiento expansivo, el umbral de 365 observaciones
  para comenzar evaluación y la fase semanal `i % 7`, tal como hace el
  productor. No se modifica dicho productor. El resumen principal de un día
  se separa del diagnóstico auxiliar de siete días.
- Ecuación (5): explicita el span relajado y sus huecos no positivos,
  permitidos pero no interpretados como habilidad positiva. La definición
  operativa del descriptor no cambia.
- Accionabilidad: identifica intervalos que merece examinar, pero exige
  considerar magnitud, incertidumbre, pérdida de decisión y coste. No prueba
  un controlador adaptativo ni beneficios de despliegue.
- Baseline: la sensibilidad estacional archivada no se vuelve a ejecutar y
  no se usa como prueba de robustez entre modelos o justificación de ARIMA.
- RMSE: cifras heredadas preservadas en el original, pero retenidas fuera de
  las afirmaciones verificadas del borrador hasta cerrar errores por origen.
  No se calcula RMSE desde MAE agregado ni se importa el RMSE de seis dominios.
- Disponibilidad: la carta reconoce expresamente que un README y recuperador
  no satisfacen una caché pública bajo control de los autores.

## Verificación

`src/build_overleaf_dmkd_working_copy.py` compila ambas fuentes desde una
carpeta limpia mediante `pdflatex`/`bibtex`. El compilador integrado se intentó
para la carta, pero no pudo descargar su bundle Tectonic; no se instaló software.

- Dos compilaciones locales satisfactorias, referencias resueltas.
- Solo dos archivos del ZIP editados; seis figuras PDF byte a byte intactas.
- 129 archivos protegidos con hashes idénticos antes/después de compilar,
  incluidos predicciones, resultados, scripts y el manuscrito de seis dominios.
- Verificador de congelación: PASS, 22 artefactos; Traffic canónico sin
  discrepancias. Esta congelación no se confunde con validar todo el paper
  histórico de cuatro dominios.
- Cinco pruebas del descriptor, veinte aserciones escalares, incluidas
  habilidad cero, huecos, aparición tardía y desempate por intervalo más temprano.
- Ajustes de modelos: cero. Recalculado de predicciones: cero. Cambios de
  hiperparámetros, splits, soporte, código de modelos o protocolo: cero.
- Auditoría reproducible y diff en
  `revision/overleaf_2026-10-01/output/editorial_manifest.json` y
  `editorial_changes.diff`; el estado de QA visual consta en el manifiesto.
- QA visual de las 23 páginas del manuscrito y cinco de la carta, con
  inspección ampliada de figuras y tablas. Sin clipping ni etiquetas
  solapadas. Sin advertencias Overfull; los Underfull verticales de la
  clase Springer se conservan en logs y no equivalen a errores de datos.

## Pendientes antes de cerrar

1. Vincular el apéndice RMSE primario con errores/pronósticos almacenados por
   origen y soporte declarado. No requiere autorizar nuevos ajustes; si esos
   registros no existen, habrá que acordar expresamente cómo retirar o limitar
   ese análisis, sin fabricarlo.
2. Publicar y comprobar una caché pública de los cuatro dominios, con permisos
   de redistribución. No hay autorización de publicación ni push en esta tarea.
3. Confirmar autoría/afiliaciones y revisar el PDF final de Overleaf después
   de importar la copia corregida. El ZIP suministrado no incluía ese PDF.
4. Retirar las notas internas solo tras cerrar estos controles, completar la
   carta final y la cover letter, y obtener aprobación de los autores.

No hay commits, pushes, uploads ni envío editorial. Los aproximadamente
25.872 ajustes continúan **no autorizados**. Los PDFs y el ZIP generados
son para revisión de los autores, no un paquete de reenvío final.
