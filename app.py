import sys
from re import fullmatch
import asyncio

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMenuBar, QLineEdit, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction

from main import *

# инициализация глобальных переменных и констант
try:
    smtp_server, port, email, password, frequency, method, server_ip = load_config()
except:
    smtp_server, port, email, password, frequency, method, server_ip = None, "465", None, None, 1, 0, 0

TIMES = {0: 60, 1: 300, 2: 600, 3: 1800, 4: 3600}
time = TIMES[frequency]

last_sent_ip = load_save_file()

do = False

# приложение
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self, last_ip):
        super().__init__()
        self.setWindowTitle("NoStaticIP")
        self.setMinimumSize(300, 200)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        settings_menu = QAction("Настройки", self)
        info_menu = QAction("Информация", self)
        self.menu_bar.addAction(settings_menu)
        self.menu_bar.addAction(info_menu)
        settings_menu.triggered.connect(self.settings_window)
        info_menu.triggered.connect(self.info_window)

        layout = QVBoxLayout()

        self.current_ip_label = QLabel(f"Ваш IP сейчас:\n{get_ip(method)}")
        self.check_ip_button = QPushButton("Проверить IP")
        self.check_ip_button.clicked.connect(self.check_ip)
        self.last_sent_ip = QLabel(f"Последний отправленный IP:\n{last_ip}")
        self.send_ip_button = QPushButton("Отправить IP")
        self.send_ip_button.clicked.connect(self.send_ip)
        
        self.start = QPushButton("Начать")
        self.start.setCheckable(True)
        self.start.clicked.connect(self.start_cycle)
        self.start.released.connect(self.stop_cycle)

        layout.addWidget(self.current_ip_label)
        layout.addWidget(self.check_ip_button)
        layout.addWidget(self.last_sent_ip)
        layout.addWidget(self.send_ip_button)
        layout.addWidget(self.start)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def check_ip(self):
        global method
        self.current_ip_label.setText(f"Ваш IP сейчас:\n{get_ip(method)}")

    def send_ip(self):
        global smtp_server, port, email, password, method, server_ip, last_sent_ip
        ip_to_send = get_ip(method)
        send_mail(ip_to_send, smtp_server, int(port), email, password)
        last_sent_ip = ip_to_send
        self.last_sent_ip.setText(f"Последний отправленный IP:\n{last_sent_ip}")
        create_save_file(last_sent_ip)

    def settings_window(self):
        global email, password, smtp_server, port, frequency, method, server_ip
        self.sw = SettingsWindow(email, password, smtp_server, str(port), frequency, method, server_ip)
        self.sw.show()

    def info_window(self):
        self.iw = InfoWindow()
        self.iw.show()

    def start_cycle(self):
        global do
        do = True

    def stop_cycle(self):
        global do
        do = False



class SettingsWindow(QWidget):
    def __init__(self, email, password, smtp_server, port, frequency, method, server_ip):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setMinimumSize(400, 250)
        grid = QGridLayout()

        self.smtp_server_line = QLineEdit()
        self.smtp_label = QLabel("Ваш smtp сервер:")
        self.smtp_server_line.setPlaceholderText("smtp.example.com")
        self.smtp_server_line.setText(smtp_server)
        self.smtp_server_line.returnPressed.connect(self.smtp_changed)
        grid.addWidget(self.smtp_label, 0, 0)
        grid.addWidget(self.smtp_server_line, 0, 1)

        self.port_chose = QComboBox()
        self.port_label = QLabel("Порт smpt сервера:")
        self.port_chose.addItems(["25", "125", "465", "587", "7659", "10024", "10025"])
        self.port_chose.setCurrentText(port)
        self.port_chose.currentTextChanged.connect(self.port_changed)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_chose, 1, 1)

        self.email_line = QLineEdit()
        self.email_line_label = QLabel("Ваш адрес электронной почты:")
        self.email_line.setPlaceholderText("example@example.com")
        self.email_line.setText(email)
        self.email_line.returnPressed.connect(self.email_changed)
        grid.addWidget(self.email_line_label, 2, 0)
        grid.addWidget(self.email_line, 2, 1)

        self.password_line = QLineEdit()
        self.password_label = QLabel("Пароль от smpt сервера:")
        self.password_line.setPlaceholderText("password")
        self.password_line.setText(password)
        self.password_line.returnPressed.connect(self.password_changed)
        grid.addWidget(self.password_label, 3, 0)
        grid.addWidget(self.password_line, 3, 1)

        self.check_frequency = QComboBox()
        self.freq_label = QLabel("Частота проверки IP-адреса:")
        self.check_frequency.addItems(["1 минута", "5 минут", "10 минут", "30 минут", "1 час"])
        self.check_frequency.setCurrentIndex(frequency)
        self.check_frequency.currentIndexChanged.connect(self.time_changed)
        grid.addWidget(self.freq_label, 4, 0)
        grid.addWidget(self.check_frequency, 4, 1)

        self.check_method = QComboBox()
        self.method_label = QLabel("Метод получения IP-адреса:") 
        self.check_method.addItems(["Получать с http сервера", "Получать через stun"])
        self.check_method.setCurrentIndex(method)
        self.check_method.currentIndexChanged.connect(self.method_changed)
        grid.addWidget(self.method_label, 5, 0)
        grid.addWidget(self.check_method, 5, 1)

        self.ip_server = QComboBox()
        self.ip_server_label = QLabel("Сервер получения IP-адреса:")
        self.ip_server.addItems(["ifconfig.me"])
        self.ip_server.setCurrentIndex(server_ip)
        self.ip_server.currentTextChanged.connect(self.ip_server_changed)
        grid.addWidget(self.ip_server_label, 6, 0)
        grid.addWidget(self.ip_server, 6, 1)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)
        grid.addWidget(self.save_button, 7, 1)

        self.setLayout(grid)

        if method == 1:
            self.ip_server.setEnabled(False)
        else:
            self.ip_server.setEnabled(True)
    
    def save(self):
        email = self.email_line.text()
        password = self.password_line.text()
        smtp_server = self.smtp_server_line.text()
        port = self.port_chose.currentText()
        frequency = self.check_frequency.currentIndex()
        method = self.check_method.currentIndex()
        server_ip = self.ip_server.currentIndex()

        ptn = r"^\S+@\S+\.\S+$"
        if email is None or fullmatch(ptn, email) is None:
            email_broken = QMessageBox(self)
            email_broken.setWindowTitle("Ошибка записи")
            email_broken.setText("Введенный email недействителен!")
            email_broken.setIcon(QMessageBox.Icon.Critical)
            button = email_broken.exec()
        
        elif (password is None) or (password == "") or (" " in password):
            password_broken = QMessageBox(self)
            password_broken.setWindowTitle("Ошибка записи")
            password_broken.setText("Введенный пароль недействителен!")
            password_broken.setIcon(QMessageBox.Icon.Critical)
            button = password_broken.exec()

        elif (smtp_server is None) or (smtp_server == "") or (" " in smtp_server):
            smtp_broken = QMessageBox(self)
            smtp_broken.setWindowTitle("Ошибка записи")
            smtp_broken.setText("Введенный smtp-сервер недействителен!")
            smtp_broken.setIcon(QMessageBox.Icon.Critical)
            button = smtp_broken.exec()

        else:
            save_dialog = QMessageBox(self)
            save_dialog.setWindowTitle("Сохранение настроек")
            save_dialog.setText("Вы хотите сохранить данные настроки?")
            save_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
            save_dialog.setIcon(QMessageBox.Icon.Question)
            button = save_dialog.exec()
            if button == QMessageBox.StandardButton.Yes:
                create_config(smtp_server, port, email, password, frequency, method, server_ip)
            else:
                pass

    def smtp_changed(self):
        global smtp_server
        smtp_server = self.smtp_server_line.text()

    def email_changed(self):
        global email
        text = self.email_line.text()
        ptn = r"^\S+@\S+\.\S+$"
        if fullmatch(ptn, text) is not None:
            email = text
        else:
            self.email_line.setText("")
            self.email_line.setPlaceholderText("Неверный адрес!")

    def password_changed(self):
        global password
        password = self.password_line.text()

    def port_changed(self):
        global port
        port = int(self.port_chose.currentText())

    def time_changed(self):
        global frequency, time, TIMES
        frequency = self.check_frequency.currentIndex()
        time = TIMES[frequency]

    def method_changed(self):
        global method
        method = self.check_method.currentIndex()
        print(method)
        if method == 1: 
            self.ip_server.setEnabled(False)
        else:
            self.ip_server.setEnabled(True)

    def ip_server_changed(self):
        pass # будет добавлено когда будут добавлены другие сервера проверки ip


class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация")
        info_layout = QVBoxLayout()
        self.info = QLabel("Information will be added further in development")
        info_layout.addWidget(self.info)
        self.setLayout(info_layout)


window = MainWindow(last_sent_ip)
window.show()
app.exec()