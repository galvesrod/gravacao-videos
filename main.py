import math
import os
import logger as log
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from gravador import Gravador
from dotenv import load_dotenv

load_dotenv()

def obterListaDeAulas(page:webdriver):
    page.get('http://google.com')
    pass

def segundos_para_minutos(seg) -> str:
    """
    Converte segundos para formato MM:SS
    
    Args:
        segundos (float): Número de segundos
    
    Returns:
        str: Tempo formatado como MM:SS
    """
    segundos_int = round(seg)

    minutos = segundos_int // 60
    segundos = segundos_int % 60
    
    return f'{minutos:02d}:{segundos:02d}'

def main():
    gravador = Gravador()

    main_url = 'https://escola.formacao.dev/'
    trilha = 'fundamentos-dev/sala/iniciando-com-html-css'    

     # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service('chromedriver.exe')  # caminho do chromedriver
    page = webdriver.Chrome(service=service, options=chrome_options)
    page.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")    

    page.get(main_url)
    page.implicitly_wait(30)

    LOGIN_NAME = os.getenv('LOGIN_NAME')
    PWD = os.getenv('PWD')
    
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[1]/div/input').send_keys(LOGIN_NAME)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[2]/div/input').send_keys(PWD)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/button[1]').click()
    page.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[2]/div/div')

    page.get(f'{main_url}{trilha}')
    elementos = page.find_elements(By.CSS_SELECTOR, "div[data-lesson-id]")
    aulas = []
    for elemento in elementos:
        id = elemento.get_attribute('data-lesson-id')
        name = elemento.find_element(By.CSS_SELECTOR,'.text-sm.overflow-hidden').text
        if name == "":
            break
        aulas.append((name,id))  

    aula_index = 0
    qtde_aulas = len(aulas)
    iniciar_em = 0

    logs.info(f"Coletado lista de {qtde_aulas} para gravar")
    
    for nome, aula in aulas:
        if (aula_index < iniciar_em):
            aula_index += 1
            continue

        aula_index += 1
        url = f'{main_url}{trilha}?aula={aula}'
        page.get(url)
        try:            
            frame = page.find_element(By.XPATH,'//*[@id="player"]')
            page.switch_to.frame(frame)
            sleep(1)
            page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()   
            
            print('========================================================================')
            logs.info('========================================================================')

            sleep(0.5)
            page.execute_script("document.querySelector('video').pause()")
            sleep(0.5)
            page.execute_script("document.querySelector('video').currentTime = 0;")
            page.execute_script("document.querySelector('video').muted = false;")
            sleep(0.5)
            page.execute_script("document.querySelector('video').play()")
            sleep(0.5)
            fullDuration = page.execute_script("return document.querySelector('video').duration")        
            fullDuration = +fullDuration
            
            os.system('cls')
            gravador.Start(nome)
            logs.info(f'Gravação da aula: {nome} iniciada! | Aula {aula_index} de {qtde_aulas}')
            duration = 0
            print(f'Gravando aula: {nome} | Aula {aula_index} de {qtde_aulas}' )
            while duration < fullDuration:
                duration = +page.execute_script("return document.querySelector('video').currentTime;")
                print(f'\r{segundos_para_minutos(duration)} de { segundos_para_minutos(fullDuration)}', end='', flush=True)
                continue
            
            gravador.Stop()
            logs.info(f'Gravação da aula: {nome} Concluída!')
            page.switch_to.default_content()
            sleep(3)

        except Exception as e:
            print(f'Erro: {e}')
            logs.erro(f'Erro: {e}')
            continue
        
    
if __name__ == "__main__":
    logs = log.Logger()
    main()
