from obsws_python import ReqClient
import os

from utils.formataNome import formataNome


class Gravador():
    def __init__(self):
        try:
            self.cl = ReqClient(host='localhost', port=4455, password='QpYakWZk4OXZk7Yf')
        except Exception as e:
            self.cl = None
            print(e)
        # self.caminho = rf'D:\Usuarios\gabrielalves\Documents\Formação Dev\Fundamentos\Trilha Inicial\Iniciando com Programacao'

    def Status(self):       
        record_status = self.cl.get_record_status()
        if record_status.output_active:
            return 'Gravando'
        if record_status.output_paused:
            return 'Pausado'

        return 'Parado'
    
    def Obter_Caminho_Gravacao_atual(self) -> str:
        caminho = self.cl.get_record_directory()
        caminho = caminho.record_directory
        return f'{caminho}'

    def Obter_Nome_Gravacao_atual(self) -> str:
        nome = self.cl.get_profile_parameter("Output","FilenameFormatting")
        nome = nome.parameter_value
        return f'{nome}'

    def Remove(self,name:str, caminho:str):
        # ignorar: \/:*?"<>|
        name = formataNome(name)
        file = fr'{caminho}\{name}.mkv'  
        os.remove(file)

    def Start(self, name:str,caminho:str)->bool:
        try:
            nome_com_data = formataNome(name)
            self.cl.set_record_directory(caminho)
            self.cl.set_profile_parameter("Output","FilenameFormatting", nome_com_data)    
            

            # Iniciar a gravação
            self.cl.start_record()
            return True
        except Exception as e:
            print(f"Erro ao iniciar gravação: {e}")
            return False
    
    def Stop(self,caminho:str, show_succ_msg:bool=True)->bool:
        try:            
            self.cl.stop_record()
            if show_succ_msg:
                print(f"\nGravação Finalizado com sucesso.\nGravado em: {caminho}")
            return True
        except Exception as e:
            print(f"Erro ao finalizar gravação: {e}")
            return False
        