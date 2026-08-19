from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


URL = "https://www.laanonima.com.ar/"


def crear_navegador():

    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--start-maximized")

    navegador = webdriver.Chrome(
        options=opciones
    )

    return navegador


def cerrar_overlay(navegador):

    try:

        overlay = navegador.find_element(
            By.CSS_SELECTOR,
            "div.fondo_negro"
        )

        if overlay.is_displayed():

            navegador.execute_script(
                "arguments[0].style.display = 'none';",
                overlay
            )

    except Exception:

        pass


def buscar_productos(navegador, termino):

    navegador.get(URL)

    wait = WebDriverWait(
        navegador,
        15
    )

    # Esperamos que aparezca el buscador
    buscador = wait.until(
        EC.presence_of_element_located(
            (By.ID, "inpBuscador")
        )
    )

    # Intentamos cerrar cualquier ventana/capa
    cerrar_overlay(
        navegador
    )

    # Hacemos visible el buscador
    navegador.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        buscador
    )

    # Click mediante JavaScript
    navegador.execute_script(
        "arguments[0].click();",
        buscador
    )

    buscador.send_keys(
        termino
    )

    buscador.send_keys(
        Keys.ENTER
    )

    # Esperamos que cambie el contenido
    wait.until(
        lambda driver:
        termino.lower()
        in driver.page_source.lower()
    )

    html = navegador.page_source

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    print(
        "\n===== HTML OBTENIDO DE LA ANÓNIMA ====="
    )

    print(
        f"Cantidad de caracteres: {len(html)}"
    )

    textos = soup.stripped_strings

    contador = 0

    for texto in textos:

        if termino.lower() in texto.lower():

            print(texto)

            contador += 1

            if contador >= 20:
                break

    return html


def buscar_lista(terminos):

    navegador = crear_navegador()

    resultados = {}

    try:

        for termino in terminos:

            print("\n")
            print("=" * 60)
            print(
                f"BUSCANDO EN LA ANÓNIMA: {termino}"
            )
            print("=" * 60)

            html = buscar_productos(
                navegador,
                termino
            )

            resultados[termino] = html

        return resultados

    finally:

        navegador.quit()


if __name__ == "__main__":

    resultados = buscar_lista(
        [
            "leche",
            "azucar",
            "yerba"
        ]
    )