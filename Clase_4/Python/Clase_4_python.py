# -*- coding: utf-8 -*-
"""Clase 4 - Datos de mercado, series de tiempo y beta.

Script guiado para trabajar con datos reales de mercado mediante yfinance.
Incluye retornos simples y logaritmicos, medias moviles, volatilidad,
estadistica descriptiva, correlacion y estimacion del beta.
"""

# ============================================================
# CLASE 4 - DATOS DE MERCADO, SERIES DE TIEMPO Y BETA
# Curso: Introduccion a la programacion para analitica financiera
# Profesor: Orlando Joaqui-Barandica
# Entorno recomendado: Google Colab
# ============================================================

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

RUTA = "Clase_4/datos/"
os.makedirs("resultados", exist_ok=True)

# ============================================================
# 1. JSON -> DATAFRAME
# ============================================================

with open(RUTA + "respuesta_api_ejemplo.json", encoding="utf-8") as archivo:
    respuesta = json.load(archivo)

print("Instrumento del JSON:", respuesta["instrument"])
print("Moneda:", respuesta["currency"])

precios_api = pd.DataFrame(respuesta["data"])

precios_api["date"] = pd.to_datetime(precios_api["date"])

precios_api = precios_api.set_index("date")

print("\n=== JSON A DATAFRAME ===")
print(precios_api)


# ============================================================
# 2. REFERENCIA LSEG WORKSPACE / REFINITIV
# ============================================================

# Este bloque se muestra como referencia.
# Requiere acceso institucional a LSEG Workspace.

LSEG_EJEMPLO = r"""
import lseg.data as ld

ld.open_session()

hist = ld.get_history(
    universe="AAPL.O",
    fields=["TRDPRC_1"],
    interval="1D",
    start="2026-01-01",
    end="2026-09-30"
)

ld.close_session()
"""

print("\n=== EJEMPLO LSEG ===")
print(LSEG_EJEMPLO)


# ============================================================
# 3. DESCARGAR DATOS DE MERCADO CON YFINANCE
# ============================================================

apple = yf.download(
    "AAPL",
    start="2025-01-01",
    end="2026-10-01",
    auto_adjust=True,
    progress=False,
    multi_level_index=False
)

print("\n=== DATOS DE AAPL ===")
print(apple.head())

print("\nForma de la base:")
print(apple.shape)

print("\nTipo de indice:")
print(type(apple.index))

apple = apple.sort_index()


# ============================================================
# 4. RETORNO SIMPLE Y RETORNO LOGARITMICO
# ============================================================

# Retorno simple:
#
# R_t = P_t / P_(t-1) - 1

apple["retorno_simple"] = apple["Close"].pct_change()


# Retorno logaritmico:
#
# r_t = ln(P_t / P_(t-1))

apple["retorno_log"] = np.log(
    apple["Close"] / apple["Close"].shift(1)
)

print("\n=== RETORNOS ===")

print(
    apple[
        [
            "Close",
            "retorno_simple",
            "retorno_log"
        ]
    ].tail()
)


# ============================================================
# 5. MEDIAS MOVILES
# ============================================================

# Media movil de 20 dias.

apple["media_20"] = (
    apple["Close"]
    .rolling(20)
    .mean()
)


# Media movil de 60 dias.

apple["media_60"] = (
    apple["Close"]
    .rolling(60)
    .mean()
)


# ============================================================
# 6. VOLATILIDAD
# ============================================================

# Volatilidad movil de 20 dias usando retornos logaritmicos.
# Se anualiza multiplicando por sqrt(252).

apple["vol_20_anual"] = (
    apple["retorno_log"]
    .rolling(20)
    .std()
    * np.sqrt(252)
)

print("\n=== VARIABLES TEMPORALES ===")

print(
    apple[
        [
            "Close",
            "retorno_simple",
            "retorno_log",
            "media_20",
            "media_60",
            "vol_20_anual"
        ]
    ].tail()
)


# ============================================================
# 7. VISUALIZACIONES
# ============================================================

# ------------------------------------------------------------
# Precio y medias moviles
# ------------------------------------------------------------


apple[["Close", "media_20", "media_60"]].plot(figsize=(13, 4.5))

plt.show()




ax = apple[
    ["Close", "media_20", "media_60"]
].plot(
    figsize=(13, 4.5),
    linewidth=1.5
)

ax.set_title(
    "AAPL: precio y medias móviles",
    fontsize=14,
    pad=12
)

ax.set_ylabel("Precio")
ax.set_xlabel("")

ax.legend(
    ["Precio", "Media móvil 20 días", "Media móvil 60 días"],
    frameon=False
)

ax.grid(
    axis="y",
    alpha=0.25
)

plt.tight_layout()

plt.savefig(
    "resultados/aapl_precio_medias.png",
    dpi=200,
    bbox_inches="tight"
)

plt.show()

plt.close()
# ------------------------------------------------------------
# Retorno logaritmico
# ------------------------------------------------------------




fig, ax = plt.subplots(figsize=(12, 4))

apple["retorno_log"].plot(ax=ax)

ax.set_title("AAPL: retorno logarítmico diario")
ax.set_ylabel("Retorno")
ax.set_xlabel("Fecha")

plt.savefig(
    "resultados/aapl_retorno_log.png",
    dpi=160
)

plt.show()
plt.close()




# ------------------------------------------------------------
# Volatilidad movil
# ------------------------------------------------------------


fig, ax = plt.subplots(figsize=(12, 4))

apple["vol_20_anual"].plot(ax=ax)

ax.set_title("AAPL: volatilidad móvil anualizada (20 días)")
ax.set_ylabel("Volatilidad")
ax.set_xlabel("Fecha")

plt.tight_layout()

plt.savefig(
    "resultados/aapl_volatilidad.png",
    dpi=160
)

plt.show()
plt.close()




# ============================================================
# 8. ESTADISTICA DESCRIPTIVA
# ============================================================

print("\n=== ESTADISTICA: RETORNO SIMPLE ===")

print(
    apple["retorno_simple"].describe()
)


print("\n=== ESTADISTICA: RETORNO LOGARITMICO ===")

print(
    apple["retorno_log"].describe()
)


# Retorno medio diario.

retorno_medio_simple = (
    apple["retorno_simple"].mean()
)

retorno_medio_log = (
    apple["retorno_log"].mean()
)


# Volatilidad diaria.

vol_diaria = (
    apple["retorno_log"].std()
)


# Volatilidad anualizada.

vol_anual = (
    vol_diaria * np.sqrt(252)
)


print(
    "\nRetorno simple medio diario:",
    retorno_medio_simple
)

print(
    "Retorno logaritmico medio diario:",
    retorno_medio_log
)

print(
    "Volatilidad diaria:",
    vol_diaria
)

print(
    "Volatilidad anualizada:",
    vol_anual
)


# ============================================================
# 9. DESCARGAR ACCION Y MERCADO
# ============================================================

datos_mercado = yf.download(
    ["AAPL", "^GSPC"],
    start="2025-01-01",
    end="2026-10-01",
    auto_adjust=True,
    progress=False
)


# Extraemos solamente los precios de cierre.

precios = (
    datos_mercado["Close"]
    .copy()
)


# Renombramos las columnas.

precios = precios.rename(
    columns={
        "AAPL": "Activo",
        "^GSPC": "Mercado"
    }
)


# Conservamos solamente observaciones completas.

precios = (
    precios[
        ["Activo", "Mercado"]
    ]
    .dropna()
)


print("\n=== PRECIOS: ACCION Y MERCADO ===")

print(precios.head())


# ============================================================
# 10. RETORNOS DE LA ACCION Y DEL MERCADO
# ============================================================

# Para estimar el beta utilizaremos retornos simples.

retornos = (
    precios
    .pct_change()
    .dropna()
)


print("\n=== RETORNOS: ACCION Y MERCADO ===")

print(retornos.head())


# ============================================================
# 11. CORRELACION
# ============================================================

print("\n=== MATRIZ DE CORRELACION ===")

print(
    retornos.corr()
)


correlacion = (
    retornos["Activo"]
    .corr(
        retornos["Mercado"]
    )
)


print(
    "\nCorrelacion entre AAPL y el mercado:",
    correlacion
)


# ============================================================
# 12. REGRESION LINEAL SIMPLE: BETA
# ============================================================

# Modelo:
#
# Retorno_Activo =
# alpha + beta * Retorno_Mercado + error
#
# np.polyfit devuelve:
# pendiente, intercepto

beta, alpha = np.polyfit(
    retornos["Mercado"],
    retornos["Activo"],
    1
)


print("\n=== REGRESION SIMPLE ===")

print(
    "Alpha diario:",
    alpha
)

print(
    "Beta:",
    beta
)


# ============================================================
# 13. COMPROBAR EL BETA
# ============================================================

# El beta tambien puede calcularse como:
#
# Cov(Activo, Mercado)
# ---------------------
# Var(Mercado)

beta_alt = (
    retornos["Activo"]
    .cov(retornos["Mercado"])
    /
    retornos["Mercado"]
    .var()
)


print(
    "\nBeta por regresion:",
    beta
)

print(
    "Beta por covarianza / varianza:",
    beta_alt
)

print(
    "Diferencia:",
    abs(beta - beta_alt)
)


# ============================================================
# 14. R CUADRADO
# ============================================================

# En una regresion lineal simple con intercepto:
#
# R2 = correlacion^2

r2 = correlacion ** 2


print(
    "\nCorrelacion:",
    correlacion
)

print(
    "R2:",
    r2
)


# ============================================================
# 15. GRAFICO DE LA REGRESION
# ============================================================

x = retornos["Mercado"]
y = retornos["Activo"]


# Ordenamos x para dibujar correctamente
# la recta de regresion.

orden = np.argsort(
    x.to_numpy()
)

x_ordenado = (
    x.to_numpy()[orden]
)


# Valores estimados por la regresion.

y_recta = (
    alpha
    + beta * x_ordenado
)


plt.figure(
    figsize=(8, 5)
)


plt.scatter(
    x,
    y,
    alpha=0.30
)


plt.plot(
    x_ordenado,
    y_recta
)


plt.xlabel(
    "Retorno del mercado"
)

plt.ylabel(
    "Retorno de AAPL"
)

plt.title(
    f"AAPL vs mercado - beta = {beta:.2f}"
)

plt.tight_layout()

plt.savefig(
    "resultados/aapl_beta.png",
    dpi=160
)

plt.show()


# ============================================================
# 16. INTERPRETACION DEL BETA
# ============================================================

if beta > 1:

    print(
        "\nLa accion presenta mayor sensibilidad "
        "que el mercado."
    )

elif beta > 0:

    print(
        "\nLa accion se mueve en la misma direccion "
        "del mercado, pero con menor sensibilidad."
    )

else:

    print(
        "\nLa accion presenta una relacion inversa "
        "con el mercado."
    )


# ============================================================
# 17. EXPORTAR RESULTADOS
# ============================================================

resumen = pd.DataFrame(
    {
        "metrica": [
            "retorno_simple_medio_diario",
            "retorno_log_medio_diario",
            "volatilidad_anualizada",
            "correlacion_mercado",
            "beta",
            "alpha_diario",
            "r2"
        ],

        "valor": [
            retorno_medio_simple,
            retorno_medio_log,
            vol_anual,
            correlacion,
            beta,
            alpha,
            r2
        ]
    }
)


resumen.to_csv(
    "resultados/resumen_clase4.csv",
    index=False
)


apple.to_csv(
    "resultados/aapl_serie_enriquecida.csv"
)


retornos.to_csv(
    "resultados/aapl_mercado_retornos.csv"
)


print(
    "\nArchivos creados en la carpeta resultados."
)
