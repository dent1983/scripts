import logging
import time
import traceback
import sys
from telnetlib import Telnet

# Класс для нестандартных исключений
class CustomError(Exception):
    pass

dut_ip = '10.65.12.8'
dut1_port = '4013'
dut2_port = '4014'
login = 'admin'
password = 'admin'


# Функция для входа на роутер
def login_to_router():
    connect.read_very_eager().decode('utf-8')
    connect.write(b'\n')
    time.sleep(4)
    prompt = connect.read_very_eager().decode('utf-8')
    if '#' in prompt:
        logging.info('Авторизация пройдена \n')
        connect.write(b'exit\n')
        connect.read_until(b'login: ', timeout=15)
    elif 'login: ' in prompt:
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

base_config_dut1 = [
    b'configure terminal',
    b'interface eth1',
    b'no ip address all',
    b'no ip address dhcp',
    b'ip address 192.168.98.1/24',
    b'no shutdown',
    b'exit',
    b'system host-name dut1-t4 domain-name istok.ad',
    b'end',
    b'save base_config'
]

base_config_dut2 = [
    b'configure terminal',
    b'interface eth1',
    b'no ip address all',
    b'no ip address dhcp',
    b'ip address 192.168.98.2/24',
    b'no shutdown',
    b'exit',
    b'system host-name dut2-t4 domain-name istok.ad',
    b'end',
    b'save base_config'
]

logging.info('Авторизация на DUT1')
try:
    with Telnet(dut_ip, dut1_port, timeout=10) as connect:
        login_to_router()
        connect.write(b'show version\n')
        time.sleep(2)
        version = connect.read_very_eager()
        logging.info('Версия ПО - \n{}'.format(version.decode('utf-8')))
        time.sleep(2)
        connect.write(b'show platform\n')
        time.sleep(5)
        platform = connect.read_very_eager()
        logging.info('Платформа - \n{}'.format(platform.decode('utf-8')))
        for command in base_config_dut1:
            connect.write(command + b'\n')
            time.sleep(2)
        connect.write(b'exit\n')
        time.sleep(2)

except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('Ошибка ПО\n %s' % traceback.format_exc())
    sys.exit(1)

logging.info('Авторизация на DUT2')
try:
    with Telnet(dut_ip, dut2_port, timeout=10) as connect:
        login_to_router()
        connect.write(b'show version\n')
        time.sleep(2)
        version = connect.read_very_eager()
        logging.info('Версия ПО - \n{}'.format(version.decode('utf-8')))
        time.sleep(2)
        connect.write(b'show platform\n')
        time.sleep(2)
        platform = connect.read_very_eager()
        logging.info('Платформа - \n{}'.format(platform.decode('utf-8')))
        for command in base_config_dut2:
            connect.write(command + b'\n')
            time.sleep(2)
        connect.write(b'ping 192.168.98.1 repeat 4\n')
        time.sleep(5)
        ping = connect.read_very_eager()
        logging.info('ping - \n{}'.format(ping.decode('utf-8')))
        time.sleep(2)
        connect.write(b'exit\n')
        time.sleep(2)
except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('Ошибка ПО\n %s' % traceback.format_exc())
    sys.exit(1)