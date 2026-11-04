"""Reporte de retos (HU G01).

Lee retos_limpio.csv, crea tres graficas con matplotlib, las guarda en
reportes/ y al final imprime las conclusiones.

Uso:
    python scripts/reporte_retos.py retos_limpio.csv
"""

import os
import sys

import matplotlib

# Backend sin ventana: el script guarda las imagenes y nunca se queda esperando.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

CARPETA_SALIDA = "reportes"
MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def leer_datos(ruta_csv):
    """Lee el CSV de retos y convierte las columnas de fecha a datetime."""
    df = pd.read_csv(ruta_csv)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")
    return df


def guardar_grafica(nombre_archivo):
    """Ajusta el diseño, guarda la figura actual con dpi=120, la cierra y devuelve la ruta."""
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_retos_por_estado(df):
    """Grafica 1 (barras): cantidad de retos por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(7, 5))
    conteo.plot(kind="bar")
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=0)
    return guardar_grafica("retos_grafica_1.png")


def calcular_retos_por_mes(df):
    """Cuenta cuantos retos empiezan en cada mes, ordenados cronologicamente."""
    meses = df["fecha_inicio"].dropna().dt.to_period("M")
    por_mes = meses.value_counts().sort_index()
    por_mes.index = por_mes.index.astype(str)  # "2026-03" para el eje x
    return por_mes


def grafica_retos_por_mes(por_mes):
    """Grafica 2 (linea): retos que empiezan cada mes."""
    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio")
    plt.ylabel("Cantidad de retos")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    plt.grid(alpha=0.3)
    return guardar_grafica("retos_grafica_2.png")


def grafica_distribucion_duracion(df):
    """Grafica 3 (histograma): como se reparte la duracion de los retos en dias."""
    plt.figure(figsize=(7, 5))
    df["duracion_dias"].plot(kind="hist", bins=20)
    plt.title("Distribucion de la duracion de los retos")
    plt.xlabel("Duracion (dias)")
    plt.ylabel("Cantidad de retos")
    return guardar_grafica("retos_grafica_3.png")


def imprimir_conclusiones(df, por_mes):
    """Imprime las conclusiones: mes con mas retos, duracion promedio por estado y fechas invertidas."""
    print("\nCONCLUSIONES")
    print("-" * 60)

    # 1. Mes en que se concentran los retos.
    mes_pico = por_mes.idxmax()
    cantidad_pico = int(por_mes.max())
    total = int(por_mes.sum())
    porcentaje = cantidad_pico / total * 100
    anio, mes = mes_pico.split("-")
    nombre_mes = f"{MESES_ES[int(mes)]} de {anio}"
    print(f"1. Mes con mas retos: {nombre_mes} con {cantidad_pico} de {total} "
          f"retos ({porcentaje:.1f}%).")
    print(f"   Promedio mensual: {por_mes.mean():.1f} retos; el minimo fue "
          f"{int(por_mes.min())} en {por_mes.idxmin()}.")
    top3 = por_mes.nlargest(3)
    print(f"   Los 3 meses con mas retos ({', '.join(top3.index)}) suman "
          f"{top3.sum() / total * 100:.1f}% del total.")
    ultimo_mes = por_mes.index[-1]
    print(f"   Posible razon: la actividad sube hacia mitad de año (periodo de "
          f"ejecucion de proyectos). La caida final ({ultimo_mes}: "
          f"{int(por_mes.iloc[-1])} retos) se explica en buena parte porque ese "
          f"mes aun no termina en los datos. Es una hipotesis: hay que "
          f"confirmarla con el negocio.")

    # 2. Duracion promedio segun estado.
    print("\n2. Duracion promedio de un reto segun su estado (en dias):")
    promedio_estado = df.groupby("estado")["duracion_dias"].mean().sort_values(ascending=False)
    for estado, promedio in promedio_estado.items():
        print(f"   - {estado}: {promedio:.1f} dias")
    print(f"   Duracion promedio general: {df['duracion_dias'].mean():.1f} dias "
          f"(se ignoran los retos sin fecha de fin).")

    # 3. Retos con la fecha de fin antes que la de inicio (dato para el back).
    invertidas = df[df["fecha_fin"] < df["fecha_inicio"]]
    sin_fin = int(df["fecha_fin"].isna().sum())
    print(f"\n3. Retos con fecha de fin ANTES de la de inicio: {len(invertidas)} "
          f"de {len(df)} (dato para el back).")
    print(f"   Ademas, {sin_fin} retos no tienen fecha de fin.")
    if len(invertidas) > 0:
        print(f"   Su duracion queda negativa (minimo {invertidas['duracion_dias'].min():.0f} dias), "
              f"lo que se ve en la cola izquierda del histograma.")


def main():
    """Punto de entrada: lee el CSV, genera las tres graficas y muestra las conclusiones."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/reporte_retos.py retos_limpio.csv")
        sys.exit(1)

    df = leer_datos(sys.argv[1])
    por_mes = calcular_retos_por_mes(df)

    print("GRAFICAS GUARDADAS")
    print("-" * 60)
    print(grafica_retos_por_estado(df))
    print(grafica_retos_por_mes(por_mes))
    print(grafica_distribucion_duracion(df))

    imprimir_conclusiones(df, por_mes)


if __name__ == "__main__":
    main()