"""Consultas de la HU Q01 sobre la tabla prioridades (proyecto integrador).

Uso:
    python scripts/consultas_prioridades.py prioridades_limpio.csv

Lee el archivo LIMPIO, resuelve cinco consultas (cada una en su propia
funcion), imprime el titulo y el resultado de cada una y guarda
prioridades_consulta_N.csv en la misma carpeta del archivo de entrada.
"""

import os
import sys

import pandas as pd

# Columnas que debe tener el archivo limpio
COLUMNAS = ["id", "nombre", "nivel", "dias_max_respuesta"]


def cargar_datos(ruta):
    """Lee el CSV limpio y verifica que tenga las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        sys.exit(f"Error: al archivo le faltan las columnas {faltan}")
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como prioridades_consulta_N.csv."""
    ruta = os.path.join(carpeta, f"prioridades_consulta_{numero}.csv")
    if isinstance(resultado.index, pd.RangeIndex):
        # indice numerico simple: no se guarda como columna
        resultado.to_csv(ruta, index=False)
    else:
        # reset_index convierte el indice (nivel, nombre...) en una columna normal
        resultado.reset_index().to_csv(ruta, index=False)
    print(f"-> guardado en {ruta}\n")


def consulta_1(df, carpeta):
    """Consulta 1: prioridades ordenadas de la mas urgente a la menos urgente."""
    print("CONSULTA 1: ¿Cuáles son las prioridades ordenadas de la más urgente a la menos urgente?")
    ordenadas = df.sort_values("nivel", kind="stable")
    print(ordenadas.to_string(index=False))
    guardar(ordenadas.reset_index(drop=True), carpeta, 1)
    return ordenadas


def consulta_2(df, carpeta):
    """Consulta 2: solo las prioridades urgentes (nivel 1 y 2)."""
    print("CONSULTA 2: ¿Cuáles son solo las prioridades urgentes (nivel 1 y 2)?")
    urgentes = df[df["nivel"] <= 2]
    print(urgentes.to_string(index=False))
    guardar(urgentes.reset_index(drop=True), carpeta, 2)
    return urgentes


def consulta_3(df, carpeta):
    """Consulta 3: cuantas veces aparece cada nombre (sirve para detectar variantes)."""
    print("CONSULTA 3: ¿Cuántas veces aparece cada nombre? (detecta variantes)")
    conteo = df["nombre"].value_counts()
    conteo.index.name = "nombre"
    conteo.name = "cantidad"
    print(conteo.to_string())
    guardar(conteo, carpeta, 3)
    return conteo


def consulta_4(df, carpeta):
    """Consulta 4 (groupby): cuantas filas hay por nivel."""
    print("CONSULTA 4: ¿Cuántas filas hay por nivel?")
    por_nivel = df.groupby("nivel")["id"].count()
    por_nivel.name = "filas"
    print(por_nivel.to_string())
    guardar(por_nivel, carpeta, 4)
    return por_nivel


def consulta_5(df, carpeta):
    """Consulta 5 (groupby): dias de respuesta minimo, promedio y maximo por prioridad."""
    print("CONSULTA 5: ¿Cuáles son los días de respuesta mínimo, promedio y máximo por prioridad?")
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    print(resumen.to_string())
    guardar(resumen, carpeta, 5)
    return resumen


def main():
    """Lee el archivo recibido por linea de comandos y corre las cinco consultas en orden."""
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/consultas_prioridades.py prioridades_limpio.csv")
    ruta = sys.argv[1]
    if not os.path.exists(ruta):
        sys.exit(f"Error: no existe el archivo {ruta}")

    carpeta = os.path.dirname(os.path.abspath(ruta))
    df = cargar_datos(ruta)

    consulta_1(df, carpeta)
    consulta_2(df, carpeta)
    consulta_3(df, carpeta)
    consulta_4(df, carpeta)
    consulta_5(df, carpeta)


if __name__ == "__main__":
    main()