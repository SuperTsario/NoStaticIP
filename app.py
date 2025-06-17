import sys
from os import remove, path
from time import sleep

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMenuBar, QLineEdit, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from main import *

basedir = path.dirname(__file__)
logo = "logo.png"

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'STFG.NoStaticIP.Server.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

# инициализация глобальных переменных и констант
VALIDATED = False

try:
    smtp_server, port, email, password, frequency, method, server_ip = load_config()
except:
    smtp_server, port, email, password, frequency, method, server_ip = None, "465", None, None, 1, 0, 0
    VALIDATED = True

def validate_config():
    global smtp_server, port, email, password, frequency, method, server_ip, VALIDATED
    if (port in ["25", "125", "465", "587", "7659", "10024", "10025"]) and validate_email(email) and (frequency in [0, 1, 2, 3, 4]) and (method in [0, 1]) and (server_ip in [0]):
        VALIDATED = True
        return True
    else:
        smtp_server, port, email, password, frequency, method, server_ip = None, "465", None, None, 1, 0, 0
        remove("config.ini")
        return False


TIMES = {0: 60, 1: 300, 2: 600, 3: 1800, 4: 3600}
time = TIMES[frequency]

last_sent_ip, last_email, last_server = load_save_file()

cycle = False

# приложение
app = QApplication([])
app.setWindowIcon(QIcon(logo))

class CycleThread(QThread):
    error_signal = pyqtSignal(int)
    ip_change_signal = pyqtSignal(str)
    sent_ip_signal = pyqtSignal(str)

    def run(self):
        global smtp_server, port, email, password, method, server_ip, time, last_sent_ip, last_email, last_server, cycle
        cycle = True
        while cycle:
            try:
                current_ip = get_ip(method)
                if current_ip != last_sent_ip or email != last_email or smtp_server != last_server:
                    self.ip_change_signal.emit(current_ip)
                    send_mail(current_ip, smtp_server, port, email, password)
                    self.sent_ip_signal.emit(current_ip)
                    create_save_file(current_ip, email, last_server)
                    last_sent_ip = current_ip
                    last_email = email
                    last_server = smtp_server
                    sleep(time)
            except smtplib.SMTPAuthenticationError:
                cycle = False
                self.error_signal.emit(1)
            except gaierror:
                cycle = False
                self.error_signal.emit(2)
            except SSLError:
                cycle = False
                self.error_signal.emit(3)
            except TimeoutError:
                cycle = False
                self.error_signal.emit(4)
            except:
                cycle = False
                self.error_signal.emit(5)


class MainWindow(QMainWindow):
    def __init__(self, last_ip):
        super().__init__()
        self.setWindowTitle("NoStaticIP")
        self.setMinimumSize(320, 240)
        self.setMaximumSize(420, 340)
        self.setWindowIcon(QIcon(logo))

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

        self.cycle_thread = CycleThread()
        self.cycle_thread.error_signal.connect(self.handle_error)
        self.cycle_thread.ip_change_signal.connect(self.changed_ip)
        self.cycle_thread.sent_ip_signal.connect(self.sent_ip)

        self.send_ip_button.repaint()

        if not VALIDATED:
            if not validate_config():
                config_error = QMessageBox(self)
                config_error.setWindowTitle("Неправильный файл конфигурации")
                config_error.setText("Файл конфигурации не может быть загружен, так как был изменен вручную.")
                config_error.setIcon(QMessageBox.Icon.Critical)
                config_error.setWindowIcon(QIcon(logo))
                button = config_error.exec()

    def handle_error(self, error):
        if error == 1:
            title = "Ошибка аунтефикации"
            text = "Неверный логин или пароль!"
        elif error == 2:
            title = "Ошибка сервера"
            text = "Невозможно подключиться к SMTP-серверу!"
        elif error == 3:
            title = "Ошибка порта"
            text = "Выбран неверный порт SMTP-сервера!"
        elif error == 4:
            title = "Ошибка подключения"
            text = "Истекло время подключения!"
        elif error == 5:
            title = "Ошибка"
            text = "Непредвиденная ошибка!"
        error = QMessageBox(self)
        error.setWindowTitle(title)
        error.setText(text)
        error.setIcon(QMessageBox.Icon.Critical)
        error.setWindowIcon(QIcon(logo))
        error.exec()

        self.start.setText("Начать")
        self.start.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
        self.start.repaint()


    def changed_ip(self, ip):
        self.current_ip_label.setText(f"Ваш IP сейчас:\n{ip}")

    def sent_ip(self, ip):
        self.last_sent_ip.setText(f"Последний отправленный IP:\n{ip}")

    def start_or_stop_cycle(self):
        global cycle
        if not cycle:
            if smtp_server is not None or email is not None or password is not None:
                self.start.setText("Остановить")
                self.start.setStyleSheet('QPushButton {background-color: #cc0a0a; color: white;} QPushButton:hover {color: black;}')
                self.start.repaint()
                self.cycle_thread.start()
                cycle = True
            else:
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка запуска")
                error.setText("Запуск невозможен из-за отсутствия данных!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
        elif cycle:
            self.start.setText("Начать")
            self.start.setStyleSheet('QPushButton {background-color: #0067c0; color: white;} QPushButton:hover {color: black;}')
            self.start.repaint()
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
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка аунтефикации")
                error.setText("Неверный логин или пароль!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
            except gaierror:
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка сервера")
                error.setText("Невозможно подключиться к SMTP-серверу!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
            except SSLError:
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка порта")
                error.setText("Выбран неверный порт SMTP-сервера!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
            except TimeoutError:
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка подключения")
                error.setText("Истекло время подключения!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
            except:
                error = QMessageBox(self)
                error.setWindowTitle("Ошибка")
                error.setText("Непредвиденная ошибка!")
                error.setIcon(QMessageBox.Icon.Critical)
                error.setWindowIcon(QIcon(logo))
                error.exec()
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
        self.setMinimumSize(400, 260)
        self.setMaximumSize(500, 350)
        self.setWindowIcon(QIcon(logo))
        grid = QGridLayout()
        buttons_layout = QHBoxLayout()
        global_layout = QVBoxLayout()

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
        

        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setMinimumHeight(30)
        

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete)
        self.delete_button.setStyleSheet('QPushButton {background-color: #cc0a0a; color: white;} QPushButton:hover {color: black;}')
        self.delete_button.setMinimumHeight(30)

        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.cancel_button)        
        buttons_layout.addWidget(self.save_button)

        global_layout.addLayout(grid)
        global_layout.addLayout(buttons_layout)
        self.setLayout(global_layout)

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

        if email_s is None or not validate_email(email_s):
            email_broken = QMessageBox(self)
            email_broken.setWindowTitle("Ошибка сохранения")
            email_broken.setText("Введенный email недействителен!")
            email_broken.setIcon(QMessageBox.Icon.Critical)
            email_broken.setWindowIcon(QIcon(logo))
            button = email_broken.exec()
        
        elif (password_s is None) or (password_s == "") or (" " in password_s):
            password_broken = QMessageBox(self)
            password_broken.setWindowTitle("Ошибка записи")
            password_broken.setText("Введенный пароль недействителен!")
            password_broken.setIcon(QMessageBox.Icon.Critical)
            password_broken.setWindowIcon(QIcon(logo))
            button = password_broken.exec()

        elif (smtp_server_s is None) or (smtp_server_s == "") or (" " in smtp_server_s):
            smtp_broken = QMessageBox(self)
            smtp_broken.setWindowTitle("Ошибка записи")
            smtp_broken.setText("Введенный smtp-сервер недействителен!")
            smtp_broken.setIcon(QMessageBox.Icon.Critical)
            smtp_broken.setWindowIcon(QIcon(logo))
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
            save_dialog.setWindowIcon(QIcon(logo))
            button = save_dialog.exec()
            if button == QMessageBox.StandardButton.Ok:
                pass

    def cancel(self):
        self.close()

    def delete(self):
        question = QMessageBox()
        question.setWindowTitle("Удаление конфигурации")
        question.setText("Данное действие уничтожит ваши настройки.\nВы уверены, что хотите продолжить?")
        question.setIcon(QMessageBox.Icon.Warning)
        question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        question.setWindowIcon(QIcon(logo))
        answer = question.exec()
        if answer == QMessageBox.StandardButton.Yes:
            self.smtp_server_line.setText(None)
            self.password_line.setText(None)
            self.email_line.setText(None)
            self.email_line.setPlaceholderText("example@example.com")
            self.port_chose.setCurrentIndex(2)
            self.check_frequency.setCurrentIndex(1)
            self.check_method.setCurrentIndex(0)
            self.ip_server.setCurrentIndex(0)
            if path.exists("config.ini"):
                remove("config.ini")
            result = QMessageBox()
            result.setWindowTitle("Удаление конфигурации")
            result.setText("Ваша конфигурация удалена.")
            result.setIcon(QMessageBox.Icon.Information)
            result.setWindowIcon(QIcon(logo))
            result.exec()
        else:
            pass
    def email_changed(self):
        text = self.email_line.text()
        if validate_email(text):
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
        self.setWindowIcon(QIcon(logo))
        self.special = ""
        info_layout = QVBoxLayout()
        self.info = QLabel("Информация о программе\n\nNoStaticIP\nВерсия: 1.0.0\nНомер сборки: 0001\n\n\u00a9Максим Легкий\n2025\n")
        # self.special_label = QLabel("Программа собрана специально для Татьяны Викторовны")
        # self.special_label.setStyleSheet('color: red;')
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.special_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.info)
        # info_layout.addWidget(self.special_label)
        self.setLayout(info_layout)
        self.setFixedSize(350, 200)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.special += "L"
        elif event.button() == Qt.MouseButton.RightButton:
            self.special += "R"
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.special += "M"

        if self.special == "LLMRL":
            # self.special_label.hide()
            self.info.setStyleSheet('color: red;')
            self.info.repaint()
            sleep(1)
            self.info.setStyleSheet('color: blue;')
            self.info.repaint()
            sleep(1)
            self.info.setStyleSheet('color: green;')
            self.info.repaint()
            sleep(1)
            self.info.setStyleSheet('color: gold;')
            self.info.repaint()
            sleep(1)
            self.info.setStyleSheet('color: black;')
            self.info.repaint()
            # self.setFixedSize(800, 500)


window = MainWindow(last_sent_ip)
if VALIDATED:
    window.show()
    sys.exit(app.exec())
