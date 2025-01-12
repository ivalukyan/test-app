import psutil
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout)
from PyQt5.QtCore import QTimer, QTime

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.init_ui()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)

        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.update_record_time)

        self.last_cpu = None
        self.last_ram = None
        self.last_disk = None
        self.record_start_time = QTime()

        self.init_db()

    def init_ui(self):
        self.setWindowTitle("Уровень загруженности")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: #1b1b1a; color: white;")

        self.label_style = "font-size: 18px;"

        layout = QVBoxLayout()

        self.cpu_label = QLabel()
        self.cpu_label.setStyleSheet(self.label_style)
        layout.addWidget(self.cpu_label)

        self.ram_label = QLabel()
        self.ram_label.setStyleSheet(self.label_style)
        layout.addWidget(self.ram_label)

        self.rom_label = QLabel()
        self.rom_label.setStyleSheet(self.label_style)
        layout.addWidget(self.rom_label)

        self.record_button = QPushButton("Начать запись")
        self.record_button.setStyleSheet("font-size: 16px;")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.record_timer_label = QLabel("Таймер записи: 00:00")
        self.record_timer_label.setStyleSheet(self.label_style)
        self.record_timer_label.hide()
        layout.addWidget(self.record_timer_label)

        self.view_button = QPushButton("Просмотр данных")
        self.view_button.setStyleSheet("font-size: 16px;")
        self.view_button.clicked.connect(self.show_data)
        layout.addWidget(self.view_button)

        self.setLayout(layout)

        self.update_stats()

    def init_db(self):
        self.conn = sqlite3.connect("database/system_stats.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                free_ram REAL,
                free_disk REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.setText("Начать запись")
            self.record_timer.stop()
            self.record_timer_label.hide()
        else:
            self.is_recording = True
            self.record_button.setText("Остановить запись")
            self.record_start_time.start()
            self.record_timer.start(1000)
            self.record_timer_label.show()

    def update_record_time(self):
        elapsed_time = self.record_start_time.elapsed() // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        self.record_timer_label.setText(f"Таймер записи: {minutes:02}:{seconds:02}")

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        rom = psutil.disk_usage('/')

        total_ram = ram.total / (1024 ** 3)
        free_ram = ram.available / (1024 ** 3)

        total_disk = rom.total / (1024 ** 3)
        free_disk = rom.free / (1024 ** 3)

        self.cpu_label.setText(f"ЦП: {cpu}%")
        self.ram_label.setText(f"ОЗУ: {free_ram:.2f}/{total_ram:.2f} ГБ")
        self.rom_label.setText(f"Диск: {free_disk:.2f}/{total_disk:.2f} ГБ")

        if self.is_recording:
            self.record_data(cpu, free_ram, free_disk)

    def record_data(self, cpu, free_ram, free_disk):
        if (self.last_cpu != cpu or
            self.last_ram != free_ram or
            self.last_disk != free_disk):

            self.cursor.execute(
                "INSERT INTO stats (cpu_usage, free_ram, free_disk) VALUES (?, ?, ?)",
                (cpu, free_ram, free_disk)
            )
            self.conn.commit()

            self.last_cpu = cpu
            self.last_ram = free_ram
            self.last_disk = free_disk

    def show_data(self):
        self.data_window = DataWindow(self.conn)
        self.data_window.show()


class DataWindow(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Данные из базы")
        self.setGeometry(500, 100, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.load_data()

        self.setLayout(layout)

    def load_data(self):
        query = "SELECT * FROM stats"
        self.cursor = self.conn.cursor()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ЦП (%)", "ОЗУ (ГБ)", "Диск (ГБ)", "Время"])

        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec()
