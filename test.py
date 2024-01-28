import logging
import time
import traceback
import sys
from telnetlib import Telnet

# Класс для нестандартных исключений
class CustomError(Exception):
    pass

dut1_ip = '10.65.5.9'
dut1_port = '4007'
login = 'admin'
password = 'admin'

# Функция для входа на роутер
def login_to_router():
    connect.read_very_eager().decode('utf-8')
    connect.write(b'\n')
    time.sleep(4)
    prompt = connect.read_very_eager().decode('utf-8')
    if 'login: ' in prompt:
        connect.write(b'%b\n' %str(login).encode('utf8'))
        connect.read_until(b'Password:', timeout=5)
        connect.write(b'%b\n' %str(password).encode('utf8'))
        connect.read_until(b'#', timeout=10)
    elif 'Password: ' in prompt:
        connect.write(b'\n')
        connect.read_until(b'login: ', timeout=10)
        connect.write(b'%b\n' %str(login).encode('utf8'))
        connect.read_until(b'Password:', timeout=5)
        connect.write(b'%b\n' %str(password).encode('utf8'))
        connect.read_until(b'#', timeout=10)
    else:
        raise CustomError('Неожиданное приглашение cli, проверьте подключение к сервисному маршрутизатору')


logging.basicConfig(level=logging.INFO, format='%(levelname)s :: %(message)s')

base_config = [
    b'configure terminal',
    b'interface eth1',
    b'no ip address all',
    b'no ip address dhcp',
    b'ip address 192.168.98.10/24',
    b'no shutdown',
    b'exit',
    b'system host-name dut-t4 domain-name istok.ad',
#    b'do save base_config',
#    b'startup-profile base_config',
    b'end'
]

# Подключение к устройству
logging.info('Авторизация на DUT')
try:
    with Telnet(dut1_ip, dut1_port, timeout=10) as connect:
        login_to_router()
        connect.write(b'show version\n')
        time.sleep(5)
        version = connect.read_very_eager()
        logging.info('Версия ПО - \n{}'.format(version.decode('utf-8')))
        time.sleep(2)
        connect.write(b'show platform\n')
        time.sleep(5)
        platform = connect.read_very_eager()
        logging.info('Платформа - \n{}'.format(platform.decode('utf-8')))
        connect.write(b'exit\n')
#        for command in base_config:
#            connect.write(command + b'\n')
#            time.sleep(2)

except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('Ошибка во время установки ПО\n %s' % traceback.format_exc())
    sys.exit(1)
