# Simula la tabla `empresas` con Faker y despues la ensucia a proposito (HU F01)
import random
import uuid
import pandas as pd
from faker import Faker

# 1. Constantes: valores del campo selector
SECTORES = ["TECNOLOGIAS", "SALUD", "ALIMENTOS"]

# 2. Configurar Faker a la region (Colombia)
fake = Faker("es_CO")

# 3. Fijar la semilla para que el resultado sea siempre el mismo
Faker.seed(42)
random.seed(42)


# 4. Genera los datos LIMPIOS
def generar_datos_limpios(numero_datos):
    filas = []
    for _ in range(numero_datos):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    return pd.DataFrame(filas)


# 5. Funciones de apoyo para ensuciar
def generar_muestra(datos, porcentaje):
    """Devuelve los indices de un porcentaje de filas elegidas al azar."""
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index


def escribir_mal(texto):
    """Devuelve el texto con mayusculas/espacios distintos."""
    variantes = [texto.lower(), f" {texto.title()} ", texto.capitalize()]
    return random.choice(variantes)


def convertir_booleano_texto(valor):
    """Convierte True/False a texto: 'SI', '1', 'No', '0'."""
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])


def nit_con_puntos(nit):
    """9001234567 o 900123456-7 -> 900.123.456-7"""
    d = nit.replace("-", "")
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9]}"


def nit_sin_nada(nit):
    """900123456-7 -> 9001234567"""
    return nit.replace("-", "")


def telefono_con_espacios(tel):
    """3001234567 -> 300 123 4567"""
    return f"{tel[:3]} {tel[3:6]} {tel[6:]}"


def telefono_con_indicativo(tel):
    """3001234567 -> +57 300-123-4567"""
    return f"+57 {tel[:3]}-{tel[3:6]}-{tel[6:]}"


# 6. Ensucia los datos
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # nombre: 10% con espacios sobrantes, 15% en MAYUSCULAS
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "nombre"] = " " + datos_df.loc[filas, "nombre"] + " "

    filas = generar_muestra(datos_df, 0.15)
    datos_df.loc[filas, "nombre"] = datos_df.loc[filas, "nombre"].str.upper()

    # nit: la mitad con puntos y guion (900.123.456-7), la otra mitad sin nada (9001234567)
    mitad = generar_muestra(datos_df, 0.5)
    otra_mitad = datos_df.index.difference(mitad)
    datos_df.loc[mitad, "nit"] = datos_df.loc[mitad, "nit"].map(nit_con_puntos)
    datos_df.loc[otra_mitad, "nit"] = datos_df.loc[otra_mitad, "nit"].map(nit_sin_nada)

    # nit: 3% repetidos entre empresas distintas (copio el NIT de otra fila)
    filas = generar_muestra(datos_df, 0.03)
    candidatas = datos_df.index.difference(filas)
    origen = random.sample(list(candidatas), len(filas))
    datos_df.loc[filas, "nit"] = datos_df.loc[origen, "nit"].values

    # sector: variantes del mismo sector ('Salud', 'SALUD', ' salud ')
    filas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas, "sector"] = datos_df.loc[filas, "sector"].map(escribir_mal)

    # contacto: 8% en None (nulos)
    filas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas, "contacto"] = None

    # correo: 6% sin la arroba (correo invalido)
    filas = generar_muestra(datos_df, 0.06)
    datos_df.loc[filas, "correo"] = datos_df.loc[filas, "correo"].str.replace("@", "", regex=False)

    # telefono: tres formatos mezclados (un tercio cada uno)
    indices = list(datos_df.index)
    random.shuffle(indices)
    tercio = len(indices) // 3
    con_espacios = indices[:tercio]
    con_indicativo = indices[tercio:2 * tercio]
    datos_df.loc[con_espacios, "telefono"] = datos_df.loc[con_espacios, "telefono"].map(telefono_con_espacios)
    datos_df.loc[con_indicativo, "telefono"] = datos_df.loc[con_indicativo, "telefono"].map(telefono_con_indicativo)

    # activa: 30% como texto ('SI', 'No', '1', '0')
    datos_df["activa"] = datos_df["activa"].astype(object)
    filas = generar_muestra(datos_df, 0.30)
    datos_df.loc[filas, "activa"] = datos_df.loc[filas, "activa"].map(convertir_booleano_texto)

    # 5% de las filas repetidas tal cual (duplicados exactos).
    # Se reemplazan filas para que el total siga siendo n.
    destino = generar_muestra(datos_df, 0.05)
    candidatas = datos_df.index.difference(destino)
    origen = random.sample(list(candidatas), len(destino))
    datos_df = pd.concat([datos_df.drop(destino), datos_df.loc[origen]], ignore_index=True)

    return datos_df


# 7. Funcion principal: genera y ensucia
def generar_empresas(n=300):
    df = ensuciar(generar_datos_limpios(n))
    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())