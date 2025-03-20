import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configuración del navegador
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Detección automática de ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL del sitio principal
url_base = "https://educacionsuperior.sep.gob.mx/"

# Lista de palabras clave que indican que no es una universidad
EXCLUDE_KEYWORDS = [
    "gob.mx", "educacionsuperior.sep.gob.mx", "tramites", "programas",
    "estructura", "aviso-de-privacidad", "historial", "direccion-general",
    "Normatividad", "conócenos", "acciones", "sep", "inicio", "búsqueda",
    "direcciones", "instituciones", "prensa"
]

EXCLUDE_NAMES = [
    "Inicio", "Trámites", "Gobierno", "Búsqueda", "Prensa", "Conócenos",
    "Direcciones", "Normatividad", "Instituciones", "Acciones y Programas",
    "Aviso de privacidad", "SEP"
]

# Función para extraer los enlaces de las categorías que comienzan con "/Instituciones-SES/"
def get_categories():
    logging.info("Accediendo a la página principal...")
    driver.get(url_base)
    time.sleep(5)  # Esperar a que cargue la página principal

    categories = []
    try:
        # Buscar los enlaces de categorías dentro de <div class="link">
        category_links = driver.find_elements(By.CSS_SELECTOR, "div.link a.btn-primary")

        for link in category_links:
            category_url = link.get_attribute("href")
            if category_url and "/Instituciones-SES/" in category_url:
                category_name = category_url.split("/")[-1]  # Obtener solo el nombre de la categoría
                categories.append({"name": category_name, "url": category_url})
        
        logging.info(f"Se encontraron {len(categories)} categorías.")
    except Exception as e:
        logging.error(f"Error al extraer categorías: {e}")

    return categories

# Función para extraer universidades de una categoría
def get_universities_from_category(category_name, category_url):
    logging.info(f"Accediendo a la categoría '{category_name}': {category_url}")
    driver.get(category_url)
    time.sleep(3)  # Esperar a que cargue la página de la categoría

    universities = []
    try:
        # Extraer los enlaces de universidades
        university_links = driver.find_elements(By.CSS_SELECTOR, "li a[href]")
        
        for link in university_links:
            university_name = link.text.strip()
            university_url = link.get_attribute("href")

            # Filtrar enlaces que no sean universidades reales
            if university_url and university_name:
                if not any(keyword in university_url.lower() for keyword in EXCLUDE_KEYWORDS) and university_name not in EXCLUDE_NAMES:
                    universities.append({"category": category_name, "name": university_name, "url": university_url})
                    logging.debug(f"Universidad encontrada: {university_name} - {university_url}")
                else:
                    logging.debug(f"Descartado: {university_name} - {university_url}")

        logging.info(f"Se encontraron {len(universities)} universidades en la categoría '{category_name}'.")
    except Exception as e:
        logging.error(f"Error al procesar la categoría '{category_name}': {e}")

    return universities

# Función principal
def main():
    logging.info("Iniciando el proceso de extracción de URLs de universidades...")

    categories = get_categories()
    all_universities = []

    for category in categories:
        universities = get_universities_from_category(category["name"], category["url"])
        all_universities.extend(universities)

    # Guardar los resultados en un archivo CSV
    if all_universities:
        df = pd.DataFrame(all_universities)
        df.to_csv("universidades_mexico_limpio.csv", index=False)
        logging.info(f"Proceso completado. Se encontraron {len(all_universities)} universidades. Los resultados se han guardado en 'universidades_mexico_limpio.csv'.")
    else:
        logging.warning("No se encontraron universidades.")

    # Cerrar el driver al finalizar
    driver.quit()

if __name__ == "__main__":
    main()



