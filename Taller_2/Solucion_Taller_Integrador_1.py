# -*- coding: utf-8 -*-
"""
SOLUCIÓN - TALLER INTEGRADOR 1
Introducción a la programación para analítica financiera

Caso: Evaluación y estrés de una cartera de crédito.

Archivos de entrada esperados en la misma carpeta:
    - solicitudes_credito.csv
    - catalogo_productos.xlsx

El script:
    1. Audita y limpia la información.
    2. Cruza solicitudes con el catálogo.
    3. Construye funciones financieras reutilizables.
    4. Aplica la política de crédito.
    5. Analiza la cartera.
    6. Construye el escenario de estrés.
    7. Genera la tabla de amortización del crédito seleccionado.
    8. Compara la política original con una política de 45%.
    9. Exporta cartera_evaluada.xlsx y resumen_cartera.xlsx.

La solución utiliza únicamente herramientas trabajadas en las primeras clases:
variables, condicionales, listas, ciclos, funciones, diccionarios y pandas.
"""

# ============================================================
# 0. IMPORTAR LIBRERÍAS Y DEFINIR RUTAS
# ============================================================

import os
import numpy as np
import pandas as pd

# La ruta "." significa: trabajar en la carpeta actual.
# En Google Colab basta con cargar los dos archivos de entrada
# en el panel de archivos antes de ejecutar el notebook/script.
RUTA = "."
RUTA_RESULTADOS = "resultados"

# Creamos la carpeta de resultados si todavía no existe.
os.makedirs(RUTA_RESULTADOS, exist_ok=True)

ARCHIVO_SOLICITUDES = os.path.join(RUTA, "solicitudes_credito.csv")
ARCHIVO_CATALOGO = os.path.join(RUTA, "catalogo_productos.xlsx")

# Ajustamos la visualización de pandas para revisar mejor los resultados.
pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 140)


# ============================================================
# 1. LEER LOS DOS ARCHIVOS
# ============================================================

# Leemos la base principal de solicitudes.
solicitudes_raw = pd.read_csv(ARCHIVO_SOLICITUDES)

# Leemos el catálogo de productos desde Excel.
catalogo_raw = pd.read_excel(ARCHIVO_CATALOGO)

print("\n=== TAMAÑO INICIAL DE LAS BASES ===")
print("Solicitudes:", solicitudes_raw.shape)
print("Catálogo:", catalogo_raw.shape)

print("\n=== PRIMERAS FILAS DE SOLICITUDES ===")
print(solicitudes_raw.head())

print("\n=== INFORMACIÓN GENERAL DE SOLICITUDES ===")
solicitudes_raw.info()

print("\n=== VALORES FALTANTES INICIALES ===")
print(solicitudes_raw.isna().sum())


# ============================================================
# 2. FUNCIONES AUXILIARES PARA LIMPIEZA
# ============================================================

def normalizar_tasa(valor):
    """
    Convierte una tasa efectiva anual a escala decimal.

    Reglas:
    - Si el valor está entre 0 y 1, asumimos que ya está en decimal.
      Ejemplo: 0.205 = 20.5%.
    - Si está entre 1 y 100, asumimos que fue registrada como porcentaje.
      Ejemplo: 20.5 = 20.5% y se convierte en 0.205.
    - Si no cumple esas condiciones, se devuelve NaN.
    """
    if pd.isna(valor):
        return np.nan

    valor = float(valor)

    if 0 < valor <= 1:
        return valor
    elif 1 < valor <= 100:
        return valor / 100
    else:
        return np.nan


def normalizar_mora(valor):
    """
    Homogeneiza distintas formas de escribir el indicador de mora.

    Devuelve:
    - True  -> tiene mora.
    - False -> no tiene mora.
    - NaN   -> el valor no puede interpretarse.
    """
    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip().lower()

    mapa_mora = {
        "sí": True,
        "si": True,
        "1": True,
        "true": True,
        "no": False,
        "0": False,
        "false": False
    }

    return mapa_mora.get(texto, np.nan)


# ============================================================
# 3. AUDITORÍA Y LIMPIEZA DE SOLICITUDES
# ============================================================

# Trabajamos sobre una copia para conservar intacta la base original.
solicitudes = solicitudes_raw.copy()

# -------- 3.1. Duplicados --------

# El id_solicitud debería identificar una sola solicitud.
duplicados_id = solicitudes.duplicated(subset="id_solicitud", keep="first")

print("\n=== DUPLICADOS POR ID ===")
print("Número de filas duplicadas:", int(duplicados_id.sum()))

# Conservamos la primera aparición del id y retiramos las repeticiones.
solicitudes = solicitudes.loc[~duplicados_id].copy()


# -------- 3.2. Limpieza de textos --------

# Estandarizamos segmento:
# 1. usamos tipo string,
# 2. quitamos espacios al inicio/final,
# 3. dejamos formato Título.
solicitudes["segmento"] = (
    solicitudes["segmento"]
    .astype("string")
    .str.strip()
    .str.title()
)

# El segmento no participa en la regla de aprobación.
# Por eso, si falta, podemos conservar el registro bajo "Sin información".
solicitudes["segmento"] = solicitudes["segmento"].fillna("Sin información")

# Estandarizamos los nombres de los productos.
solicitudes["producto"] = (
    solicitudes["producto"]
    .astype("string")
    .str.strip()
    .str.title()
)

# Corregimos variantes ortográficas conocidas sin cambiar el producto.
solicitudes["producto"] = solicitudes["producto"].replace({
    "Microcredito": "Microcrédito",
    "Libre Inversion": "Libre Inversión"
})


# -------- 3.3. Conversión de variables numéricas --------

columnas_numericas = [
    "ingreso_mensual",
    "obligaciones_mensuales",
    "monto_solicitado",
    "tasa_ea",
    "plazo_meses",
    "score",
    "antiguedad_meses"
]

# errors="coerce" convierte en NaN cualquier valor que no pueda ser numérico.
for columna in columnas_numericas:
    solicitudes[columna] = pd.to_numeric(
        solicitudes[columna],
        errors="coerce"
    )

# La tasa viene deliberadamente en más de una escala.
solicitudes["tasa_ea"] = solicitudes["tasa_ea"].apply(normalizar_tasa)

# Homogeneizamos el indicador de mora.
solicitudes["tiene_mora"] = solicitudes["tiene_mora"].apply(normalizar_mora)

# Convertimos la fecha.
solicitudes["fecha_solicitud"] = pd.to_datetime(
    solicitudes["fecha_solicitud"],
    errors="coerce"
)


# ============================================================
# 4. AUDITORÍA Y LIMPIEZA DEL CATÁLOGO
# ============================================================

catalogo = catalogo_raw.copy()

# Limpiamos la llave que usaremos para cruzar las dos tablas.
catalogo["producto"] = (
    catalogo["producto"]
    .astype("string")
    .str.strip()
    .str.title()
)

catalogo["producto"] = catalogo["producto"].replace({
    "Microcredito": "Microcrédito",
    "Libre Inversion": "Libre Inversión"
})

# Convertimos las columnas numéricas del catálogo.
columnas_catalogo_numericas = [
    "monto_maximo",
    "tasa_referencia_ea",
    "plazo_max_meses",
    "comision_estudio_pct"
]

for columna in columnas_catalogo_numericas:
    catalogo[columna] = pd.to_numeric(
        catalogo[columna],
        errors="coerce"
    )

# También normalizamos la escala de la tasa de referencia.
catalogo["tasa_referencia_ea"] = (
    catalogo["tasa_referencia_ea"]
    .apply(normalizar_tasa)
)

# Revisamos si, después de limpiar texto, aparecen productos duplicados.
duplicados_catalogo = catalogo.duplicated(
    subset="producto",
    keep=False
)

print("\n=== PRODUCTOS DUPLICADOS EN EL CATÁLOGO ===")
print(catalogo.loc[duplicados_catalogo, ["producto", "monto_maximo", "tasa_referencia_ea"]])

# Como el duplicado suministrado contiene exactamente las mismas condiciones,
# conservamos una sola fila por producto.
catalogo = catalogo.drop_duplicates(
    subset="producto",
    keep="first"
).copy()


# ============================================================
# 5. CRUZAR SOLICITUDES CON EL CATÁLOGO
# ============================================================

# how="left" conserva todas las solicitudes.
trabajo = solicitudes.merge(
    catalogo,
    on="producto",
    how="left"
)

print("\n=== VERIFICACIÓN DEL CRUCE ===")
print("Filas antes del merge:", len(solicitudes))
print("Filas después del merge:", len(trabajo))

# Una solicitud sin monto_maximo no encontró producto en el catálogo.
sin_catalogo = trabajo["monto_maximo"].isna()

print("Solicitudes sin correspondencia en catálogo:", int(sin_catalogo.sum()))

if sin_catalogo.sum() > 0:
    print(
        trabajo.loc[
            sin_catalogo,
            ["id_solicitud", "producto"]
        ]
    )

# Si la tasa de una solicitud está ausente, utilizamos la tasa de referencia
# del producto como imputación explícita y trazable.
trabajo["tasa_ea"] = trabajo["tasa_ea"].fillna(
    trabajo["tasa_referencia_ea"]
)


# ============================================================
# 6. DEFINIR QUÉ REGISTROS SON UTILIZABLES
# ============================================================

def identificar_problemas_calidad(fila):
    """
    Devuelve una cadena con los problemas que impiden evaluar la solicitud.

    No todo dato extremo es un error:
    por ejemplo, un monto superior al máximo del producto NO se elimina,
    porque precisamente debe ser evaluado por la política y puede ser NEGADO.
    """
    problemas = []

    if pd.isna(fila["monto_maximo"]):
        problemas.append("Producto no catalogado")

    if pd.isna(fila["ingreso_mensual"]) or fila["ingreso_mensual"] <= 0:
        problemas.append("Ingreso faltante o no positivo")

    if (
        pd.isna(fila["obligaciones_mensuales"])
        or fila["obligaciones_mensuales"] < 0
    ):
        problemas.append("Obligaciones faltantes o negativas")

    if pd.isna(fila["monto_solicitado"]) or fila["monto_solicitado"] <= 0:
        problemas.append("Monto solicitado faltante o no positivo")

    if pd.isna(fila["tasa_ea"]) or not (0 < fila["tasa_ea"] <= 1):
        problemas.append("Tasa faltante o inválida")

    if pd.isna(fila["plazo_meses"]) or fila["plazo_meses"] <= 0:
        problemas.append("Plazo faltante o no positivo")

    if pd.isna(fila["score"]):
        problemas.append("Score faltante")

    if (
        pd.isna(fila["antiguedad_meses"])
        or fila["antiguedad_meses"] < 0
    ):
        problemas.append("Antigüedad faltante o negativa")

    if pd.isna(fila["tiene_mora"]):
        problemas.append("Estado de mora faltante/no reconocible")

    # Unimos la lista para que el diagnóstico quede visible por fila.
    return " | ".join(problemas)


# Aplicamos la función a cada fila.
trabajo["motivo_calidad"] = trabajo.apply(
    identificar_problemas_calidad,
    axis=1
)

# Un registro es utilizable si no quedó ningún motivo de exclusión.
trabajo["registro_utilizable"] = trabajo["motivo_calidad"].eq("")

# Separamos las observaciones que no pueden evaluarse.
no_utilizables = trabajo.loc[
    ~trabajo["registro_utilizable"]
].copy()

# La cartera que sí entra al análisis.
cartera = trabajo.loc[
    trabajo["registro_utilizable"]
].copy()

print("\n=== RESULTADO DE LA DEPURACIÓN ===")
print("Registros originales:", len(solicitudes_raw))
print("Duplicados retirados:", int(duplicados_id.sum()))
print("Registros no utilizables:", len(no_utilizables))
print("Registros utilizables:", len(cartera))

print("\n=== REGISTROS NO UTILIZABLES Y MOTIVO ===")
print(
    no_utilizables[
        ["id_solicitud", "motivo_calidad"]
    ].to_string(index=False)
)


# ============================================================
# 7. FUNCIONES FINANCIERAS
# ============================================================

def tasa_mensual(tasa_ea):
    """
    Convierte una tasa efectiva anual (EA) en tasa efectiva mensual.
    """
    return (1 + tasa_ea) ** (1 / 12) - 1


def cuota_fija(monto, tasa_ea, plazo_meses):
    """
    Calcula la cuota de un crédito bajo el sistema de cuota fija.
    """
    i = tasa_mensual(tasa_ea)

    factor = 1 - (1 + i) ** (-plazo_meses)

    return monto * i / factor


def endeudamiento_proyectado(
    obligaciones_actuales,
    cuota_nueva,
    ingreso_mensual
):
    """
    Calcula la carga financiera después de incluir el nuevo crédito.
    """
    return (
        obligaciones_actuales + cuota_nueva
    ) / ingreso_mensual


def clasificar_credito(
    score,
    endeudamiento,
    antiguedad_meses,
    tiene_mora,
    monto_solicitado,
    monto_maximo,
    politica
):
    """
    Aplica las reglas APROBADA / REVISIÓN / NEGADA.

    La política se recibe como diccionario.
    Esto permite cambiar umbrales sin reescribir toda la función.
    """

    # Condición para aprobación directa.
    cumple_aprobada = (
        score >= politica["score_aprobado"]
        and endeudamiento <= politica["endeudamiento_aprobado"]
        and antiguedad_meses >= politica["antiguedad_aprobado"]
        and tiene_mora == False
        and monto_solicitado <= monto_maximo
    )

    # Condición para revisión.
    cumple_revision = (
        score >= politica["score_revision"]
        and endeudamiento <= politica["endeudamiento_revision"]
        and antiguedad_meses >= politica["antiguedad_revision"]
        and tiene_mora == False
        and monto_solicitado <= monto_maximo
    )

    if cumple_aprobada:
        return "APROBADA"
    elif cumple_revision:
        return "REVISIÓN"
    else:
        return "NEGADA"


# ============================================================
# 8. POLÍTICA ORIGINAL Y EVALUACIÓN DE LA CARTERA
# ============================================================

# Guardamos los parámetros en un diccionario.
politica_original = {
    "score_aprobado": 700,
    "endeudamiento_aprobado": 0.40,
    "antiguedad_aprobado": 12,
    "score_revision": 650,
    "endeudamiento_revision": 0.50,
    "antiguedad_revision": 6
}

# Calculamos la cuota estimada de cada solicitud.
cartera["cuota_estimada"] = cartera.apply(
    lambda fila: cuota_fija(
        fila["monto_solicitado"],
        fila["tasa_ea"],
        int(fila["plazo_meses"])
    ),
    axis=1
)

# Calculamos el endeudamiento después de incorporar la nueva cuota.
cartera["endeudamiento_proyectado"] = cartera.apply(
    lambda fila: endeudamiento_proyectado(
        fila["obligaciones_mensuales"],
        fila["cuota_estimada"],
        fila["ingreso_mensual"]
    ),
    axis=1
)

# Aplicamos la política original.
cartera["decision_base"] = cartera.apply(
    lambda fila: clasificar_credito(
        fila["score"],
        fila["endeudamiento_proyectado"],
        fila["antiguedad_meses"],
        fila["tiene_mora"],
        fila["monto_solicitado"],
        fila["monto_maximo"],
        politica_original
    ),
    axis=1
)


# ============================================================
# 9. ANÁLISIS GENERAL DE LA CARTERA
# ============================================================

# -------- 9.1. Número y porcentaje por decisión --------

resumen_decision = (
    cartera["decision_base"]
    .value_counts()
    .rename_axis("decision")
    .reset_index(name="solicitudes")
)

resumen_decision["porcentaje"] = (
    resumen_decision["solicitudes"]
    / len(cartera)
)

print("\n=== DECISIONES DE CRÉDITO ===")
print(resumen_decision)


# -------- 9.2. Monto solicitado y monto aprobado --------

# Esta columna vale el monto solicitado únicamente si la solicitud fue aprobada.
cartera["monto_aprobado_base"] = np.where(
    cartera["decision_base"].eq("APROBADA"),
    cartera["monto_solicitado"],
    0
)

monto_total_solicitado = cartera["monto_solicitado"].sum()
monto_total_aprobado = cartera["monto_aprobado_base"].sum()

print("\n=== MONTOS PRINCIPALES ===")
print(f"Monto total solicitado: ${monto_total_solicitado:,.0f}")
print(f"Monto total aprobado:   ${monto_total_aprobado:,.0f}")


# -------- 9.3. Resumen por segmento --------

resumen_segmento = (
    cartera.groupby("segmento", as_index=False)
    .agg(
        solicitudes=("id_solicitud", "count"),
        monto_solicitado=("monto_solicitado", "sum"),
        monto_aprobado=("monto_aprobado_base", "sum"),
        endeudamiento_promedio=("endeudamiento_proyectado", "mean")
    )
)

print("\n=== RESUMEN POR SEGMENTO ===")
print(resumen_segmento)


# -------- 9.4. Resumen por producto --------

resumen_producto = (
    cartera.groupby("producto", as_index=False)
    .agg(
        solicitudes=("id_solicitud", "count"),
        monto_solicitado=("monto_solicitado", "sum"),
        monto_aprobado=("monto_aprobado_base", "sum"),
        endeudamiento_promedio=("endeudamiento_proyectado", "mean")
    )
)

print("\n=== RESUMEN POR PRODUCTO ===")
print(resumen_producto)


# -------- 9.5. Tabla de doble entrada --------

tabla_segmento_producto = cartera.pivot_table(
    index=["segmento", "producto"],
    columns="decision_base",
    values="id_solicitud",
    aggfunc="count",
    fill_value=0
)

print("\n=== DECISIÓN POR SEGMENTO Y PRODUCTO ===")
print(tabla_segmento_producto)


# -------- 9.6. Casos extremos solicitados --------

top_aprobadas_endeudamiento = (
    cartera.loc[cartera["decision_base"].eq("APROBADA")]
    .sort_values("endeudamiento_proyectado", ascending=False)
    .head(3)
)

top_negadas_monto = (
    cartera.loc[cartera["decision_base"].eq("NEGADA")]
    .sort_values("monto_solicitado", ascending=False)
    .head(3)
)

print("\n=== 3 APROBADAS CON MAYOR ENDEUDAMIENTO ===")
print(
    top_aprobadas_endeudamiento[
        [
            "id_solicitud",
            "segmento",
            "producto",
            "monto_solicitado",
            "endeudamiento_proyectado"
        ]
    ]
)

print("\n=== 3 NEGADAS CON MAYOR MONTO SOLICITADO ===")
print(
    top_negadas_monto[
        [
            "id_solicitud",
            "segmento",
            "producto",
            "monto_solicitado",
            "score",
            "endeudamiento_proyectado",
            "tiene_mora"
        ]
    ]
)


# ============================================================
# 10. ESCENARIO DE ESTRÉS
# ============================================================

# Los supuestos se guardan en un diccionario para que sean fáciles de modificar.
escenario_estres = {
    "factor_ingreso": 0.88,     # ingreso cae 12%
    "aumento_tasa_ea": 0.03     # tasa EA aumenta 3 puntos porcentuales
}

# Construimos las variables del escenario adverso.
cartera["ingreso_estres"] = (
    cartera["ingreso_mensual"]
    * escenario_estres["factor_ingreso"]
)

cartera["tasa_ea_estres"] = (
    cartera["tasa_ea"]
    + escenario_estres["aumento_tasa_ea"]
)

# Reutilizamos la misma función de cuota.
cartera["cuota_estres"] = cartera.apply(
    lambda fila: cuota_fija(
        fila["monto_solicitado"],
        fila["tasa_ea_estres"],
        int(fila["plazo_meses"])
    ),
    axis=1
)

# Reutilizamos la función de endeudamiento.
cartera["endeudamiento_estres"] = cartera.apply(
    lambda fila: endeudamiento_proyectado(
        fila["obligaciones_mensuales"],
        fila["cuota_estres"],
        fila["ingreso_estres"]
    ),
    axis=1
)

# Reutilizamos exactamente la misma función de decisión.
cartera["decision_estres"] = cartera.apply(
    lambda fila: clasificar_credito(
        fila["score"],
        fila["endeudamiento_estres"],
        fila["antiguedad_meses"],
        fila["tiene_mora"],
        fila["monto_solicitado"],
        fila["monto_maximo"],
        politica_original
    ),
    axis=1
)

# Indicamos si la categoría cambió.
cartera["cambio_estres"] = (
    cartera["decision_base"]
    != cartera["decision_estres"]
)

# Monto aprobado bajo estrés.
cartera["monto_aprobado_estres"] = np.where(
    cartera["decision_estres"].eq("APROBADA"),
    cartera["monto_solicitado"],
    0
)

numero_cambios = int(cartera["cambio_estres"].sum())

monto_aprobado_estres = cartera["monto_aprobado_estres"].sum()

perdida_monto_aprobado = (
    monto_total_aprobado
    - monto_aprobado_estres
)

print("\n=== ESCENARIO DE ESTRÉS ===")
print("Solicitudes que cambian de clasificación:", numero_cambios)
print(f"Monto aprobado base:   ${monto_total_aprobado:,.0f}")
print(f"Monto aprobado estrés: ${monto_aprobado_estres:,.0f}")
print(f"Monto aprobado perdido:${perdida_monto_aprobado:,.0f}")


# -------- 10.1. Deterioro por segmento --------

# Definimos un orden para poder saber si una decisión empeora.
orden_decision = {
    "NEGADA": 0,
    "REVISIÓN": 1,
    "APROBADA": 2
}

cartera["nivel_base"] = cartera["decision_base"].map(orden_decision)
cartera["nivel_estres"] = cartera["decision_estres"].map(orden_decision)

# Hay deterioro si el nivel bajo estrés es menor que el nivel original.
cartera["deterioro_estres"] = (
    cartera["nivel_estres"]
    < cartera["nivel_base"]
)

deterioro_segmento = (
    cartera.groupby("segmento", as_index=False)
    .agg(
        solicitudes=("id_solicitud", "count"),
        deterioros=("deterioro_estres", "sum")
    )
)

deterioro_segmento["proporcion_deterioro"] = (
    deterioro_segmento["deterioros"]
    / deterioro_segmento["solicitudes"]
)

deterioro_segmento = deterioro_segmento.sort_values(
    "proporcion_deterioro",
    ascending=False
)

print("\n=== DETERIORO POR SEGMENTO ===")
print(deterioro_segmento)


# ============================================================
# 11. ANÁLISIS DE UN CRÉDITO INDIVIDUAL
# ============================================================

# Seleccionamos automáticamente el crédito APROBADO de mayor monto.
credito_seleccionado = (
    cartera.loc[cartera["decision_base"].eq("APROBADA")]
    .sort_values("monto_solicitado", ascending=False)
    .iloc[0]
)

print("\n=== CRÉDITO SELECCIONADO PARA AMORTIZACIÓN ===")
print(
    credito_seleccionado[
        [
            "id_solicitud",
            "producto",
            "monto_solicitado",
            "tasa_ea",
            "plazo_meses"
        ]
    ]
)


def construir_amortizacion(monto, tasa_ea, plazo_meses):
    """
    Construye la tabla de amortización usando:
    - una lista,
    - un ciclo for,
    - las funciones financieras ya definidas.
    """

    # Cuota fija contractual.
    cuota = cuota_fija(
        monto,
        tasa_ea,
        plazo_meses
    )

    # Tasa mensual necesaria para calcular el interés de cada período.
    i = tasa_mensual(tasa_ea)

    # Saldo inicial.
    saldo = float(monto)

    # Aquí iremos guardando cada fila de la tabla.
    filas = []

    # Recorremos los meses del crédito.
    for periodo in range(1, plazo_meses + 1):

        # Interés del período sobre el saldo pendiente.
        interes = saldo * i

        # Parte de la cuota que realmente amortiza capital.
        abono_capital = cuota - interes

        # Por precisión numérica, ajustamos el último período.
        cuota_real = cuota

        if periodo == plazo_meses or abono_capital > saldo:
            abono_capital = saldo
            cuota_real = interes + abono_capital

        # Actualizamos el saldo.
        saldo = max(0, saldo - abono_capital)

        # Guardamos el período como un diccionario.
        filas.append({
            "periodo": periodo,
            "cuota": cuota_real,
            "interes": interes,
            "abono_capital": abono_capital,
            "saldo": saldo
        })

    # Una lista de diccionarios se convierte fácilmente en DataFrame.
    return pd.DataFrame(filas)


tabla_amortizacion = construir_amortizacion(
    float(credito_seleccionado["monto_solicitado"]),
    float(credito_seleccionado["tasa_ea"]),
    int(credito_seleccionado["plazo_meses"])
)

# Total de intereses.
total_intereses = tabla_amortizacion["interes"].sum()

# Usamos un while para localizar el primer período en que
# el saldo queda por debajo del 50% del monto inicial.
mitad_monto = credito_seleccionado["monto_solicitado"] * 0.50

posicion = 0

while (
    posicion < len(tabla_amortizacion)
    and tabla_amortizacion.loc[posicion, "saldo"] >= mitad_monto
):
    posicion += 1

if posicion < len(tabla_amortizacion):
    periodo_mitad = int(
        tabla_amortizacion.loc[posicion, "periodo"]
    )
else:
    periodo_mitad = None

# Proporción de la cuota destinada a intereses al inicio y al final.
porcentaje_interes_primera = (
    tabla_amortizacion.iloc[0]["interes"]
    / tabla_amortizacion.iloc[0]["cuota"]
)

porcentaje_interes_ultima = (
    tabla_amortizacion.iloc[-1]["interes"]
    / tabla_amortizacion.iloc[-1]["cuota"]
)

print("\n=== RESULTADOS DE AMORTIZACIÓN ===")
print(f"Total de intereses: ${total_intereses:,.0f}")
print("Primer período con saldo < 50% del monto inicial:", periodo_mitad)
print(f"% de la primera cuota destinado a intereses: {porcentaje_interes_primera:.2%}")
print(f"% de la última cuota destinado a intereses: {porcentaje_interes_ultima:.2%}")


# ============================================================
# 12. CAMBIO DE POLÍTICA: 40% -> 45%
# ============================================================

# Copiamos el diccionario original.
# Así no alteramos la política utilizada en el escenario base.
politica_45 = politica_original.copy()

# Modificamos un solo parámetro.
politica_45["endeudamiento_aprobado"] = 0.45

# Recalculamos la decisión SIN reescribir el motor.
cartera["decision_politica_45"] = cartera.apply(
    lambda fila: clasificar_credito(
        fila["score"],
        fila["endeudamiento_proyectado"],
        fila["antiguedad_meses"],
        fila["tiene_mora"],
        fila["monto_solicitado"],
        fila["monto_maximo"],
        politica_45
    ),
    axis=1
)

# Creamos monto aprobado bajo la política propuesta.
cartera["monto_aprobado_45"] = np.where(
    cartera["decision_politica_45"].eq("APROBADA"),
    cartera["monto_solicitado"],
    0
)

# Indicadores política original.
n_aprobadas_original = int(
    cartera["decision_base"].eq("APROBADA").sum()
)

monto_aprobado_original = cartera["monto_aprobado_base"].sum()

endeudamiento_aprobadas_original = (
    cartera.loc[
        cartera["decision_base"].eq("APROBADA"),
        "endeudamiento_proyectado"
    ]
    .mean()
)

# Indicadores política propuesta.
n_aprobadas_45 = int(
    cartera["decision_politica_45"].eq("APROBADA").sum()
)

monto_aprobado_45 = cartera["monto_aprobado_45"].sum()

endeudamiento_aprobadas_45 = (
    cartera.loc[
        cartera["decision_politica_45"].eq("APROBADA"),
        "endeudamiento_proyectado"
    ]
    .mean()
)

comparacion_politica = pd.DataFrame({
    "politica": [
        "Original - 40%",
        "Propuesta - 45%"
    ],
    "numero_aprobaciones": [
        n_aprobadas_original,
        n_aprobadas_45
    ],
    "monto_aprobado": [
        monto_aprobado_original,
        monto_aprobado_45
    ],
    "endeudamiento_promedio_aprobadas": [
        endeudamiento_aprobadas_original,
        endeudamiento_aprobadas_45
    ]
})

print("\n=== COMPARACIÓN DE POLÍTICAS ===")
print(comparacion_politica)


# ============================================================
# 13. CONCLUSIONES DEL COMITÉ
# ============================================================

segmento_mayor_deterioro = deterioro_segmento.iloc[0]

hallazgo_1 = (
    f"La cartera evaluable contiene {len(cartera)} solicitudes; "
    f"{n_aprobadas_original} quedan aprobadas bajo la política original, "
    f"por un monto de ${monto_aprobado_original:,.0f}."
)

hallazgo_2 = (
    f"Bajo estrés, {numero_cambios} solicitudes cambian de categoría y "
    f"el monto aprobado disminuye en ${perdida_monto_aprobado:,.0f}."
)

hallazgo_3 = (
    f"El segmento con mayor proporción de deterioro es "
    f"{segmento_mayor_deterioro['segmento']}, con "
    f"{segmento_mayor_deterioro['proporcion_deterioro']:.1%}."
)

print("\n=== TRES HALLAZGOS PRINCIPALES ===")
print("1.", hallazgo_1)
print("2.", hallazgo_2)
print("3.", hallazgo_3)

# Esta conclusión queda por debajo de 120 palabras.
conclusion_comite = (
    f"La flexibilización del límite de endeudamiento de 40% a 45% "
    f"eleva las aprobaciones de {n_aprobadas_original} a {n_aprobadas_45} "
    f"y aumenta el monto aprobado de ${monto_aprobado_original:,.0f} "
    f"a ${monto_aprobado_45:,.0f}. Al mismo tiempo, el endeudamiento "
    f"promedio de los aprobados pasa de "
    f"{endeudamiento_aprobadas_original:.1%} a "
    f"{endeudamiento_aprobadas_45:.1%}. El escenario de estrés muestra "
    f"que {numero_cambios} solicitudes deterioran su clasificación y se "
    f"pierden ${perdida_monto_aprobado:,.0f} de colocación aprobada. "
    f"Por tanto, la flexibilización incrementa la colocación, pero debería "
    f"acompañarse de seguimiento a los nuevos aprobados y a los segmentos "
    f"más sensibles al estrés."
)

print("\n=== CONCLUSIÓN PARA EL COMITÉ ===")
print(conclusion_comite)


# ============================================================
# 14. EXPORTAR LOS RESULTADOS
# ============================================================

# -------- 14.1. Cartera evaluada --------

archivo_cartera = os.path.join(
    RUTA_RESULTADOS,
    "cartera_evaluada.xlsx"
)

cartera.to_excel(
    archivo_cartera,
    index=False
)


# -------- 14.2. Libro resumen --------

archivo_resumen = os.path.join(
    RUTA_RESULTADOS,
    "resumen_cartera.xlsx"
)

with pd.ExcelWriter(archivo_resumen) as writer:

    # Auditoría de registros excluidos.
    no_utilizables.to_excel(
        writer,
        sheet_name="Auditoria_excluidos",
        index=False
    )

    # Resultados generales.
    resumen_decision.to_excel(
        writer,
        sheet_name="Decisiones",
        index=False
    )

    resumen_segmento.to_excel(
        writer,
        sheet_name="Por_segmento",
        index=False
    )

    resumen_producto.to_excel(
        writer,
        sheet_name="Por_producto",
        index=False
    )

    tabla_segmento_producto.to_excel(
        writer,
        sheet_name="Segmento_producto"
    )

    deterioro_segmento.to_excel(
        writer,
        sheet_name="Deterioro_estres",
        index=False
    )

    comparacion_politica.to_excel(
        writer,
        sheet_name="Comparacion_politica",
        index=False
    )

    tabla_amortizacion.to_excel(
        writer,
        sheet_name="Amortizacion",
        index=False
    )

print("\n=== ARCHIVOS GENERADOS ===")
print(archivo_cartera)
print(archivo_resumen)
