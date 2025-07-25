import logging
import os

class Logger:
    def __init__(self):        
        self.path = r".\logs"        
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.logger = logging.getLogger('gravador')        

        logging.basicConfig(
            filename= self.path + rf'\logs.log',
            encoding='utf-8',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logging.getLogger("paramiko").setLevel(logging.CRITICAL)
        logging.getLogger("asyncio").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        logging.getLogger("obsws_python.baseclient.ObsClient").setLevel(logging.CRITICAL)
        logging.getLogger("obsws_python.reqs.ReqClient").setLevel(logging.CRITICAL)

    def info(self, msg:str):
        self.logger.info(f"{msg}")

    def erro(self, msg:str):
        self.logger.info(f"{msg}")

    def warning(self, msg:str):
        self.logger.info(f"{msg}")