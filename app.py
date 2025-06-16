import sys
from re import fullmatch

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMenuBar, QLineEdit, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction

from main import *
import threading

# инициализация глобальных переменных и констант
try:
    smtp_server, port, email, password, frequency, method, server_ip = load_config()
except:
    smtp_server, port, email, password, frequency, method, server_ip = None, "465", None, None, 1, 0, 0

TIMES = {0: 60, 1: 300, 2: 600, 3: 1800, 4: 3600}
time = TIMES[frequency]

last_sent_ip, last_email, last_server = load_save_file()

cycle = False

# приложение
app = QApplication([])

class MainWindow(QMainWindow):
    def __init__(self, last_ip):
        super().__init__()
        self.setWindowTitle("NoStaticIP")
        self.setMinimumSize(320, 200)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        settings_menu = QAction("Настройки", self)
        self.menu_bar.addAction(settings_menu)
        settings_menu.triggered.connect(self.settings_window)

        info_menu = QAction("Информация", self)
        self.menu_bar.addAction(info_menu)
        info_menu.triggered.connect(self.info_window)

        layout = QVBoxLayout()

        self.current_ip_label = QLabel(f"Ваш IP сейчас:\n{get_ip(method)}")
        self.check_ip_button = QPushButton("Проверить IP")
        self.check_ip_button.setMinimumSize(300, 30)
        self.check_ip_button.clicked.connect(self.check_ip)
        self.last_sent_ip = QLabel(f"Последний отправленный IP:\n{last_ip}")
        self.send_ip_button = QPushButton("Отправить IP")
        self.send_ip_button.setMinimumSize(300, 30)
        self.send_ip_button.clicked.connect(self.send_ip)
        
        self.start = QPushButton("Начать")
        self.start.setMinimumSize(300, 30)
        self.start.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
        # self.start.setCheckable(True)
        self.start.clicked.connect(self.start_or_stop_cycle)

        layout.addWidget(self.current_ip_label)
        layout.addWidget(self.check_ip_button)
        layout.addWidget(self.last_sent_ip)
        layout.addWidget(self.send_ip_button)
        layout.addWidget(self.start)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def cycle_of_checking(self):
        global smtp_server, port, email, password, method, server_ip, time, last_sent_ip, last_email, last_server, cycle
        self.do = True
        while self.do:
            try:
                current_ip = get_ip(method)
                if current_ip != last_sent_ip or email != last_email or smtp_server != last_server:
                    self.current_ip_label.setText(f"Ваш IP сейчас:\n{current_ip}")
                    send_mail(current_ip, smtp_server, port, email, password)
                    self.last_sent_ip.setText(f"Последний отправленный IP:\n{current_ip}")
                    create_save_file(current_ip, email, last_server)
                    last_sent_ip = current_ip
                    last_email = email
                    last_server = smtp_server
                    sleep(time)
            except smtplib.SMTPAuthenticationError:
                self.do = False
                cycle = False
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка аунтефикации")
                erorr.setText("Неверный логин или пароль!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except socket.gaierror:
                self.do = False
                cycle = False
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка сервера")
                erorr.setText("Невозможно подключиться к SMTP-серверу!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except ssl.SSLError:
                self.do = False
                cycle = False
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка порта")
                erorr.setText("Выбран неверный порт SMTP-сервера!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except TimeoutError:
                self.do = False
                cycle = False
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка подключения")
                erorr.setText("Истекло время подключения!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except:
                self.do = False
                cycle = False
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка")
                erorr.setText("Непредвиденная ошибка!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            finally:
                self.do = False
                cycle = False
                self.start.setText("Начать")
                self.start.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
                self.start.repaint()

    def start_or_stop_cycle(self):
        global cycle
        if not cycle:
            if smtp_server is not None or email is not None or password is not None:
                self.start.setText("Остановить")
                self.start.setStyleSheet('QPushButton {background-color: #cc0a0a; color: white;} QPushButton:hover {color: black;}')
                self.start.repaint()
                self.check_tread = threading.Thread(target=self.cycle_of_checking, daemon=True)
                self.check_tread.start()
                self.check_tread.join()
                cycle = True
            else:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка запуска")
                erorr.setText("Запуск невозможен из-за отсутствия данных!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
        elif cycle:
            self.start.setText("Начать")
            self.start.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
            self.start.repaint()
            self.do = False
            cycle = False

    def check_ip(self):
        global method
        self.check_ip_button.setText("Выполняется проверка...")
        self.check_ip_button.repaint()
        self.check_ip_button.setEnabled(False)
        ip = get_ip(method)
        if ip is None:
            self.current_ip_label.setText(f"Ваш IP не был получен из-за ошибки.\nПопробуйте еще раз или измените метод.")
        else:
            self.current_ip_label.setText(f"Ваш IP сейчас:\n{ip}")
        self.check_ip_button.setEnabled(True)
        self.check_ip_button.setText("Проверить IP")
        self.check_ip_button.repaint()

    def send_ip(self):
        self.send_ip_button.setEnabled(False)
        self.send_ip_button.setText("Отправляется...")
        self.send_ip_button.repaint()
        global smtp_server, port, email, password, method, server_ip, last_sent_ip
        ip_to_send = get_ip(method)
        if ip_to_send is None:
            self.current_ip_label.setText(f"Ваш IP не был получен из-за ошибки.\nПопробуйте еще раз или измените метод.")
            self.send_ip_button.setEnabled(True)
            self.send_ip_button.setText("Отправить IP")
            self.send_ip_button.repaint()
        else:
            try:
                send_mail(ip_to_send, smtp_server, int(port), email, password)
                last_sent_ip = ip_to_send
                self.current_ip_label.setText(f"Ваш IP сейчас:\n{ip_to_send}")
                self.last_sent_ip.setText(f"Последний отправленный IP:\n{last_sent_ip}")
                create_save_file(last_sent_ip, email, smtp_server)
            except smtplib.SMTPAuthenticationError:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка аунтефикации")
                erorr.setText("Неверный логин или пароль!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except socket.gaierror:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка сервера")
                erorr.setText("Невозможно подключиться к SMTP-серверу!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except ssl.SSLError:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка порта")
                erorr.setText("Выбран неверный порт SMTP-сервера!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except TimeoutError:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка подключения")
                erorr.setText("Истекло время подключения!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            except:
                erorr = QMessageBox(self)
                erorr.setWindowTitle("Ошибка")
                erorr.setText("Непредвиденная ошибка!")
                erorr.setIcon(QMessageBox.Icon.Critical)
                button = erorr.exec()
            finally:
                self.send_ip_button.setEnabled(True)
                self.send_ip_button.setText("Отправить IP")
                self.send_ip_button.repaint()

    def settings_window(self):
        global email, password, smtp_server, port, frequency, method, server_ip
        self.sw = SettingsWindow(email, password, smtp_server, str(port), frequency, method, server_ip)
        self.sw.show()

    def info_window(self):
        self.iw = InfoWindow()
        self.iw.show()



class SettingsWindow(QWidget):
    def __init__(self, email, password, smtp_server, port, frequency, method, server_ip):
        global cycle
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setMinimumSize(400, 250)
        grid = QGridLayout()

        self.smtp_server_line = QLineEdit()
        self.smtp_label = QLabel("Ваш SMTP сервер:")
        self.smtp_server_line.setPlaceholderText("smtp.example.com")
        self.smtp_server_line.setText(smtp_server)
        grid.addWidget(self.smtp_label, 0, 0)
        grid.addWidget(self.smtp_server_line, 0, 1)

        self.port_chose = QComboBox()
        self.port_label = QLabel("Порт SMTP сервера:")
        self.port_chose.addItems(["25", "125", "465", "587", "7659", "10024", "10025"])
        self.port_chose.setCurrentText(port)
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
        self.password_label = QLabel("Пароль приложения SMTP сервера:")
        self.password_line.setPlaceholderText("password")
        self.password_line.setText(password)
        grid.addWidget(self.password_label, 3, 0)
        grid.addWidget(self.password_line, 3, 1)

        self.check_frequency = QComboBox()
        self.freq_label = QLabel("Частота проверки IP-адреса:")
        self.check_frequency.addItems(["1 минута", "5 минут", "10 минут", "30 минут", "1 час"])
        self.check_frequency.setCurrentIndex(frequency)
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
        grid.addWidget(self.ip_server_label, 6, 0)
        grid.addWidget(self.ip_server, 6, 1)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)
        self.save_button.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
        self.save_button.setMinimumHeight(30)
        grid.addWidget(self.save_button, 7, 1)

        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setMinimumHeight(30)
        grid.addWidget(self.cancel_button, 7, 0)

        self.setLayout(grid)

        if method == 1:
            self.ip_server.setEnabled(False)
        else:
            self.ip_server.setEnabled(True)

        if cycle:
            self.smtp_server_line.setEnabled(False)
            self.port_chose.setEnabled(False)
            self.email_line.setEnabled(False)
            self.password_line.setEnabled(False)
            self.check_frequency.setEnabled(False)
            self.check_method.setEnabled(False)
            self.ip_server.setEnabled(False)
            self.save_button.setEnabled(False)
            self.save_button.setStyleSheet('QPushButton {background-color: #bdbdbd; color: gray;}')
            self.cancel_button.setEnabled(False)
    
    def save(self):
        global smtp_server, port, email, password, frequency, method, server_ip, time, TIMES

        email_s = self.email_line.text()
        password_s = self.password_line.text()
        smtp_server_s = self.smtp_server_line.text()
        port_s = self.port_chose.currentText()
        frequency_s = self.check_frequency.currentIndex()
        method_s = self.check_method.currentIndex()
        server_ip_s = self.ip_server.currentIndex()

        ptn = r"^\S+@\S+\.\S+$"
        if email_s is None or fullmatch(ptn, email_s) is None:
            email_broken = QMessageBox(self)
            email_broken.setWindowTitle("Ошибка сохранения")
            email_broken.setText("Введенный email недействителен!")
            email_broken.setIcon(QMessageBox.Icon.Critical)
            button = email_broken.exec()
        
        elif (password_s is None) or (password_s == "") or (" " in password_s):
            password_broken = QMessageBox(self)
            password_broken.setWindowTitle("Ошибка записи")
            password_broken.setText("Введенный пароль недействителен!")
            password_broken.setIcon(QMessageBox.Icon.Critical)
            button = password_broken.exec()

        elif (smtp_server_s is None) or (smtp_server_s == "") or (" " in smtp_server_s):
            smtp_broken = QMessageBox(self)
            smtp_broken.setWindowTitle("Ошибка записи")
            smtp_broken.setText("Введенный smtp-сервер недействителен!")
            smtp_broken.setIcon(QMessageBox.Icon.Critical)
            button = smtp_broken.exec()

        else:
            create_config(smtp_server_s, port_s, email_s, password_s, frequency_s, method_s, server_ip_s)
            smtp_server = smtp_server_s
            port = int(port_s)
            email = email_s
            password = password_s
            frequency = frequency_s
            method = int(method_s)
            server_ip = int(server_ip_s)
            time = TIMES[frequency]
            save_dialog = QMessageBox(self)
            save_dialog.setWindowTitle("Сохранение настроек")
            save_dialog.setText("Изменения сохранены")
            save_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            save_dialog.setIcon(QMessageBox.Icon.Information)
            button = save_dialog.exec()
            if button == QMessageBox.StandardButton.Ok:
                pass

    def cancel(self):
        self.close()

    def email_changed(self):
        text = self.email_line.text()
        ptn = r"^\S+@\S+\.\S+$"
        if fullmatch(ptn, text) is not None:
            pass
        else:
            self.email_line.setText("")
            self.email_line.setPlaceholderText("Неверный адрес!")

    def method_changed(self):
        global method
        method = self.check_method.currentIndex()
        print(method)
        if method == 1: 
            self.ip_server.setEnabled(False)
        else:
            self.ip_server.setEnabled(True)

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация")
        self.special = ""
        info_layout = QVBoxLayout()
        self.info = QLabel("Информация о программе\n\nNoStaticIP\nВерсия: 1.0.0\nНомер сборки: 0001\n\n\u00a9Maksim Legkii\n2025")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.info)
        self.setLayout(info_layout)
        self.setMinimumSize(300, 150)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.special += "L"
        elif event.button() == Qt.MouseButton.RightButton:
            self.special += "R"
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.special += "M"

        if self.special == "LLMRL":
            self.info.setText("""
Государственное автономное нетиповое образовательное учреждение Свердловской области «Губернаторский лицей»
(ГАНОУ СО «Губернаторский лицей»)


Предметная область: информатика






Проект
«Создание системы передачи IP-адреса для использования RDP»








Автор проекта: Легкий Максим Борисович, 10Ш
Научный руководитель проекта: Александров Иван Николаевич




2025 

""")
            self.setFixedSize(800, 500)


window = MainWindow(last_sent_ip)
window.show()
sys.exit(app.exec())