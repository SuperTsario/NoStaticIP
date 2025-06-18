import smtplib
import http.client
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from stun import get_ip_info
from socket import gaierror
from ssl import SSLError
from re import fullmatch
from os import remove, path, getenv, makedirs

BASEDIR = path.dirname(__file__)
APPDATADIR = path.join(getenv('APPDATA'), "STFG", "NoStaticIP")
if not(path.exists(APPDATADIR)):
    makedirs(APPDATADIR)
CONFIG_FILE = path.join(APPDATADIR, "config.ini")
LOGO = path.join(BASEDIR, "logo.png")
SAVE_FILE = path.join(APPDATADIR, "save")
FIRST_START_DIR = path.join(APPDATADIR, "firststart")
IS_FIRST_START = not(path.exists(FIRST_START_DIR))

def create_save_file(ip, email, server):
    file = open(SAVE_FILE, "w")
    file.write(f"{ip}\n{email}\n{server}")
    file.close()

def load_save_file():
    try:
        file = open(SAVE_FILE, "r")
        save = file.readlines()
        file.close()
        return save[0], save[1], save[2]
    except:
        return "0.0.0.0", "example@example.com", "smtp.example.com"
    

def create_config(server, port, login, password, frequency, method, ip_server):
    global CONFIG_FILE
    config = configparser.ConfigParser()
    config.add_section("ACCOUNT")
    config.add_section("SETTINGS")
    config.set("ACCOUNT", "server", server)
    config.set("ACCOUNT", "port", str(port))
    config.set("ACCOUNT", "login", login)
    config.set("ACCOUNT", "password", password)
    config.set("SETTINGS", "frequency", str(frequency))
    config.set("SETTINGS", "method", str(method))
    config.set("SETTINGS", "ip_server", str(ip_server))
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    server = config.get("ACCOUNT", "server")
    port = config.get("ACCOUNT", "port")
    login = config.get("ACCOUNT", "login")
    password = config.get("ACCOUNT", "password")
    frequency = config.get("SETTINGS", "frequency")
    method = config.get("SETTINGS", "method")
    ip_server = config.get("SETTINGS", "ip_server")
    return server, port, login, password, int(frequency), int(method), int(ip_server)

def get_ip_by_server():
    try:
        conn = http.client.HTTPConnection("ifconfig.me")
        conn.request("GET", "/ip")
        return conn.getresponse().read().decode()
    except:
        return None

def get_ip_by_stun():
    info = get_ip_info()
    return info[1]

def get_ip(method):
    if method == 0:
        return get_ip_by_server()
    else:
        return get_ip_by_stun()

def send_mail(ip, server, port, login, password):
    connection = smtplib.SMTP_SSL(server, port)
    connection.login(login, password)
    connection.send_message(create_message(ip, login))
    connection.quit()

def create_message(ip, login):
    message = MIMEMultipart("alternative")
    message["Subject"], message["From"], message["To"] = "Ваш IP", login, login
    html = f"""<html><body><p>Ваш IP сейчас: {ip}</p></body></html>"""
    message.attach(MIMEText(html, "html"))
    return message

def validate_email(email):
    EMAIL_PATTERN = r"^\S+@\S+\.\S+$"
    if fullmatch(EMAIL_PATTERN, email) is None:
        return False
    else:
        return True