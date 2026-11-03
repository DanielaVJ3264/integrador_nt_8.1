"""
HU F01 - Simulacion de la tabla `prioridades`.

Genera 200 filas falsas con las mismas columnas que usa Backend II y despues
las ENSUCIA a proposito (nulos, duplicados, espacios, mayusculas mezcladas y
formatos distintos) para arreglarlas en la etapa de limpieza.

OJO: `dias_max_respuesta` NO esta en el modelo de Backend II: es una columna
EXTRA solo para este ejercicio de analisis.
"""
import random
import uuid

import pandas as pd
from faker import Faker

# 1. Constantes (selectores)
NIVELES = {"CRITICA": 5, "ALTA": 4, "MEDIA": 3, "BAJA": 2, "MINIMA": 1}
DIAS = {5: 1, 4: 3, 3: 7, 2: 10, 1: 15}
PALABRAS_NIVEL = {5: "cinco", 4: "cuatro", 3: "tres", 2: "dos", 1: "uno"}

# 2. Region y semilla fija (resultado reproducible)
fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)


# 3. Datos LIMPIOS
def generar_datos_limpios(n):
    """Devuelve una lista de n diccionarios con datos limpios."""
    filas = []
    for _ in range(n):
        nombre = random.choice(list(NIVELES.keys()))
        nivel = NIVELES[nombre]
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "nivel": nivel,
            "dias_max_respuesta": DIAS[nivel],
        })
    return filas


# 4. Utilidades para ensuciar
def elegir_indices(df, porcentaje, excluir=()):
    """Elige, con la semilla fija, un porcentaje de indices sin repetir."""
    disponibles = [i for i in df.index if i not in set(excluir)]
    cantidad = round(len(df) * porcentaje)
    return random.sample(disponibles, cantidad)


def escribir_mal(texto):
    """Devuelve el texto con espacios sobrantes y mayusculas mezcladas."""
    variantes = [texto.lower(), f" {texto.lower()} ", texto.capitalize(),
                 f"  {texto}  ", texto.title()]
    return random.choice(variantes)


def ensuciar(df_limpio, n_total):
    """Ensucia el DataFrame y agrega duplicados exactos hasta n_total filas."""
    df = df_limpio.copy()
    df["nivel"] = df["nivel"].astype(object)
    df["dias_max_respuesta"] = df["dias_max_respuesta"].astype("Int64")

    # nombre: 'ALTA', ' alta ', 'Alta'
    idx = elegir_indices(df, 0.30)
    df.loc[idx, "nombre"] = df.loc[idx, "nombre"].map(escribir_mal)

    # nivel: 7% None, 15% como texto ('3') y 15% como palabra ('tres')
    idx_nulos = elegir_indices(df, 0.07)
    idx_texto = elegir_indices(df, 0.15, excluir=idx_nulos)
    idx_palabra = elegir_indices(df, 0.15, excluir=idx_nulos + idx_texto)
    df.loc[idx_texto, "nivel"] = df.loc[idx_texto, "nivel"].map(str)
    df.loc[idx_palabra, "nivel"] = df.loc[idx_palabra, "nivel"].map(PALABRAS_NIVEL)
    df.loc[idx_nulos, "nivel"] = None

    # dias_max_respuesta: 5% None y 3% con 999
    idx_nulos_d = elegir_indices(df, 0.05)
    idx_absurdos = elegir_indices(df, 0.03, excluir=idx_nulos_d)
    df.loc[idx_nulos_d, "dias_max_respuesta"] = pd.NA
    df.loc[idx_absurdos, "dias_max_respuesta"] = 999

    # 8% de filas repetidas tal cual (duplicados exactos)
    n_duplicados = round(n_total * 0.08)
    copias = df.loc[random.sample(list(df.index), n_duplicados)]
    df = pd.concat([df, copias], ignore_index=True)
    return df


# 5. Funcion principal
def generar_prioridades(n=200):
    """Devuelve el DataFrame sucio de prioridades con n filas en total."""
    n_duplicados = round(n * 0.08)
    df_limpio = pd.DataFrame(generar_datos_limpios(n - n_duplicados))
    df = ensuciar(df_limpio, n)
    return df


if __name__ == "__main__":
    df = generar_prioridades(200)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())