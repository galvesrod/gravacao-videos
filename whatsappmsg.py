from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import os
import time

class WhatsAppWeb:
    def __init__(self, profile_path="./whatsapp_profile"):
        self.profile_path = profile_path
        self.driver = None
        
    def setup_chrome_options(self):
        """Configura as opções do Chrome para manter a sessão"""
        chrome_options = Options()
        
        # Criar diretório do perfil se não existir
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
        
        # Configurações ESSENCIAIS para manter sessão
        chrome_options.add_argument(f"--user-data-dir={os.path.abspath(self.profile_path)}")
        chrome_options.add_argument("--profile-directory=Default")
        
        # Configurações básicas de estabilidade
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Configurações para Windows
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        
        # REMOVER configurações que podem interferir na sessão:
        # NÃO usar --disable-javascript (WhatsApp precisa de JS)
        # NÃO usar --disable-images (pode causar problemas)
        # NÃO usar configurações muito restritivas
        
        # Configurações para evitar detecção (mantendo funcionalidades)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent atualizado
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Configurações de janela
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument("--window-size=1920,1080")
        
        # Configurações importantes para persistência de sessão
        chrome_options.add_argument("--enable-local-storage")
        chrome_options.add_argument("--enable-cookies")
        chrome_options.add_argument("--allow-running-insecure-content")

        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--headless")

        # Desabilitar som/áudio
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-audio-output")

        # Outras opções úteis para silenciar notificações
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        return chrome_options
    
    def detectar_chromedriver(self):
        """Detecta e configura o ChromeDriver automaticamente"""
        try:
            # Primeiro, tentar sem especificar caminho (se estiver no PATH)
            return webdriver.Chrome()
        except WebDriverException:
            # Tentar caminhos comuns do ChromeDriver
            caminhos_comuns = [
                "./chromedriver.exe",
                "./chromedriver",
                "C:/chromedriver/chromedriver.exe",
                "/usr/local/bin/chromedriver",
                "/usr/bin/chromedriver"
            ]
            
            for caminho in caminhos_comuns:
                if os.path.exists(caminho):
                    try:
                        service = Service(caminho)
                        return webdriver.Chrome(service=service)
                    except:
                        continue
            
            raise WebDriverException("ChromeDriver não encontrado")
    
    def iniciar_whatsapp(self):
        """Inicia o WhatsApp Web"""
        try:
            chrome_options = self.setup_chrome_options()
            
            # Método 1: Tentar com webdriver-manager (automático)
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())                
                
                # Tentar inicializar com configurações robustas
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except ImportError:
                print("webdriver-manager não instalado. Tentando métodos alternativos...")
                
                # Método 2: Tentar sem service específico
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    
                except WebDriverException as e:
                    print(f"Erro ao iniciar ChromeDriver: {e}")
                    
                    # Método 3: Tentar com configurações mínimas
                    try:
                        minimal_options = Options()
                        minimal_options.add_argument("--no-sandbox")
                        minimal_options.add_argument("--disable-dev-shm-usage")
                        minimal_options.add_argument("--remote-debugging-port=9222")
                        minimal_options.add_argument(f"--user-data-dir={os.path.abspath(self.profile_path)}")
                        
                        self.driver = webdriver.Chrome(options=minimal_options)
                        
                    except Exception as final_error:
                        print(f"\n❌ ERRO FINAL: {final_error}")
                        print("\n=== SOLUÇÕES PARA DevToolsActivePort ===")
                        print("1. Feche TODOS os processos do Chrome no Gerenciador de Tarefas")
                        print("2. Execute como Administrador")
                        print("3. Instale: pip install webdriver-manager")
                        print("4. Tente reiniciar o computador")
                        print("5. Atualize o Google Chrome")
                        print("6. Desabilite antivírus temporariamente")
                        return False
            
            # Aguardar um pouco antes de navegar
            time.sleep(0.5)
            
            # Navegar para WhatsApp Web
            # print("Navegando para WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            
            # Verificar se já está logado ou precisa escanear QR
            self.verificar_login()
            return True
            
        except Exception as e:
            print(f"Erro geral ao iniciar WhatsApp: {e}")
            return False
            
    def verificar_login(self):
        """Verifica se está logado ou se precisa escanear QR Code"""
        try:
            # Aguardar a página carregar
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            
            # Verificar se o QR Code está presente (não logado)
            qr_selectors = [
                "[data-ref]",
                "canvas[aria-label]",
                "[data-testid='qr-code']",
                "div[data-ref] canvas"
            ]
            
            qr_encontrado = False
            for selector in qr_selectors:
                try:
                    qr_element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if qr_element:
                        
                        qr_encontrado = True
                        break
                except:
                    continue
            
            if qr_encontrado:
                print("📱 Escaneie o QR Code com seu celular para fazer login.")
                print("⏳ Aguardando login... (timeout em 120 segundos)")
                
                # Aguardar até que o QR Code desapareça (login realizado)
                for selector in qr_selectors:
                    try:
                        WebDriverWait(self.driver, 120).until_not(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        break
                    except:
                        continue
                        
                time.sleep(0.5)  # Aguardar estabilizar
                
            else:
                # Verificar se já está logado procurando por elementos da interface principal
                interface_selectors = [
                    # "[data-testid='chat-list']",
                    # "[data-testid='side']",
                    # "div[data-testid='chat-list-search']",
                    "#side"
                ]
                
                interface_encontrada = False
                for selector in interface_selectors:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if element:
                            interface_encontrada = True
                            break
                    except:
                        continue
                if not interface_encontrada:
                    print("⚠️ Status de login incerto. Aguardando interface carregar...")
                    time.sleep(1)
            
            # Verificação final da interface principal
            # print("Verificando se a interface principal carregou...")
            interface_carregada = False
            
            final_selectors = [
                "#side",
                # "[data-testid='chat-list']",
                # "div[title='Nova conversa']",
                # "[data-testid='side']"
            ]
            
            for selector in final_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    interface_carregada = True
                    break
                except:
                    continue
            
            if interface_carregada:
                # print("🎉 WhatsApp Web carregado completamente!")
                # print("💾 Sessão será salva automaticamente para próximas execuções.")
                return True
            else:
                print("⚠️ Interface não carregou completamente. Pode haver problemas de conexão.")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante verificação de login: {e}")
            print("💡 Tente recarregar a página ou reiniciar o script.")
            return False
    
    def buscar_contato(self, nome_contato):
        """Busca um contato específico"""
        try:
            
            # Aguardar a interface estar completamente carregada
            interface_carregada = False
            
            # Múltiplos seletores para a caixa de pesquisa
            search_selectors = [
                "div[contenteditable='true'][data-tab='3']",
                # "[data-testid='chat-list-search']",
                # "div[title='Pesquisar ou começar uma nova conversa']",
                # "div[role='textbox'][contenteditable='true']",
                # "#side div[contenteditable='true']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    break
                except:
                    continue
            
            if not search_box:
                print("❌ Não foi possível encontrar a caixa de pesquisa")
                print("💡 Tentando método alternativo...")
                
                # Método alternativo - clicar em nova conversa
                try:
                    nova_conversa_selectors = [
                        "div[title='Nova conversa']",
                        "[data-testid='compose-btn']",
                        "div[role='button'][title='Nova conversa']"
                    ]
                    
                    for selector in nova_conversa_selectors:
                        try:
                            nova_conversa = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            nova_conversa.click()
                            print("✓ Botão 'Nova conversa' clicado")
                            time.sleep(0.5)
                            
                            # Tentar encontrar a caixa de pesquisa novamente
                            search_box = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true']"))
                            )
                            break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"❌ Método alternativo falhou: {e}")
                    return False
            
            if not search_box:
                print("❌ Não foi possível acessar a função de pesquisa")
                return False
            
            # Clicar na caixa de pesquisa
            search_box.click()
            time.sleep(1)
            
            # Limpar e digitar o nome do contato
            search_box.clear()
            search_box.send_keys(nome_contato)
            
            # Aguardar resultados aparecerem
            time.sleep(3)
            
            # Múltiplos seletores para resultados de pesquisa
            result_selectors = [
                "div[role='listitem']",
                "[data-testid='cell-frame-container']",
                "div[data-testid='chat-list'] > div > div",
                "#pane-side div[data-testid='chat']",
                "div[data-id] span[title*='" + nome_contato + "']"
            ]
            
            result_found = False
            for selector in result_selectors:
                try:
                    results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if results:
                        
                        # Procurar o resultado que contém o nome
                        for result in results:
                            if nome_contato.lower() in result.text.lower():
                                result.click()
                                result_found = True
                                break
                        
                        if result_found:
                            break
                        
                        # Se não encontrou pelo texto, clicar no primeiro resultado
                        if not result_found and results:
                            print("⚠️ Clicando no primeiro resultado disponível")
                            results[0].click()
                            result_found = True
                            break
                            
                except Exception as e:
                    print(f"✗ Erro com seletor {selector}: {e}")
                    continue
            
            if result_found:
                time.sleep(2)  # Aguardar conversa carregar
                return True
            else:
                print(f"❌ Contato '{nome_contato}' não encontrado nos resultados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar contato: {e}")
            print("💡 Dicas:")
            print("   - Verifique se o WhatsApp Web carregou completamente")
            print("   - Tente usar o nome exato do contato")
            print("   - Verifique se o contato existe na sua lista")
            return False
    
    def enviar_mensagem(self, mensagem):
        """Envia uma mensagem no chat atual"""
        try:
            
            # Múltiplos seletores para a caixa de mensagem
            message_selectors = [
                "div[contenteditable='true'][data-tab='10']",
                "[data-testid='conversation-compose-box-input']",
                "div[contenteditable='true'][role='textbox']",
                "div[contenteditable='true'][data-testid='conversation-compose-box-input']",
                "#main div[contenteditable='true']"
            ]
            
            message_box = None
            for selector in message_selectors:
                try:
                    message_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not message_box:
                print("❌ Não foi possível encontrar a caixa de mensagem")
                print("💡 Certifique-se de que uma conversa está aberta")
                return False
            
            # Clicar na caixa de mensagem
            message_box.click()
            time.sleep(1)
            
            # Digitar a mensagem
            message_box.clear()
            message_box.send_keys(mensagem)
            time.sleep(1)
            
            # Múltiplos seletores para o botão enviar
            send_selectors = [
                "button[aria-label='Enviar']",
                "[data-testid='send']",
                "button[data-testid='send']",
                "span[data-testid='send']",
                "div[role='button'][data-testid='send']"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not send_button:
                print("⚠️ Botão enviar não encontrado, tentando Enter...")
                from selenium.webdriver.common.keys import Keys
                message_box.send_keys(Keys.ENTER)
                print("✓ Mensagem enviada com Enter")
            else:
                # Clicar no botão enviar
                send_button.click()
            
            time.sleep(0.5)  # Aguardar mensagem ser processada
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            print("💡 Dicas:")
            print("   - Certifique-se de que uma conversa está aberta")
            print("   - Verifique se o WhatsApp Web está funcionando normalmente")
            return False
    
    def aguardar_usuario(self):
        """Mantém o navegador aberto para uso manual"""
        try:
            print("\nWhatsApp pronto para uso!")
            print("Pressione Ctrl+C para fechar o programa...")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nFechando WhatsApp...")
            self.fechar()
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("Navegador fechado!")

# Exemplo de uso
if __name__ == "__main__":
    # Criar instância do WhatsApp
    whatsapp = WhatsAppWeb()
    
    try:
        # Iniciar WhatsApp Web
        if whatsapp.iniciar_whatsapp():
            print("\n" + "="*50)
            print("🚀 WhatsApp Web iniciado com sucesso!")
            print("="*50)
            
            # Exemplo de como usar as funções
            while True:
                print("\n📋 Opções:")
                print("1 - Buscar contato e enviar mensagem")
                print("2 - Enviar mensagem no chat atual")
                print("3 - Apenas usar manualmente")
                print("0 - Sair")
                
                try:
                    opcao = input("\n👉 Escolha uma opção: ").strip()
                    
                    if opcao == "1":
                        nome = input("📱 Nome do contato: ").strip()
                        if nome:
                            if whatsapp.buscar_contato(nome):
                                mensagem = input("💬 Mensagem: ").strip()
                                if mensagem:
                                    whatsapp.enviar_mensagem(mensagem)
                    
                    elif opcao == "2":
                        mensagem = input("💬 Mensagem: ").strip()
                        if mensagem:
                            whatsapp.enviar_mensagem(mensagem)
                    
                    elif opcao == "3":
                        print("\n✅ WhatsApp pronto para uso manual!")
                        print("⚠️ Não feche esta janela - use o WhatsApp normalmente")
                        print("🔄 A sessão será salva automaticamente")
                        whatsapp.aguardar_usuario()
                        break
                    
                    elif opcao == "0":
                        print("👋 Fechando WhatsApp...")
                        break
                    
                    else:
                        print("❌ Opção inválida!")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Fechando WhatsApp...")
                    break
        else:
            print("❌ Falha ao iniciar o WhatsApp Web")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        whatsapp.fechar()