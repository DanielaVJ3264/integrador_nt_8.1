"""
HU F01 - Simulacion de la tabla `retos`.

Genera 500 filas falsas con las mismas columnas que usa Backend II y despues
las ensucia a proposito (nulos, duplicados, espacios, mayusculas y formatos
mezclados) para arreglarlas en la etapa de limpieza.

Uso:  python src/simular_retos.py
"""

import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

# 1. Configurar Faker para Colombia
fake = Faker("es_CO")

# 2. Semillas fijas para que el resultado sea reproducible
Faker.seed(42)
random.seed(42)

# 3. Constantes (selectores y llaves foraneas fijas)
ESTADOS = ["EN_CURSO", "PENDIENTE", "CERRADO"]

IDS_EMPRESA = [
    "6513270e-269e-4d37-b2a7-4de452e6b438",
    "d23f0824-128b-4f33-8c5c-7fd0a6a3a450",
    "9531985d-5d9d-49f8-9818-e811892f902b",
    "36f675cc-81e7-4ef5-a8e2-5d940ed90475",
    "6b0d549b-6f03-475a-9600-a35a099950d8",
]
IDS_CATEGORIA = [
    "8d116ece-1738-47d9-bd9c-172411e20b8f",
    "90c192cf-d3ac-44af-8f21-ddb66cad4a26",
    "a170b338-3926-4059-b28c-105d1fb17c23",
    "0fd630f1-f29d-4da9-953f-48f1a09f76b5",
]
IDS_PRIORIDAD = [
    "0cb1e29c-658c-4a14-95e6-0af593bd04cf",
    "8e81973e-0bec-47b0-b898-d190f9ebdacc",
    "6b4cb242-4a23-4596-a217-beaddbc496cb",
]

FILAS = 500
PORC_DUPLICADOS = 0.05


# 4. Datos limpios
def generar_datos_limpios(numero_datos):
    """Devuelve una lista de diccionarios con filas limpias de retos."""
    filas = []
    for _ in range(numero_datos):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return filas  # el return va FUERA del for


# 5. Utilidades para ensuciar
def generar_muestra(datos, porcentaje, excluir=None):
    """Devuelve los indices de una muestra aleatoria (reproducible).

    `excluir` permite no repetir filas ya elegidas para otro error.
    """
    base = datos if excluir is None else datos.drop(index=excluir)
    return base.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def escribir_mal(texto):
    """Devuelve el estado escrito de forma inconsistente."""
    variantes = [
        texto.lower(),                    # en_curso
        texto.replace("_", " "),          # EN CURSO
        texto.title(),                    # En_Curso
        f" {texto.capitalize()} ",        # ' Cerrado '
    ]
    return random.choice(variantes)


def ensuciar(datos_df):
    """Introduce los errores pedidos por la HU y devuelve un DataFrame nuevo."""
    df = datos_df.copy()

    # nombre: 10% con espacios sobrantes
    idx = generar_muestra(df, 0.10)
    df.loc[idx, "nombre"] = " " + df.loc[idx, "nombre"] + " "

    # descripcion: 12% nulos
    idx = generar_muestra(df, 0.12)
    df.loc[idx, "descripcion"] = None

    # fecha_inicio: dos formatos mezclados (30% en dd/mm/aaaa)
    fecha_inicio = pd.to_datetime(df["fecha_inicio"])
    iso = fecha_inicio.dt.strftime("%Y-%m-%d")
    latino = fecha_inicio.dt.strftime("%d/%m/%Y")
    df["fecha_inicio"] = iso
    idx = generar_muestra(df, 0.30)
    df.loc[idx, "fecha_inicio"] = latino.loc[idx]

    # fecha_fin: formato texto ISO, 8% nulos y 5% anterior a fecha_inicio
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"]).dt.strftime("%Y-%m-%d")
    idx_nulos = generar_muestra(df, 0.08)
    idx_antes = generar_muestra(df, 0.05, excluir=idx_nulos)  # sin pisar los nulos
    df.loc[idx_antes, "fecha_fin"] = (
        fecha_inicio.loc[idx_antes] - pd.Timedelta(days=5)
    ).dt.strftime("%Y-%m-%d")
    df.loc[idx_nulos, "fecha_fin"] = None

    # estado: variantes mal escritas
    idx = generar_muestra(df, 0.10)
    df.loc[idx, "estado"] = df.loc[idx, "estado"].map(escribir_mal)

    return df


def agregar_duplicados(datos_df, total):
    """Rellena hasta `total` filas repitiendo filas tal cual (duplicados exactos)."""
    n_dup = total - len(datos_df)
    repetidas = datos_df.sample(n=n_dup, random_state=random.randint(0, 999))
    return pd.concat([datos_df, repetidas], ignore_index=True)


# 6. Funcion principal (importable desde exportar_retos.py)
def generar_retos(n=FILAS):
    """Genera `n` filas sucias de retos (incluye 5% de duplicados exactos)."""
    n_dup = round(n * PORC_DUPLICADOS)
    limpios = pd.DataFrame(generar_datos_limpios(n - n_dup))
    sucios = ensuciar(limpios)
    df = agregar_duplicados(sucios, n)
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())