"""
Widget de planilha para visualização e edição de dados CSV
"""
import csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QPushButton, QFileDialog, 
                              QMessageBox, QHeaderView, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction


class SpreadsheetWidget(QWidget):
    """Widget de planilha com funcionalidades de edição completas"""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar com botões de ação
        toolbar = QHBoxLayout()
        
        self.btn_add_row = QPushButton("➕ Linha")
        self.btn_add_row.setToolTip("Adicionar nova linha")
        self.btn_add_row.clicked.connect(self.add_row)
        
        self.btn_remove_row = QPushButton("➖ Linha")
        self.btn_remove_row.setToolTip("Remover linha selecionada")
        self.btn_remove_row.clicked.connect(self.remove_row)
        
        self.btn_add_column = QPushButton("➕ Coluna")
        self.btn_add_column.setToolTip("Adicionar nova coluna")
        self.btn_add_column.clicked.connect(self.add_column)
        
        self.btn_remove_column = QPushButton("➖ Coluna")
        self.btn_remove_column.setToolTip("Remover coluna selecionada")
        self.btn_remove_column.clicked.connect(self.remove_column)
        
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.setToolTip("Salvar alterações no arquivo")
        self.btn_save.clicked.connect(self.save_file)
        
        self.btn_export = QPushButton("📤 Exportar")
        self.btn_export.setToolTip("Exportar para novo arquivo")
        self.btn_export.clicked.connect(self.export_file)
        
        self.btn_clear = QPushButton("🗑️ Limpar")
        self.btn_clear.setToolTip("Limpar toda a planilha")
        self.btn_clear.clicked.connect(self.clear_table)
        
        toolbar.addWidget(self.btn_add_row)
        toolbar.addWidget(self.btn_remove_row)
        toolbar.addWidget(self.btn_add_column)
        toolbar.addWidget(self.btn_remove_column)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_save)
        toolbar.addWidget(self.btn_export)
        toolbar.addWidget(self.btn_clear)
        
        layout.addLayout(toolbar)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.table)
        
        # Status info
        self.status_label = QWidget()
        status_layout = QHBoxLayout(self.status_label)
        status_layout.setContentsMargins(5, 2, 5, 2)
        
        from PyQt6.QtWidgets import QLabel
        self.file_label = QLabel("Nenhum arquivo carregado")
        self.file_label.setStyleSheet("color: #666; font-size: 11px;")
        status_layout.addWidget(self.file_label)
        status_layout.addStretch()
        
        layout.addWidget(self.status_label)
        
    def load_csv(self, file_path):
        """Carrega um arquivo CSV na tabela"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                data = list(csv_reader)
                
            if not data:
                QMessageBox.warning(self, "Aviso", "Arquivo CSV vazio")
                return
                
            # Configurar tabela
            self.table.setRowCount(len(data) - 1)  # -1 para header
            self.table.setColumnCount(len(data[0]))
            
            # Definir headers
            self.table.setHorizontalHeaderLabels(data[0])
            
            # Preencher dados
            for row_idx, row_data in enumerate(data[1:]):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(cell_data)
                    self.table.setItem(row_idx, col_idx, item)
            
            self.current_file = file_path
            self.file_label.setText(f"📄 {file_path}")
            self.table.resizeColumnsToContents()
            
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar CSV:\n{str(e)}")
            
    def save_file(self):
        """Salva as alterações no arquivo atual"""
        if not self.current_file:
            self.export_file()
            return
            
        try:
            self._save_to_file(self.current_file)
            QMessageBox.information(self, "Sucesso", "Arquivo salvo com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar:\n{str(e)}")
            
    def export_file(self):
        """Exporta a tabela para um novo arquivo CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self._save_to_file(file_path)
                QMessageBox.information(self, "Sucesso", f"Arquivo exportado para:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")
                
    def _save_to_file(self, file_path):
        """Salva os dados da tabela em um arquivo CSV"""
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            csv_writer = csv.writer(file)
            
            # Escrever headers
            headers = []
            for col in range(self.table.columnCount()):
                header_item = self.table.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"Column_{col}")
            csv_writer.writerow(headers)
            
            # Escrever dados
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                csv_writer.writerow(row_data)
                
    def add_row(self):
        """Adiciona uma nova linha no final da tabela"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.insertRow(current_row + 1)
        else:
            self.table.insertRow(self.table.rowCount())
        self.data_changed.emit()
        
    def remove_row(self):
        """Remove a linha selecionada"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha para remover")
            
    def add_column(self):
        """Adiciona uma nova coluna no final da tabela"""
        current_col = self.table.currentColumn()
        if current_col >= 0:
            self.table.insertColumn(current_col + 1)
            self.table.setHorizontalHeaderItem(
                current_col + 1, 
                QTableWidgetItem(f"Nova_Coluna_{current_col + 1}")
            )
        else:
            col_count = self.table.columnCount()
            self.table.insertColumn(col_count)
            self.table.setHorizontalHeaderItem(
                col_count, 
                QTableWidgetItem(f"Nova_Coluna_{col_count}")
            )
        self.data_changed.emit()
        
    def remove_column(self):
        """Remove a coluna selecionada"""
        current_col = self.table.currentColumn()
        if current_col >= 0:
            self.table.removeColumn(current_col)
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma coluna para remover")
            
    def clear_table(self):
        """Limpa toda a tabela"""
        reply = QMessageBox.question(
            self, "Confirmar",
            "Deseja realmente limpar toda a planilha?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.current_file = None
            self.file_label.setText("Nenhum arquivo carregado")
            self.data_changed.emit()
            
    def show_context_menu(self, position):
        """Mostra menu de contexto ao clicar com botão direito"""
        menu = QMenu()
        
        add_row_action = QAction("➕ Adicionar Linha", self)
        add_row_action.triggered.connect(self.add_row)
        
        remove_row_action = QAction("➖ Remover Linha", self)
        remove_row_action.triggered.connect(self.remove_row)
        
        add_col_action = QAction("➕ Adicionar Coluna", self)
        add_col_action.triggered.connect(self.add_column)
        
        remove_col_action = QAction("➖ Remover Coluna", self)
        remove_col_action.triggered.connect(self.remove_column)
        
        menu.addAction(add_row_action)
        menu.addAction(remove_row_action)
        menu.addSeparator()
        menu.addAction(add_col_action)
        menu.addAction(remove_col_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
        
    def on_item_changed(self, item):
        """Callback quando um item é alterado"""
        self.data_changed.emit()
