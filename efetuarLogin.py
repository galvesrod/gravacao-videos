import os
from playwright.sync_api import sync_playwright, Page

URL = "https://escola.formacao.dev/"
SESSION_FILE = os.path.exists(rf'config\state.json')

class RealizarLogin:
    def __init__(self):
        path = os.path.exists(rf'config')
        if not path:
            os.mkdir(rf'config')
    
    def getLogin(self) -> Page:
        USERNAME = 'galves.rod@gmail.com'
        PWD = 'eJ%Qr!J8K6XKEk'
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)

            if SESSION_FILE:
                context = browser.new_context(
                    viewport={ 'width': 1600, 'height': 1200 }, 
                    storage_state=rf'config\state.json',
                    
                    # record_video_dir='videos/',
                    # record_video_size={"width": 1600, "height": 1200} 
                )
            else:
                context = browser.new_context(viewport={ 'width': 1600, 'height': 1200 })

            page = context.new_page()
            page.set_viewport_size({"width": 1600, "height": 1200})
            page.goto(URL)

            page.wait_for_selector('xpath=//*[@id="__next"]/section/div[2]/div[1]/div/input').fill(USERNAME)
            page.wait_for_selector('xpath=//*[@id="__next"]/section/div[2]/div[2]/div/input').fill(PWD)
            page.wait_for_selector('xpath=//*[@id="__next"]/section/div[2]/button[1]').click()

            page.wait_for_selector('xpath=//*[@id="__next"]/div[1]/div[2]/div/aside/div/div[10]/span')            
            context.storage_state(path=rf'config\state.json')            
            
        return page