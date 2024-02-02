import logging
import time
import traceback
import sys
from telnetlib import Telnet
from netmiko import ConnectHandler

dut_ip = '10.65.12.8'
dut1_port = '4013'
dut2_port = '4014'
login = 'admin'
password = 'admin'

test_description = '''DUT2 анонсирует префиксы 200.1.0.0/24 – 200.1.9.0/24 и 1.18.116.0/24 для DUT1.
На DUT1 необходимо отфильтровать префиксы 200.1.0.0/24 – 200.1.9.0/24, принимаемые от DUT2.
Таким образом в таблице маршрутизации должен остаться префикс 1.18.116.0/24 принимаемый от DUT2.
Фильтрация должна быть осуществлена следующим образом: 
- префикс 1.18.116.0/24 разрешен;
- остальные префиксы запрещены.'''


# Класс для нестандартных исключений
class CustomError(Exception):
    pass

# Функция для входа на роутер
def login_to_router():
    connect.read_very_eager().decode('utf-8')
    connect.write(b'\n')
    time.sleep(4)
    prompt = connect.read_very_eager().decode('utf-8')
    if '#' in prompt:
        logging.info('Авторизация пройдена')
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

# Настройка логирования событий
logging.basicConfig(level=logging.INFO, format='%(levelname)s :: %(message)s')

# Конфигурация устройства DUT1
base_config_dut1 = [
    b'configure terminal',
    b'interface eth1',
    b'no ip address all',
    b'no ip address dhcp',
    b'ip address 100.1.0.1/24',
    b'no shutdown',
    b'exit',
    b'system host-name dut1-t4 domain-name istok.ad',
    b'interface lo 1',
    b'no shutdown',
    b'ip address 198.18.255.1/32',
    b'exit',
    b'interface lo 2',
    b'no shutdown',
    b'ip address 198.18.255.2/32',
    b'exit',
    b'interface lo 3',
    b'no shutdown',
    b'ip address 198.18.255.3/32',
    b'exit',
    b'interface lo 4',
    b'no shutdown',
    b'ip address 198.18.255.4/32',
    b'exit',
    b'interface lo 5',
    b'no shutdown',
    b'ip address 198.18.255.5/32',
    b'exit',
    b'interface lo 6',
    b'no shutdown',
    b'ip address 198.18.255.6/32',
    b'exit',
    b'interface lo 7',
    b'no shutdown',
    b'ip address 198.18.255.7/32',
    b'exit',
    b'interface lo 8',
    b'no shutdown',
    b'ip address 198.18.255.8/32',
    b'exit',
    b'interface lo 9',
    b'no shutdown',
    b'ip address 198.18.255.9/32',
    b'exit',
    b'interface lo 10',
    b'no shutdown',
    b'ip address 198.18.255.10/32',
    b'exit',
    b'router bgp 65001',
    b'bgp router-id 100.1.0.1',
    b'network 198.18.255.1/32',
    b'network 198.18.255.2/32',
    b'network 198.18.255.3/32',
    b'network 198.18.255.4/32',
    b'network 198.18.255.5/32',
    b'network 198.18.255.6/32',
    b'network 198.18.255.7/32',
    b'network 198.18.255.8/32',
    b'network 198.18.255.9/32',
    b'network 198.18.255.10/32',
    b'neighbor 100.1.0.2 remote-as 65002',
    b'exit',
    b'ip prefix-list d35870-t1 seq 10 permit 1.18.116.0/24',
    b'ip prefix-list d35870-t1 seq 20 deny any',
    b'router bgp 65001',
    b'neighbor 100.1.0.2 prefix-list d35870-t1 in',
    b'end',
    b'clear ip bgp 100.1.0.2 in'
]
# Конфигурация устройства DUT2
base_config_dut2 = [
    b'configure terminal',
    b'interface eth1',
    b'no ip address all',
    b'no ip address dhcp',
    b'ip address 100.1.0.2/24',
    b'no shutdown',
    b'exit',
    b'system host-name dut2-t4 domain-name istok.ad',
    b'interface lo 1',
    b'no shutdown',
    b'ip address 201.1.0.1/32',
    b'exit',
    b'interface lo 2',
    b'no shutdown',
    b'ip address 201.1.0.2/32',
    b'exit',
    b'interface lo 3',
    b'no shutdown',
    b'ip address 201.1.0.3/32',
    b'exit',
    b'interface lo 4',
    b'no shutdown',
    b'ip address 201.1.0.4/32',
    b'exit',
    b'interface lo 5',
    b'no shutdown',
    b'ip address 201.1.0.5/32',
    b'exit',
    b'interface lo 6',
    b'no shutdown',
    b'ip address 201.1.0.6/32',
    b'exit',
    b'interface lo 7',
    b'no shutdown',
    b'ip address 201.1.0.7/32',
    b'exit',
    b'interface lo 8',
    b'no shutdown',
    b'ip address 201.1.0.8/32',
    b'exit',
    b'interface lo 9',
    b'no shutdown',
    b'ip address 201.1.0.9/32',
    b'exit',
    b'interface lo 10',
    b'no shutdown',
    b'ip address 201.1.0.10/32',
    b'exit',
    b'interface lo 11',
    b'no shutdown',
    b'ip address 1.18.116.1/24',
    b'exit',
    b'router bgp 65002',
    b'bgp router-id 100.1.0.2',
    b'network 201.1.0.1/32',
    b'network 201.1.0.2/32',
    b'network 201.1.0.3/32',
    b'network 201.1.0.4/32',
    b'network 201.1.0.5/32',
    b'network 201.1.0.6/32',
    b'network 201.1.0.7/32',
    b'network 201.1.0.8/32',
    b'network 201.1.0.9/32',
    b'network 201.1.0.10/32',
    b'network 1.18.116.0/24',
    b'neighbor 100.1.0.1 remote-as 65001',
    b'exit',
    b'end'
]

# Вывод цели тестирования
logging.info('--------------------------------------------------------------------------------------------')
logging.info(test_description)
logging.info('--------------------------------------------------------------------------------------------')
# Выполнение сценария на DUT1
logging.info('Авторизация на DUT1')
logging.info('--------------------------------------------------------------------------------------------')
try:
    with Telnet(dut_ip, dut1_port, timeout=10) as connect:
        login_to_router()
        connect.write(b'load startup\n')
        time.sleep(45)
        logging.info('Настраиваем конфигурацию на DUT1')
        logging.info('--------------------------------------------------------------------------------------------')
        for command in base_config_dut1:
            connect.write(command + b'\n')
            time.sleep(2)
        connect.write(b'exit\n')
        time.sleep(2)
        connect.close()
        time.sleep(2)
except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('При выполнении теста возникла ошибка - \n %s' % traceback.format_exc())
    logging.info('--------------------------------------------------------------------------------------------')
    sys.exit(1)

# Выполнение сценария на DUT2
logging.info('Авторизация на DUT2')
logging.info('--------------------------------------------------------------------------------------------')
try:
    with Telnet(dut_ip, dut2_port, timeout=10) as connect:
        login_to_router()
        connect.write(b'load startup\n')
        time.sleep(45)
        logging.info('Настраиваем конфигурацию на DUT2')
        logging.info('--------------------------------------------------------------------------------------------')
        for command in base_config_dut2:
            connect.write(command + b'\n')
        time.sleep(2)
        connect.write(b'exit\n')
        time.sleep(2)
        connect.close()
        time.sleep(2)
except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('При выполнении теста возникла ошибка - \n %s' % traceback.format_exc())
    sys.exit(1)

time.sleep(5)

def ssh_res():
    net_connect = ConnectHandler(
        device_type="linux",
        host='10.65.12.5',
        username='admin',
        password='admin',
    )
    answer = net_connect.send_command("show ip route")
    logging.info(answer)
    return answer

logging.info('Сравниваем результаты c эталонными значениями')
logging.info('--------------------------------------------------------------------------------------------')
time.sleep(5)
try:
    res = ssh_res()
    time.sleep(2)
    if '1.18.116.0/24' in str(res) and '201.1.0.' not in str(res):
        logging.info('--------------------------------------------------------------------------------------------')
        logging.info('Тест пройден успешно')
        logging.info('--------------------------------------------------------------------------------------------')
    else:
        logging.error('--------------------------------------------------------------------------------------------')
        logging.error('Тест не пройден')
        logging.error('--------------------------------------------------------------------------------------------')
except CustomError as e:
    logging.error(e)
    sys.exit(1)
except:
    logging.error('При выполнении теста возникла ошибка - \n %s' % traceback.format_exc())
    sys.exit(1)
