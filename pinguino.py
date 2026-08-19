from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re


# =========================================================
# CONFIGURACIÓN
# =========================================================

URL = "https://www.pinguino.com.ar/"


# =========================================================
# CARPETA DE DEBUG
# =========================================================

# La carpeta queda dentro del proyecto:
#
# proyecto_esperancita/
# └── debug/
#
# Si no existe, se crea automáticamente.

CARPETA_DEBUG = (
    Path(__file__).resolve().parent / "debug"
)

CARPETA_DEBUG.mkdir(
    exist_ok=True
)


# =========================================================
# CREAR NAVEGADOR
# =========================================================

def crear_navegador():

    opciones = webdriver.ChromeOptions()

    opciones.add_argument(
        "--start-maximized"
    )

    navegador = webdriver.Chrome(
        options=opciones
    )

    return navegador


# =========================================================
# BUSCAR PRODUCTOS
# =========================================================

def buscar_productos(
    navegador,
    termino
):

    navegador.get(URL)

    wait = WebDriverWait(
        navegador,
        20
    )

    # -----------------------------------------------------
    # ESPERAR CONTENIDO DINÁMICO
    # -----------------------------------------------------

    time.sleep(3)

    # -----------------------------------------------------
    # BUSCAR EL CAMPO DE BÚSQUEDA
    # -----------------------------------------------------

    try:

        buscador = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[placeholder*='Buscar']"
                )
            )
        )

    except Exception:

        print("\n")
        print("=" * 60)
        print(
            "ERROR AL ENCONTRAR EL "
            "BUSCADOR DE PINGÜINO"
        )
        print("=" * 60)

        print(
            "URL actual:",
            navegador.current_url
        )

        print(
            "Título:",
            navegador.title
        )

        print(
            "Estado:",
            navegador.execute_script(
                "return document.readyState"
            )
        )

        print(
            "Cantidad de HTML:",
            len(navegador.page_source)
        )

        # -------------------------------------------------
        # CAPTURA DE ERROR
        # -------------------------------------------------

        navegador.save_screenshot(
            str(
                CARPETA_DEBUG /
                "debug_pinguino.png"
            )
        )

        raise

    # -----------------------------------------------------
    # LIMPIAR BUSCADOR
    # -----------------------------------------------------

    buscador.clear()

    buscador.click()

    buscador.send_keys(
        termino
    )

    buscador.send_keys(
        Keys.ENTER
    )

    # -----------------------------------------------------
    # ESPERAR RESULTADOS
    # -----------------------------------------------------

    try:

        WebDriverWait(
            navegador,
            20
        ).until(
            lambda driver:
            len(
                driver.page_source
            ) > 50000
        )

    except Exception:

        print(
            f"\n[ADVERTENCIA] "
            f"Pingüino no terminó de cargar "
            f"los productos para: {termino}"
        )

    # -----------------------------------------------------
    # OBTENER HTML
    # -----------------------------------------------------

    html = navegador.page_source

    # =====================================================
    # DEBUG: INSPECCIONAR ESTRUCTURA DE UN PRODUCTO
    # =====================================================

    if termino.lower() == "banana":

        print("\n")
        print("=" * 60)
        print("DEBUG ESTRUCTURA HTML - BANANA")
        print("=" * 60)

        soup_debug = BeautifulSoup(
            html,
            "html.parser"
        )

        encontrados = []

        for elemento in soup_debug.find_all(
            string=re.compile(
                r"banana ecuador",
                re.IGNORECASE
            )
        ):

            encontrados.append(
                elemento.parent
            )

        if not encontrados:

            print(
                "No se encontró 'banana ecuador' "
                "como texto dentro del HTML."
            )

        else:

            elemento = encontrados[0]

            print(
                "\nTEXTO ENCONTRADO:"
            )

            print(
                elemento.get_text(
                    " ",
                    strip=True
                )
            )

            print(
                "\n--- PADRES DEL ELEMENTO ---"
            )

            padre = elemento

            for nivel in range(1, 7):

                padre = padre.parent

                if padre is None:
                    break

                print(
                    f"\nPADRE NIVEL {nivel}"
                )

                print(
                    padre.prettify()[:5000]
                )

        print(
            "\n" + "=" * 60
        )

    print(
        "\nURL ACTUAL:"
    )

    print(
        navegador.current_url
    )

    print(
        "\nTÍTULO:"
    )

    print(
        navegador.title
    )

    print(
        "\nPRIMEROS 1000 CARACTERES:"
    )

    print(
        html[:1000]
    )

    # -----------------------------------------------------
    # CAPTURA DE DEBUG
    # -----------------------------------------------------

    navegador.save_screenshot(
        str(
            CARPETA_DEBUG /
            f"debug_{termino}.png"
        )
    )

    # -----------------------------------------------------
    # ANALIZAR HTML
    # -----------------------------------------------------

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    print(
        "\n===== HTML OBTENIDO DE PINGÜINO ====="
    )

    print(
        f"Cantidad de caracteres: "
        f"{len(html)}"
    )

    textos = soup.stripped_strings

    contador = 0

    for texto in textos:

        if termino.lower() in texto.lower():

            print(
                texto
            )

            contador += 1

            if contador >= 20:

                break

    return html


# =========================================================
# BUSCAR UNA LISTA COMPLETA
# =========================================================

def buscar_lista(
    terminos
):

    navegador = crear_navegador()

    resultados = {}

    try:

        for termino in terminos:

            print("\n")

            print(
                "=" * 60
            )

            print(
                f"BUSCANDO EN PINGÜINO: "
                f"{termino}"
            )

            print(
                "=" * 60
            )

            html = buscar_productos(
                navegador,
                termino
            )

            resultados[
                termino
            ] = html

        return resultados

    finally:

        navegador.quit()


# =========================================================
# PRUEBA DIRECTA
# =========================================================

if __name__ == "__main__":

    resultados = buscar_lista(
        [
            "leche",
            "azucar",
            "yerba"
        ]
    )