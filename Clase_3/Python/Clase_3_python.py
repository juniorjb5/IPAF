# -*- coding: utf-8 -*-
"""Clase 3 - Funciones, diccionarios, pandas, limpieza y agregación.

Este script acompaña la clase guiada. La idea es ejecutarlo lentamente,
leyendo los comentarios y revisando cada resultado antes de continuar.
"""

# ============================================================
# CLASE 3 - FUNCIONES, DICCIONARIOS Y PANDAS
# Curso: Introduccion a la programacion para analitica financiera
# Profesor: Orlando Joaqui-Barandica
# Entorno recomendado: Google Colab
# ============================================================

# ============================================================
# 0. LIBRERIAS Y RUTAS
# ============================================================

import os
import numpy as np
import pandas as pd

# En Colab, si la carpeta esta en Drive, cambie esta ruta.
# Si ejecuta desde la carpeta de la clase, deje RUTA = "datos/".
RUTA = "datos/"

# Esta carpeta guardara los archivos finales de la clase.
os.makedirs("resultados", exist_ok=True)

# ============================================================
# 1. FUNCIONES: GUARDAR UNA REGLA CON NOMBRE
# ============================================================

# Una funcion recibe datos de entrada, ejecuta una logica y devuelve un resultado.
# parametro: nombre que aparece dentro de la definicion de la funcion.
# argumento: valor real que entregamos al llamar la funcion.
# return: resultado que la funcion deja disponible para seguir trabajando.

def tasa_mensual(tasa_ea):
    """Convierte una tasa efectiva anual en tasa mensual vencida."""
    return (1 + tasa_ea) ** (1 / 12) - 1


def cuota_fija(monto, tasa_ea, plazo_meses):
    """Calcula la cuota fija mensual de un credito."""
    i = tasa_mensual(tasa_ea)
    cuota = monto * i / (1 - (1 + i) ** (-plazo_meses))
    return cuota


def endeudamiento_total(obligaciones_actuales, cuota_nueva, ingreso_mensual):
    """Calcula la carga financiera total del cliente."""
    return (obligaciones_actuales + cuota_nueva) / ingreso_mensual


def decidir_credito(score, carga, antiguedad_meses, tiene_mora):
    """Aplica un motor didactico de reglas para decidir una solicitud."""
    if score >= 700 and carga <= 0.40 and antiguedad_meses >= 12 and not tiene_mora:
        return "APROBADO"
    elif score >= 650 and carga <= 0.50 and antiguedad_meses >= 6 and not tiene_mora:
        return "REVISION"
    else:
        return "NEGADO"

print("=== 1. FUNCIONES ===")
print("Tasa mensual equivalente:", tasa_mensual(0.215))
print("Cuota estimada:", cuota_fija(34_500_000, 0.215, 36))

# Ojo: print muestra; return devuelve.
# Si una funcion no tiene return, Python devuelve None y el error aparece mas adelante.

# ============================================================
# 2. DICCIONARIOS: UNA FICHA DE CLIENTE
# ============================================================

cliente = {
    "id": "SOL-PRUEBA-001",
    "ingreso_mensual": 7_200_000,
    "obligaciones_actuales": 1_150_000,
    "score": 718,
    "antiguedad_meses": 28,
    "tiene_mora": False,
}

print("\n=== 2. DICCIONARIO ===")
print(cliente)
print("Score:", cliente["score"])

# Agregar una clave nueva.
cliente["ciudad"] = "Cali"

# Modificar una clave existente.
cliente["score"] = 724

# get() evita que el codigo se rompa cuando una clave no existe.
print("Calificacion:", cliente.get("calificacion", "Sin dato"))

# Una lista de diccionarios ya se parece a una tabla: cada diccionario es una fila.
portafolio = [
    {"activo": "CDT Banco Agrario", "clase": "renta fija", "valor": 71_900_000, "retorno": 0.094},
    {"activo": "TES 2034", "clase": "renta fija", "valor": 58_400_000, "retorno": 0.112},
    {"activo": "PFBCOLOM", "clase": "renta variable", "valor": 27_300_000, "retorno": 0.163},
]

valor_total = 0
for posicion in portafolio:
    valor_total += posicion["valor"]

retorno_ponderado = 0
for posicion in portafolio:
    peso = posicion["valor"] / valor_total
    posicion["peso"] = peso
    retorno_ponderado += peso * posicion["retorno"]

print("Valor total del portafolio:", valor_total)
print("Retorno ponderado:", retorno_ponderado)
print("Portafolio con pesos:", portafolio)

# ============================================================
# 3. ARRAYS Y OPERACIONES VECTORIZADAS
# ============================================================

# NumPy permite escribir una operacion una vez y aplicarla sobre muchos datos.
# En pandas pasara lo mismo con columnas completas.

montos = np.array([12_500_000, 8_300_000, 21_700_000, 6_900_000])
comisiones = montos * 0.015

print("\n=== 3. NUMPY ===")
print("Comisiones:", comisiones)
print("Comision total:", comisiones.sum())

# VPN sin ciclo.
flujos = np.array([-95_000_000, 27_400_000, 31_900_000, 35_600_000, 39_200_000])
periodos = np.arange(len(flujos))
tasa = 0.168
vpn = (flujos / (1 + tasa) ** periodos).sum()
print("VPN del proyecto:", vpn)

# ============================================================
# 4. LECTURA DE DATOS CON PANDAS
# ============================================================

# read_csv debe leer el archivo como viene, no como uno quisiera que viniera.
# sep=";" indica que las columnas estan separadas por punto y coma.
# decimal="," indica que los decimales vienen con coma.
# encoding="cp1252" ayuda a leer tildes y caracteres comunes en archivos de Excel en español.

cartera = pd.read_csv(
    RUTA + "cartera_credito_clase3.csv",
    sep=";",
    decimal=",",
    encoding="cp1252",
)

catalogo = pd.read_excel(RUTA + "catalogo_productos_clase3.xlsx", sheet_name="Catalogo")

print("\n=== 4. LECTURA ===")
print(cartera.head())
print("Forma:", cartera.shape)
print("Columnas:", list(cartera.columns))

# ============================================================
# 5. DIAGNOSTICO ANTES DE TOCAR LA BASE
# ============================================================

print("\n=== 5. DIAGNOSTICO ===")
print("Info general")
print(cartera.info())

print("\nFaltantes por columna")
print(cartera.isna().sum())

print("\nResumen numerico")
print(cartera.describe())

print("\nDuplicados exactos:", cartera.duplicated().sum())
print("Duplicados por id_solicitud:", cartera.duplicated(subset="id_solicitud").sum())

print("\nOficinas antes de limpiar")
print(cartera["oficina"].value_counts(dropna=False).head(12))

# ============================================================
# 6. LIMPIEZA Y TRANSFORMACION
# ============================================================

# Trabajamos sobre una copia para mantener el archivo original intacto.
trabajo = cartera.copy()

# 6.1. Quitar duplicados exactos.
antes = len(trabajo)
trabajo = trabajo.drop_duplicates()
print("\nFilas eliminadas por duplicado exacto:", antes - len(trabajo))

# 6.2. Si un id aparece mas de una vez, conservamos el registro mas reciente.
trabajo["fecha_solicitud"] = pd.to_datetime(trabajo["fecha_solicitud"], errors="coerce")
trabajo = trabajo.sort_values("fecha_solicitud")
antes = len(trabajo)
trabajo = trabajo.drop_duplicates(subset="id_solicitud", keep="last")
print("Filas eliminadas por id_solicitud repetido:", antes - len(trabajo))

# 6.3. Normalizar texto: quitar espacios y unificar mayusculas/minusculas.
columnas_texto = ["oficina", "segmento", "producto", "canal"]
for col in columnas_texto:
    trabajo[col] = trabajo[col].astype("string").str.strip().str.title()

# 6.4. Convertir columnas que pudieron llegar como texto.
trabajo["monto_solicitado"] = pd.to_numeric(trabajo["monto_solicitado"], errors="coerce")
trabajo["ingreso_mensual"] = pd.to_numeric(trabajo["ingreso_mensual"], errors="coerce")
trabajo["obligaciones_actuales"] = pd.to_numeric(trabajo["obligaciones_actuales"], errors="coerce")
trabajo["score"] = pd.to_numeric(trabajo["score"], errors="coerce")
trabajo["tasa_ea"] = pd.to_numeric(trabajo["tasa_ea"], errors="coerce")

# 6.5. Una tasa mayor que 1 normalmente indica que llego en escala porcentual.
# Ejemplo: 23.5 debe ser 0.235.
trabajo["tasa_ea"] = np.where(trabajo["tasa_ea"] > 1, trabajo["tasa_ea"] / 100, trabajo["tasa_ea"])

# 6.6. Obligaciones negativas no tienen sentido en este ejercicio.
# Las corregimos a cero y dejamos documentada la regla.
trabajo.loc[trabajo["obligaciones_actuales"] < 0, "obligaciones_actuales"] = 0

# 6.7. Faltantes.
# En variables categoricas dejamos una etiqueta visible.
trabajo["oficina"] = trabajo["oficina"].fillna("Sin Oficina")
trabajo["segmento"] = trabajo["segmento"].fillna("Sin Segmento")

# En variables numericas usamos mediana como salida didactica.
# En un informe real, esta decision debe justificarse.
for col in ["score", "ingreso_mensual", "monto_solicitado", "obligaciones_actuales"]:
    trabajo[col] = trabajo[col].fillna(trabajo[col].median())

# 6.8. Mora a booleano.
trabajo["tiene_mora"] = (
    trabajo["tiene_mora"]
    .astype("string")
    .str.lower()
    .str.strip()
    .map({"sí": True, "si": True, "no": False})
    .fillna(False)
)

print("\nFaltantes despues de limpiar")
print(trabajo.isna().sum())
print("Forma final de la tabla limpia:", trabajo.shape)

# ============================================================
# 7. FILTROS Y MASCARAS BOOLEANAS
# ============================================================

# Una mascara booleana es una columna de True/False que se puede guardar con nombre.
en_mora = trabajo["tiene_mora"]
score_alto = trabajo["score"] >= 700
monto_grande = trabajo["monto_solicitado"] > 35_000_000

print("\n=== 7. FILTROS ===")
print("Solicitudes en mora:", en_mora.sum())
print("Proporcion en mora:", en_mora.mean())

# & significa Y; | significa O; ~ significa NO.
prioridad = trabajo[score_alto & monto_grande & ~en_mora]
print("Solicitudes prioridad:", prioridad.shape[0])

# .loc permite filtrar filas y seleccionar columnas en una sola instruccion.
print(trabajo.loc[en_mora, ["id_solicitud", "oficina", "score", "monto_solicitado"]].head())

# ============================================================
# 8. COLUMNAS CALCULADAS Y MOTOR DE DECISION
# ============================================================

# Cuando la formula usa columnas completas, pandas aplica el calculo fila a fila internamente.
trabajo["tasa_mensual"] = (1 + trabajo["tasa_ea"]) ** (1 / 12) - 1

# apply(axis=1) entrega cada fila completa a una funcion.
# Es util cuando la regla necesita varias columnas al tiempo.
trabajo["cuota_estimada"] = trabajo.apply(
    lambda f: cuota_fija(f["monto_solicitado"], f["tasa_ea"], f["plazo_meses"]),
    axis=1,
)

trabajo["endeudamiento_total"] = (
    trabajo["obligaciones_actuales"] + trabajo["cuota_estimada"]
) / trabajo["ingreso_mensual"]

trabajo["decision"] = trabajo.apply(
    lambda f: decidir_credito(
        f["score"],
        f["endeudamiento_total"],
        f["antiguedad_meses"],
        f["tiene_mora"],
    ),
    axis=1,
)

print("\n=== 8. DECISION ===")
print(trabajo[["id_solicitud", "score", "endeudamiento_total", "decision"]].head())
print(trabajo["decision"].value_counts())

# ============================================================
# 9. CRUCE CON CATALOGO DE PRODUCTOS
# ============================================================

print("\n=== 9. CATALOGO ===")
print(catalogo)

filas_antes = len(trabajo)
saldo_antes = trabajo["monto_solicitado"].sum()

trabajo = trabajo.merge(catalogo, on="producto", how="left")

# Verificaciones sencillas del cruce.
assert len(trabajo) == filas_antes
assert round(trabajo["monto_solicitado"].sum(), 2) == round(saldo_antes, 2)
print("Productos sin cruce:", trabajo["linea"].isna().sum())

# ============================================================
# 10. AGREGACION: CAMBIAR LA GRANULARIDAD
# ============================================================

# groupby divide la tabla por grupos; agg calcula resumenes en cada grupo.
resumen_segmento = trabajo.groupby("segmento", as_index=False).agg(
    solicitudes=("id_solicitud", "count"),
    monto_total=("monto_solicitado", "sum"),
    ingreso_promedio=("ingreso_mensual", "mean"),
    cuota_promedio=("cuota_estimada", "mean"),
    endeudamiento_promedio=("endeudamiento_total", "mean"),
)

resumen_decision = trabajo.groupby(["segmento", "decision"], as_index=False).agg(
    solicitudes=("id_solicitud", "count"),
    monto_total=("monto_solicitado", "sum"),
)

# pivot_table funciona como una tabla dinamica.
tabla_decisiones = trabajo.pivot_table(
    index="segmento",
    columns="decision",
    values="monto_solicitado",
    aggfunc="sum",
    fill_value=0,
)

print("\n=== 10. RESUMENES ===")
print(resumen_segmento)
print(resumen_decision)
print(tabla_decisiones)

# ============================================================
# 11. BASE FINAL Y EXPORTACION
# ============================================================

base_final = trabajo[[
    "id_solicitud", "fecha_solicitud", "oficina", "segmento", "producto", "linea",
    "score", "ingreso_mensual", "obligaciones_actuales", "monto_solicitado",
    "tasa_ea", "plazo_meses", "cuota_estimada", "endeudamiento_total", "decision",
]].copy()

base_final = base_final.sort_values(["decision", "endeudamiento_total"], ascending=[True, False])

base_final.to_csv("resultados/base_final_clase3.csv", index=False, encoding="utf-8-sig")

with pd.ExcelWriter("resultados/informe_clase3.xlsx") as libro:
    base_final.to_excel(libro, sheet_name="Base final", index=False)
    resumen_segmento.to_excel(libro, sheet_name="Resumen segmento", index=False)
    resumen_decision.to_excel(libro, sheet_name="Resumen decision", index=False)
    tabla_decisiones.to_excel(libro, sheet_name="Tabla dinamica")

print("\n=== ARCHIVOS EXPORTADOS ===")
print("resultados/base_final_clase3.csv")
print("resultados/informe_clase3.xlsx")

# ============================================================
# 12. RETOS RAPIDOS PARA CLASE
# ============================================================

# 1. Cambie el umbral de aprobacion de 40% a 45% y revise cuantas solicitudes cambian.
# 2. Liste las 10 solicitudes con mayor endeudamiento_total usando nlargest().
# 3. Construya un resumen por oficina y decision.
# 4. Repita el groupby por linea de producto en vez de segmento.
# 5. Exporte solamente las solicitudes en REVISION.
