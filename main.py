import math
import os
import logger as log

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from gravador import Gravador
from dotenv import load_dotenv
import cv2

from progresso import Progresso

load_dotenv()

def definir_volume_audio(percentual):
    """
    Define o volume para um percentual específico
    percentual: valor entre 0 e 100
    """
    try:
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Converte percentual para escala 0-1
        volume_normalizado = max(0.0, min(1.0, percentual / 100.0))
        
        # Obtém range do volume
        volume_min, volume_max, _ = volume.GetVolumeRange()
        
        # Calcula volume na escala do sistema
        volume_sistema = volume_min + (volume_normalizado * (volume_max - volume_min))
        
        # Define o volume
        volume.SetMasterVolumeLevel(volume_sistema, None)
        
        print(f"Volume definido para {percentual}%")
        return True
        
    except Exception as e:
        print(f"Erro ao definir volume: {e}")
        return False

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

def configurarChrome() -> webdriver:
    #  Configurar Selenium
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
    page.implicitly_wait(30)
    return page

def logar(page:webdriver):
    LOGIN_NAME = os.getenv('LOGIN_NAME')
    PWD = os.getenv('PWD')
    
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[1]/div/input').send_keys(LOGIN_NAME)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/div[2]/div/input').send_keys(PWD)
    page.find_element(By.XPATH,'//*[@id="__next"]/section/div[2]/button[1]').click()
    page.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[2]/div/div')

def get_video_duration_cv2(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        duration_seconds = frame_count / fps
        duration_minutes = duration_seconds / 60
        
        cap.release()
        
        print(f"Duração: {duration_seconds:.2f} segundos")
        print(f"Duração: {duration_minutes:.2f} minutos")
        return duration_seconds
    except Exception as e:
        print(f"Erro ao processar o vídeo: {e}")
        return None


def main(page:webdriver):
    gravador = Gravador()
    page = page
    trilha = 'fundamentos-dev/sala/iniciando-com-programacao'    

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

        while True:
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
                print(f'Gravando aula: {nome} | Aula {aula_index} de {qtde_aulas}' )
                
                duration = 0
                prev_duration = 0
                err_ctrl = 0
                while duration < fullDuration:
                    duration = page.execute_script("return document.querySelector('video').currentTime;")
                    print(f'\r{segundos_para_minutos(duration)} de { segundos_para_minutos(fullDuration)}', end='', flush=True)

                    if prev_duration != duration:
                        prev_duration = duration
                        err_ctrl = 0
                        
                    else:
                        err_ctrl += 1
                        
                        if err_ctrl >= 15:
                            # implementar uma correção                            
                            logs.erro(f"A Gravação da aula {aula} está travada, será feito um nova tentativa")
                            gravador.Stop()
                            sleep(2)
                            gravador.Remove(nome)
                            break                
                    continue
                else:
                    gravador.Stop()
                    # caminho = rf'D:\Usuarios\gabrielalves\Documents\Formação Dev\Fundamentos\Trilha Inicial\Iniciando com Programacao'
                    # caminho = rf'{caminho}\{nome}.mkv'
                    # tamanho_video = get_video_duration_cv2(caminho)
                    # print(rf'tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                    # 1/0
                    logs.info(f'Gravação da aula: {nome} Concluída!')
                    page.switch_to.default_content()
                    sleep(3)
                    break

            except Exception as e:
                print(f'Erro: {e}')
                logs.erro(f'Erro: {e}')
                continue
        
    
if __name__ == "__main__":
    main_url = 'https://escola.formacao.dev/'    

    logs = log.Logger()
    definir_volume_audio(100)    
    page = configurarChrome()
    page.get(main_url)
    logar(page)
    # Progresso.run(page)
    main(page)
