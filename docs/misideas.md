Aquí tienes tus ideas organizadas en un formato Markdown limpio, profesional y fácil de leer. He estructurado el contenido para que la distinción entre ambos trabajos sea inmediata.

---

# Clarificación de Líneas de Investigación: Paper 1 vs. Paper 2

### 1. Paper Enviado a *Atmospheric Environment*

**Estado: Metodológicamente Cerrado.**
Nada de lo que descubras ahora afecta a este envío. Este trabajo es sólido porque su objetivo es la comparación interna.

* **Dataset:** PM10 Elche.
* **Modelos:** ARIMA / SARIMA / XGBoost.
* **Horizontes:** 1–7 días.
* **Evaluación:** Rolling-origin.
* **Definición de Horizonte Crítico:** 
$$H^* = \sup \{h \geq 1 : \text{Skill}(h) > 0\}$$



> [!IMPORTANT]
> **¿Por qué sigue siendo válido?** Porque en este paper $H^*$ se utiliza para comparar modelos dentro del **mismo sistema**. No busca comparar dominios cruzados.

---

### 2. Trabajo Actual: Paper 2 (*Cross-Domain Predictability*)

Este experimento pertenece al repositorio `paper2H` y tiene un enfoque totalmente distinto.

* **Objetivo:** Comparar la predictibilidad entre sistemas/dominios totalmente diferentes.
* **Configuración Multidominio:**

| Dominio | Dataset |
| --- | --- |
| **Calidad del Aire** | PM2.5 Beijing |
| **Energía** | PJM |
| **Viento** | NREL |
| **Tráfico** | PeMS |

---

### 3. Análisis de los Nuevos Hallazgos

Lo que acabas de descubrir (la persistencia dominando a corto plazo y la media móvil mejorando a horizontes largos) **no invalida $H^*$**.

Al contrario, confirma que $H^*$ es sensible a:

1. El **Dataset**.
2. El **Modelo**.
3. El **Baseline** elegido.

---

### 4. Evolución Metodológica (Paper 2)

En este segundo trabajo, es natural que la definición de $H^*$ evolucione para ser más robusta, por ejemplo:

* **Nueva definición propuesta:**

$$H^* = \max \{h : \text{Skill}(h) > 0 \text{ before the first zero crossing}\}$$


* **Refinamiento:** Inclusión de intervalos de confianza.

---

### 5. Perspectiva Científica

Este proceso no es una contradicción, sino el flujo natural de la investigación:

1. **Paper 1:** Introduce la métrica en un entorno controlado.
2. **Paper 2:** Explora el comportamiento en diversos dominios.
3. **Paper 3:** Refina el formalismo matemático.

---

### 6. Próximos Pasos

Tu prioridad absoluta es el **Paper 2**. Ya has superado la parte más compleja del trabajo:

* [x] Selección de Datasets.
* [x] Construcción del Pipeline.
* [x] Definición de Baselines.
* [x] Generación de Figuras.

**Tu objetivo ahora:** Obtener las curvas de $\text{Skill}(h)$ reales para todos los dominios.

---

**¿Te gustaría que redacte un párrafo formal para la sección de "Trabajo Futuro" del Paper 2 donde se explique esta evolución de la métrica?**
