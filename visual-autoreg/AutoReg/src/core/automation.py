from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
import time

class Automation(QObject):
    extraction_completed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()

    def extrai_codigos_internacao(self, url):
        self.browser.setUrl(url)
        time.sleep(5)  # Simula o tempo de carregamento da página
        # Aqui você implementaria a lógica para extrair os códigos de internação
        extracted_data = "Códigos de internação extraídos com sucesso!"
        self.extraction_completed.emit(extracted_data)