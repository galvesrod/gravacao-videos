from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def configurarChrome(headless:bool=False, muted:bool=False) -> webdriver:
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

    # Configurações para desabilitar áudio
    if muted:
        print('mudo')
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-audio")
        chrome_options.add_argument("--disable-audio-output")
        chrome_options.add_argument("--disable-background-media-suspend")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--autoplay-policy=document-user-activation-required")
    service = Service('chromedriver.exe')  # caminho do chromedriver
    
    page = webdriver.Chrome(service=service, options=chrome_options)
    page.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    page.implicitly_wait(30)

    return page