from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import io
import sys
from PyQt6.QtCore import Qt

class BrowserWidget(QWidget):
    """Widget que exibe capturas do navegador Selenium em tempo real"""
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.screenshot_timer = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para exibir o screenshot
        self.screenshot_label = QLabel("🌐 Aguardando navegador Selenium...")
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #888;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.screenshot_label.setScaledContents(False)  # Desabilitar auto-escala
        self.screenshot_label.setMinimumSize(640, 480)  # Tamanho mínimo
        self.screenshot_label.setMaximumSize(1920, 1080)  # Tamanho máximo
        
        layout.addWidget(self.screenshot_label)
        self.setLayout(layout)
    
    def set_driver(self, driver):
        """Conecta ao driver Selenium e inicia captura de screenshots"""
        self.driver = driver
        self.screenshot_label.setText("🔄 Conectado ao navegador, capturando...")
        self.start_screenshot_capture()
    
    def start_screenshot_capture(self):
        """Inicia timer para capturar screenshots periodicamente"""
        if self.screenshot_timer:
            self.screenshot_timer.stop()
        
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.capture_screenshot)
        self.screenshot_timer.start(500)  # Captura a cada 500ms
    
    def capture_screenshot(self):
        """Captura screenshot do Selenium e exibe no label"""
        if not self.driver:
            return
        
        try:
            # Captura screenshot como PNG em bytes
            png_bytes = self.driver.get_screenshot_as_png()
            
            # Converte para QPixmap
            qimage = QImage.fromData(png_bytes)
            pixmap = QPixmap.fromImage(qimage)
            
            # Escala para caber no widget mantendo proporção
            label_size = self.screenshot_label.size()
            scaled_pixmap = pixmap.scaled(
                label_size.width(),
                label_size.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Define o pixmap SEM permitir que o label cresça
            self.screenshot_label.setPixmap(scaled_pixmap)
            self.screenshot_label.setFixedSize(label_size)  # Mantém tamanho fixo
            
        except Exception as e:
            # Se falhar (ex: navegador fechado), para o timer
            if self.screenshot_timer:
                self.screenshot_timer.stop()
            self.screenshot_label.setText(f"❌ Erro na captura: {str(e)}")
    
    def stop_capture(self):
        """Para a captura de screenshots"""
        if self.screenshot_timer:
            self.screenshot_timer.stop()
        self.driver = None
        self.screenshot_label.clear()
        self.screenshot_label.setText("🌐 Aguardando navegador Selenium...")
    
    def resizeEvent(self, event):
        """Reajusta o screenshot quando a janela é redimensionada"""
        super().resizeEvent(event)
        if hasattr(self, 'screenshot_label') and self.screenshot_label.pixmap():
            # Força recaptura no próximo ciclo
            pass
