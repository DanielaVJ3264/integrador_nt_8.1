"""Punto de entrada del proyecto integrador.

Ejecuta el flujo de las cuatro tablas (prioridades, empresas, registros, retos),
siempre desde la raiz del proyecto y con rutas relativas.

Flujo por tabla (si el script no existe en src/, se omite ese paso):
    1. exportar_<tabla>.py   -> data/crudo/<tabla>_sucio.(csv|xlsx|json)
    2. limpiar_<tabla>.py    -> data/limpio/<tabla>_limpio.csv
    3. consultas_<tabla>.py  -> data/limpio/<tabla>_consulta_1..5.csv
    4. reporte_<tabla>.py    -> reportes/<tabla>_grafica_1..3.png
    5. mostrar               -> imprime la tabla limpia, las 5 consultas y las graficas
    6. imagenes              -> al final, abre en el navegador los PNG de reportes/ (una sola vez, todas las tablas)

Uso (con el venv activo, parado en la carpeta del proyecto):
    python main.py                                  # todas las tablas, todos los pasos
    python main.py prioridades retos                # solo esas tablas
    python main.py --pasos limpiar consultas        # solo esos pasos, en todas las tablas
    python main.py empresas --pasos reporte         # una tabla y un paso
    python main.py --pasos mostrar                  # solo mostrar las tablas (sin recalcular)
    python main.py --pasos imagenes                 # abrir las imagenes PNG de reportes/

Tablas: prioridades, empresas, registros, retos
Pasos:  simular, exportar, limpiar, consultas, reporte, mostrar, imagenes
"""

import argparse
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = "src"

TABLAS = ["prioridades", "empresas", "registros", "retos"]
PASOS_COMPLETOS = ["exportar", "limpiar", "consultas", "reporte", "mostrar", "imagenes"]
PASOS_VALIDOS = ["simular"] + PASOS_COMPLETOS


def ruta_sucio(tabla):
    return os.path.join("data", "crudo", f"{tabla}_sucio.csv")


def ruta_limpio(tabla):
    return os.path.join("data", "limpio", f"{tabla}_limpio.csv")


def ruta_entrada(tabla):
    """Archivo que leen consultas y reporte: siempre el limpio."""
    return ruta_limpio(tabla)


def argumentos_del_paso(paso, tabla):
    """Argumentos que recibe cada script (los de exportar y simular no reciben nada)."""
    if paso == "limpiar":
        return [ruta_sucio(tabla)]
    if paso in ("consultas", "reporte"):
        return [ruta_entrada(tabla)]
    return []


TIMEOUT_SEGUNDOS = 180  # si un script tarda mas que esto, se considera colgado


def correr(script, argumentos):
    """Corre un script de src/ desde la raiz y devuelve True si termina sin error.

    - MPLBACKEND=Agg: plt.show() no abre ventanas ni se queda esperando.
    - stdin cerrado: si un script llama a input(), falla de una vez en vez de colgarse.
    - timeout: si algo se cuelga, se corta y se indica cual script fue.
    """
    comando = [sys.executable, os.path.join(SRC, script), *argumentos]
    print(f"\n$ python {os.path.join(SRC, script)} {' '.join(argumentos)}".rstrip())
    entorno = {**os.environ, "MPLBACKEND": "Agg"}
    try:
        resultado = subprocess.run(
            comando, cwd=RAIZ, env=entorno, stdin=subprocess.DEVNULL, timeout=TIMEOUT_SEGUNDOS
        )
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {script} tardo mas de {TIMEOUT_SEGUNDOS} s y se corto "
              "(probablemente espera input() o una ventana de grafica).")
        return False
    except KeyboardInterrupt:
        sys.exit(f"\nInterrumpido por el usuario mientras corria {script}.")
    return resultado.returncode == 0


def mostrar_imagenes(tablas):
    """Abre en el navegador una galeria con los PNG de reportes/ (agrupados por tabla)."""
    import base64
    import html
    import tempfile
    import webbrowser

    carpeta = os.path.join(RAIZ, "reportes")
    secciones = []
    total = 0
    for tabla in tablas:
        pngs = sorted(f for f in os.listdir(carpeta) if f.startswith(f"{tabla}_") and f.lower().endswith(".png")) \
            if os.path.isdir(carpeta) else []
        if not pngs:
            print(f"[AVISO] No hay imagenes de {tabla} en reportes/")
            continue
        figuras = []
        for nombre in pngs:
            with open(os.path.join(carpeta, nombre), "rb") as f:
                datos = base64.b64encode(f.read()).decode("ascii")
            figuras.append(
                f'<figure><img src="data:image/png;base64,{datos}" alt="{html.escape(nombre)}" '
                f'onclick="this.classList.toggle(\'zoom\')"><figcaption>{html.escape(nombre)}</figcaption></figure>'
            )
            total += 1
        secciones.append(f"<h2>{html.escape(tabla.capitalize())}</h2><div class='fila'>{''.join(figuras)}</div>")

    if not total:
        print("[ERROR] No se encontro ningun PNG en reportes/. Corre primero el paso 'reporte'.")
        return "error"

    pagina = (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Reportes del proyecto</title>"
        "<style>body{font-family:sans-serif;margin:24px;background:#f5f5f5;color:#222}"
        "h1{margin-top:0}h2{border-bottom:2px solid #ccc;padding-bottom:4px;margin-top:32px}"
        ".fila{display:flex;flex-wrap:wrap;gap:16px}figure{margin:0;background:#fff;padding:8px;"
        "border-radius:8px;box-shadow:0 1px 4px #0003}img{width:420px;max-width:100%;cursor:zoom-in;display:block}"
        "img.zoom{width:min(95vw,1100px);cursor:zoom-out}figcaption{font-size:13px;color:#555;margin-top:4px}"
        "</style></head><body><h1>Graficas de reportes/</h1><p>Haz clic en una imagen para ampliarla.</p>"
        + "".join(secciones) + "</body></html>"
    )
    ruta = os.path.join(tempfile.gettempdir(), "galeria_reportes.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(pagina)
    print(f"\nGaleria con {total} imagenes: {ruta}")
    if not webbrowser.open("file:///" + ruta.replace("\\", "/")):
        print("No se pudo abrir el navegador; abre ese archivo a mano.")
    return "ok"


def mostrar_tabla(tabla):
    """Imprime la tabla limpia, sus 5 consultas y las graficas guardadas."""
    import pandas as pd  # se importa aqui: solo este paso lo necesita

    ancho = 70

    def leer(ruta):
        ruta_abs = os.path.join(RAIZ, ruta)
        return pd.read_csv(ruta_abs) if os.path.exists(ruta_abs) else None

    print(f"\n{'=' * ancho}\nTABLA {tabla.upper()}\n{'=' * ancho}")

    df = leer(ruta_limpio(tabla))
    if df is None:
        print(f"[ERROR] No existe {ruta_limpio(tabla)}")
        return "error"
    print(f"\n--- {tabla}_limpio.csv ({df.shape[0]} filas, {df.shape[1]} columnas) - primeras 10 filas ---")
    print(df.head(10).to_string(index=False))

    for n in range(1, 6):
        ruta = os.path.join("data", "limpio", f"{tabla}_consulta_{n}.csv")
        consulta = leer(ruta)
        if consulta is None:
            print(f"\n--- Consulta {n}: no existe {ruta} ---")
            continue
        print(f"\n--- Consulta {n} ({tabla}_consulta_{n}.csv) ---")
        print(consulta.head(15).to_string(index=False))
        if len(consulta) > 15:
            print(f"... ({len(consulta)} filas en total)")

    graficas = [os.path.join("reportes", f"{tabla}_grafica_{n}.png") for n in range(1, 4)]
    print("\n--- Graficas ---")
    for g in graficas:
        print(f"{'OK     ' if os.path.exists(os.path.join(RAIZ, g)) else 'FALTA  '}{g}")
    return "ok"


def ejecutar_paso(paso, tabla):
    """Devuelve 'ok', 'omitido' o 'error'."""
    if paso == "mostrar":
        return mostrar_tabla(tabla)

    script = f"{paso}_{tabla}.py"
    if not os.path.exists(os.path.join(RAIZ, SRC, script)):
        print(f"\n[OMITIDO] No existe {SRC}/{script}")
        return "omitido"

    argumentos = argumentos_del_paso(paso, tabla)

    # consultas y reporte leen un archivo de datos: debe existir
    if paso in ("consultas", "reporte") and not os.path.exists(os.path.join(RAIZ, ruta_entrada(tabla))):
        print(f"\n[ERROR] Falta {ruta_entrada(tabla)}.")
        if not os.path.exists(os.path.join(RAIZ, SRC, f"limpiar_{tabla}.py")):
            print(f"        Tampoco existe {SRC}/limpiar_{tabla}.py: falta el paso de limpieza de {tabla}.")
        else:
            print(f"        Ejecuta primero: python main.py {tabla} --pasos limpiar")
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

    pasos_por_tabla = [p for p in args.pasos if p != "imagenes"]

    resumen = {}
    for tabla in (tablas if pasos_por_tabla else []):
        print(f"\n{'#' * 60}\n# TABLA: {tabla.upper()}\n{'#' * 60}")
        for paso in pasos_por_tabla:
            estado = ejecutar_paso(paso, tabla)
            resumen[(tabla, paso)] = estado
            if estado == "error":
                print(f"[ERROR] '{paso}' de {tabla} fallo; se salta el resto de esa tabla.")
                break

    # La galeria se abre una sola vez, con todas las tablas, al final
    if "imagenes" in args.pasos:
        resumen[("todas", "imagenes")] = mostrar_imagenes(tablas)

    # --- Resumen final ---
    print(f"\n{'=' * 60}\nRESUMEN\n{'=' * 60}")
    for (tabla, paso), estado in resumen.items():
        print(f"{tabla:<12} {paso:<10} {estado.upper()}")

    if any(e == "error" for e in resumen.values()):
        sys.exit(1)
    print("\nProyecto ejecutado sin errores.")


if __name__ == "__main__":
    main()