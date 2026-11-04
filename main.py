"""Punto de entrada del proyecto integrador.

Ejecuta el flujo de las cuatro tablas (prioridades, empresas, registros, retos),
siempre desde la raiz del proyecto y con rutas relativas.

Flujo por tabla (si el script no existe en src/, se omite ese paso):
    1. exportar_<tabla>.py   -> data/crudo/<tabla>_sucio.(csv|xlsx|json)
    2. limpiar_<tabla>.py    -> data/limpio/<tabla>_limpio.csv
    3. consultas_<tabla>.py  -> data/limpio/<tabla>_consulta_1..5.csv
       (retos no tiene limpiar: sus consultas y gráficas leen data/crudo/retos_sucio.csv)
    4. reporte_<tabla>.py    -> reportes/<tabla>_grafica_1..3.png

Uso (con el venv activo, parado en la carpeta del proyecto):
    python main.py                                  # todas las tablas, todos los pasos
    python main.py prioridades retos                # solo esas tablas
    python main.py --pasos limpiar consultas        # solo esos pasos, en todas las tablas
    python main.py empresas --pasos reporte         # una tabla y un paso

Tablas: prioridades, empresas, registros, retos
Pasos:  simular, exportar, limpiar, consultas, reporte
"""

import argparse
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = "src"

TABLAS = ["prioridades", "empresas", "registros", "retos"]
PASOS_COMPLETOS = ["exportar", "limpiar", "consultas", "reporte"]
PASOS_VALIDOS = ["simular"] + PASOS_COMPLETOS


def ruta_sucio(tabla):
    return os.path.join("data", "crudo", f"{tabla}_sucio.csv")


def ruta_limpio(tabla):
    return os.path.join("data", "limpio", f"{tabla}_limpio.csv")


def ruta_entrada(tabla):
    """Archivo que leen consultas y reporte.

    Si la tabla tiene limpiar_<tabla>.py usa el limpio; si no la tiene
    (caso de retos) usa el archivo crudo (_sucio.csv).
    """
    hay_limpiar = os.path.exists(os.path.join(RAIZ, SRC, f"limpiar_{tabla}.py"))
    return ruta_limpio(tabla) if hay_limpiar else ruta_sucio(tabla)


def argumentos_del_paso(paso, tabla):
    """Argumentos que recibe cada script (los de exportar y simular no reciben nada)."""
    if paso == "limpiar":
        return [ruta_sucio(tabla)]
    if paso in ("consultas", "reporte"):
        return [ruta_entrada(tabla)]
    return []


def correr(script, argumentos):
    """Corre un script de src/ desde la raiz y devuelve True si termina sin error."""
    comando = [sys.executable, os.path.join(SRC, script), *argumentos]
    print(f"\n$ python {os.path.join(SRC, script)} {' '.join(argumentos)}".rstrip())
    return subprocess.run(comando, cwd=RAIZ).returncode == 0


def ejecutar_paso(paso, tabla):
    """Devuelve 'ok', 'omitido' o 'error'."""
    script = f"{paso}_{tabla}.py"
    if not os.path.exists(os.path.join(RAIZ, SRC, script)):
        print(f"\n[OMITIDO] No existe {SRC}/{script}")
        return "omitido"

    argumentos = argumentos_del_paso(paso, tabla)

    # consultas y reporte leen un archivo de datos: debe existir
    if paso in ("consultas", "reporte") and not os.path.exists(os.path.join(RAIZ, ruta_entrada(tabla))):
        print(f"\n[ERROR] Falta {ruta_entrada(tabla)}. Ejecuta primero los pasos anteriores de {tabla}.")
        return "error"

    if correr(script, argumentos):
        return "ok"

    # Algunos scripts no reciben la ruta por linea de comandos: se reintenta sin argumentos
    if argumentos:
        print("[AVISO] Fallo con argumento; reintentando sin argumentos...")
        if correr(script, []):
            return "ok"
    return "error"


def main():
    parser = argparse.ArgumentParser(description="Ejecuta el proyecto integrador.")
    parser.add_argument("tablas", nargs="*", default=[], metavar="tabla",
                        help=f"Tablas a procesar (por defecto todas): {', '.join(TABLAS)}")
    parser.add_argument("--pasos", nargs="+", choices=PASOS_VALIDOS, default=PASOS_COMPLETOS,
                        help=f"Pasos a correr (por defecto: {', '.join(PASOS_COMPLETOS)})")
    args = parser.parse_args()

    invalidas = [t for t in args.tablas if t not in TABLAS]
    if invalidas:
        parser.error(f"tabla(s) desconocida(s): {invalidas}. Opciones: {TABLAS}")
    tablas = args.tablas or TABLAS

    for carpeta in (os.path.join("data", "crudo"), os.path.join("data", "limpio"), "reportes"):
        os.makedirs(os.path.join(RAIZ, carpeta), exist_ok=True)

    resumen = {}
    for tabla in tablas:
        print(f"\n{'#' * 60}\n# TABLA: {tabla.upper()}\n{'#' * 60}")
        for paso in args.pasos:
            estado = ejecutar_paso(paso, tabla)
            resumen[(tabla, paso)] = estado
            if estado == "error":
                print(f"[ERROR] '{paso}' de {tabla} fallo; se salta el resto de esa tabla.")
                break

    # --- Resumen final ---
    print(f"\n{'=' * 60}\nRESUMEN\n{'=' * 60}")
    for (tabla, paso), estado in resumen.items():
        print(f"{tabla:<12} {paso:<10} {estado.upper()}")

    if any(e == "error" for e in resumen.values()):
        sys.exit(1)
    print("\nProyecto ejecutado sin errores.")


if __name__ == "__main__":
    main()