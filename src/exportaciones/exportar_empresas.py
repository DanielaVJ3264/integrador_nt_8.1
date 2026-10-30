# Rutina para convertir el DataFrame sucio en multiples fuentes de informacion (HU X01)
import os
import sys
from importlib import import_module
from pathlib import Path

# 1. Configuracion (cambiar segun su tabla)
NOMBRE_ARCHIVO = "empresas_sucio"
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]  # exportaciones -> src -> raiz
CARPETA_CRUDOS = CARPETA_PROYECTO / "data" / "crudo"

# Importo la funcion del script de simulacion (esta en otra carpeta)
sys.path.insert(0, str(CARPETA_PROYECTO / "src" / "simulaciones"))
generar_empresas = import_module("simular_empresas").generar_empresas


# 2.1 Crear la carpeta si no existe
def preparar_carpeta(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


# 2.2 Exportar a CSV
def exportar_csv(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.csv"
    datos_df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


# 2.3 Exportar a JSON
def exportar_json(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.json"
    datos_df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


# 2.4 Exportar a Excel
def exportar_excel(datos_df, carpeta, nombre_archivo):
    ruta = preparar_carpeta(carpeta) / f"{nombre_archivo}.xlsx"
    datos_df.to_excel(ruta, index=False, sheet_name="empresas")
    return ruta


# 3. Genero los archivos en mi proyecto
def exportar_empresas_crudas(datos_sucios_df):
    return [
        exportar_csv(datos_sucios_df, CARPETA_CRUDOS, NOMBRE_ARCHIVO),
        exportar_json(datos_sucios_df, CARPETA_CRUDOS, NOMBRE_ARCHIVO),
        exportar_excel(datos_sucios_df, CARPETA_CRUDOS, NOMBRE_ARCHIVO),
    ]


if __name__ == "__main__":
    df = generar_empresas()
    for ruta in exportar_empresas_crudas(df):
        print(f"{ruta} -> {df.shape}")