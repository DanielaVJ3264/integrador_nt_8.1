"""Punto de entrada del proyecto integrador (tabla prioridades).

Ejecuta todo el flujo en orden, siempre desde la raiz del proyecto:

    1. exportar_prioridades.py  -> data/crudo/prioridades_sucio.(csv|xlsx|json)
    2. limpiar_prioridades.py   -> data/limpio/prioridades_limpio.csv
    3. consultas_prioridades.py -> data/limpio/prioridades_consulta_1..5.csv
    4. reporte_prioridades.py   -> reportes/prioridades_grafica_1..3.png

Uso (con el venv activo, parado en la carpeta integrador_nt_8.1):

    python main.py                  # corre todos los pasos
    python main.py limpiar          # corre solo un paso
    python main.py consultas reporte  # corre varios pasos, en el orden dado

Pasos disponibles: simular, exportar, limpiar, consultas, reporte
"""

import os
import subprocess
import sys

# --- Rutas relativas a la raiz del proyecto ---------------------------------
RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = "src"

RUTA_SUCIO = os.path.join("data", "crudo", "prioridades_sucio.csv")
RUTA_LIMPIO = os.path.join("data", "limpio", "prioridades_limpio.csv")

# Cada paso: nombre -> (script dentro de src/, argumentos del script)
PASOS = {
    "simular": ("simular_prioridades.py", []),
    "exportar": ("exportar_prioridades.py", []),
    "limpiar": ("limpiar_prioridades.py", [RUTA_SUCIO]),
    "consultas": ("consultas_prioridades.py", [RUTA_LIMPIO]),
    "reporte": ("reporte_prioridades.py", [RUTA_LIMPIO]),
}

# Flujo completo. 'simular' no va aqui porque solo imprime una revision;
# exportar ya genera los datos sucios.
FLUJO_COMPLETO = ["exportar", "limpiar", "consultas", "reporte"]


def ejecutar_paso(nombre):
    """Corre un script de src/ como proceso aparte, desde la raiz del proyecto."""
    script, argumentos = PASOS[nombre]
    ruta_script = os.path.join(SRC, script)

    if not os.path.exists(os.path.join(RAIZ, ruta_script)):
        print(f"[ERROR] No existe {ruta_script}")
        return False

    print(f"\n{'=' * 60}\nPASO: {nombre}  ->  python {ruta_script} {' '.join(argumentos)}\n{'=' * 60}")
    resultado = subprocess.run([sys.executable, ruta_script, *argumentos], cwd=RAIZ)

    if resultado.returncode != 0:
        print(f"[ERROR] El paso '{nombre}' fallo (codigo {resultado.returncode}).")
        return False
    return True


def main():
    pasos = sys.argv[1:] or FLUJO_COMPLETO

    desconocidos = [p for p in pasos if p not in PASOS]
    if desconocidos:
        sys.exit(f"Paso(s) desconocido(s): {desconocidos}. Opciones: {list(PASOS)}")

    # Crea las carpetas de salida si no existen
    for carpeta in (os.path.join("data", "crudo"), os.path.join("data", "limpio"), "reportes"):
        os.makedirs(os.path.join(RAIZ, carpeta), exist_ok=True)

    for nombre in pasos:
        if not ejecutar_paso(nombre):
            sys.exit(f"Flujo detenido en el paso '{nombre}'.")

    print("\nFlujo terminado sin errores.")


if __name__ == "__main__":
    main()