from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException,StaleElementReferenceException

from time import sleep

class Progresso:
    def __init__(self):
        file = {
            "curso":"Formação DEV",
            "url":"https://escola.formacao.dev/",
            "formacoes": []
        }
        "aside>div>div:nth-child(5)>div>div>div"
        pass

    def run(page:webdriver):
        seletor = "aside>div>div:nth-child(5)>div>div>div"
    
        try:
            # Aguarda os elementos carregarem inicialmente
            wait = WebDriverWait(page, 10)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor)))
            
            # Conta quantos elementos existem
            divs = page.find_elements(By.CSS_SELECTOR, seletor)
            total_elementos = len(divs)
            print(f"Total de elementos encontrados: {total_elementos}")
            
            # Clica em cada elemento re-encontrando a cada iteração
            for i in range(total_elementos):
                try:
                    # Re-encontra os elementos a cada iteração para evitar stale reference
                    divs_atuais = page.find_elements(By.CSS_SELECTOR, seletor)
                    
                    if i >= len(divs_atuais):
                        print(f"Elemento {i+1} não existe mais, pulando...")
                        continue
                    
                    elemento = divs_atuais[i]
                    
                    # Verifica se o elemento ainda está no DOM
                    try:
                        elemento.is_displayed()  # Testa se o elemento ainda é válido
                    except StaleElementReferenceException:
                        print(f"Elemento {i+1} ficou stale, re-encontrando...")
                        divs_atuais = page.find_elements(By.CSS_SELECTOR, seletor)
                        if i < len(divs_atuais):
                            elemento = divs_atuais[i]
                        else:
                            continue
                    
                    # Aguarda o elemento ser clicável
                    WebDriverWait(page, 5).until(EC.element_to_be_clickable(elemento))
                    
                    # Rola até o elemento
                    page.execute_script("arguments[0].scrollIntoView(true);", elemento)
                    sleep(0.5)
                    
                    # Tenta clicar
                    elemento.click()
                    print(f"Clicou no elemento {i+1}")
                    
                except StaleElementReferenceException:
                    print(f"Elemento {i+1} ficou stale, tentando com JavaScript...")
                    # Re-encontra e usa JavaScript como fallback
                    divs_atuais = page.find_elements(By.CSS_SELECTOR, seletor)
                    if i < len(divs_atuais):
                        page.execute_script("arguments[0].click();", divs_atuais[i])
                        print(f"Clicou (JS) no elemento {i+1}")
                        
                except ElementClickInterceptedException:
                    print(f"Elemento {i+1} interceptado, usando JavaScript...")
                    divs_atuais = page.find_elements(By.CSS_SELECTOR, seletor)
                    if i < len(divs_atuais):
                        page.execute_script("arguments[0].click();", divs_atuais[i])
                        print(f"Clicou (JS) no elemento {i+1}")
                        
                except Exception as e:
                    print(f"Erro ao clicar no elemento {i+1}: {str(e)}")
                    continue
                
                # Pausa entre cliques
                sleep(1)
            
        except TimeoutException:
            print("Timeout: Elementos não encontrados dentro do tempo limite")
        except Exception as e:
            print(f"Erro geral: {str(e)}")
