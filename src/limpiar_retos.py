"""Limpieza de la tabla retos (HU L01 de Kaizen).

Uso:
    python scripts/limpiar_retos.py retos_sucio.csv [ruta_salida]

Lee el CSV sucio, imprime el diagnóstico, corrige los errores, imprime el
diagnóstico otra vez y guarda el resultado en data/limpio/retos_limpio.csv
(o en la ruta de salida opcional).
"""
import os
import sys

import pandas as pd

RUTA_SALIDA_POR_DEFECTO = os.path.join("data", "limpio", "retos_limpio.csv")
# Columnas que no pueden quedar nulas. fecha_fin queda fuera porque un reto
# EN_CURSO o PENDIENTE puede no tener fecha de cierre todavía.
COLUMNAS_OBLIGATORIAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnóstico: shape, info, nulos por columna y duplicados."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Elimina las filas duplicadas exactas y devuelve el DataFrame."""
    return df.drop_duplicates()


def limpiar_texto(df):
    """Quita espacios sobrantes al inicio y al final de las columnas de texto."""
    for col in ["id", "nombre", "descripcion", "id_empresa", "id_categoria", "id_prioridad"]:
        df[col] = df[col].str.strip()
    return df


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime aunque vengan en dos formatos.

    Los textos ISO (2026-07-08) se leen año-mes-día y los textos con barras
    (14/03/2026) se leen día/mes/año. Se separan para que dayfirst no
    confunda el formato ISO. Lo que no se pueda leer queda como NaT.
    """
    for col in ["fecha_inicio", "fecha_fin"]:
        texto = df[col].astype("string").str.strip()
        con_barras = texto.str.contains("/", na=False)
        iso = pd.to_datetime(texto.where(~con_barras), format="%Y-%m-%d", errors="coerce")
        dmy = pd.to_datetime(texto.where(con_barras), format="%d/%m/%Y", errors="coerce")
        df[col] = iso.fillna(dmy)
    return df


def unificar_estado(df):
    """Unifica el estado en MAYÚSCULAS con guion bajo (EN_CURSO, PENDIENTE, CERRADO)."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def rellenar_descripcion(df):
    """Rellena las descripciones vacías con 'Sin descripcion'."""
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def crear_duracion_y_validez(df):
    """Crea duracion_dias y fecha_valida; marca las fechas con fin antes que inicio."""
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    df["fecha_valida"] = df["duracion_dias"] >= 0
    return df


def main():
    """Ejecuta todo el flujo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/limpiar_retos.py retos_sucio.csv [ruta_salida]")
        sys.exit(1)
    ruta_entrada = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else RUTA_SALIDA_POR_DEFECTO

    df = pd.read_csv(ruta_entrada, dtype=str)  # todo como texto; se convierte después
    filas_inicio = len(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados(df)
    # Nulos medidos después de quitar duplicados, para que la comparación solo
    # refleje lo que corrigen las demás funciones.
    nulos_antes = df.isna().sum()
    df = limpiar_texto(df)
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripcion(df)
    df = crear_duracion_y_validez(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")

    # Resumen de lo corregido
    nulos_despues = df.isna().sum()
    print("\n===== RESUMEN =====")
    print("Filas eliminadas (duplicados exactos):", filas_inicio - len(df))
    print("Nulos corregidos por columna (antes - después):")
    print((nulos_antes - nulos_despues.reindex(nulos_antes.index)).to_string())
    print("Estados únicos:", sorted(df["estado"].unique()))
    incoherentes = int((df["duracion_dias"] < 0).sum())
    sin_fin = int(df["fecha_fin"].isna().sum())
    print(f"Fechas incoherentes (fin antes que inicio): {incoherentes}")
    print(f"Retos sin fecha_fin (duracion_dias vacía, fecha_valida=False): {sin_fin}")
    print("fecha_valida=False en total:", int((~df["fecha_valida"]).sum()))

    # Comprobaciones finales
    nulos_obligatorios = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("Nulos en columnas obligatorias:", nulos_obligatorios)
    print("Duplicados exactos:", duplicados)
    assert nulos_obligatorios == 0 and duplicados == 0, "La limpieza no quedó completa"

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\nArchivo limpio guardado en: {ruta_salida}")


if __name__ == "__main__":
    main()