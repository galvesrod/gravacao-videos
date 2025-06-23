import os
import traceback, sys
from configurarChrome import configurarChrome
from logar import logar
import logger as log

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from gravador import Gravador
from dotenv import load_dotenv
import cv2

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

def obterDuracaoDoArquivo(video_path):
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

def criar_diretorio(path:str):
    if not os.path.exists(path):
            os.makedirs(path)

def verificaHaVideo(page:webdriver, xpath:str, timeout=30)-> bool:
    try:
        WebDriverWait(driver=page, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        return False

def main(page:webdriver, gravar:bool=True, enviarMsg:bool=True):
    gravador = Gravador() if gravar else None
    page = page
    lista_aulas = progresso.obter_lista_gravacao()
    qtde_aulas = len(lista_aulas)
    aula_index = 0
    for aula in lista_aulas:
        formacao, trilha, curso, captiulo, aula, caminho, link, aula_id, indice, qtde_aulas_curso = aula        
        criar_diretorio(caminho)

        while True:
            sucesso_gravacao = True
            page.get(link)

            try:
                video = verificaHaVideo(page, '//*[@id="player"]',10)
                if not video:
                    elemento = page.find_element(By.CSS_SELECTOR,'div[editor-record-id]')
                    elemento = elemento.get_attribute('outerHTML')
                    file_name = f'{caminho}/{aula}.html'
                    with open(file_name, 'w',encoding='utf-8') as arquivo: 
                        arquivo.write(elemento)
                    
                    progresso.concluir_aula(aula_id)
                    break

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
                page.execute_script("document.querySelector('video').playbackRate = 1")
                page.execute_script("document.querySelector('video').currentTime = 0;")
                page.execute_script("document.querySelector('video').muted = false;")
                sleep(0.5)
                page.execute_script("document.querySelector('video').play()")
                sleep(0.5)
                fullDuration = page.execute_script("return document.querySelector('video').duration")        
                fullDuration = +fullDuration
                
                os.system('cls')
                if gravar:
                    gravador.Start(aula,caminho)
                msg = f'Gravação Iniciada: Formação: {formacao}, Trilha: {trilha}, Curso:{curso}, Aula: {aula} | Aula {aula_index+1} de {qtde_aulas_curso}/{qtde_aulas} - Previsão: {segundos_para_minutos(fullDuration)}'
                logs.info(msg)
                print(msg)

                if enviarMsg:
                    whatsapp.buscar_contato(contato_msg)
                    whatsapp.enviar_mensagem(msg)
                
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
                            logs.erro(f"Erro linha 183: A Gravação da aula '{aula}' está travada, será feito um nova tentativa")
                            if gravar:
                                gravador.Stop(caminho,show_succ_msg=False)
                                sleep(2)
                                gravador.Remove(aula,caminho)
                            if enviarMsg:
                                whatsapp.buscar_contato(contato_msg)
                                whatsapp.enviar_mensagem(f"Erro linha 183: A Gravação da aula '{aula}' está travada, será feito um nova tentativa")
                            sucesso_gravacao = False
                            break                

                else:
                    if gravar:
                        gravador.Stop(caminho)                    
                        arquivo = rf'{caminho}\{aula.replace('/','').replace('?','')}.mkv'                    
                        sleep(2)
                        tamanho_video = obterDuracaoDoArquivo(arquivo)

                        if tamanho_video -1 > fullDuration or tamanho_video +1 < fullDuration:
                            print(rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                            logs.erro(rf'Erro linha: 196 Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                            gravador.Remove(aula,caminho)
                            whatsapp.buscar_contato(contato_msg)
                            whatsapp.enviar_mensagem(rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')                        
                            sucesso_gravacao = False
                            continue
                    
                        if sucesso_gravacao:
                            aula_index += 1
                            curso_concluido = indice == qtde_aulas_curso
                            if curso_concluido:
                                logs.info(f'Gravação da aula: "{aula}" Concluída! Esta é a ultima aula deste curso')
                            else:
                                logs.info(f'Gravação da aula: "{aula}" Concluída!')
                            # Mudar gravado no banco de dados
                            progresso.concluir_aula(aula_id)

                            if enviarMsg:
                                whatsapp.buscar_contato(contato_msg)
                                if curso_concluido:
                                    whatsapp.enviar_mensagem(f'Gravação da aula: "{aula}" Concluída! Esta é a ultima aula deste curso')
                                else:
                                    whatsapp.enviar_mensagem(f'Gravação da aula: "{aula}" Concluída!')
                            

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
    contato_msg = 'Gravação Curso'
    enviarMsg = True
    gravar= True

    if enviarMsg:
        whatsapp = WhatsAppWeb()
        whatsapp.iniciar_whatsapp()

    logs = log.Logger()
    definir_volume_audio(100)    
    page = configurarChrome()
    page = logar(page)
    progresso = Progresso()
    
    # # Progresso.run(page)
    main(page, enviarMsg=enviarMsg, gravar=gravar)
    sleep(2)
