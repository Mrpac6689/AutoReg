"""
Integração entre Selenium e QWebEngineView
Permite visualizar automações do Selenium no navegador embutido
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import RemoteConnection


class CustomRemoteConnection(RemoteConnection):
    """Conexão customizada para capturar URLs visitadas"""
    def __init__(self, *args, url_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_callback = url_callback
        

def get_chrome_options_for_gui(debugger_address="127.0.0.1:9222"):
    """
    Retorna opções do Chrome configuradas para integração com a GUI
    
    Estratégia: Usar Chrome em modo de debug remoto para que possamos
    replicar a navegação no QWebEngineView
    """
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--remote-debugging-address=0.0.0.0")
    chrome_options.add_argument(f"--remote-debugging-port=9222")
    
    # Configurações de download
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": user_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    })
    
    return chrome_options


def create_monitored_driver(url_change_callback=None):
    """
    Cria um driver do Selenium que notifica mudanças de URL
    
    Args:
        url_change_callback: Função chamada quando a URL muda (url_change_callback(new_url))
    
    Returns:
        WebDriver do Selenium configurado
    """
    # Por enquanto, usar as opções padrão do autoreg
    # TODO: Implementar monitoramento de URL para sincronizar com QWebEngineView
    from autoreg.chrome_options import get_chrome_options
    chrome_options = get_chrome_options()
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Se houver callback, podemos monitorar mudanças de URL
    if url_change_callback:
        original_get = driver.get
        
        def monitored_get(url):
            result = original_get(url)
            url_change_callback(url)
            return result
        
        driver.get = monitored_get
    
    return driver


class SeleniumMonitor:
    """
    Monitora um driver Selenium e sincroniza com QWebEngineView
    """
    def __init__(self, driver, webview):
        self.driver = driver
        self.webview = webview
        self.last_url = None
        
    def sync_url(self):
        """Sincroniza a URL atual do Selenium com o QWebEngineView"""
        try:
            current_url = self.driver.current_url
            if current_url != self.last_url and current_url != "data:,":
                self.last_url = current_url
                self.webview.setUrl(current_url)
        except Exception as e:
            print(f"Erro ao sincronizar URL: {e}")
    
    def start_monitoring(self, interval_ms=1000):
        """
        Inicia monitoramento periódico da URL
        
        Args:
            interval_ms: Intervalo em milissegundos para verificar mudanças
        """
        from PyQt6.QtCore import QTimer
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_url)
        self.timer.start(interval_ms)
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        if hasattr(self, 'timer'):
            self.timer.stop()
