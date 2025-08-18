import os
import traceback, sys

from WAHAClient import WAHAClient
from utils import fazerLogin
from utils import ConfigurarChrome
from utils.formataNome import formataNome
from utils.lock import criar_lock, remover_lock
from utils.progresso import Progresso
import utils.logger as log
import cv2
import atexit
import signal
# from sys import platform
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from gravador import Gravador
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()

cleanup_executado = False

def cleanup():
    global cleanup_executado
    if cleanup_executado:
        return
    cleanup_executado = True
    print("Executando limpeza antes de sair...")
    status = gravador.Status() if gravador else None
    if status == 'Gravando':        
        caminho = gravador.Obter_Caminho_Gravacao_atual()
        nome = gravador.Obter_Nome_Gravacao_atual()        
        gravador.Stop(caminho,show_succ_msg=False)
        sleep(2)
        # gravador.Remove(nome,caminho)
    logs.info('='*50)
    for aula_assistida in aulas_assistidas:
        logs.info(aula_assistida)

def abrir_obs():
    import psutil
    import subprocess
    for processo in psutil.process_iter(['name', 'exe']):
        try:
            if processo.info['name'] and 'obs' in processo.info['name'].lower():
                return
            if processo.info['exe'] and 'obs' in processo.info['exe'].lower():
                return
        except(psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    try:
        obs_path = rf"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
        diretorio_trabalho = rf"C:\Program Files\obs-studio\bin\64bit"
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 2

        if os.path.exists(obs_path):
            subprocess.Popen([obs_path,"--disable-shutdown-check"], cwd=diretorio_trabalho, startupinfo=startupinfo )
        else:
            subprocess.Popen(['obs64',"--disable-shutdown-check"])
    except:
        print("Erro ao abrir o OBS")

def interromperGravacao():    
    status = gravador.Status() if gravador else None
    if status == 'Gravando':        
        caminho = gravador.Obter_Caminho_Gravacao_atual()
        nome = gravador.Obter_Nome_Gravacao_atual()        
        gravador.Stop(caminho,show_succ_msg=False)
        sleep(2)
        gravador.Remove(nome,caminho)
        logs.info('='*50)
        logs.info(f'Aula {nome} excluída')
# Registra função para saída normal

# Captura sinais de interrupção (Ctrl+C, etc.)
def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)

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

def obter_se_aula_assistido(page:webdriver, id:str) -> bool:
    page = page
    element = page.find_element(By.CSS_SELECTOR, f'div[data-lesson-id="{id}"]')
    element = element.find_element(By.CSS_SELECTOR,'.flex.justify-center.items-center.rounded-full')
    classes = element.get_attribute('class')
    return True if "bg-green-500" in classes else False

def main(page:webdriver, gravar:bool=True, enviarMsg:bool=True):
    page = page
    lista_aulas = progresso.obter_lista_gravacao()
    qtde_aulas = len(lista_aulas)
    aula_index = 0
    tentativas = 0
    for aula in lista_aulas:
        formacao, trilha, curso, captiulo, aula, link, aula_id, indice, qtde_aulas_curso, cd_aula, win_path = aula
        print(aula)
        caminho = formataNome(win_path, 'DIR')
        # if platform.system() == 'Windows':
        #     caminho = win_path
        # else:
        #     caminho = linux_path
        criar_diretorio(caminho)
        while True:
            if tentativas >= 3:
                logs.erro('Foram feitas três tentativas sem sucesso de gravação. O programa será reiniciado')
                raise Exception ('Foram feitas três tentativas sem sucesso de gravação. O programa será reiniciado')
            sucesso_gravacao = True
            page.get(link)
            # assistido = obter_se_aula_assistido(page, cd_aula)
            assistido = True

            try:
                video = verificaHaVideo(page, '//*[@id="player"]',10)
                if not video:
                    elemento = page.find_element(By.CSS_SELECTOR,'div[last-selected-record]') #last-selected-record
                    elemento = elemento.get_attribute('outerHTML')
                    file_name = f'{caminho}/{aula}.html'
                    with open(file_name, 'w',encoding='utf-8') as arquivo: 
                        arquivo.write(elemento)
                    
                    progresso.concluir_aula(aula_id)
                    if enviarMsg:
                        client.send_text_message(GROUP_MESSAGE, f'Gravação da aula: "{aula}" Concluída!')
                    break

                frame = page.find_element(By.XPATH,'//*[@id="player"]') # acessa o elemento player

                page.switch_to.frame(frame)
                sleep(0.5)
                page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()   # Clica em maximizar                
                
                print('========================================================================')
                logs.info('========================================================================')

                sleep(0.5)
                page.execute_script("document.querySelector('video').pause()") # pausa o video
                sleep(0.5)
                page.execute_script("document.querySelector('video').quality = 1080;") # Garante qualidade de 1080p
                page.execute_script("document.querySelector('video').playbackRate = 1") # Garante que video será rodado em velocidade normal
                page.execute_script("document.querySelector('video').muted = false;") # Garante que video não está mudo
                sleep(0.5)
                page.execute_script("document.querySelector('video').currentTime = 0;") # Garante que video está no começo                
                currentTime = page.execute_script("return document.querySelector('video').currentTime;") # Atualiza o tempo atual do video
                while currentTime != 0: 
                    logs.erro("Tentando iniciar o video do zero")
                    page.execute_script("document.querySelector('video').currentTime = 0;") # Garante que video está no começo
                    currentTime = page.execute_script("return document.querySelector('video').currentTime;") # Atualiza o tempo atual do video                    


                fullDuration = page.execute_script("return document.querySelector('video').duration") # obtem a duaração do video
                fullDuration = +fullDuration

                
                if gravar:
                    status = gravador.Start(aula,caminho) # inicia a gravação
                    if not status:
                        raise Exception("Gravador nao conseguiu iniciar o vídeo")
                
                msg = f'Gravação Iniciada: Formação: {formacao}, Trilha: {trilha}, Curso:{curso}, Aula: {aula} | Aula {indice} de {qtde_aulas_curso}/{qtde_aulas} - Previsão: {segundos_para_minutos(fullDuration)}'                
                page.execute_script("document.querySelector('video').play()") # Inicia o vídeo
                logs.info(msg)
                os.system('cls')
                print(msg)

                if enviarMsg:
                    client.send_text_message(GROUP_MESSAGE ,msg)
                
                currentTime = 0
                prev_duration = 0
                err_ctrl = 0
                currentUrl = newUrl = page.current_url

                while True:
                    newUrl = page.current_url # Atualiza a pagina atual
                    if currentUrl != newUrl:
                        logs.erro('Pagina atualizada')
                        break

                    if currentTime + 0.5 >= fullDuration:
                        break

                    currentTime = page.execute_script("return document.querySelector('video').currentTime;") # Atualiza o tempo atual do video
                    print(f'\r{segundos_para_minutos(currentTime)} de { segundos_para_minutos(fullDuration)}', end='', flush=True) #imprime o tempo

                    if prev_duration != currentTime: # se a duração atual for diferente da anterior, video em andamento
                        prev_duration = currentTime # atualiza a duração anterior
                        err_ctrl = 0 # limpa o contador de erro
                        continue

                    if currentTime == 0 and prev_duration == 0:
                        sucesso_gravacao = False
                        break

                    # identifica video travado
                    err_ctrl += 1 
                    if err_ctrl >= 15:
                        logs.erro(f"Erro linha 257: A Gravação da aula '{aula}' está travada, será feito um nova tentativa - currentTime:{currentTime} | prev_duration: {prev_duration}")
                        
                        if gravar:
                            status = gravador.Stop(caminho,show_succ_msg=False)
                            sleep(2)
                            gravador.Remove(aula,caminho)
                        
                        sleep(0.3)

                # Fim do vídeo
                page.execute_script("document.querySelector('video').pause()") # parar o video
                if not sucesso_gravacao:
                    tentativas += 1
                    logs.erro(f'Houve um erro na gravação do vídeo.')
                    continue

                if gravar:
                    status = gravador.Stop(caminho) # Parar o gravador
                    if not status:
                        sucesso_gravacao = False
                        tentativas += 1
                        raise Exception("Gravador não conseguiu finalizar o vídeo.")
                    aula = formataNome(aula) # formata o nome da aula
                                    
                    arquivo = rf'{caminho}\{aula}.mkv'                    
                    sleep(2)

                    tamanho_video = obterDuracaoDoArquivo(arquivo)
                    if tamanho_video -2 > fullDuration or tamanho_video +2 < fullDuration:
                        print(rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                        logs.erro(rf'Erro linha: 288 Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}')
                        gravador.Remove(aula,caminho)
                        sucesso_gravacao = False
                        if enviarMsg:
                            msg = rf'Aconteceu algum erro. A gravação do arquivo está difente da duração prevista: Tamanho da aula web: {fullDuration}, tamanho do arquivo: {tamanho_video}'
                            client.send_text_message(GROUP_MESSAGE, msg)
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
                        
                        aulas_assistidas.append(
                            f'Aula: {formacao} > {trilha} > {curso} > {aula} foi gravada. Aula {'JÁ' if assistido else "NÃO"} assistida!'
                        )
                        if enviarMsg:
                            if curso_concluido:
                                client.send_text_message(GROUP_MESSAGE, f'Gravação da aula: "{aula}" Concluída! Esta é a ultima aula deste curso')
                            else:
                                client.send_text_message(GROUP_MESSAGE, f'Gravação da aula: "{aula}" Concluída!')
                        
                        try:
                            # Minimiza a tela
                            page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()
                        except:
                            pass
                        
                        page.switch_to.default_content()                     
                        sleep(0.5)
                        tentativas = 0
                        break
                else:
                    try:
                        # Minimiza a tela
                        page.find_element(By.XPATH,'//*[@id="video-container"]/div[1]/div[3]/button[5]').click()
                    except:
                        pass           
                    page.switch_to.default_content()                     
                    sleep(0.5)
                    tentativas = 0
                    break

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_list = traceback.extract_tb(exc_traceback)
                last_frame = tb_list[-1]
                line_number = last_frame.lineno
                logs.info('='*50)
                logs.erro('Exceção lançada. O Código será reiniciado!')
                logs.erro(f'Erro ocorreu na linha: {line_number}')
                logs.erro(f"Exception type: {exc_type.__name__}")
                logs.erro(f'Exception message: {exc_value}')
                logs.info('='*50)
                interromperGravacao()
                continue
        
        # # Desmarcar video como não assistido
        # if not assistido:
        #     element = page.find_element(By.CSS_SELECTOR, f'div[data-lesson-id="{cd_aula}"]')
        #     element = element.find_element(By.CSS_SELECTOR,'.flex.justify-center.items-center.rounded-full')
        #     # element.click() #ver problema
        
    
if __name__ == "__main__":
    sleep(2)
    while True:
        if not criar_lock():
            sys.exit(1)

        WAHA_URL = "http://localhost:3000"  # URL DO WAHA
        SESSION_NAME = "default"
        GROUP_MESSAGE = "120363402733138387@g.us"  # Número do destinatário (sem @c.us)

        # Criar cliente
        client = WAHAClient(WAHA_URL, SESSION_NAME)        
        enviarMsg = client.wait_for_ready(15)      

        logs = log.Logger()
        logs.info(f'\n{'='*50}Código inciado{'='*50}')
        if enviarMsg:
            logs.info("Será realizado comunicação via whatsapp")
        else:
            logs.info("Não será feito comunicação via whatsapp")


        load_dotenv()
        atexit.register(cleanup)
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Terminação    
        aulas_assistidas = []
        try:
            abrir_obs()
            gravar = os.getenv('GRAVAR')
            gravar= True if gravar.upper() == 'S' else False
            if gravar:
                gravador = Gravador() if gravar else None
                if gravador.cl is None:
                    continue

            definir_volume_audio(100) 

            page = ConfigurarChrome.configurarChrome(headless=False, muted=False)
            page = fazerLogin.fazerLogin(page)
            progresso = Progresso()            
            main(page, enviarMsg=enviarMsg, gravar=gravar)    
            sleep(2)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            tb_list = traceback.extract_tb(exc_traceback)
            last_frame = tb_list[-1]
            line_number = last_frame.lineno

            print(f'Erro: {e}')
            logs.erro(f'Erro ocorreu na linha? {line_number}')
            logs.erro(f"Exception type: {exc_type.__name__}")
            logs.erro(f'Exception message: {exc_value}')
        
        finally:
            if page:
                page.close()
            logs.info(f'\n{'='*50}Código Finalizado{'='*50}')
            remover_lock()