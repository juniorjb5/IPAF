# -*- coding: utf-8 -*-
"""Solucion_Actividad_Clase_2_Motor_Credito_Amortizacion.ipynb

# Solución — Actividad Clase 2

Solución de referencia para el motor de crédito, la amortización y el while de ahorro.
"""

# ============================================================
# ACTIVIDAD CLASE 2 - SOLUCION DE REFERENCIA
# ============================================================

# 1. DATOS DEL CASO
monto = 18_000_000
tasa_ea = 0.18
plazo = 24

ingreso = 6_500_000
obligaciones = 1_100_000
score = 715
antiguedad_meses = 18
tiene_mora = False

# 2. TASA MENSUAL EQUIVALENTE Y CUOTA FIJA
tasa_mensual = (1 + tasa_ea) ** (1 / 12) - 1

cuota = monto * (
    tasa_mensual * (1 + tasa_mensual) ** plazo
) / ((1 + tasa_mensual) ** plazo - 1)

# 3. ENDEUDAMIENTO TOTAL
endeudamiento_total = (obligaciones + cuota) / ingreso

print("=== DATOS CALCULADOS ===")
print(f"Tasa mensual equivalente: {tasa_mensual:.4%}")
print(f"Cuota mensual: ${cuota:,.0f}")
print(f"Endeudamiento total: {endeudamiento_total:.2%}")

# 4. MOTOR DE REGLAS
if (
    score >= 700
    and endeudamiento_total <= 0.40
    and antiguedad_meses >= 12
    and not tiene_mora
):
    decision = "APROBADO"
elif (
    score >= 650
    and endeudamiento_total <= 0.50
    and antiguedad_meses >= 6
    and not tiene_mora
):
    decision = "REVISION"
else:
    decision = "NEGADO"

print(f"Decision: {decision}")

# 5. AMORTIZACION: SOLO SI NO FUE NEGADO
periodos = []
saldos_iniciales = []
intereses = []
abonos_capital = []
cuotas = []
saldos_finales = []
total_intereses = 0

if decision != "NEGADO":
    saldo = monto

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

    print("\n=== PRIMEROS 3 PERIODOS ===")
    for i in range(3):
        print(
            f"Mes {periodos[i]} | "
            f"Saldo inicial: ${saldos_iniciales[i]:,.0f} | "
            f"Interes: ${intereses[i]:,.0f} | "
            f"Abono: ${abonos_capital[i]:,.0f} | "
            f"Saldo final: ${saldos_finales[i]:,.0f}"
        )

    print("\n=== ULTIMO PERIODO ===")
    print(
        f"Mes {periodos[-1]} | "
        f"Saldo inicial: ${saldos_iniciales[-1]:,.0f} | "
        f"Interes: ${intereses[-1]:,.0f} | "
        f"Abono: ${abonos_capital[-1]:,.0f} | "
        f"Saldo final: ${saldos_finales[-1]:,.2f}"
    )

    print(f"Intereses totales: ${total_intereses:,.0f}")
else:
    print("El credito fue negado. No se construye la amortizacion.")

# 6. WHILE: FONDO DE EMERGENCIA EQUIVALENTE A 3 CUOTAS
meta_fondo = 3 * cuota
ahorro = 0
aporte_mensual = 350_000
meses_ahorro = 0

while ahorro < meta_fondo:
    ahorro += aporte_mensual
    meses_ahorro += 1

print("\n=== FONDO DE EMERGENCIA ===")
print(f"Meta equivalente a 3 cuotas: ${meta_fondo:,.0f}")
print(f"Aporte mensual: ${aporte_mensual:,.0f}")
print(f"Meses necesarios: {meses_ahorro}")
print(f"Ahorro alcanzado: ${ahorro:,.0f}")

# 7. REPORTE FINAL
print("\n=== REPORTE FINAL ===")
print(f"Decision: {decision}")
print(f"Cuota mensual: ${cuota:,.0f}")
print(f"Endeudamiento total: {endeudamiento_total:.2%}")

if decision != "NEGADO":
    print(f"Intereses totales: ${total_intereses:,.0f}")
    print(f"Saldo final: ${saldos_finales[-1]:,.2f}")

print(f"Meses para alcanzar el fondo: {meses_ahorro}")

# Interpretacion esperada:
# El cliente queda APROBADO porque cumple simultaneamente el score minimo,
# el limite de endeudamiento, la antiguedad y la condicion de no tener mora.
# Una variable especialmente sensible es el ingreso o las obligaciones actuales,
# porque cambian directamente el indicador de endeudamiento total.
