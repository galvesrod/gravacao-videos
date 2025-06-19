import math
import os
import traceback, sys
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
from datetime import datetime

from progresso import Progresso
from whatsappmsg import WhatsAppWeb

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

def configurarChrome(headless:bool=False) -> webdriver:
    #  Configurar Selenium
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        chrome_options.add_argument("--headless")  
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
        cap.release()       

        return duration_seconds
    except Exception as e:
        print(f"Erro ao processar o vídeo: {e}")
        return None

def main(page:webdriver):
    gravador = Gravador()
    page = page
    trilha = 'fundamentos-dev/sala/controlando-codigo'    

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
    iniciar_em = 52

    logs.info(f"Coletado lista de {qtde_aulas} para gravar")
    
    for nome, aula in aulas:
        # Avança no loop até aula desejada
        if (aula_index < iniciar_em):
            aula_index += 1
            continue

        while True:
            sucesso_gravacao = True
            # aula_index += 1
            url = f'{main_url}{trilha}?aula={aula}'
            page.get(url)
            caminho = rf'D:\Usuarios\gabrielalves\Documents\Formação Dev\Fundamentos\Trilha Inicial\4 - Controlando Codigo'
            

            try:            
                frame = page.find_element(By.XPATH,'//*[@id="player"]') # acessa o elemento player
                page.switch_to.frame(frame)
                sleep(1)
                page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()   
                
                print('========================================================================')
                logs.info('========================================================================')

                sleep(0.5)
                page.execute_script("document.querySelector('video').pause()")
                sleep(0.5)
                page.execute_script("document.querySelector('video').quality = 1080;")
                page.execute_script("document.querySelector('video').currentTime = 0;")
                page.execute_script("document.querySelector('video').muted = false;")
                sleep(0.5)
                page.execute_script("document.querySelector('video').play()")
                sleep(0.5)
                fullDuration = page.execute_script("return document.querySelector('video').duration")        
                fullDuration = +fullDuration
                
                os.system('cls')
                gravador.Start(nome,caminho)
                logs.info(f'Gravação da aula: {nome} iniciada! | Aula {aula_index+1} de {qtde_aulas}')
                print(f'Gravando aula: {nome} | Aula {aula_index+1} de {qtde_aulas}' )
                
                currentTime = 0
                prev_duration = 0
                err_ctrl = 0
                while currentTime < fullDuration:
                    currentTime = page.execute_script("return document.querySelector('video').currentTime;")
                    print(f'\r{segundos_para_minutos(currentTime)} de { segundos_para_minutos(fullDuration)}', end='', flush=True) #imprime o tempo

                    if prev_duration != currentTime: # se a duração atual for diferente da anterior, video em andamento
                        prev_duration = currentTime # atualiza a duração anterior
                        err_ctrl = 0 # limpa o contador de erro
                        
                    else: # quando o vídeo estiver travado
                        err_ctrl += 1 
                        if err_ctrl >= 15:                         
                            logs.erro(f"Erro linha 183: A Gravação da aula '{nome}' está travada, será feito um nova tentativa")
                            gravador.Stop(caminho,show_succ_msg=False)
                            sleep(2)
                            gravador.Remove(nome,caminho)
                            whatsapp.buscar_contato(contato_msg)
                            whatsapp.enviar_mensagem(f"Erro linha 183: A Gravação da aula '{nome}' está travada, será feito um nova tentativa")
                            sucesso_gravacao = False
                            break                

                else:
                    gravador.Stop(caminho)                    
                    arquivo = rf'{caminho}\{nome.replace('/','').replace('?','')}.mkv'                    
                    sleep(2)
                    tamanho_video = get_video_duration_cv2(arquivo)
                    logs.erro(f'tamanho_video: {tamanho_video}, {type(tamanho_video)}')
                    logs.erro(f'fullDuration: {fullDuration}, {type(fullDuration)}')
                    if tamanho_video -1 > fullDuration or tamanho_video +1 < fullDuration:
                        print(rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                        logs.erro(rf'Erro linha: 196 Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                        gravador.Remove(nome,caminho)
                        whatsapp.buscar_contato(contato_msg)
                        whatsapp.enviar_mensagem(rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')                        
                        sucesso_gravacao = False
                        # aula_index -= 1
                        continue
                    
                    if sucesso_gravacao:
                        aula_index += 1
                        logs.info(f'Gravação da aula: "{nome}" Concluída!')

                        whatsapp.buscar_contato(contato_msg)
                        whatsapp.enviar_mensagem(f'Gravação da aula: "{nome}" Concluída!')
                        
                        sleep(1)
                        break                   

                    page.switch_to.default_content()

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()

                tb_list = traceback.extract_tb(exc_traceback)
                last_frame = tb_list[-1]
                line_number = last_frame.lineno

                print(f'Erro: {e}')
                logs.erro(f'Erro Linha 208: {e}')
                logs.erro(f'Erro ocorreu na linha? {line_number}')
                logs.erro(f"Exception type: {exc_type.__name__}")
                logs.erro(f'Exception message: {exc_value}')
        
    
if __name__ == "__main__":
    main_url = 'https://escola.formacao.dev/'
    contato_msg = 'Gravação Curso'
    
    whatsapp = WhatsAppWeb()
    whatsapp.iniciar_whatsapp()

    logs = log.Logger()
    definir_volume_audio(100)    
    page = configurarChrome()
    page.get(main_url)

    logar(page)
    # # Progresso.run(page)
    main(page)
    sleep(2)
