"""
HU X01 - Exportacion de la tabla `retos` sucia a CSV, Excel y JSON.

Importa generar_retos() de simular_retos.py (no copia el codigo de generacion).

Uso (desde la raiz del proyecto):  python src/exportar_retos.py
"""

import os

from simular_retos import generar_retos

CARPETA = "data/crudo"
NOMBRE = "retos_sucio"


def exportar_csv(df, carpeta, nombre):
    ruta = os.path.join(carpeta, f"{nombre}.csv")
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def exportar_excel(df, carpeta, nombre):
    ruta = os.path.join(carpeta, f"{nombre}.xlsx")
    df.to_excel(ruta, index=False, sheet_name="retos")
    return ruta


def exportar_json(df, carpeta, nombre):
    ruta = os.path.join(carpeta, f"{nombre}.json")
    df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


if __name__ == "__main__":
    df = generar_retos()
    os.makedirs(CARPETA, exist_ok=True)

    rutas = [
        exportar_csv(df, CARPETA, NOMBRE),
        exportar_excel(df, CARPETA, NOMBRE),
        exportar_json(df, CARPETA, NOMBRE),
    ]
    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")