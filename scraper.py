import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.common.exceptions import TimeoutException

class RuesScraperSelenium:
    def __init__(self):
        self.chrome_options = Options()
        # self.chrome_options.add_argument('--headless')  # Ejecutar en segundo plano
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')  # Deshabilitar aceleración GPU
        self.chrome_options.add_argument('--disable-extensions')  # Deshabilitar extensiones
        
    def buscar_empresa(self, nombre_empresa):
        driver = None
        try:
            print(f"1. Iniciando búsqueda para: {nombre_empresa}")
            
            driver = webdriver.Chrome(options=self.chrome_options)
            wait = WebDriverWait(driver, 10)  # Aumentado el tiempo de espera a 20 segundos
            
            print("2. Accediendo a la página principal...")
            driver.get("https://www.rues.org.co")
            
            # Esperar a que la página cargue completamente
            time.sleep(5)  # Dar tiempo extra para la carga inicial
            
            print("3. Buscando campo de búsqueda...")
            try:
                # Intentar primero con CSS Selector
                search_box = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.form-control.w-100")
                ))
            except TimeoutException:
                # Si falla, intentar con XPath
                search_box = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='text']")
                ))
            
            search_box.clear()
            time.sleep(1)  # Pequeña pausa después de limpiar
            search_box.send_keys(nombre_empresa)
            time.sleep(1)  # Pequeña pausa después de escribir
            
            print("4. Realizando búsqueda...")
            try:
                search_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.d-none.d-sm-block.btn.btn-primary.input-group-append.btn-busqueda.busqueda__button--xs")
                ))
                search_button.click()
            except Exception as e:
                print(f"Error al hacer clic en el botón de búsqueda: {str(e)}")
                # Intento alternativo usando JavaScript
                driver.execute_script("arguments[0].click();", search_button)
            
            time.sleep(5)  # Aumentado el tiempo de espera después de la búsqueda
            
            print("5. Buscando enlace 'Ver información'...")
            ver_info = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Ver información')]")
            ))
            ver_info.click()
            
            time.sleep(3)
            
            print("6. Accediendo a actividad económica...")
            actividad_tab = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Actividad')]")
            ))
            actividad_tab.click()
            
            time.sleep(3)
            
            print("7. Extrayendo códigos de actividad...")
            codigos = []
            
            # Buscar todos los divs que contienen actividades económicas
            actividades_divs = driver.find_elements(By.CSS_SELECTOR, "#detail-tabs-tabpane-pestana_economica > div")
            
            for div in actividades_divs:
                try:
                    # Encontrar todos los párrafos dentro del div
                    parrafos = div.find_elements(By.TAG_NAME, "p")
                    if len(parrafos) >= 2:
                        codigo = parrafos[0].text.strip()
                        descripcion = parrafos[1].text.strip()
                        
                        if codigo and descripcion:
                            codigos.append({
                                'codigo': codigo,
                                'descripcion': descripcion
                            })
                except Exception as e:
                    print(f"Error al procesar actividad: {str(e)}")
                    continue
            
            if driver:
                driver.quit()
            
            return {
                'nombre_empresa': nombre_empresa,
                'codigos_actividad': codigos,
                'estado': 'éxito'
            }
            
        except Exception as e:
            print(f"\nError durante el proceso: {str(e)}")
            if driver:
                driver.quit()
            return {
                'nombre_empresa': nombre_empresa,
                'codigos_actividad': [],
                'estado': f'error: {str(e)}'
            }

def main():
    scraper = RuesScraperSelenium()
    empresas = ["sura", "proteccion", "exito", "carulla"]
    
    resultados = []
    
    for empresa in empresas:
        print(f"\nIniciando búsqueda para {empresa}")
        resultado = scraper.buscar_empresa(empresa)
        
        if resultado['codigos_actividad']:
            for actividad in resultado['codigos_actividad']:
                resultados.append({
                    'nombre_empresa': resultado['nombre_empresa'],
                    'codigo_actividad': actividad['codigo'],
                    'descripcion_actividad': actividad['descripcion'],
                    'estado': resultado['estado']
                })
        else:
            resultados.append({
                'nombre_empresa': resultado['nombre_empresa'],
                'codigo_actividad': 'No encontrado',
                'descripcion_actividad': 'No encontrado',
                'estado': resultado['estado']
            })
    
    df = pd.DataFrame(resultados)
    df.to_csv('actividades_economicas_rues.csv', index=False, encoding='utf-8-sig')
    print("\nResultados guardados en 'actividades_economicas_rues.csv'")
    print("\nResultados encontrados:")
    print(df)

if __name__ == "__main__":
    main()

