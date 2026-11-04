"""
HU F01 - Simulacion de la tabla `registros` (tabla puente Usuario-Reto).

Genera 800 filas falsas con Faker("es_CO") y las ensucia a proposito:
nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos de fecha distintos.
Las semillas estan fijas (42) para que el resultado sea siempre el mismo.
"""
import random
import uuid

import pandas as pd
from faker import Faker

# 1. Configuracion de Faker y semillas (reproducibilidad)
fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)

# 2. Constantes (columnas con valores de un conjunto fijo)
ESTADOS = ["PENDIENTE", "ACEPTADO", "RECHAZADO", "EN_PROCESO", "FINALIZADO"]
IDS_USUARIO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(5)]
IDS_RETO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(5)]


# 3. Generacion de datos LIMPIOS
def generar_datos_limpios(n=800):
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO),
        })
    return pd.DataFrame(filas)


# 4. Utilidades para ensuciar
def elegir_filas(df, porcentaje):
    """Devuelve los indices de una muestra del `porcentaje` de filas."""
    return df.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def escribir_mal_estado(texto):
    """Variantes sucias de `estado`: minusculas, espacios y 'EN PROCESO' / 'inscrito'."""
    variantes = [
        texto.lower(),
        f" {texto.title()} ",
        texto.capitalize(),
        texto.replace("_", " "),
    ]
    return random.choice(variantes)


def ensuciar(df_limpio, n_duplicados):
    df = df_limpio.copy()

    # fecha_registro: dos formatos mezclados
    iso = df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    df["fecha_registro"] = iso
    idx = elegir_filas(df, 0.40)
    df.loc[idx, "fecha_registro"] = latino.loc[idx]

    # observacion: 20% en None
    idx = elegir_filas(df, 0.20)
    df.loc[idx, "observacion"] = None

    # estado: variantes mal escritas (incluye 'inscrito' y 'EN PROCESO')
    idx = elegir_filas(df, 0.10)
    df.loc[idx, "estado"] = df.loc[idx, "estado"].map(escribir_mal_estado)
    # algunos casos con 'inscrito' como pide la HU
    idx_inscrito = df.loc[idx].sample(frac=0.2, random_state=42).index
    df.loc[idx_inscrito, "estado"] = "inscrito"

    # 10%: par id_usuario + id_reto REPETIDO (mismo usuario dos veces en el mismo reto)
    n_pares = int(len(df) * 0.10)
    originales = df.sample(n=n_pares, random_state=random.randint(0, 999))
    destino = df.drop(originales.index).sample(n=n_pares, random_state=random.randint(0, 999)).index
    df.loc[destino, ["id_usuario", "id_reto"]] = originales[["id_usuario", "id_reto"]].values

    # 5%: filas repetidas tal cual (duplicados exactos); el total final queda en n
    idx = df.sample(n=n_duplicados, random_state=random.randint(0, 999)).index
    df = pd.concat([df, df.loc[idx]], ignore_index=True)

    return df


# 5. Funcion principal importable
def generar_registros(n=800):
    n_duplicados = round(n * 0.05)
    df_limpio = generar_datos_limpios(n - n_duplicados)
    df = ensuciar(df_limpio, n_duplicados)
    return df


if __name__ == "__main__":
    df = generar_registros(800)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())