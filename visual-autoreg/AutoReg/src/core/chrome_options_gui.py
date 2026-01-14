"""
Configuração de Chrome Options otimizada para GUI
Permite controle remoto e integração com QWebEngineView
"""
import os
from selenium.webdriver.chrome.options import Options


def get_chrome_options_for_visual_autoreg():
    """
    Retorna opções do Chrome otimizadas para uso com a GUI Visual AutoReg
    
    O navegador roda normalmente, mas podemos capturar screenshots
    e sincronizar a URL com o QWebEngineView
    """
    user_dir = os.path.expanduser('~/AutoReg')
    os.makedirs(user_dir, exist_ok=True)
    
    chrome_options = Options()
    
    # Configurações de janela
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # NÃO usar headless para que o usuário possa ver
    # chrome_options.add_argument("--headless=new")
    
    # Configurações de download
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": user_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    })
    
    return chrome_options


def patch_autoreg_chrome_options():
    """
    Substitui temporariamente a função get_chrome_options do autoreg
    para usar nossa versão otimizada para GUI
    """
    try:
        import autoreg.chrome_options
        autoreg.chrome_options.get_chrome_options = get_chrome_options_for_visual_autoreg
        print("✅ Chrome options patcheado para Visual AutoReg")
        return True
    except ImportError:
        print("⚠️ Não foi possível patchear chrome_options")
        return False
