import math
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from gravador import Gravador
from dotenv import load_dotenv

load_dotenv()


def main():
    gravador = Gravador()
    
    # Configuração da conexão (padrão é localhost:4455)
    aulas = [
        ('1-Introdução', f'https://escola.formacao.dev/fundamentos-dev/sala/iniciando-com-html-css?aula=50430e86-8c56-4295-8157-8f28e5da081f' ),
        ('2-Pré-requisitos', f'https://escola.formacao.dev/fundamentos-dev/sala/iniciando-com-html-css?aula=6d327106-3656-4444-8502-11bf1bd2944c' ),
        ('3-Configuração Inicial', f'https://escola.formacao.dev/fundamentos-dev/sala/iniciando-com-html-css?aula=be1fe251-575d-4bdc-9139-cec0fb4c511b' ),
    ]

     # Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # Remove a propriedade webdriver


    service = Service('chromedriver.exe')  # caminho do chromedriver
    page = webdriver.Chrome(service=service, options=chrome_options)
    page.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    url = 'https://escola.formacao.dev/'

    page.get(url)
    page.implicitly_wait(30)

    USERNAME = os.getenv('USERNAME')
    PWD = os.getenv('PWD')

    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[1]/div/input').send_keys(USERNAME)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[2]/div/input').send_keys(PWD)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/button[1]').click()
    page.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[2]/div/div')

    for nome, url in aulas:
        page.get(url)
        frame = page.find_element(By.XPATH,'//*[@id="player"]')
        page.switch_to.frame(frame)
        sleep(1)
        page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()   
        
        print('========================================================================') 

        sleep(0.5)
        page.execute_script("document.querySelector('video').pause()")
        sleep(0.5)
        page.execute_script("document.querySelector('video').currentTime = 0;")
        sleep(0.5)
        page.execute_script("document.querySelector('video').play()")

        duration = page.execute_script("return document.querySelector('video').duration")        
        duration = math.ceil(+duration)
        
        gravador.Start(nome)
        sleep(duration)
        gravador.Stop()
        page.switch_to.default_content()
        
    
if __name__ == "__main__":
    # main()
    ...
