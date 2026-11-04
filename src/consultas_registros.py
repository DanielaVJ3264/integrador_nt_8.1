"""Consultas de la HU Q01 sobre la tabla registros (archivo LIMPIO).

Uso:
    python scripts/consultas_registros.py registros_limpio.csv

Cada consulta vive en su propia funcion, imprime la pregunta que responde
y su resultado, y guarda registros_consulta_N.csv en la misma carpeta
del archivo de entrada.
"""

import os
import sys

import pandas as pd


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como registros_consulta_N.csv."""
    ruta = os.path.join(carpeta, f"registros_consulta_{numero}.csv")
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    print(f"-> Guardado en {ruta}\n")


def consulta_1_finalizados(df):
    """Consulta 1: devuelve las participaciones con estado FINALIZADO."""
    print("Consulta 1 - Que participaciones ya estan finalizadas?")
    finalizados = df[df["estado"] == "FINALIZADO"]
    print(finalizados.to_string(index=False))
    return finalizados


def consulta_2_repetidos(df):
    """Consulta 2: devuelve las participaciones del mismo usuario en el mismo reto."""
    print("Consulta 2 - Que participaciones estan repetidas (mismo usuario en el mismo reto)?")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    if repetidos.empty:
        print("No hay participaciones repetidas.")
    else:
        print(repetidos.to_string(index=False))
    return repetidos


def consulta_3_por_estado(df):
    """Consulta 3: cuenta cuantas participaciones hay por cada estado."""
    print("Consulta 3 - Cuantas participaciones hay por estado?")
    conteo = df["estado"].value_counts().reset_index()
    conteo.columns = ["estado", "participaciones"]
    print(conteo.to_string(index=False))
    return conteo


def consulta_4_top_retos(df):
    """Consulta 4 (groupby): los 10 retos con mas participaciones."""
    print("Consulta 4 - Cuales son los 10 retos con mas participantes?")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10).reset_index()
    top_retos.columns = ["id_reto", "participaciones"]
    print(top_retos.to_string(index=False))
    return top_retos


def consulta_5_por_mes(df):
    """Consulta 5 (groupby): cuantas participaciones hubo cada mes."""
    print("Consulta 5 - Cuantas participaciones hubo cada mes?")
    por_mes = df.groupby("mes")["id"].count().reset_index()
    por_mes.columns = ["mes", "participaciones"]
    print(por_mes.to_string(index=False))
    return por_mes


def main():
    """Lee el CSV limpio, ejecuta las cinco consultas en orden y guarda cada resultado."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_por_defecto = os.path.join(raiz, "data", "limpio", "registros_limpio.csv")

    # Si no pasas argumento, usa data/limpio/registros_limpio.csv
    ruta = sys.argv[1] if len(sys.argv) > 1 else ruta_por_defecto

    if not os.path.exists(ruta):
        print(f"No encontre el archivo: {ruta}")
        sys.exit(1)

    carpeta = os.path.dirname(os.path.abspath(ruta))
    df = pd.read_csv(ruta, dtype=str)

    consultas = [
        consulta_1_finalizados,
        consulta_2_repetidos,
        consulta_3_por_estado,
        consulta_4_top_retos,
        consulta_5_por_mes,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        guardar(resultado, carpeta, numero)
if __name__ == "__main__":
    main()