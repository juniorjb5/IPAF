# Clase 4 — Datos de mercado, series de tiempo y beta

Esta clase integra las sesiones 7 y 8 del microcurrículo en una sola sesión de 3 horas.

Contenido del paquete:

- `Clase_4.Rmd`: diapositivas xaringan con la misma plantilla visual de las clases anteriores.
- `Clase_4.html`: versión HTML lista para abrir en navegador.
- `Python/Clase_4_python.py`: código guía para ejecutar durante la clase.
- `Python/Clase_4_python.ipynb`: notebook guía para Google Colab.
- `Python/solucion_actividad_clase_4_beta.py`: solución de referencia de la actividad.
- `Python/Solucion_Actividad_Clase_4_Beta.ipynb`: notebook solución.
- `datos/respuesta_api_ejemplo.json`: ejemplo didáctico para mostrar JSON → DataFrame.
- `datos/mercado_respaldo_clase4.csv`: base **simulada** de contingencia si no hay Internet.

## Flujo sugerido de la clase

1. API, endpoint y JSON.
2. Referencia de consulta con LSEG Data Library / Refinitiv.
3. Descarga con `yfinance` en Colab.
4. Fechas, retornos, medias móviles y volatilidad.
5. Estadística descriptiva y correlación.
6. Regresión lineal simple y beta.
7. Actividad por grupos con una acción distinta.

## Nota sobre LSEG Workspace / Refinitiv

La LSEG Data Library permite consultar datos desde Python. Una Desktop Session necesita que LSEG Workspace/Eikon esté abierto en la misma máquina donde corre Python. Por ello, una sesión de escritorio no se conecta directamente desde un Colab convencional; para Colab se requeriría un acceso/configuración de plataforma institucional compatible. En clase, `yfinance` permite practicar el flujo completo de consulta y análisis desde Colab sin exponer credenciales.

## Nota sobre yfinance

En Colab puede instalarse con:

```python
!pip -q install yfinance
```

La sintaxis del material usa `auto_adjust=True`. Para una sola acción también se usa `multi_level_index=False` para mantener una tabla sencilla.

## Respaldo sin Internet

Los scripts intentan primero usar `yfinance`. Si falla, cargan `datos/mercado_respaldo_clase4.csv`. Esa base es simulada y solo sirve para continuidad pedagógica; no debe presentarse como dato real de mercado.
