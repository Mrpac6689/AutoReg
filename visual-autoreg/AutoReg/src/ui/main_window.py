from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                              QTextEdit, QPushButton, QSplitter, QComboBox, QLabel)
from PyQt6.QtCore import Qt
from ui.browser_widget import BrowserWidget
from ui.spreadsheet_widget import SpreadsheetWidget
from workers.thread_worker import ThreadWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoReg")
        self.setGeometry(100, 100, 1200, 800)
        
        # Mantém janela sempre no topo
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Splitter horizontal: Navegador/Logs à esquerda, Planilha à direita
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Container esquerdo: Navegador + Logs + Botão
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.browser = BrowserWidget()
        left_layout.addWidget(self.browser)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(150)
        left_layout.addWidget(self.log_console)

        # Área de seleção de função
        function_layout = QVBoxLayout()
        function_layout.setSpacing(5)
        
        function_label = QLabel("🔧 Selecione a Função AutoReg:")
        function_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        function_layout.addWidget(function_label)
        
        self.function_combo = QComboBox()
        self.function_combo.addItems(self.get_autoreg_functions())
        self.function_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #2980b9;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        function_layout.addWidget(self.function_combo)
        
        left_layout.addLayout(function_layout)

        self.start_button = QPushButton("▶️ Executar Função Selecionada")
        self.start_button.clicked.connect(self.start_process)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        left_layout.addWidget(self.start_button)
        
        # Widget de planilha à direita
        self.spreadsheet = SpreadsheetWidget()
        
        # Adicionar widgets ao splitter
        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(self.spreadsheet)
        
        # Definir proporções iniciais (60% esquerda, 40% direita)
        self.main_splitter.setSizes([700, 500])
        
        self.layout.addWidget(self.main_splitter)

        # Configurar worker
        self.worker = ThreadWorker()
        self.worker.log_signal.connect(self.update_log)
        self.worker.csv_generated.connect(self.load_csv)
        self.worker.url_changed.connect(self.update_browser_url)
        self.worker.driver_ready.connect(self.connect_driver)
        self.worker.error_signal.connect(self.handle_error)

    def get_autoreg_functions(self):
        """Retorna lista de todas as funções disponíveis no autoreg"""
        return [
            "extrai_codigos_internacao",
            "interna_pacientes",
            "extrai_internados_sisreg",
            "extrai_internados_ghosp",
            "compara_internados",
            "motivo_alta",
            "extrai_codigos_sisreg_alta",
            "executa_alta",
            "dar_alta",
            "atualiza_restos",
            "extrai_internacoes_duplicadas",
            "trata_duplicados",
            "devolvidos",
            "pdf2csv",
            "ghosp_nota",
            "ghosp_cns",
            "ghosp_especial",
            "ghosp_especial_parallel",
            "solicita_inf_aih",
            "solicita_sisreg",
            "solicita_nota",
            "consulta_solicitacao_sisreg",
            "internados_ghosp_avancado",
            "internados_ghosp_nota",
            "trata_altas",
            "limpa_cache",
            "solicita_trata_dados",
            "solicita_pre_aih",
            "producao_ambulatorial",
            "producao_ambulatorial_dados",
            "producao_ambulatorial_gmus",
        ]
    
    def start_process(self):
        selected_function = self.function_combo.currentText()
        self.log_console.append(f"✅ Iniciando processo: {selected_function}...")
        self.start_button.setEnabled(False)
        self.function_combo.setEnabled(False)
        
        # Atualizar worker com a função selecionada
        self.worker.selected_function = selected_function
        self.worker.start()

    def update_log(self, message):
        self.log_console.append(message)
        # Auto-scroll para o final
        self.log_console.verticalScrollBar().setValue(
            self.log_console.verticalScrollBar().maximum()
        )
        
    def load_csv(self, csv_path):
        """Carrega o CSV gerado na planilha"""
        self.log_console.append(f"📊 Carregando planilha: {csv_path}")
        self.spreadsheet.load_csv(csv_path)
        self.start_button.setEnabled(True)
        self.function_combo.setEnabled(True)
    
    def update_browser_url(self, url):
        """Atualiza a URL do navegador embutido"""
        from PyQt6.QtCore import QUrl
        self.log_console.append(f"🌐 Navegando para: {url}")
        self.browser.load_url(url)
    
    def connect_driver(self, driver):
        """Conecta o driver do Selenium ao widget de navegador"""
        self.log_console.append("🔗 Conectando driver ao navegador embutido...")
        self.browser.set_driver(driver)
        
        # Opcionalmente, habilitar modo screenshot para visualização real
        # Descomente a linha abaixo se preferir screenshots ao invés de URL sync
        # self.browser.enable_screenshot_mode()
    
    def handle_error(self, error_msg):
        """Trata erros da execução"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            self, 
            "Erro na Execução", 
            f"Ocorreu um erro ao executar a função:\n\n{error_msg}"
        )
        self.start_button.setEnabled(True)
        self.function_combo.setEnabled(True)

    def start_worker(self):
        """Inicia a thread de trabalho"""
        selected_function = self.function_combo.currentText()
        
        self.worker = ThreadWorker(selected_function)
        self.worker.log_message.connect(self.update_console)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.csv_generated.connect(self.on_csv_generated)
        self.worker.driver_ready.connect(self.on_driver_ready)  # Conecta novo sinal
        
        self.start_button.setEnabled(False)
        self.function_combo.setEnabled(False)
        self.start_button.setText("⏳ Executando...")
        self.worker.start()
    
    def on_driver_ready(self, driver):
        """Conecta o driver Selenium ao widget de navegador"""
        self.browser.set_driver(driver)
        self.update_console("🌐 Navegador conectado ao widget!")