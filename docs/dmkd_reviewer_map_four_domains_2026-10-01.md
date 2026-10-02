# DMKD: mapa de revisores contra el PDF sometido confirmado

Referencia sometida: PDF de 22 páginas aportado el 1 de octubre. Fuente activa:
exportación actual de Overleaf preservada en
`revision/overleaf_2026-10-01/original/`. Copia editada aislada:
`revision/overleaf_2026-10-01/working/`. Las ubicaciones de la segunda tabla
corresponden a la compilación local de trabajo, no a un PDF final de Overleaf.

La primera tabla conserva el diagnóstico contra el PDF sometido y la revisión
recuperada antes de recibir el ZIP. Su columna «pendiente» es histórica;
el estado actualizado está en la segunda tabla.

| Solicitud | Ubicación sometida | Estado de la revisión recuperada | Pendiente de cierre |
| --- | --- | --- | --- |
| R1.1: dos puntos | p. 6, definiciones | Etiquetas corregidas | Sincronizar con Overleaf. |
| R1.2: huecos en ecuación (5) | p. 6 | Aclara huecos en prosa; ecuación mantiene endpoint | Incorporar explícitamente el span y huecos para contestar la petición literal sin cambiar el descriptor. |
| R1.3: aclarar alcance relajado | pp. 6, 11, 15 | Prosa explicativa añadida | Usar ejemplos numéricos trazables; reconciliar PM2.5. |
| R1.4: unidades Tabla 2 | p. 11 | Unidades añadidas | Verificar redacción exacta de la escala Load; no rescalar datos. |
| R1.5 / R2.2: citar Figuras 1–3 | pp. 7, 8, 11–12 | Citas explícitas presentes | Revisar referencias tras compilación final. |
| R2.3: solapamiento Figura 1 | p. 7 | Redibujo recuperado | QA de la figura en la compilación canónica final. |
| R2.4: cajas Figura 2 | p. 8 | Cajas mayores y texto envuelto | QA en compilación final. |
| R1.6 / R2.5: baseline alternativo | §4.1, p. 7 | Sensibilidad estacional de cuatro dominios verificada numéricamente | Mantener separación del soporte primario y corregir la explicación PM2.5 no acreditada. No ejecutada otra vez. |
| R1.7 / R2.7: ARIMA(2,0,0) | p. 10; pp. 14–15; 17–19 | Comparaciones y claims retirados | Confirmar esa retirada en la fuente canónica y explicar sin inventar selección ACF/PACF. |
| R1.8–9 / R2.1: accionabilidad y utilidad adicional | Formulación y Discussion | Subapartado añadido | Acotar a diagnóstico de habilidad; ganancias pequeñas o incertidumbre pueden impedir utilidad real. |
| R1.10: rolling-window adaptativo y feedback | Discussion | Riesgo de selección adaptativa y validación independiente discutidos | No presentar un controlador dinámico como validado. |
| R2.6: caché única | p. 20 | README/manifest y recuperador único; Wind/Traffic no cacheados | Publicación verificable en ubicación controlada por autores; no marcar DONE solo por tener un script. |
| Editor: reporte exacto y limitaciones | Todo; apéndice pp. 19–20 | Existen mejoras de redacción | PM2.5 texto–figura; trazabilidad RMSE; protocolo real Load; autoría y versiones. |

La auditoría propia de RMSE, modelos y preparación no se atribuye a solicitudes
que los revisores no hicieron. Las respuestas explicarán los cambios realmente
realizados y los análisis históricos recuperados, no experimentos inexistentes.

## Estado actualizado sobre la copia de Overleaf

| Comentario | Ubicación local de trabajo | Estado y evidencia |
| --- | --- | --- |
| R1.1 | §3.1, p. 6 | Dos puntos presentes en ambas etiquetas. |
| R1.2 | Ecuación (5), p. 6 | Span relajado y conjunto explícito de huecos no positivos; no cambia algoritmo. |
| R1.3 | §3.1–3.2, pp. 6–7; PM2.5 pp. 12–13; Traffic pp. 15–16 | Endpoint no significa habilidad en todos los horizontes anteriores; ejemplos coherentes con curvas. |
| R1.4 | Tabla 2, p. 11 | Unidades y escala Load explícitas, sin rescalar datos. |
| R1.5 | Figs. 1–3, pp. 7, 9, 13 | Citas de figuras resueltas; figuras inspeccionadas en la compilación local. |
| R1.6 | §10.4, pp. 17–18, Tabla 4 | Sensibilidad estacional histórica verificada; no repetida. PM2.5 13→22 tratado como corrección de reporte, no efecto de soporte. |
| R1.7 | §6.2, p. 11; carta R1.7 | No se inventa selección ARIMA. Retirada de claims numéricos mantenida; baseline sensitivity no es model robustness. |
| R1.8 | §3.2, p. 7; Discussion pp. 17–19 | Accionabilidad acotada a diagnóstico; considerar magnitud, incertidumbre, pérdidas y costes. |
| R1.9 | §3.2, p. 7; perfiles pp. 12–18 | Explica alcance y continuidad frente a errores en pocos horizontes fijos. |
| R1.10 | Discussion p. 18; Limitations p. 19 | Riesgo de selección adaptativa y necesidad de evaluación independiente; controlador no validado. |
| R2.1 | §3.2, p. 7 | Mismo cambio de accionabilidad que R1.8. |
| R2.2 | Figs. 1–2, pp. 7, 9 | Referencias textuales resueltas. |
| R2.3 | Fig. 1, p. 7 | Layout del ZIP inspeccionado: curva y etiquetas separadas. PDF de figura intacto. |
| R2.4 | Fig. 2, p. 9 | Layout del ZIP inspeccionado: texto dentro de cajas, sin clipping. PDF de figura intacto. |
| R2.5 | §10.4, pp. 17–18, Tabla 4 | Baseline alternativo reportado a partir de evidencia archivada. Cero nuevos ajustes. |
| R2.6 | Data Availability p. 21; carta R2.6 | **ABIERTO:** falta caché pública controlada por los autores con descargas y permisos comprobados. |
| R2.7 | §6.2, p. 11; carta R2.7 | Mismo tratamiento transparente de ARIMA que R1.7. |
| Editor | PM2.5 pp. 12–13, Tabla 3 p. 17, Limitations p. 19, apéndice p. 20 | Correcciones de reporte, Load e inferencia aplicadas. **ABIERTO:** trazabilidad RMSE primario. |

Estado general: **compilación local y revisión editorial avanzadas, no listo
para envío**. La autoría/afiliaciones se preserva como en el ZIP y requiere
confirmación final de autores; la afiliación de Julio difiere del PDF sometido.
Las notas internas del manuscrito y carta no deben enviarse. También falta
revisar el PDF final de Overleaf tras importar la copia editada. No se certifica
todo el protocolo histórico a partir de la congelación separada de seis dominios.

El diff y los hashes están en
`revision/overleaf_2026-10-01/output/editorial_manifest.json`. El detalle de
estilo, correcciones y restricciones se documenta en
`docs/dmkd_humanized_working_revision_2026-10-01.md`.
