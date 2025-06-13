from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMenuBar, QLineEdit, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from re import fullmatch
from main import *
import sys

app = QApplication([])

try:
    smtp_server, port, email, password, frequency, method, server_ip = load_config()
except:
    smtp_server, port, email, password, frequency, method, server_ip = None, "465", None, None, 1, 0, 0

class MainWindow(QMainWindow):
    def __init__(self, ip, last_ip):
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

        current_ip_label = QLabel(f"Ваш IP сейчас:\n{ip}")
        check_ip_button = QPushButton("Проверить IP")
        last_sent_ip = QLabel(f"Последний отправленный IP:\n{last_ip}")
        send_ip_button = QPushButton("Отправить IP")
        
        start = QPushButton("Начать")

        layout.addWidget(current_ip_label)
        layout.addWidget(check_ip_button)
        layout.addWidget(last_sent_ip)
        layout.addWidget(send_ip_button)
        layout.addWidget(start)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def settings_window(self):
        global email, password, smtp_server, port, frequency, method, server_ip
        self.sw = SettingsWindow(email, password, smtp_server, port, frequency, method, server_ip)
        self.sw.show()

    def info_window(self):
        self.iw = InfoWindow()
        self.iw.show()



class SettingsWindow(QWidget):
    def __init__(self, email, password, smtp_server, port, frequency, method, server_ip):
        super().__init__()
        grid = QGridLayout()

        self.smtp_server_line = QLineEdit()
        self.smtp_label = QLabel("Ваш smtp сервер:")
        self.smtp_server_line.setPlaceholderText("smtp.example.com")
        self.smtp_server_line.returnPressed.connect(self.smtp_changed)
        self.smtp_server_line.setText(smtp_server)
        grid.addWidget(self.smtp_label, 0, 0)
        grid.addWidget(self.smtp_server_line, 0, 1)

        self.port_chose = QComboBox()
        self.port_label = QLabel("Порт smpt сервера:")
        self.port_chose.addItems(["25", "125", "465", "587", "7659", "10024", "10025"])
        self.port_chose.currentTextChanged.connect(self.port_changed)
        self.port_chose.setCurrentText(port)
        grid.addWidget(self.port_label, 1, 0)
        grid.addWidget(self.port_chose, 1, 1)

        self.email_line = QLineEdit()
        self.email_line_label = QLabel("Ваш адрес электронной почты:")
        self.email_line.setPlaceholderText("example@example.com")
        self.email_line.returnPressed.connect(self.email_changed)
        self.email_line.setText(email)
        grid.addWidget(self.email_line_label, 2, 0)
        grid.addWidget(self.email_line, 2, 1)

        self.password_line = QLineEdit()
        self.password_label = QLabel("Пароль от smpt сервера:")
        self.password_line.setPlaceholderText("password")
        self.password_line.returnPressed.connect(self.password_changed)
        self.password_line.setText(password)
        grid.addWidget(self.password_label, 3, 0)
        grid.addWidget(self.password_line, 3, 1)

        self.check_frequency = QComboBox()
        self.freq_label = QLabel("Частота проверки IP-адреса:")
        self.check_frequency.addItems(["1 минута", "5 минут", "10 минут", "30 минут", "1 час"])
        self.check_frequency.currentIndexChanged.connect(self.time_changed)
        self.check_frequency.setCurrentIndex(frequency)
        grid.addWidget(self.freq_label, 4, 0)
        grid.addWidget(self.check_frequency, 4, 1)

        self.check_method = QComboBox()
        self.method_label = QLabel("Метод получения IP-адреса:") 
        self.check_method.addItems(["Получать с http сервера", "Получать через stun"])
        self.check_method.currentIndexChanged.connect(self.method_changed)
        self.check_method.setCurrentIndex(method)
        grid.addWidget(self.method_label, 5, 0)
        grid.addWidget(self.check_method, 5, 1)

        self.ip_server = QComboBox()
        self.ip_server_label = QLabel("Сервер получения IP-адреса:")
        self.ip_server.addItems(["ifconfig.me"])
        self.ip_server.currentTextChanged.connect(self.ip_server_changed)
        self.ip_server.setCurrentIndex(server_ip)
        grid.addWidget(self.ip_server_label, 6, 0)
        grid.addWidget(self.ip_server, 6, 1)

        self.setLayout(grid)
    
    def smtp_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        smtp_server = self.smtp_server_line.text()
        try:
            create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
        except:
            pass
    def email_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        text = self.email_line.text()
        email = text
        ptn = r"^\S+@\S+\.\S+$"
        if fullmatch(ptn, text) is not None:
            try:
                create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
            except:
                pass
        else:
            self.email_line.setText("")
            self.email_line.setPlaceholderText("Неверный адрес!")

    def password_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        text = self.password_line.text()
        password = text
        try:
            create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
        except:
            pass

    def port_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        port = int(self.port_chose.currentText())
        try:
            create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
        except:
            pass

    def time_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        times = {0: 60, 1: 300, 2: 600, 3: 1800, 4: 3600}
        time = times[self.check_frequency.currentIndex()]
        frequency = self.check_frequency.currentIndex()
        try:
            create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
        except:
            pass

    def method_changed(self):
        global smtp_server, port, email, password, frequency, method, server_ip
        method = self.check_method.currentIndex()
        try:
            create_config(smtp_server, str(port), email, password, str(frequency), str(method), str(server_ip))
        except:
            pass

    def ip_server_changed(self):
        pass


class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        info_layout = QVBoxLayout()
        self.info = QLabel("Информация")
        info_layout.addWidget(self.info)
        self.setLayout(info_layout)

    
window = MainWindow("127.0.0.1", "127.0.0.1")
window.show()
app.exec()