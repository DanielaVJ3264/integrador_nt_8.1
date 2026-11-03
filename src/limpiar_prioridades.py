#!/usr/bin/env python3
"""Limpia la tabla prioridades siguiendo los criterios de la HU L01 de Kaizen.

Uso:
    python scripts/limpiar_prioridades.py prioridades_sucio.csv

Qué hace:
    1. Lee el CSV con pd.read_csv() e imprime el diagnóstico inicial.
    2. Quita duplicados exactos, unifica `nombre`, convierte `nivel` y
       `dias_max_respuesta` a número, rellena nulos y marca el valor absurdo.
    3. Imprime el diagnóstico final y cuántas filas se eliminaron.
    4. Guarda data/limpio/prioridades_limpio.csv y data/limpio/prioridades_catalogo.csv.

Se usa pandas porque los criterios piden pd.read_csv() y df.drop_duplicates().
"""

import os
import sys

import pandas as pd

# --- Constantes ------------------------------------------------------------
# Debe ser el mismo diccionario NIVELES de simular_prioridades.py.
# Clave: nombre ya unificado (str.capitalize). Valor: nivel numérico.
# Valores tomados de los propios datos: cada nombre trae siempre el mismo nivel.
NIVELES = {
    "Critica": 5,
    "Alta": 4,
    "Media": 3,
    "Baja": 2,
    "Minima": 1,
}

DIAS_ABSURDO = 60                      # más de 60 días se considera un error
CARPETA_SALIDA = os.path.join("data", "limpio")
RUTA_LIMPIO = os.path.join(CARPETA_SALIDA, "prioridades_limpio.csv")
RUTA_CATALOGO = os.path.join(CARPETA_SALIDA, "prioridades_catalogo.csv")
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]


def leer_datos(ruta):
    """Lee el CSV sucio con pd.read_csv() y devuelve el DataFrame."""
    if not os.path.exists(ruta):
        sys.exit(f"No existe el archivo: {ruta}")
    return pd.read_csv(ruta, encoding="utf-8")


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y cantidad de duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print(f"df.shape: {df.shape}")
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\ndf.duplicated().sum(): {df.duplicated().sum()}")


def quitar_duplicados_exactos(df):
    """Quita las filas repetidas tal cual con df.drop_duplicates()."""
    return df.drop_duplicates()


def unificar_nombre(df):
    """Quita espacios y deja la primera letra en mayúscula: 'ALTA', ' alta ' -> 'Alta'."""
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    return df


def convertir_nivel(df):
    """Convierte `nivel` a número: cambia las palabras por dígitos y luego usa to_numeric.

    Los textos '3' y las palabras 'tres' terminan como número; lo que no se
    pueda convertir queda como nulo (NaN).
    """
    df["nivel"] = df["nivel"].astype("object").replace(
        {"cinco": 5, "cuatro": 4, "tres": 3, "dos": 2, "uno": 1}
    )
    df["nivel"] = pd.to_numeric(df["nivel"], errors="coerce")
    return df


def rellenar_nivel(df):
    """Rellena el nivel vacío buscando el nombre en el diccionario NIVELES."""
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES))
    return df


def limpiar_dias(df):
    """Convierte `dias_max_respuesta` a número, anula el valor absurdo y rellena con la mediana."""
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    # El valor absurdo (por ejemplo 999) se marca como nulo antes de calcular la mediana.
    df.loc[df["dias_max_respuesta"] > DIAS_ABSURDO, "dias_max_respuesta"] = None
    mediana = df["dias_max_respuesta"].median()
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(mediana)
    print(f"\nMediana usada para rellenar dias_max_respuesta: {mediana}")
    return df


def ajustar_tipos(df):
    """Deja `nivel` y `dias_max_respuesta` como enteros (la mediana puede traer decimales)."""
    df["nivel"] = df["nivel"].round().astype("Int64")
    df["dias_max_respuesta"] = df["dias_max_respuesta"].round().astype("Int64")
    return df


def sacar_catalogo(df):
    """Devuelve el catálogo real: una fila por prioridad (se espera que sean 5)."""
    return df.drop_duplicates(subset=["nombre"])


def guardar(df, ruta):
    """Crea la carpeta si no existe y guarda el DataFrame en CSV (utf-8, sin índice)."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")


def main():
    """Ejecuta todo el flujo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    # Si no se pasa ruta, usa la que indica el criterio.
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "crudo", "prioridades_sucio.csv")

    df = leer_datos(ruta)
    filas_inicio = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    # --- Limpieza (en el orden de los criterios) ---
    df = quitar_duplicados_exactos(df)
    df = unificar_nombre(df)
    df = convertir_nivel(df)
    df = rellenar_nivel(df)
    df = limpiar_dias(df)
    df = ajustar_tipos(df)
    # Segunda pasada: unificar texto y rellenar valores pudo dejar filas idénticas.
    df = quitar_duplicados_exactos(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")

    # --- Resultado ---
    eliminadas = filas_inicio - len(df)
    print(f"\nFilas al inicio: {filas_inicio} | filas al final: {len(df)} | filas eliminadas: {eliminadas}")

    # Verificación del criterio final: sin nulos obligatorios ni duplicados exactos.
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print(f"Nulos en columnas obligatorias: {nulos} | duplicados exactos: {duplicados}")
    if nulos or duplicados:
        print("ATENCIÓN: todavía quedan nulos o duplicados. Revisa el diccionario NIVELES.")

    catalogo = sacar_catalogo(df)
    print(f"\nCatálogo real: {len(catalogo)} filas (se esperan 5)")
    print(catalogo.to_string(index=False))

    guardar(df, RUTA_LIMPIO)
    guardar(catalogo, RUTA_CATALOGO)
    print(f"\nArchivo limpio guardado en: {RUTA_LIMPIO}")
    print(f"Catálogo guardado en: {RUTA_CATALOGO}")


if __name__ == "__main__":
    main()
