from PyQt6.QtCore import QThread, pyqtSignal
import sys
import io
import time

class OutputRedirector(io.StringIO):
    """Redireciona stdout/stderr para sinais Qt"""
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
    
    def write(self, text):
        if text.strip():
            self.signal.emit(text)
        return len(text)
    
    def flush(self):
        pass

class ThreadWorker(QThread):
    log_signal = pyqtSignal(str)  # Renomeado de log_message para log_signal
    url_changed = pyqtSignal(str)
    csv_generated = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    driver_ready = pyqtSignal(object)
    
    def __init__(self, selected_function="extrai_codigos_internacao"):
        super().__init__()
        self.selected_function = selected_function
        self.driver = None
    
    def run(self):
        """Thread principal de execução"""
        try:
            self.log_signal.emit(f"🚀 Iniciando: {self.selected_function}")
            self.execute_autoreg_function()
            self.log_signal.emit(f"✅ Concluído: {self.selected_function}")
            
        except Exception as e:
            import traceback
            error_msg = f"❌ Erro na execução:\n{traceback.format_exc()}"
            self.log_signal.emit(error_msg)
            self.error_signal.emit(str(e))
    
    def execute_autoreg_function(self):
        """Executa a função real do AutoReg"""
        # Adiciona o caminho do autoreg ao sys.path
        import os
        from pathlib import Path
        
        # Caminho para o diretório raiz do AutoReg (4 níveis acima)
        autoreg_root = Path(__file__).parent.parent.parent.parent.parent
        autoreg_path = str(autoreg_root.resolve())
        
        if autoreg_path not in sys.path:
            sys.path.insert(0, autoreg_path)
            self.log_signal.emit(f"📂 Adicionado ao PATH: {autoreg_path}")
        
        # Redireciona stdout/stderr
        stdout_redirector = OutputRedirector(self.log_signal)
        stderr_redirector = OutputRedirector(self.log_signal)
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector
        
        try:
            # Importa o módulo autoreg
            import autoreg
            self.log_signal.emit(f"✅ Módulo 'autoreg' importado com sucesso")
            
            # Verifica se a função existe
            if not hasattr(autoreg, self.selected_function):
                raise AttributeError(f"Função '{self.selected_function}' não encontrada no módulo autoreg")
            
            # Obtém a função
            func = getattr(autoreg, self.selected_function)
            
            self.log_signal.emit(f"✅ Função encontrada: {self.selected_function}")
            self.log_signal.emit(f"⚙️  Executando...")
            
            # Patch para capturar o driver quando for criado
            self.patch_webdriver_creation()
            
            # Executa a função
            result = func()
            
            self.log_signal.emit(f"✅ Execução concluída!")
            
            # Busca CSVs gerados
            self.find_generated_csv()
            
        finally:
            # Restaura stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def patch_webdriver_creation(self):
        """Intercepta a criação do WebDriver para capturar o driver"""
        try:
            from selenium import webdriver
            original_chrome = webdriver.Chrome
            
            def patched_chrome(*args, **kwargs):
                driver = original_chrome(*args, **kwargs)
                self.driver = driver
                self.log_signal.emit("🌐 Driver Selenium capturado!")
                self.driver_ready.emit(driver)  # Envia driver para a GUI
                return driver
            
            webdriver.Chrome = patched_chrome
            
        except Exception as e:
            self.log_signal.emit(f"⚠️  Não foi possível interceptar WebDriver: {e}")
    
    def find_generated_csv(self):
        """Busca CSVs gerados recentemente"""
        import os
        from pathlib import Path
        from datetime import datetime, timedelta
        
        search_dirs = [
            Path.home() / "AutoReg",
            Path("output"),
            Path.cwd()
        ]
        
        cutoff_time = datetime.now() - timedelta(seconds=60)
        recent_csvs = []
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for csv_file in search_dir.glob("*.csv"):
                mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)
                if mtime > cutoff_time:
                    recent_csvs.append((csv_file, mtime))
        
        if recent_csvs:
            recent_csvs.sort(key=lambda x: x[1], reverse=True)
            newest_csv = recent_csvs[0][0]
            self.log_signal.emit(f"📊 CSV encontrado: {newest_csv.name}")
            self.csv_generated.emit(str(newest_csv))
        else:
            self.log_signal.emit("ℹ️  Nenhum CSV gerado nos últimos 60 segundos")