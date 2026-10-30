"""limpiar_empresas.py - HU L01: limpieza de la tabla empresas.

Uso:
    python scripts/limpiar_empresas.py empresas_sucio.csv

Lee el CSV sucio, imprime el diagnostico, corrige los errores que piden los
criterios, imprime el diagnostico otra vez y guarda empresas_limpio.csv.
"""

import sys
from pathlib import Path

import pandas as pd

# Archivo de salida (se guarda en la carpeta desde donde se ejecuta el script)
RAIZ = Path(__file__).resolve().parent.parent
ENTRADA_POR_DEFECTO = RAIZ / "data" / "crudo" / "empresas_sucio.csv"
SALIDA_POR_DEFECTO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"


def leer_datos(ruta):
    """Lee el CSV con pandas. Todo entra como texto (dtype=str) para no perder
    los ceros iniciales del nit y para que 'activa' llegue como "True"/"False"."""
    return pd.read_csv(ruta, dtype=str)


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnostico: shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print("\nDuplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Elimina las filas que son duplicados exactos de otra."""
    return df.drop_duplicates()


def limpiar_nombre(df):
    """Quita los espacios sobrantes al inicio y al final del nombre."""
    df["nombre"] = df["nombre"].str.strip()
    return df


def unificar_sector(df):
    """Unifica el sector: sin espacios sobrantes y con formato Titulo
    (asi 'LOGISTICA' y ' logistica ' quedan iguales)."""
    df["sector"] = df["sector"].str.strip().str.title()
    return df


def unificar_nit(df):
    """Deja el nit en un solo formato: sin puntos ni guiones."""
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)
    return df


def limpiar_telefono(df):
    """Deja el telefono solo con digitos (quita espacios, guiones y el signo +)."""
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    return df


def convertir_activa(df):
    """Convierte 'activa' a booleano de verdad. Al leer el CSV llega como texto
    ("True", "False", "SI", "No", "1", "0"), asi que se normaliza y se mapea."""
    df["activa"] = (
        df["activa"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({"TRUE": True, "SI": True, "1": True,
              "FALSE": False, "NO": False, "0": False})
    )
    # Si no quedo ningun valor sin mapear, pasa a dtype bool de verdad
    if df["activa"].notna().all():
        df["activa"] = df["activa"].astype(bool)
    return df


def rellenar_contacto(df):
    """Rellena los contactos vacios (o solo espacios) con 'Sin contacto'."""
    df["contacto"] = df["contacto"].replace(r"^\s*$", pd.NA, regex=True)
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    return df


def marcar_correo_valido(df):
    """Crea la columna correo_valido: True si el correo contiene '@'."""
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    return df


def limpiar(df):
    """Aplica todas las correcciones en orden y devuelve el DataFrame limpio."""
    df = quitar_duplicados(df).copy()
    df = limpiar_nombre(df)
    df = unificar_sector(df)
    df = unificar_nit(df)
    df = limpiar_telefono(df)
    df = convertir_activa(df)
    df = rellenar_contacto(df)
    df = marcar_correo_valido(df)
    # Tras normalizar el texto pueden aparecer duplicados nuevos: se quitan tambien
    df = quitar_duplicados(df)
    return df


def verificar(df):
    """Comprueba el criterio final: sin nulos ni duplicados exactos."""
    nulos = int(df.isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("\nVerificacion final:")
    print(f"  Nulos en total: {nulos} -> {'OK' if nulos == 0 else 'REVISAR'}")
    print(f"  Duplicados exactos: {duplicados} -> {'OK' if duplicados == 0 else 'REVISAR'}")
    print(f"  Correos invalidos marcados (correo_valido=False): {int((~df['correo_valido']).sum())}")


def main():
    """Punto de entrada: lee, diagnostica, limpia, diagnostica, guarda."""
    # Si no se pasa argumento, usa la ruta por defecto del proyecto
    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else ENTRADA_POR_DEFECTO
    if not ruta_entrada.exists():
        print(f"No se encontro el archivo: {ruta_entrada}")
        sys.exit(1)

    df = leer_datos(ruta_entrada)
    filas_antes = df.shape[0]
    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_antes - df.shape[0]} "
          f"({filas_antes} -> {df.shape[0]})")
    verificar(df)

    # Crea la carpeta data/limpio si todavia no existe
    SALIDA_POR_DEFECTO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA_POR_DEFECTO, index=False, encoding="utf-8")
    print(f"\nArchivo guardado en: {SALIDA_POR_DEFECTO.resolve()}")


if __name__ == "__main__":
    main()