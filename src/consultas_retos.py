"""Consultas de la HU Q01 sobre la tabla retos (proyecto integrador).

Uso:
    python scripts/consultas_retos.py retos_limpio.csv

Lee el archivo LIMPIO de retos, resuelve cinco consultas con pandas
(cada una en su propia funcion), imprime el titulo y el resultado y
guarda cada resultado como retos_consulta_N.csv en la misma carpeta
del archivo de entrada.
"""

import os
import sys

import pandas as pd


def cargar_datos(ruta):
    """Lee el CSV limpio y convierte las fechas a tipo fecha."""
    df = pd.read_csv(ruta)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"])
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"])
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como retos_consulta_N.csv."""
    ruta = os.path.join(carpeta, f"retos_consulta_{numero}.csv")
    resultado.to_csv(ruta, index=False)
    print(f"(guardado en {ruta})\n")


def consulta_1(df):
    """Consulta 1: retos que estan en curso (filtro por estado)."""
    print("CONSULTA 1 - Que retos estan en curso?")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(en_curso[["nombre", "fecha_inicio", "fecha_fin", "estado"]].to_string(index=False))
    print(f"Total en curso: {len(en_curso)}")
    return en_curso


def consulta_2(df):
    """Consulta 2: los 10 retos mas largos segun duracion_dias."""
    print("CONSULTA 2 - Cuales son los 10 retos mas largos?")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos.to_string(index=False))
    return largos


def consulta_3(df):
    """Consulta 3: cuantos retos hay por estado (conteo de valores)."""
    print("CONSULTA 3 - Cuantos retos hay por estado?")
    conteo = df["estado"].value_counts().rename_axis("estado").reset_index(name="cantidad")
    print(conteo.to_string(index=False))
    return conteo


def consulta_4(df):
    """Consulta 4 (groupby): duracion promedio, minima y maxima por estado."""
    print("CONSULTA 4 - Cual es la duracion promedio, minima y maxima por estado?")
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(1)
    resumen = resumen.reset_index()
    print(resumen.to_string(index=False))
    return resumen


def consulta_5(df):
    """Consulta 5 (groupby): cuantos retos empiezan cada mes."""
    print("CONSULTA 5 - Cuantos retos empiezan cada mes?")
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    por_mes = por_mes.rename_axis("mes").reset_index(name="cantidad")
    por_mes["mes"] = por_mes["mes"].astype(str)
    print(por_mes.to_string(index=False))
    return por_mes


def main():
    """Punto de entrada: valida el argumento y corre las cinco consultas."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/consultas_retos.py retos_limpio.csv")
        sys.exit(1)

    ruta = sys.argv[1]
    carpeta = os.path.dirname(os.path.abspath(ruta))
    df = cargar_datos(ruta)

    consultas = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]
    for numero, funcion in enumerate(consultas, start=1):
        resultado = funcion(df)
        guardar(resultado, carpeta, numero)


if __name__ == "__main__":
    main()