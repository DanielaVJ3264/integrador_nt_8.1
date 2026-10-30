"""HU G01 - Graficas de la tabla empresas.

Uso:
    python scripts/reporte_empresas.py empresas_limpio.csv

Lee el CSV limpio, crea tres graficas con matplotlib, las guarda en
reportes/ e imprime la ruta de cada una y las conclusiones.
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

CARPETA = "reportes"


def leer_datos(ruta_csv):
    """Lee el CSV limpio y convierte activa y correo_valido a booleanos."""
    df = pd.read_csv(ruta_csv)
    for columna in ("activa", "correo_valido"):
        if df[columna].dtype != bool:
            df[columna] = (
                df[columna].astype(str).str.strip().str.lower()
                .isin(["true", "1", "si", "sí"])
            )
    return df


def guardar(ruta):
    """Ajusta el diseno, guarda la grafica con dpi=120 y cierra la figura."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    print(f"Grafica guardada en: {ruta}")


def grafica_1_por_sector(df):
    """Grafica 1 (barras): cantidad de empresas por sector."""
    por_sector = df["sector"].value_counts()
    plt.figure(figsize=(7, 5))
    por_sector.plot(kind="bar")
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=0)
    guardar(os.path.join(CARPETA, "empresas_grafica_1.png"))
    return por_sector


def grafica_2_activas(df):
    """Grafica 2 (torta): empresas activas vs inactivas."""
    conteo = df["activa"].value_counts()
    conteo.index = ["Activas" if v else "Inactivas" for v in conteo.index]
    plt.figure(figsize=(6, 6))
    conteo.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Proporcion de empresas")
    guardar(os.path.join(CARPETA, "empresas_grafica_2.png"))
    return df["activa"].value_counts(normalize=True) * 100


def grafica_3_apiladas(df):
    """Grafica 3 (barras apiladas): activas e inactivas por sector."""
    tabla = pd.crosstab(df["sector"], df["activa"])
    tabla = tabla.rename(columns={True: "Activas", False: "Inactivas"})
    plt.figure(figsize=(7, 5))
    tabla.plot(kind="bar", stacked=True)
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=0)
    plt.legend(title="Estado")
    guardar(os.path.join(CARPETA, "empresas_grafica_3.png"))
    return tabla


def imprimir_conclusiones(df, por_sector, porcentajes):
    """Imprime las conclusiones que responden a las preguntas de la HU."""
    total = len(df)
    maximo = por_sector.max()
    top = list(por_sector[por_sector == maximo].index)
    pct_inactivas = float(porcentajes.get(False, 0.0))
    invalidos = int((~df["correo_valido"]).sum())

    print("\nCONCLUSIONES")
    print("------------")
    print(f"1. El sector con mas empresas registradas es {' y '.join(top)} "
          f"con {maximo} de {total} ({maximo / total * 100:.1f}%).")
    print(f"2. El {pct_inactivas:.1f}% de las empresas esta inactivo "
          f"({int((~df['activa']).sum())} de {total}). Significa que una "
          "parte grande de la plataforma no esta operando: hay que "
          "revisar por que se van o no se activan y como reactivarlas.")
    print(f"3. Aparecieron {invalidos} correos invalidos. Hay que validarlos "
          "en el back porque la validacion del front se puede saltar y el "
          "back es la ultima barrera antes de guardar los datos.")


def main():
    """Punto de entrada: lee el CSV, crea las graficas e imprime todo."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else "data/limpio/empresas_limpio.csv"
    df = leer_datos(ruta)
    os.makedirs(CARPETA, exist_ok=True)
    por_sector = grafica_1_por_sector(df)
    porcentajes = grafica_2_activas(df)
    grafica_3_apiladas(df)
    imprimir_conclusiones(df, por_sector, porcentajes)


if __name__ == "__main__":
    main()