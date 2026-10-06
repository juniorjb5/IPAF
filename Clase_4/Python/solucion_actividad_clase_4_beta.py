# -*- coding: utf-8 -*-
"""Solucion de referencia - Actividad Clase 4.

Ejemplo resuelto con MSFT y el S&P 500. Si yfinance no esta disponible,
usa la base simulada de respaldo para que el flujo completo se pueda revisar.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TICKER = "MSFT"
MERCADO = "^GSPC"
INICIO = "2024-10-01"
FIN = "2026-10-01"
RUTA = "datos/"
os.makedirs("resultados", exist_ok=True)


def cargar_precios(ticker):
    try:
        import yfinance as yf
        bruto = yf.download(
            [ticker, MERCADO],
            start=INICIO,
            end=FIN,
            auto_adjust=True,
            progress=False,
        )
        if bruto.empty:
            raise ValueError("La descarga llego vacia.")
        precios = bruto["Close"].rename(
            columns={ticker: "Activo", MERCADO: "Mercado"}
        )[["Activo", "Mercado"]].dropna()
        return precios, "yfinance"
    except Exception as error:
        print("No fue posible usar yfinance:", error)
        print("Se usara respaldo simulado.")
        respaldo = pd.read_csv(
            RUTA + "mercado_respaldo_clase4.csv",
            parse_dates=["Date"]
        ).set_index("Date")
        columna = ticker + "_SIM"
        if columna not in respaldo.columns:
            columna = "MSFT_SIM"
        precios = respaldo[[columna, "MARKET_SIM"]].rename(
            columns={columna: "Activo", "MARKET_SIM": "Mercado"}
        ).loc[INICIO:FIN].dropna()
        return precios, "respaldo_simulado"


# ============================================================
# 1. CONSULTA Y REVISION
# ============================================================

precios, fuente = cargar_precios(TICKER)
print("Fuente:", fuente)
print("Forma:", precios.shape)
print(precios.head())
print(precios.tail())

# ============================================================
# 2. RETORNOS Y VARIABLES MOVILES
# ============================================================

retornos = precios.pct_change().dropna()

analisis = pd.DataFrame(index=precios.index)
analisis["precio"] = precios["Activo"]
analisis["media_20"] = analisis["precio"].rolling(20).mean()
analisis["media_60"] = analisis["precio"].rolling(60).mean()
analisis["retorno"] = precios["Activo"].pct_change()
analisis["vol_20_anual"] = analisis["retorno"].rolling(20).std() * np.sqrt(252)

# ============================================================
# 3. ESTADISTICA DESCRIPTIVA
# ============================================================

estadistica = retornos["Activo"].describe()
retorno_medio = retornos["Activo"].mean()
vol_anual = retornos["Activo"].std() * np.sqrt(252)

print("\nEstadistica descriptiva")
print(estadistica)
print("Retorno medio diario:", retorno_medio)
print("Volatilidad anualizada:", vol_anual)

# Fecha de mayor volatilidad movil.
fecha_max_vol = analisis["vol_20_anual"].idxmax()
max_vol = analisis.loc[fecha_max_vol, "vol_20_anual"]
print("Mayor volatilidad movil:", max_vol, "en", fecha_max_vol.date())

# ============================================================
# 4. CORRELACION Y BETA
# ============================================================

correlacion = retornos["Activo"].corr(retornos["Mercado"])
beta, alpha = np.polyfit(retornos["Mercado"], retornos["Activo"], 1)
r2 = correlacion ** 2

print("\nCorrelacion con el mercado:", correlacion)
print("Beta:", beta)
print("Alpha diario:", alpha)
print("R2:", r2)

# Verificacion del beta.
beta_alt = retornos["Activo"].cov(retornos["Mercado"]) / retornos["Mercado"].var()
print("Beta por covarianza/varianza:", beta_alt)

# ============================================================
# 5. VISUALIZACIONES
# ============================================================

ax = analisis[["precio", "media_20", "media_60"]].plot(figsize=(11, 5))
ax.set_title(f"{TICKER}: precio y medias moviles")
ax.set_ylabel("Precio")
plt.tight_layout()
plt.savefig(f"resultados/{TICKER}_precio_medias.png", dpi=160)
plt.close()

ax = analisis["vol_20_anual"].plot(figsize=(11, 4))
ax.set_title(f"{TICKER}: volatilidad movil anualizada")
ax.set_ylabel("Volatilidad")
plt.tight_layout()
plt.savefig(f"resultados/{TICKER}_volatilidad.png", dpi=160)
plt.close()

x = retornos["Mercado"]
y = retornos["Activo"]
orden = np.argsort(x.to_numpy())
x_ordenado = x.to_numpy()[orden]
y_recta = alpha + beta * x_ordenado

plt.figure(figsize=(8, 5))
plt.scatter(x, y, alpha=0.30)
plt.plot(x_ordenado, y_recta)
plt.xlabel("Retorno del mercado")
plt.ylabel(f"Retorno de {TICKER}")
plt.title(f"{TICKER} vs mercado - beta = {beta:.2f}")
plt.tight_layout()
plt.savefig(f"resultados/{TICKER}_beta.png", dpi=160)
plt.close()

# ============================================================
# 6. RESUMEN EJECUTIVO
# ============================================================

if beta > 1:
    lectura_beta = "mas sensible que el mercado"
elif beta >= 0:
    lectura_beta = "menos sensible que el mercado"
else:
    lectura_beta = "con sensibilidad inversa al mercado en la muestra"

print("\n=== INTERPRETACION SUGERIDA ===")
print(f"Se analizaron {len(retornos)} retornos diarios de {TICKER}.")
print(f"La volatilidad anualizada fue aproximadamente {vol_anual:.2%}.")
print(f"La correlacion con el mercado fue {correlacion:.2f}.")
print(f"El beta estimado fue {beta:.2f}, por lo que la accion fue {lectura_beta}.")
print(f"El R2 fue {r2:.2f}; el beta resume sensibilidad, pero no explica toda la variacion.")
print("La conclusion depende del periodo, la frecuencia y la calidad de los datos usados.")

# ============================================================
# 7. EXPORTACION
# ============================================================

resumen = pd.DataFrame({
    "ticker": [TICKER],
    "fuente": [fuente],
    "observaciones": [len(retornos)],
    "retorno_medio_diario": [retorno_medio],
    "volatilidad_anualizada": [vol_anual],
    "correlacion_mercado": [correlacion],
    "beta": [beta],
    "alpha_diario": [alpha],
    "r2": [r2],
    "fecha_max_volatilidad": [fecha_max_vol],
    "max_volatilidad_movil": [max_vol],
})

resumen.to_csv(f"resultados/{TICKER}_resumen_actividad_clase4.csv", index=False)
analisis.to_csv(f"resultados/{TICKER}_serie_actividad_clase4.csv")

print("Archivos de la actividad creados en resultados.")
