# Revisión mayor de DMKD: estado comprobado y criterios de cierre

**Actualización, 1 de octubre:** el autor ha aportado el PDF sometido y su
hash confirma cuatro dominios y dos autores. Este informe conserva la
auditoría de la ampliación local de seis dominios; no es el estado de cierre
del artículo sometido. Para la revisión activa usar
`docs/dmkd_submitted_pdf_identity_2026-10-01.md` y
`docs/dmkd_reviewer_map_four_domains_2026-10-01.md`. Madrid/Barcelona y el
PM2.5 comprimido de seis dominios no se transfieren automáticamente a aquél.

Fecha: 30 de septiembre de 2026. Submission ID: `1e58c388-d7ec-4084-b792-df20a48e3e75`.

**Estado: borrador de revisión preparado; NO LISTO PARA ENVIAR.** La reparación
Traffic A1 y la congelación numérica están verificadas. No se ha entrenado,
ajustado ni seleccionado ningún modelo. Los aproximadamente 25.872 ajustes
continúan sin autorización. Tampoco se han hecho commits, pushes ni envíos.

## Qué se ha terminado

- Reparación exacta de las 15 representaciones `y_true` de Traffic A1, con
  auditoría antes/después y predicciones idénticas.
- Verificación de hashes y dimensiones de los 22 artefactos congelados.
- Revisión editorial del borrador local: referencias a figuras, semántica de
  la ecuación relajada, puntuación, unidades, accionabilidad, riesgo de selección
  adaptativa, límites de generalización y retirada de comparaciones ARIMA no
  sustentadas. Las decisiones DM/BH y las etiquetas históricas no se alteran;
  se explican sus limitaciones reales.
- Diagnóstico MAE/RMSE de los cinco modelos en los seis dominios, calculado
  exclusivamente desde las predicciones guardadas. Se sustituye el apéndice
  numérico heredado de otra configuración; no se recalculan predicciones.
- Sensibilidad frente a persistencia estacional sobre el mismo soporte de
  LightGBM para Load, Wind y Traffic. Los periodos se fijaron en 7 días/24 horas;
  no se eligió un baseline a partir de sus resultados.
- Respuesta provisional para todas las solicitudes: 10 subcomentarios de R1,
  7 comentarios de R2 y 2 requisitos editoriales. La carta distingue trabajo
  completado de requisitos pendientes y no inventa páginas ni experimentos.
- Archivo local de entradas exactas con README y hashes. Esto NO demuestra
  publicación ni acceso independiente por terceros.
- Recuperación separada de una revisión anterior de cuatro dominios y
  verificación independiente de sus 12 artefactos de sensibilidad.

## Identidad de versiones: primer requisito para finalizar

| Versión | Evidencia | Alcance y cautela |
| --- | --- | --- |
| Candidato sometido | `/home/fede/forense_paper2H/paper2_H_ (1).pdf`, SHA-256 `464916a0b2f8d780343cc4721eee338623aee52fa3a8b292f914a2c13bd629f8` | Cuatro dominios y dos autores. No verificado todavía contra la descarga original de Editorial Manager. |
| Revisión recuperada | Commit `bb9c375ead2fe1f313127b77849296a144270f68`; PDF SHA-256 `bca5fe7cf846be29745f66a16913246e8dce7b98710cf206dd4176d8c7b2bb20` | Cuatro dominios. El PDF recuperado coincide exactamente con el PDF forense de septiembre. Su autoría difiere del candidato sometido: no se acepta ese cambio sin reconciliación. |
| Borrador local revisado aquí | `paper/paper2_submission.tex` y `revision/dmkd_2026-09-30/sources/main.tex` | Seis dominios y título distinto. Borrador de trabajo, no sustituto silencioso de Overleaf ni de la versión sometida. |

La anterior evaluación que presentaba todos los cambios editoriales como
pendientes se basaba en el borrador local antiguo. La recuperación demuestra
que ya existía otra revisión con esos cambios. Tampoco se aceptan sin auditoría
las etiquetas `DONE / VERIFIED` de su matriz histórica.

Es necesario confirmar cuál es la revisión activa en Overleaf y aportar su
ZIP/PDF actual. No es una preferencia de estilo: decide qué soporte, cifras,
autores y respuestas pertenecen al mismo artículo. No se mezclan los resultados
de cuatro y seis dominios. Recomendación: reconciliar primero la revisión que
corresponde al alcance realmente sometido, sin añadir dominios por defecto.

## Hallazgos científicos de la versión local de seis dominios

| Comprobación | Resultado | Consecuencia |
| --- | --- | --- |
| Wind y Traffic | Calendarios regulares, enlace objetivo/origen correcto; escalado dentro de cada ventana de entrenamiento | La reparación numérica no requiere reentrenamiento. La procedencia histórica sigue documentándose por separado. |
| PM2.5 | La secuencia de 41.757 valores coincide exactamente con el raw después de eliminar NA. Quedan 213 huecos; 5.755 filas de predicciones tienen tiempo transcurrido diferente de `h` (1.151 claves únicas); máximo 284 horas | El `h` congelado es un índice de observaciones, no siempre horas. No se puede certificar una evaluación de 1–48 horas por edición del texto. |
| Barcelona | 2.827 observaciones, 11 huecos; 1.400 filas de predicciones con días transcurridos distintos de `h` (280 claves); máximo 75 días | No se puede certificar 1–7 días calendario a partir de esas filas. |
| Madrid | Eje de 2.922 días regular; preparación exacta de valores ausentes aún no trazada | No se afirma imputación causal ni ausencia de leakage. Un raw relacionado no prueba por sí solo qué productor generó el CSV congelado. |
| Load | 667 días; último valor muy inferior al habitual | Falta comprobar cobertura de los intervalos del último día. No se eliminó ni corrigió ninguna fila. |
| DM/BH | Lotes históricos de modelos ajustados por separado; test bilateral; incluye deterioros | No hay control FDR conjunto de toda la expansión. No se cambian decisiones ni se interpreta ausencia de rechazo como equivalencia. |
| Taxonomía | Etiquetas por regla heurística almacenada | No prueban una causa física ni invariancia entre familias de modelos. |

Fuentes reproducibles: `src/audit_dmkd_revision.py` y
`results/dmkd_revision_audit_2026-09-30/{calendar_audit,calendar_mismatches,support_audit}.csv`.
Las auditorías propias de preparación de datos no se atribuyen falsamente a
un comentario de revisor.

La revisión recuperada tiene una sensibilidad alternativa propia sobre
calendarios y soporte emparejado comprobados para sus cuatro dominios. Esto
no verifica por extensión sus experimentos primarios históricos, su apéndice
RMSE ni su identidad con Overleaf. Load en esa sensibilidad evalúa solamente
el horizonte de un día, no los siete de la expansión local.

## Cambios numéricos diagnósticos, no experimentos nuevos

Para LightGBM, bajo MAE, `H_strict` pasa de 0 a 4 días en Load, de 48 a 29
horas en Wind y de 4 a 13 horas en Traffic al sustituir persistencia por
persistencia estacional. El pronóstico del modelo permanece fijo. La igualdad
de los endpoints relajados a múltiplos del periodo no demuestra invariancia.

Con persistencia, RMSE cambia Traffic de `72/4 [64,67]` a `72/53 [20,72]`
y Load de `0/0` a `2/2 [1,2]`. Wind sigue `48/48`. Estas cifras pertenecen
solo a los artefactos locales de seis dominios y no se trasladan a la otra
revisión. Se conservan las métricas primarias y sus hashes originales.

## Condiciones pendientes de aceptación

1. Confirmar identidad sometida, fuente revisada de Overleaf, alcance, título
   y autoría. No autorizar implícitamente cambios en los autores.
2. Cerrar preparación y soporte temporal de los experimentos que pertenezcan
   a esa versión. Si se requiere corregir una evaluación calendarizada de
   PM2.5/Barcelona, hará falta una decisión metodológica y autorización de
   la recomputación estrictamente afectada. No se ejecuta aquí.
3. Resolver causalidad de la preparación Madrid y cobertura Load si esos
   artefactos forman parte de la versión final.
4. Publicar la caché única solo después de verificar redistribución y con
   autorización; comprobar descarga independiente y añadir URL real.
5. Vincular cada respuesta a páginas/líneas del manuscrito confirmado y crear
   versión marcada respecto de la fuente realmente sometida.
6. Compilar y revisar visualmente el paquete final sincronizado; obtener
   aprobación autoral y autorización específica antes del envío.

Una compilación correcta de los borradores no cierra los requisitos científicos.
Se entrega un paquete local con estado `NOT_READY_FOR_SUBMISSION`, no un
paquete de reenvío aprobado. La comparación editorial local conserva el texto
previo en `revision/pre_edit_2026-09-30/editorial_sources.tar.gz`.

## Reproducción segura

Usar el Python ya instalado en `/home/fede/repos/hstar/.venv-lightgbm-validation/bin/python`:

```bash
python src/verify_dmkd_freeze.py
python src/audit_dmkd_revision.py
python src/verify_recovered_dmkd_revision.py
python src/build_dmkd_review_package.py
```

Estos scripts no entrenan. No ejecutar el pipeline general de reconstrucción
ni regenerar artefactos primarios durante la sincronización editorial.
