# -*- coding: utf-8 -*-
"""Clase_2_python.ipynb

# Código guiado — Clase 2

Este notebook está pensado para ejecutarse lentamente durante la clase.

## Clase 2 - Condicionales, listas y ciclos para analítica financiera
"""

# ============================================================
# CLASE 2 - CONDICIONALES, LISTAS Y CICLOS
# Curso: Introduccion a la programacion para analitica financiera
# Profesor: Orlando Joaqui-Barandica
# Entorno recomendado: Google Colab
# ============================================================


# ============================================================
# 1. COMPARADORES Y BOOLEANOS
# ============================================================

score = 720
ingreso = 6_000_000
obligaciones = 1_800_000
tiene_mora = False

endeudamiento = obligaciones / ingreso

print("=== COMPARACIONES ===")
print("Score >= 700:", score >= 700)
print("Score < 650:", score < 650)
print("Endeudamiento <= 40%:", endeudamiento <= 0.40)
print("Tiene mora:", tiene_mora)
print("No tiene mora:", not tiene_mora)

# Recuerde:
# =  asigna un valor
# == compara dos valores

print("Score exactamente igual a 720:", score == 720)
print("Score diferente de 720:", score != 720)

# ============================================================
# 2. OPERADORES LOGICOS: and, or, not
# ============================================================

antiguedad_meses = 18
tiene_codeudor = True

regla_aprobacion = (
    score >= 700
    and endeudamiento <= 0.40
    and antiguedad_meses >= 12
    and not tiene_mora
)

regla_garantia = score >= 750 or tiene_codeudor

print("\n=== REGLAS LOGICAS ===")
print("Cumple regla de aprobacion:", regla_aprobacion)
print("Cumple regla alternativa de garantia:", regla_garantia)

# ============================================================
# 3. IF / ELIF / ELSE
# ============================================================

# Una primera decision de tres niveles.
if score >= 700:
    decision_score = "APROBADO POR SCORE"
elif score >= 650:
    decision_score = "REVISAR SCORE"
else:
    decision_score = "NO CUMPLE SCORE"

print("\nDecision por score:", decision_score)

# Ahora combinamos varias reglas.
if (
    score >= 700
    and endeudamiento <= 0.40
    and antiguedad_meses >= 12
    and not tiene_mora
):
    decision = "APROBADO"
elif score >= 650 and endeudamiento <= 0.50 and not tiene_mora:
    decision = "REVISION"
else:
    decision = "NEGADO"

print("Decision integral:", decision)

# PRUEBA EN CLASE:
# Cambie score a 680 y vuelva a ejecutar este bloque.
# Luego cambie tiene_mora a True.

# ============================================================
# 4. LISTAS: CREAR, INDEXAR Y RECORTAR
# ============================================================

flujos = [-10_000_000, 3_000_000, 4_000_000, 5_000_000]
tasas = [0.12, 0.14, 0.16]

print("\n=== LISTAS ===")
print("Flujos:", flujos)
print("Primer flujo:", flujos[0])
print("Segundo flujo:", flujos[1])
print("Ultimo flujo:", flujos[-1])
print("Primeros tres flujos:", flujos[:3])
print("Ultimos dos flujos:", flujos[-2:])
print("Numero de flujos:", len(flujos))

# append() agrega un nuevo valor al final.
tasas.append(0.18)
print("Tasas despues de append:", tasas)

# ============================================================
# 5. FOR: RECORRER UNA LISTA
# ============================================================

print("\n=== RECORRER FLUJOS ===")
for flujo in flujos:
    print(f"Flujo: ${flujo:,.0f}")

# ============================================================
# 6. RANGE(): REPETIR UN NUMERO CONOCIDO DE VECES
# ============================================================

print("\n=== RANGE ===")
for mes in range(1, 6):
    print("Mes", mes)

# range(1, 6) genera 1, 2, 3, 4, 5.
# El limite derecho no se incluye.

# ============================================================
# 7. PATRON ACUMULADOR
# ============================================================

flujos_positivos = [3_000_000, 4_000_000, 5_000_000]
total = 0

for flujo in flujos_positivos:
    total += flujo

print("\n=== ACUMULADOR ===")
print(f"Suma acumulada de flujos: ${total:,.0f}")

# Analisis periodo a periodo de una serie completa.
flujos_proyecto = [-10_000_000, 3_000_000, 4_000_000, 5_000_000]
acumulado = 0

print("\n=== FLUJOS PERIODO A PERIODO ===")
for periodo in range(len(flujos_proyecto)):
    flujo = flujos_proyecto[periodo]
    acumulado += flujo
    print(
        f"Periodo {periodo}: flujo ${flujo:,.0f} | "
        f"acumulado ${acumulado:,.0f}"
    )

# ============================================================
# 8. WHILE: REPETIR HASTA CUMPLIR UNA META
# ============================================================

meta = 3_000_000
ahorro = 0
mes = 0
aporte_mensual = 500_000

while ahorro < meta:
    ahorro += aporte_mensual
    mes += 1

print("\n=== WHILE: META DE AHORRO ===")
print(f"Meta: ${meta:,.0f}")
print(f"Aporte mensual: ${aporte_mensual:,.0f}")
print(f"Meses necesarios: {mes}")
print(f"Ahorro acumulado: ${ahorro:,.0f}")

# Cuidado: un while debe modificar la variable de su condicion.
# Si ahorro nunca cambiara, ahorro < meta seguiria siendo verdadero para siempre.

# ============================================================
# 9. CASO INTEGRADO: MOTOR DE CREDITO + AMORTIZACION
# ============================================================

# Datos del credito
monto = 20_000_000
tasa_ea = 0.19
plazo = 24

# Datos del cliente
ingreso = 7_000_000
obligaciones = 1_300_000
score = 725
antiguedad_meses = 30
tiene_mora = False

# Paso 1. Convertir tasa efectiva anual a tasa mensual equivalente.
tasa_mensual = (1 + tasa_ea) ** (1 / 12) - 1

# Paso 2. Calcular cuota fija.
cuota = monto * (
    tasa_mensual * (1 + tasa_mensual) ** plazo
) / ((1 + tasa_mensual) ** plazo - 1)

# Paso 3. Calcular endeudamiento incluyendo la nueva cuota.
endeudamiento_total = (obligaciones + cuota) / ingreso

print("\n=== DATOS DEL CREDITO ===")
print(f"Monto: ${monto:,.0f}")
print(f"Tasa EA: {tasa_ea:.2%}")
print(f"Tasa mensual equivalente: {tasa_mensual:.4%}")
print(f"Cuota estimada: ${cuota:,.0f}")
print(f"Endeudamiento total: {endeudamiento_total:.2%}")

# Paso 4. Motor de reglas.
if (
    score >= 700
    and endeudamiento_total <= 0.40
    and antiguedad_meses >= 12
    and not tiene_mora
):
    decision = "APROBADO"
elif score >= 650 and endeudamiento_total <= 0.50 and not tiene_mora:
    decision = "REVISION"
else:
    decision = "NEGADO"

print(f"Decision: {decision}")

# Paso 5. Si no esta negado, construimos la amortizacion.
if decision != "NEGADO":
    periodos = []
    saldos_iniciales = []
    intereses = []
    abonos_capital = []
    cuotas = []
    saldos_finales = []

    saldo = monto
    total_intereses = 0

    for periodo in range(1, plazo + 1):
        saldo_inicial = saldo
        interes = saldo_inicial * tasa_mensual
        abono = cuota - interes
        saldo_final = max(0, saldo_inicial - abono)

        periodos.append(periodo)
        saldos_iniciales.append(saldo_inicial)
        intereses.append(interes)
        abonos_capital.append(abono)
        cuotas.append(cuota)
        saldos_finales.append(saldo_final)

        total_intereses += interes
        saldo = saldo_final

    print("\n=== RESUMEN DE AMORTIZACION ===")
    print("Primeros tres periodos:", periodos[:3])
    print("Primeros tres saldos finales:")
    for i in range(3):
        print(f"Mes {periodos[i]}: ${saldos_finales[i]:,.0f}")

    print(f"Ultimo periodo: {periodos[-1]}")
    print(f"Saldo final: ${saldos_finales[-1]:,.2f}")
    print(f"Intereses totales: ${total_intereses:,.0f}")
else:
    print("No se construye amortizacion porque el credito fue negado.")

# ============================================================
# 10. PRUEBAS RAPIDAS PARA HACER EN VIVO
# ============================================================

# Prueba 1: cambie el score de 725 a 675.
# Prueba 2: cambie tiene_mora de False a True.
# Prueba 3: cambie el plazo de 24 a 36 meses.
# Prueba 4: observe como cambia cuota, endeudamiento y decision.
#
# La idea no es reescribir el proceso: solo cambiar los datos de entrada
# y ejecutar nuevamente.
