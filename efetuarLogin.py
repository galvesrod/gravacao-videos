import os
from playwright.sync_api import sync_playwright

URL = "https://escola.formacao.dev/"
SESSION_FILE = os.path.exists(rf'config\state.json')

class RealizarLogin:
    def __init__(self):
        pass
    
    def getLogin(self) -> str:
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

            if not SESSION_FILE:
                pass


        return page