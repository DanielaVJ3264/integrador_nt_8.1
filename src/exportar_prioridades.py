"""HU X01 - Exporta la tabla sucia de prioridades a CSV, XLSX y JSON."""
import os
import sys
from importlib import import_module
from pathlib import Path

# exportaciones/ -> src/ -> raiz del proyecto (integrador_nt_8.1)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

# Para poder importar el script que esta en src/simulaciones/
sys.path.insert(0, str(RAIZ_PROYECTO / "src" / "simulaciones"))
generar_prioridades = import_module("simular_prioridades").generar_prioridades

NOMBRE_ENTIDAD = "prioridades"
CARPETA_CRUDO = RAIZ_PROYECTO / "data" / "crudo"

def exportar_csv(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.csv"
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def exportar_excel(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.xlsx"
    df.to_excel(ruta, index=False, sheet_name="prioridades")
    return ruta


def exportar_json(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.json"
    df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


def exportar_crudos(df):
    os.makedirs(CARPETA_CRUDO, exist_ok=True)
    nombre = f"{NOMBRE_ENTIDAD}_sucio"
    return [
        exportar_csv(df, CARPETA_CRUDO, nombre),
        exportar_excel(df, CARPETA_CRUDO, nombre),
        exportar_json(df, CARPETA_CRUDO, nombre),
    ]


if __name__ == "__main__":
    df = generar_prioridades(200)
    for ruta in exportar_crudos(df):
        print(f"{ruta} -> {df.shape}")