"""
Wrapper para funções do AutoReg com monitoramento de driver
Permite capturar o driver do Selenium durante a execução
"""
import sys
from selenium import webdriver


class DriverCapture:
    """Captura instâncias de WebDriver criadas durante execução"""
    def __init__(self):
        self.drivers = []
        self.original_init = None
        
    def start_capture(self):
        """Inicia captura de drivers"""
        # Salvar o __init__ original do Chrome WebDriver
        self.original_init = webdriver.Chrome.__init__
        
        # Criar wrapper que captura a instância
        def wrapped_init(driver_self, *args, **kwargs):
            result = self.original_init(driver_self, *args, **kwargs)
            self.drivers.append(driver_self)
            return result
        
        # Substituir o __init__
        webdriver.Chrome.__init__ = wrapped_init
    
    def stop_capture(self):
        """Para a captura e restaura o __init__ original"""
        if self.original_init:
            webdriver.Chrome.__init__ = self.original_init
    
    def get_latest_driver(self):
        """Retorna o driver mais recentemente criado"""
        return self.drivers[-1] if self.drivers else None
    
    def clear(self):
        """Limpa a lista de drivers capturados"""
        self.drivers.clear()


# Instância global para captura de drivers
_driver_capture = DriverCapture()


def get_driver_capture():
    """Retorna a instância global de captura de drivers"""
    return _driver_capture
