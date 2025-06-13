import smtplib
import http.client
import configparser
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from stun import get_ip_info

def create_config(server, port, login, password, frequency, method, ip_server):
    config = configparser.ConfigParser()
    config.add_section("INFO")
    config.set("INFO", "server", server)
    config.set("INFO", "port", str(port))
    config.set("INFO", "login", login)
    config.set("INFO", "password", password)
    config.set("INFO", "frequency", frequency)
    config.set("INFO", "method", method)
    config.set("INFO", "ip_server", ip_server)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    server = config.get("INFO", "server")
    port = config.get("INFO", "port")
    login = config.get("INFO", "login")
    password = config.get("INFO", "password")
    frequency = config.get("INFO", "frequency")
    method = config.get("INFO", "method")
    ip_server = config.get("INFO", "ip_server")
    return server, port, login, password, int(frequency), int(method), int(ip_server)

def get_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

def get_ip_stun():
    info = get_ip_info()
    return info[1]

def send_mail(ip, server, port, login, password):
    connection = smtplib.SMTP_SSL(server, port)
    connection.login(login, password)
    connection.send_message(create_message(ip))
    connection.quit()

def create_message(ip, login):
    message = MIMEMultipart("alternative")
    message["Subject"], message["From"], message["To"] = "Ваш IP", login, login
    html = f"""<html><body><p>Ваш IP сейчас: {ip}</p></body></html>"""
    message.attach(MIMEText(html, "html"))
    return message
