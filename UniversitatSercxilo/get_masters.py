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

# Cargar el CSV con las universidades
universities_df = pd.read_csv("universidades_mexico_limpio.csv")

# Palabras clave para identificar la sección de oferta académica
OFFER_SECTION_KEYWORDS = ["oferta académica", "oferta educativa", "programas", "estudios"]

# Palabras clave para identificar maestrías y especialidades
MASTERS_SPECIALIZATION_KEYWORDS = ["maestría", "especialización", "posgrado", "doctorado"]

# Lista para registrar universidades sin maestrías ni especializaciones
no_masters_universities = []

# Función para extraer los programas de Maestría y Especialización
def get_masters_and_specializations(university_name, university_url):
    logging.info(f"Accediendo a la universidad: {university_name} - {university_url}")
    
    try:
        driver.get(university_url)
        time.sleep(3)  # Esperar a que cargue la página

        # Buscar enlaces en el menú de navegación
        menu_links = driver.find_elements(By.TAG_NAME, "a")

        offer_url = None
        for link in menu_links:
            link_text = link.text.strip().lower()
            if any(keyword in link_text for keyword in OFFER_SECTION_KEYWORDS):
                offer_url = link.get_attribute("href")
                logging.info(f"Se encontró sección de oferta académica en {university_name}: {offer_url}")
                break

        if not offer_url:
            logging.warning(f"No se encontró una sección de oferta académica en {university_name}")
            no_masters_universities.append({"university_name": university_name, "university_url": university_url})
            return []

        # Entrar a la página de oferta académica
        driver.get(offer_url)
        time.sleep(3)

        # Buscar los programas de Maestría y Especialización
        program_links = driver.find_elements(By.TAG_NAME, "a")
        masters_programs = []

        for link in program_links:
            program_name = link.text.strip()
            program_url = link.get_attribute("href")

            if program_url and any(keyword in program_name.lower() for keyword in MASTERS_SPECIALIZATION_KEYWORDS):
                masters_programs.append({
                    "university_name": university_name,
                    "university_url": university_url,
                    "program_name": program_name,
                    "program_url": program_url
                })
                logging.info(f"Programa encontrado: {program_name} - {program_url}")

        if not masters_programs:
            logging.warning(f"No se encontraron maestrías ni especializaciones en {university_name}")
            no_masters_universities.append({"university_name": university_name, "university_url": university_url})

        return masters_programs

    except Exception as e:
        logging.error(f"Error al procesar {university_name}: {e}")
        no_masters_universities.append({"university_name": university_name, "university_url": university_url})
        return []

# Función principal
def main():
    logging.info("Iniciando extracción de programas de Maestría y Especialización...")

    all_masters_programs = []

    for index, row in universities_df.iterrows():
        university_name = row["name"]
        university_url = row["url"]
        masters_programs = get_masters_and_specializations(university_name, university_url)
        all_masters_programs.extend(masters_programs)

    # Guardar los resultados en un CSV
    if all_masters_programs:
        df = pd.DataFrame(all_masters_programs)
        df.to_csv("maestrias_especializaciones_mexico.csv", index=False)
        logging.info(f"Proceso completado. Se encontraron {len(all_masters_programs)} programas. Guardado en 'maestrias_especializaciones_mexico.csv'.")
    else:
        logging.warning("No se encontraron programas de Maestría ni Especialización en ninguna universidad.")

    # Guardar el reporte de universidades sin programas de posgrado
    if no_masters_universities:
        df_no_masters = pd.DataFrame(no_masters_universities)
        df_no_masters.to_csv("universidades_sin_maestrias.csv", index=False)
        logging.info(f"Se encontraron {len(no_masters_universities)} universidades sin programas de Maestría ni Especialización. Guardado en 'universidades_sin_maestrias.csv'.")

    # Cerrar el driver al finalizar
    driver.quit()

if __name__ == "__main__":
    main()
