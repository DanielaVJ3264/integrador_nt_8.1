"""HU Q01 - Consultas sobre la tabla empresas (proyecto integrador).

Uso:
    python scripts/consultas_empresas.py empresas_limpio.csv [sector]

Lee el archivo LIMPIO, resuelve cinco consultas (cada una en su funcion),
imprime el titulo y el resultado, y guarda empresas_consulta_N.csv en la
misma carpeta del archivo de entrada.
"""
import os
import sys

import pandas as pd

# Sector que se consulta en la consulta 2 (se puede cambiar con el 2.o argumento)
SECTOR_POR_DEFECTO = "Logistica"


def cargar_datos(ruta):
    """Lee el CSV limpio y asegura que 'activa' sea booleana."""
    df = pd.read_csv(ruta)
    if df["activa"].dtype != bool:
        df["activa"] = df["activa"].astype(str).str.strip().str.lower().isin(["true", "1", "si", "sí"])
    return df


def guardar(resultado, carpeta, numero, con_indice):
    """Guarda el resultado de una consulta como empresas_consulta_N.csv."""
    ruta = os.path.join(carpeta, f"empresas_consulta_{numero}.csv")
    if isinstance(resultado, pd.Series):
        resultado = resultado.to_frame()
    resultado.to_csv(ruta, index=con_indice)
    print(f"(guardado en {ruta})")


def consulta_1(df):
    """Consulta 1: empresas activas (filtro simple)."""
    print("Consulta 1 - ¿Cuáles son las empresas activas?")
    activas = df[df["activa"] == True]
    print(activas[["id", "nombre", "sector", "activa"]].to_string(index=False))
    print(f"Total: {len(activas)}")
    return activas


def consulta_2(df, sector=SECTOR_POR_DEFECTO):
    """Consulta 2: empresas de un sector, ordenadas por nombre."""
    print(f"Consulta 2 - ¿Cuáles son las empresas del sector {sector}, ordenadas por nombre?")
    resultado = df[df["sector"] == sector].sort_values("nombre")
    if resultado.empty:
        print(f"No hay empresas en el sector '{sector}'. Sectores disponibles: "
              f"{', '.join(sorted(df['sector'].dropna().unique()))}")
    else:
        print(resultado[["id", "nombre", "sector", "activa"]].to_string(index=False))
        print(f"Total: {len(resultado)}")
    return resultado


def consulta_3(df):
    """Consulta 3: cuántas empresas hay por sector (conteo rápido con value_counts)."""
    print("Consulta 3 - ¿Cuántas empresas hay por sector? (conteo rápido)")
    conteo = df["sector"].value_counts()
    conteo.index.name = "sector"
    conteo.name = "empresas"
    print(conteo.to_string())
    return conteo


def consulta_4(df):
    """Consulta 4 (GROUPBY): empresas por sector, de mayor a menor."""
    print("Consulta 4 - GROUPBY: ¿cuántas empresas hay por sector, de mayor a menor?")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    por_sector.name = "empresas"
    print(por_sector.to_string())
    return por_sector


def consulta_5(df):
    """Consulta 5 (GROUPBY doble): empresas activas e inactivas por sector."""
    print("Consulta 5 - GROUPBY doble: ¿cuántas empresas activas e inactivas hay por sector?")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    return tabla


def main():
    """Carga los datos, ejecuta las cinco consultas en orden y guarda los resultados."""
    # Si no se pasa ruta, usa data/limpio/empresas_limpio.csv del proyecto
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_por_defecto = os.path.join(raiz, "data", "limpio", "empresas_limpio.csv")

    ruta = sys.argv[1] if len(sys.argv) > 1 else ruta_por_defecto
    sector = sys.argv[2] if len(sys.argv) > 2 else SECTOR_POR_DEFECTO
    carpeta = os.path.dirname(os.path.abspath(ruta))

    if not os.path.exists(ruta):
        print(f"No encuentro el archivo: {ruta}")
        sys.exit(1)

    df = cargar_datos(ruta)
    print(f"Empresas cargadas: {len(df)}\n")

    # Cada consulta imprime su resultado y se guarda enseguida, en orden.
    # con_indice=True cuando el indice es parte de la respuesta (groupby/conteos).
    pasos = [
        (lambda: consulta_1(df), False),
        (lambda: consulta_2(df, sector), False),
        (lambda: consulta_3(df), True),
        (lambda: consulta_4(df), True),
        (lambda: consulta_5(df), True),
    ]
    for numero, (consulta, con_indice) in enumerate(pasos, start=1):
        resultado = consulta()
        guardar(resultado, carpeta, numero, con_indice)
        print("-" * 60)


if __name__ == "__main__":
    main()