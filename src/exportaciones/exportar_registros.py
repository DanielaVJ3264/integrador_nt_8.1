"""
HU X01 - Exportacion de la tabla `registros` sucia a CSV, Excel y JSON.

Importa generar_registros() del script de simulacion (no copia el codigo de generacion)
y deja los tres archivos en data/crudo/.
"""
import os
import sys
from pathlib import Path

# Carpeta del proyecto = dos niveles arriba de este archivo (src/exportaciones/)
CARPETA_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_CRUDO = CARPETA_PROYECTO / "data" / "crudo"

# Permite importar desde src/simulaciones/
sys.path.insert(0, str(CARPETA_PROYECTO / "src" / "simulaciones"))
from simular_registros import generar_registros  # noqa: E402


def exportar_registros_crudos(df):
    os.makedirs(CARPETA_CRUDO, exist_ok=True)

    ruta_csv = CARPETA_CRUDO / "registros_sucio.csv"
    ruta_xlsx = CARPETA_CRUDO / "registros_sucio.xlsx"
    ruta_json = CARPETA_CRUDO / "registros_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    df = generar_registros(800)
    rutas = exportar_registros_crudos(df)
    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")