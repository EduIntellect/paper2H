# DMKD: PDF evaluado por los revisores y alcance de la revisión

Fecha: 1 de octubre de 2026. Estado: **identidad del PDF aportado verificada;
exportación actual de Overleaf recibida y preservada; PDF compilado por
Overleaf aún pendiente**.

El autor identifica `/home/fede/Descargas/paper2_H_-1.pdf` como el artículo
evaluado por los revisores. Es byte a byte idéntico al candidato forense
`/home/fede/forense_paper2H/paper2_H_ (1).pdf`.

- SHA-256: `464916a0b2f8d780343cc4721eee338623aee52fa3a8b292f914a2c13bd629f8`.
- MD5: `9e37f986d9b88779dd4217f5ed808a21`.
- Tamaño: 647.008 bytes; 22 páginas.
- Título: *Baseline-Relative Predictability Horizons for Cross-Domain Forecast Evaluation*.
- Autores en p. 1: Federico Garcia Crespi y Julio Alberto Ramos Martinez.
- Alcance: cuatro dominios: PM2.5, Load, Wind y Traffic.
- Load principal: un día; figura auxiliar de siete días.
- No contiene Madrid/Barcelona ni un estudio principal de cinco modelos con DM/BH.

La identificación procede del PDF facilitado por el autor y su coincidencia
criptográfica. No se afirma haber accedido independientemente a Editorial
Manager, ni haber identificado todavía la fuente exacta que compiló ese PDF.

## Corrección del alcance de nuestra auditoría

El paquete local `revision/dmkd_2026-09-30` corresponde a una ampliación de
seis dominios y se conserva únicamente como borrador/auditoría separada. No
es el paquete de revisión del artículo sometido. La reparación Traffic A1 y
su congelación numérica siguen siendo válidas para esos artefactos, pero no
demuestran por extensión todas las afirmaciones del PDF de cuatro dominios.

Los problemas de calendario Barcelona y preparación Madrid **no son
bloqueadores del artículo sometido**, porque esos dominios no aparecen en él.
Tampoco se debe atribuir automáticamente al PM2.5 sometido el defecto de la
secuencia comprimida de 41.757 filas de la ampliación: el productor LightGBM
histórico de cuatro dominios lee el raw horario de 43.824 filas y conserva NA.

La revisión recuperada del commit `bb9c375` corresponde al alcance de cuatro
dominios y contiene buena parte de las modificaciones editoriales solicitadas.
No es todavía una revisión final aprobada: conserva inconsistencias y solo
incluye un autor. No se elimina a Julio ni se trasladan cifras de seis dominios.

## Inconsistencia PM2.5 demostrada sin experimentos nuevos

| Evidencia | Hrelax / Hstrict | Intervalo | Interpretación verificable |
| --- | --- | --- | --- |
| Texto sometido, p. 11, y Tabla 3, p. 17 | 48 / 13 | [36,48] | Atribuido en el manuscrito a LightGBM. |
| Figura 3 sometida, p. 12; `results/pm25_lightgbm_full_skill.csv` | 48 / 22 | [27,48] | La geometría vectorial de los 48 puntos del PDF coincide con este CSV de LightGBM. |
| `results/pm25_real_skill.csv` y su productor `experiments/pm25_predictability_real.py` | 48 / 13 | [36,48] | Experimento de media móvil de tres pasos, no LightGBM; aplica interpolación global. |

La comprobación de Figura 3 no es una comparación visual aproximada: se
extraen sus 48 coordenadas vectoriales y la línea de habilidad cero. Tras la
transformación afín de escala del gráfico, la diferencia máxima con el CSV
LightGBM es `4.03e-7` puntos PDF; con la media móvil llega a `38.79` puntos.
La línea cero coincide también, con diferencia `6.38e-8` puntos. Esto demuestra
la inconsistencia texto–figura; no prueba por sí solo toda la procedencia de
los pronósticos históricos.

Los intervalos positivos de la curva LightGBM mostrada son `[7,11]`, `[13,14]`
y `[27,48]`, con cinco cambios de signo. No es correcto describirla como una
única aparición tardía sin intervalos positivos anteriores.

La revisión recuperada mantiene el `48/13` primario y lo contrasta con un
`48/22` de sensibilidad alegando efecto de soporte. Los CSV de sensibilidad
tienen efectivamente soporte y métricas diferentes del agregado histórico,
pero el agregado LightGBM primario localizado **ya da 48/22**. La explicación
no acredita que el `48/13` sometido sea LightGBM. No se debe conservar esa
justificación sin la evidencia correspondiente.

Acción recomendada: reconciliar texto, Tabla 3, interpretación, figura y carta
con la evidencia LightGBM confirmada. Esto es una corrección de reporte; no
requiere reentrenar para obtener la curva que ya figura en el PDF. No se ha
modificado ninguna cifra primaria ni la fuente recuperada durante este examen.

## Qué está comprobado y qué falta

- Las tuplas históricas MAE de Wind `48/48 [1,48]`, Traffic `72/7 [46,52]`
  y Load principal `1/1 [1,1]` coinciden con el PDF. Skill se obtiene de sus
  agregados MAE guardados sin recalcular pronósticos.
- Wind y Traffic canónicos no tienen valores ausentes; la interpolación
  global de sus loaders es una operación nula sobre esas entradas. Sus ejes
  horarios son regulares. La lectura del código distingue esta comprobación
  concreta de una afirmación general de imputación train-only.
- La sensibilidad recuperada de cuatro dominios tiene hashes, métricas,
  objetivos, soporte emparejado y horizontes calendario comprobados. Su
  verificación no significa que se haya ejecutado ahora el experimento.
- El apéndice RMSE primario aún necesita errores cuadrados o pronósticos
  por origen trazables. MAE agregado no basta para reconstruir RMSE; las
  cifras de la versión de seis dominios no lo sustituyen.
- Deben reconciliarse la figura auxiliar Load y sus configuraciones. El
  productor histórico usa `365` como comienzo de evaluación con entrenamiento
  expansivo, no un recorte móvil de 365 filas; `i % 7` es fase semanal de índice,
  no una extracción explícita del día de la semana desde el timestamp.
- El ZIP actual de Overleaf ya está recibido y preservado. Conserva dos
  autores y cambia la afiliación de Julio respecto del PDF sometido; se
  mantiene la metadata aportada, sin decidir afiliaciones por los autores.
  Los cambios locales se aplican solo en una copia separada de cuatro
  dominios. Falta el PDF final de Overleaf tras la importación.
- La caché local no cierra por sí sola la solicitud de publicación en un
  sitio controlado por los autores. Redistribución y descarga pública deben
  verificarse antes de afirmar que ese punto está cumplido.

## Próximo paso

La exportación ZIP está recibida: SHA-256
`d383ead3ff2b5bafbb23e25467c274e4af7730c3a27eaa9676695bcaddcc302b`.
Consta de trece archivos sin PDF del manuscrito, se conserva intacta en
`revision/overleaf_2026-10-01/original/` y confirma el alcance de cuatro
dominios. La copia editada y compilada localmente está documentada en
`docs/dmkd_humanized_working_revision_2026-10-01.md`. Se corrige el reporte
PM2.5 sin alterar CSV ni predicciones. El apéndice RMSE y la caché pública
siguen abiertos. No se edita Overleaf ni se identifica este borrador como
la fuente exacta que produjo el PDF sometido.

No se han realizado nuevos ajustes, cambios de predicciones, commits, pushes
ni envíos. Los aproximadamente 25.872 ajustes siguen sin autorización.

## Evidencia reproducible

- `src/audit_submitted_four_domain_evidence.py` (Python de auditoría numérica).
- `src/verify_submitted_pm25_figure.py` (Python incluido en Codex con pdfplumber).
- `revision/submitted_pdf_2026-10-01/evidence_identity.json`.
- `revision/submitted_pdf_2026-10-01/submitted_pm25_figure_linkage.json`.
- `results/dmkd_revision_audit_2026-09-30/recovered_revision_verification.json`.

Las fuentes originales se mantienen intactas; estos JSON/Markdown son
resultados de auditoría, no evidencia de nuevos experimentos.
