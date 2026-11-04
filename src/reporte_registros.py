"""Reporte gráfico de la tabla registros (HU G01).

Uso:
    python src/reporte_registros.py data/limpio/registros_limpio.csv

Lee el CSV limpio, genera tres gráficas en la carpeta reportes/ e imprime
la ruta de cada una junto con las conclusiones.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")  # Backend sin ventana: el script nunca se queda esperando.
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
import pandas as pd  # noqa: E402

CARPETA_SALIDA = "reportes"


def leer_datos(ruta_csv):
    """Lee el CSV limpio y devuelve un DataFrame con la fecha convertida."""
    df = pd.read_csv(ruta_csv)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
    return df


def guardar_grafica(ruta):
    """Ajusta el diseño, guarda la figura actual con dpi=120 y la cierra."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_estados(df):
    """Gráfica 1 (barras): participaciones por estado. Devuelve (ruta, conteo)."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar", color="#4C78A8")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de participaciones")
    plt.xticks(rotation=0)
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_1.png")
    guardar_grafica(ruta)
    return ruta, conteo


def grafica_meses(df):
    """Gráfica 2 (línea): participaciones por mes en orden cronológico."""
    por_mes = df["mes"].value_counts().sort_index()
    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o", color="#F58518")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes (AAAA-MM)")
    plt.ylabel("Cantidad de participaciones")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))  # solo enteros
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_2.png")
    guardar_grafica(ruta)
    return ruta, por_mes


def grafica_retos(df):
    """Gráfica 3 (barras horizontales): los 10 retos con más participantes."""
    top_retos = (
        df.groupby("id_reto")["id_usuario"]
        .nunique()
        .sort_values(ascending=False)
        .head(10)
    )
    # Se invierte para que el reto con más participantes quede arriba.
    grafico = top_retos.iloc[::-1].copy()
    grafico.index = [r[:8] for r in grafico.index]  # id abreviado para que quepa
    plt.figure(figsize=(8, 5))
    grafico.plot(kind="barh", color="#54A24B")
    plt.title("Top 10 retos con más participantes")
    plt.xlabel("Cantidad de participantes")
    plt.ylabel("Reto (primeros 8 caracteres del id)")
    ruta = os.path.join(CARPETA_SALIDA, "registros_grafica_3.png")
    guardar_grafica(ruta)
    return ruta, top_retos


def contar_duplicados(df):
    """Cuenta inscripciones repetidas (mismo usuario y mismo reto)."""
    return int(df.duplicated(subset=["id_usuario", "id_reto"]).sum())


def construir_conclusiones(conteo, por_mes, top_retos, duplicados):
    """Arma la lista de conclusiones en texto a partir de los resultados."""
    lineas = []

    maximo = top_retos.max()
    lideres = list(top_retos[top_retos == maximo].index)
    if len(lideres) == 1:
        lineas.append(
            f"1. El reto más popular es {lideres[0]} con {maximo} participantes."
        )
    else:
        lineas.append(
            f"1. Hay {len(lideres)} retos empatados como los más populares, "
            f"con {maximo} participantes cada uno: {', '.join(lideres)}."
        )

    maximo_mes = por_mes.max()
    meses = list(por_mes[por_mes == maximo_mes].index)
    lineas.append(
        f"2. El mes con más inscripciones fue {', '.join(meses)} "
        f"con {maximo_mes} inscripciones."
    )

    estado_top = conteo.idxmax()
    lineas.append(
        f"3. El estado más frecuente es {estado_top} ({conteo.max()} de "
        f"{conteo.sum()} participaciones)."
    )

    if duplicados == 0:
        lineas.append(
            "4. Se encontraron 0 inscripciones duplicadas (mismo usuario en el "
            "mismo reto): los datos limpios no repiten inscripciones."
        )
    else:
        lineas.append(
            f"4. Se encontraron {duplicados} inscripciones duplicadas "
            "(mismo usuario en el mismo reto)."
        )
    lineas.append(
        "5. El back debe bloquear las inscripciones duplicadas con 409 "
        "(Conflict) porque la petición choca con un recurso que ya existe: si "
        "una inscripción se repite, se inflan los conteos de participantes y "
        "las gráficas mienten. Responder 409 le dice al cliente que ese "
        "usuario ya está inscrito en el reto, en vez de crear otro registro."
    )
    return lineas


RUTA_CSV = "data/limpio/registros_limpio.csv"


def main():
    """Punto de entrada: lee el CSV, crea las gráficas e imprime resultados."""
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else RUTA_CSV

    df = leer_datos(ruta_csv)
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    ruta1, conteo = grafica_estados(df)
    ruta2, por_mes = grafica_meses(df)
    ruta3, top_retos = grafica_retos(df)

    print("Gráficas generadas:")
    for ruta in (ruta1, ruta2, ruta3):
        print(f"  - {ruta}")

    print("\nConclusiones:")
    for linea in construir_conclusiones(conteo, por_mes, top_retos, contar_duplicados(df)):
        print(linea)
if __name__ == "__main__":
    main()