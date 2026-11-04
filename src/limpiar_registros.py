"""Limpieza de la tabla registros (HU L01 de Kaizen).

Uso:
    python scripts/limpiar_registros.py registros_sucio.csv [registros_limpio.csv]

Si no se indica la ruta de salida, el archivo limpio se guarda como
registros_limpio.csv en la misma carpeta del archivo de entrada.
"""

import sys
from pathlib import Path

import pandas as pd

COLUMNAS_OBLIGATORIAS = ["id", "fecha_registro", "estado", "id_usuario", "id_reto"]


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico del DataFrame: shape, info, nulos y duplicados."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def leer_datos(ruta):
    """Lee el CSV sucio con pd.read_csv y devuelve el DataFrame."""
    return pd.read_csv(ruta)


def quitar_duplicados_exactos(df):
    """Elimina las filas completamente iguales con drop_duplicates()."""
    return df.drop_duplicates()


def convertir_fecha(df):
    """Convierte fecha_registro a datetime aunque venga en dos formatos.

    Acepta '2026-07-04 21:28:48' y '29/09/2026 05:16' (día primero).
    Los valores que no se puedan convertir quedan como NaT.
    """
    df["fecha_registro"] = pd.to_datetime(
        df["fecha_registro"], format="mixed", dayfirst=True, errors="coerce"
    )
    return df


def unificar_estado(df):
    """Quita espacios sobrantes, pasa a mayúsculas y cambia espacios por '_'."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def rellenar_observaciones(df):
    """Rellena las observaciones vacías con 'Sin observacion'."""
    df["observacion"] = df["observacion"].fillna("Sin observacion")
    return df


def quitar_participaciones_repetidas(df):
    """Detecta e imprime las participaciones repetidas (mismo usuario y reto)
    y deja solo la primera de cada par."""
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"\nParticipaciones repetidas (usuario + reto): {len(repetidos)}")
    return df.drop_duplicates(subset=["id_usuario", "id_reto"], keep="first")


def crear_columna_mes(df):
    """Crea la columna mes (periodo mensual) para agrupar después."""
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    return df


def verificar_resultado(df):
    """Comprueba que no queden nulos en columnas obligatorias ni duplicados exactos."""
    nulos = df[COLUMNAS_OBLIGATORIAS].isna().sum().sum()
    duplicados = df.duplicated().sum()
    print("\nVerificación final:")
    print(f"  Nulos en columnas obligatorias: {nulos}")
    print(f"  Duplicados exactos: {duplicados}")
    if nulos or duplicados:
        print("  ATENCIÓN: quedan problemas sin resolver.")


def guardar_resultado(df, ruta):
    """Guarda el DataFrame limpio en CSV (UTF-8, sin índice)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"\nArchivo guardado en: {ruta}")


def main():
    """Ejecuta todo el proceso de limpieza de principio a fin."""
    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/crudo/registros_sucio.csv")
    ruta_salida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/limpio/registros_limpio.csv")

    df = leer_datos(ruta_entrada)
    filas_iniciales = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados_exactos(df)
    df = convertir_fecha(df)
    df = unificar_estado(df)
    df = rellenar_observaciones(df)
    df = quitar_participaciones_repetidas(df)
    df = crear_columna_mes(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_iniciales - len(df)} "
          f"({filas_iniciales} -> {len(df)})")

    verificar_resultado(df)
    guardar_resultado(df, ruta_salida)


if __name__ == "__main__":
    main()