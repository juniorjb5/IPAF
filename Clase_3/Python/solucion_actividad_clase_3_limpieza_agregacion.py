# -*- coding: utf-8 -*-
"""Solucion de la actividad - Clase 3.

Actividad: limpiar solicitudes de credito, calcular cuota y endeudamiento,
aplicar el motor de decision y construir resumenes ejecutivos.
"""

import os
import numpy as np
import pandas as pd

RUTA = "datos/"
os.makedirs("resultados", exist_ok=True)

# ============================================================
# 1. FUNCIONES NECESARIAS
# ============================================================

def tasa_mensual(tasa_ea):
    return (1 + tasa_ea) ** (1 / 12) - 1


def cuota_fija(monto, tasa_ea, plazo_meses):
    i = tasa_mensual(tasa_ea)
    return monto * i / (1 - (1 + i) ** (-plazo_meses))


def decidir_credito(score, carga, antiguedad_meses, tiene_mora):
    if score >= 700 and carga <= 0.40 and antiguedad_meses >= 12 and not tiene_mora:
        return "APROBADO"
    elif score >= 650 and carga <= 0.50 and antiguedad_meses >= 6 and not tiene_mora:
        return "REVISION"
    else:
        return "NEGADO"

# ============================================================
# 2. LECTURA Y DIAGNOSTICO
# ============================================================

actividad = pd.read_csv(
    RUTA + "clientes_credito_actividad.csv",
    sep=";",
    decimal=",",
    encoding="cp1252",
)

print("Forma inicial:", actividad.shape)
print(actividad.head())
print(actividad.info())
print("Faltantes iniciales")
print(actividad.isna().sum())
print("Duplicados exactos:", actividad.duplicated().sum())

# ============================================================
# 3. LIMPIEZA
# ============================================================

base = actividad.copy()
base = base.drop_duplicates()
base["fecha_solicitud"] = pd.to_datetime(base["fecha_solicitud"], errors="coerce")

for col in ["oficina", "segmento", "producto", "canal"]:
    base[col] = base[col].astype("string").str.strip().str.title()

for col in ["monto_solicitado", "ingreso_mensual", "obligaciones_actuales", "score", "tasa_ea"]:
    base[col] = pd.to_numeric(base[col], errors="coerce")

base["tasa_ea"] = np.where(base["tasa_ea"] > 1, base["tasa_ea"] / 100, base["tasa_ea"])
base.loc[base["obligaciones_actuales"] < 0, "obligaciones_actuales"] = 0

base["oficina"] = base["oficina"].fillna("Sin Oficina")
base["segmento"] = base["segmento"].fillna("Sin Segmento")

for col in ["score", "ingreso_mensual", "monto_solicitado", "obligaciones_actuales"]:
    base[col] = base[col].fillna(base[col].median())

base["tiene_mora"] = (
    base["tiene_mora"].astype("string").str.lower().str.strip()
    .map({"sí": True, "si": True, "no": False})
    .fillna(False)
)

print("Faltantes despues de limpieza")
print(base.isna().sum())

# ============================================================
# 4. COLUMNAS CALCULADAS Y DECISION
# ============================================================

base["cuota_estimada"] = base.apply(
    lambda f: cuota_fija(f["monto_solicitado"], f["tasa_ea"], f["plazo_meses"]),
    axis=1,
)

base["endeudamiento_total"] = (
    base["obligaciones_actuales"] + base["cuota_estimada"]
) / base["ingreso_mensual"]

base["decision"] = base.apply(
    lambda f: decidir_credito(
        f["score"], f["endeudamiento_total"], f["antiguedad_meses"], f["tiene_mora"]
    ),
    axis=1,
)

# ============================================================
# 5. CRUCE CON CATALOGO
# ============================================================

catalogo = pd.read_excel(RUTA + "catalogo_productos_clase3.xlsx", sheet_name="Catalogo")
filas_antes = len(base)
base = base.merge(catalogo, on="producto", how="left")
assert len(base) == filas_antes

# ============================================================
# 6. RESUMENES
# ============================================================

resumen_segmento = base.groupby("segmento", as_index=False).agg(
    solicitudes=("id_solicitud", "count"),
    aprobadas=("decision", lambda x: (x == "APROBADO").sum()),
    revision=("decision", lambda x: (x == "REVISION").sum()),
    negadas=("decision", lambda x: (x == "NEGADO").sum()),
    monto_total=("monto_solicitado", "sum"),
    endeudamiento_promedio=("endeudamiento_total", "mean"),
)

resumen_decision = base.groupby(["segmento", "decision"], as_index=False).agg(
    solicitudes=("id_solicitud", "count"),
    monto_total=("monto_solicitado", "sum"),
    cuota_promedio=("cuota_estimada", "mean"),
)

tabla_decisiones = base.pivot_table(
    index="segmento",
    columns="decision",
    values="id_solicitud",
    aggfunc="count",
    fill_value=0,
)

print("Resumen por segmento")
print(resumen_segmento)
print("Resumen por segmento y decision")
print(resumen_decision)
print("Tabla cruzada")
print(tabla_decisiones)

# ============================================================
# 7. EXPORTACION
# ============================================================

base_final = base[[
    "id_solicitud", "fecha_solicitud", "oficina", "segmento", "producto", "linea",
    "score", "ingreso_mensual", "obligaciones_actuales", "monto_solicitado",
    "tasa_ea", "plazo_meses", "cuota_estimada", "endeudamiento_total", "decision"
]].copy()

base_final = base_final.sort_values("endeudamiento_total", ascending=False)

base_final.to_csv("resultados/actividad_clase3_base_final.csv", index=False, encoding="utf-8-sig")
with pd.ExcelWriter("resultados/actividad_clase3_informe.xlsx") as libro:
    base_final.to_excel(libro, sheet_name="Base final", index=False)
    resumen_segmento.to_excel(libro, sheet_name="Resumen segmento", index=False)
    resumen_decision.to_excel(libro, sheet_name="Resumen decision", index=False)
    tabla_decisiones.to_excel(libro, sheet_name="Tabla cruzada")

print("Archivos creados en la carpeta resultados.")

# Interpretacion sugerida para escribir en texto:
# 1. Identificar el segmento con mas solicitudes.
# 2. Comparar aprobadas, revision y negadas.
# 3. Revisar si el endeudamiento promedio ayuda a explicar las negaciones.
# 4. Mencionar una decision de limpieza que pueda afectar el resultado.
