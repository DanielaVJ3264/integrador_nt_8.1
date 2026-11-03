"""Reporte de la HU G01 sobre la tabla prioridades (proyecto integrador).

Uso:
    python scripts/reporte_prioridades.py prioridades_limpio.csv

Lee el archivo LIMPIO, crea tres graficas con matplotlib, las guarda en la
carpeta reportes/ (dpi=120) e imprime la ruta de cada grafica y las
conclusiones al final.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")  # Backend sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

# Columnas que debe tener el archivo limpio
COLUMNAS = ["id", "nombre", "nivel", "dias_max_respuesta"]

CARPETA_REPORTES = "reportes"   # Carpeta donde se guardan las graficas
DPI = 120                       # Resolucion de las imagenes
PRIORIDADES_ESPERADAS = 5       # Cantidad de prioridades reales del catalogo
NIVEL_MIN, NIVEL_MAX = 1, 5     # Rango valido de la columna nivel


def cargar_datos(ruta):
    """Lee el CSV limpio, verifica las columnas y deja `nivel` como numero."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        sys.exit(f"Error: al archivo le faltan las columnas {faltan}")
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    # Si todos los niveles son enteros, se muestran como 1, 2, 3 (no 1.0, 2.0...)
    if df["nivel"].notna().all() and (df["nivel"] % 1 == 0).all():
        df["nivel"] = df["nivel"].astype(int)
    return df


def guardar_grafica(numero):
    """Aplica tight_layout, guarda la figura actual con dpi=120 y la cierra; devuelve la ruta."""
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    ruta = os.path.join(CARPETA_REPORTES, f"prioridades_grafica_{numero}.png")
    plt.tight_layout()
    plt.savefig(ruta, dpi=DPI)
    plt.close()
    return ruta


def grafica_1(df):
    """Grafica 1 (barras): cuantas filas hay por nivel."""
    por_nivel = df.groupby("nivel")["id"].count()
    plt.figure(figsize=(7, 5))
    por_nivel.plot(kind="bar", color="#4C78A8")
    plt.title("Cantidad de filas por nivel de prioridad")
    plt.xlabel("Nivel")
    plt.ylabel("Cantidad de filas")
    plt.xticks(rotation=0)
    return guardar_grafica(1)


def grafica_2(df):
    """Grafica 2 (barras): dias promedio de respuesta por prioridad."""
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    plt.figure(figsize=(7, 5))
    resumen["mean"].plot(kind="bar", color="#F58518")
    plt.title("Días promedio de respuesta por prioridad")
    plt.xlabel("Prioridad")
    plt.ylabel("Días promedio de respuesta")
    plt.xticks(rotation=30, ha="right")
    return guardar_grafica(2)


def grafica_3(df):
    """Grafica 3 (torta): reparto de las prioridades segun su nombre."""
    conteo = df["nombre"].value_counts()
    plt.figure(figsize=(6, 6))
    conteo.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Reparto de las prioridades")
    plt.xlabel("Prioridad")
    plt.ylabel("Proporción de filas")
    return guardar_grafica(3)


def conclusion_1(df):
    """Conclusion 1: cuantas prioridades REALES quedaron al final (deben ser 5)."""
    nombres = sorted(df["nombre"].dropna().unique())
    reales = len(nombres)
    lineas = [f"1. ¿Cuántas prioridades REALES quedaron? {reales} ({', '.join(nombres)})."]
    if reales == PRIORIDADES_ESPERADAS:
        lineas.append("   Correcto: coinciden con las 5 esperadas, no quedaron variantes de nombre.")
    else:
        lineas.append(f"   ATENCIÓN: deberían ser {PRIORIDADES_ESPERADAS}. "
                      "Hay variantes de escritura o nombres de más: vuelve a limpiar el archivo.")
    return "\n".join(lineas)


def conclusion_2(df):
    """Conclusion 2: relacion entre el nivel y los dias maximos de respuesta (calculada con los datos)."""
    por_nivel = df.groupby("nivel")["dias_max_respuesta"].mean().round(1)
    detalle = ", ".join(f"nivel {n}: {d} días" for n, d in por_nivel.items())
    lineas = [f"2. Relación entre nivel y días máximos de respuesta (promedio por nivel): {detalle}."]
    corr = df["nivel"].corr(df["dias_max_respuesta"])
    if pd.isna(corr):
        lineas.append("   No hay datos suficientes para medir la relación.")
    elif corr < -0.3:
        lineas.append(f"   Relación inversa (correlación {corr:.2f}): a mayor nivel, menos días para responder; "
                      "las prioridades más urgentes tienen los plazos más cortos.")
    elif corr > 0.3:
        lineas.append(f"   Relación directa (correlación {corr:.2f}): a mayor nivel, más días para responder. "
                      "Revisa que el significado del nivel sea el esperado.")
    else:
        lineas.append(f"   No se ve una relación clara (correlación {corr:.2f}).")
    return "\n".join(lineas)


def conclusion_3(df):
    """Conclusion 3: por que el back debe validar que nivel este entre 1 y 5."""
    fuera = df[(df["nivel"] < NIVEL_MIN) | (df["nivel"] > NIVEL_MAX) | df["nivel"].isna()]
    lineas = [f"3. ¿Por qué el back debe validar que nivel esté entre {NIVEL_MIN} y {NIVEL_MAX}?",
              "   Porque el front y el CSV no son confiables: un nivel fuera del rango (0, 9, vacío o texto)",
              "   rompe el orden de urgencia, los gráficos y los plazos de respuesta, y se guardaría en la base",
              "   de datos como un dato inválido. La validación en el back es la última barrera."]
    if fuera.empty:
        lineas.append(f"   En este archivo todos los niveles están entre {NIVEL_MIN} y {NIVEL_MAX}.")
    else:
        lineas.append(f"   ATENCIÓN: este archivo tiene {len(fuera)} fila(s) con nivel inválido (ids: "
                      f"{', '.join(str(i) for i in fuera['id'])}).")
    return "\n".join(lineas)


def imprimir_conclusiones(df):
    """Imprime las tres conclusiones de la HU al final del reporte."""
    print("\nCONCLUSIONES")
    print("=" * 60)
    print(conclusion_1(df))
    print(conclusion_2(df))
    print(conclusion_3(df))


def main():
    """Lee el archivo recibido por linea de comandos, crea las graficas e imprime las conclusiones."""
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/reporte_prioridades.py prioridades_limpio.csv")
    ruta = sys.argv[1]
    if not os.path.exists(ruta):
        sys.exit(f"Error: no existe el archivo {ruta}")

    df = cargar_datos(ruta)

    print("GRÁFICAS GUARDADAS")
    for crear in (grafica_1, grafica_2, grafica_3):
        print(f"-> {crear(df)}")

    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()