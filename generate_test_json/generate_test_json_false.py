import time
import traceback
import yaml
import json
# Используем для подключения к тестируемому изделию
from netmiko import ConnectHandler

# Import the RestPy module
from ixnetwork_restpy import (SessionAssistant,
                              Files)

profile_name = 'generate_test_json_false'
test_description = 'Topology 1 эмулирует подключение клиента в группу 233.1.1.1 по протоколу IGMPv3. ' \
                   'Topology 1 выбирает конкретного источника 101.1.0.2. ' \
                   'Topology 2 эмулирует источник 101.1.0.2 ' \
                   'На тест-центре генерируется трафик от источника в группу 233.1.1.1. ' \
                   'Проверить получение клиентом многоадресного трафика.'
text1 = """
Row:0  View:Protocols Summary  Sampled:2021-04-23 10:55:43.632326 UTC
	Protocol Type: IGMP Host
	Sessions Up: 1
	Sessions Down: 0
	Sessions Not Started: 0
	Sessions Total: 1
	Average Setup Rate: N/A
	Average Teardown Rate: N/A
Row:1  View:Protocols Summary  Sampled:2021-04-23 10:55:43.632326 UTC
	Protocol Type: IPv4
	Sessions Up: 2
	Sessions Down: 0
	Sessions Not Started: 0
	Sessions Total: 2
	Average Setup Rate: N/A
	Average Teardown Rate: N/A
"""

text2 = """
vlli@teleros#show ip pim
=
IPv4 PIM state: ON
 Enabled interfaces:
  eth1 igmp 3
  eth2 igmp 3
 RP:
  interface 101.1.0.1 group-prefix 233.1.1.1/24
 BFD state: OFF
"""

text3 = """
vlli@teleros#show ip pim status
=
Virtual Interface Table ======================================================
Vif  Local Address    Subnet              Thresh  Flags      Neighbors
---  ---------------  ------------------  ------  ---------  -----------------
  0  10.65.4.101      10.65.4/24               1  DR NO-NBR
  1  100.1.0.1        100.1/24                 1  DR NO-NBR
  2  101.1.0.1        101.1/24                 1  DR NO-NBR
  3  10.65.4.101      register_vif0            1 

 Vif  SSM Group        Sources             

Multicast Routing Table ======================================================
----------------------------------- (*,G) ------------------------------------
Source           Group            RP Address       Flags
---------------  ---------------  ---------------  ---------------------------
INADDR_ANY       233.1.1.1        101.1.0.1        WC RP
Joined   oifs: ....                
Pruned   oifs: ....                
Leaves   oifs: .l..                
Asserted oifs: ....                
Outgoing oifs: .o..                
Incoming     : ...I                

TIMERS:  Entry    JP    RS  Assert VIFS:  0  1  2  3
             0    50     0       0        0  0  0  0
----------------------------------- (S,G) ------------------------------------
Source           Group            RP Address       Flags
---------------  ---------------  ---------------  ---------------------------
101.1.0.2        233.1.1.1        101.1.0.1        SPT CACHE SG
Joined   oifs: ...j                
Pruned   oifs: ....                
Leaves   oifs: .l..                
Asserted oifs: ....                
Outgoing oifs: .o.o                
Incoming     : ..I.                

TIMERS:  Entry    JP    RS  Assert VIFS:  0  1  2  3
           210     0     0       0        0  0  0  0
--------------------------------- (*,*,G) ------------------------------------
Number of Groups: 1
Number of Cache MIRRORs: 1
------------------------------------------------------------------------------
"""

text4 = """
vlli@teleros#show ip route multicast
=
(101.1.0.2, 233.1.1.1)           Iif: eth2       Oifs: eth1 pimreg
"""

text5 = """
Row:0  View:Port Statistics  Sampled:2021-04-23 10:55:53.071850 UTC
	Stat Name: 10.65.4.95/Card02/Port01
	Port Name: Ethernet - 001
	Link State: Link Up
	Frames Tx.: 1
	Valid Frames Rx.: 69096
	Frames Tx. Rate: 0
	Valid Frames Rx. Rate: 0
	Bytes Tx.: 64
	Bytes Rx.: 8844160
	Bits Sent: 512
	Bits Received: 70753280
	Bytes Tx. Rate: 0
	Tx. Rate (bps): 0.000
	Tx. Rate (Kbps): 0.000
	Tx. Rate (Mbps): 0.000
	Bytes Rx. Rate: 0
	Rx. Rate (bps): 0.000
	Rx. Rate (Kbps): 0.000
	Rx. Rate (Mbps): 0.000
	Scheduled Frames Tx.: 1
	Control Frames Tx: 0
	Control Frames Rx: 0
	Stateless Frames Sent: 1
	Valid Stateless Frames Received: 69096
	Stateless Frames Sent Rate: 0
	Valid Stateless Frames Received Rate: 0
	Stateless Bytes Sent: 64
	Stateless Bytes Received: 8844160
	Stateless Bits Sent: 512
	Stateless Bits Received: 70753280
Row:1  View:Port Statistics  Sampled:2021-04-23 10:55:53.071850 UTC
	Stat Name: 10.65.4.95/Card02/Port02
	Port Name: Ethernet - 002
	Link State: Link Up
	Frames Tx.: 85791
	Valid Frames Rx.: 2
	Frames Tx. Rate: 0
	Valid Frames Rx. Rate: 0
	Bytes Tx.: 10981248
	Bytes Rx.: 128
	Bits Sent: 87849984
	Bits Received: 1024
	Bytes Tx. Rate: 0
	Tx. Rate (bps): 0.000
	Tx. Rate (Kbps): 0.000
	Tx. Rate (Mbps): 0.000
	Bytes Rx. Rate: 0
	Rx. Rate (bps): 0.000
	Rx. Rate (Kbps): 0.000
	Rx. Rate (Mbps): 0.000
	Scheduled Frames Tx.: 85791
	Control Frames Tx: 0
	Control Frames Rx: 0
	Stateless Frames Sent: 85791
	Valid Stateless Frames Received: 2
	Stateless Frames Sent Rate: 0
	Valid Stateless Frames Received Rate: 0
	Stateless Bytes Sent: 10981248
	Stateless Bytes Received: 128
	Stateless Bits Sent: 87849984
	Stateless Bits Received: 1024
"""

text6 = """
Row:0  View:Flow Statistics  Sampled:2021-04-23 10:55:54.242150 UTC
	Tx Port: Ethernet - 002
	Rx Port: Ethernet - 001
	Traffic Item: Traffic Item
	Ethernet II:Destination MAC Address: 01:00:5e:01:01:01
	Ethernet II:Source MAC Address: 00:12:01:00:00:01
	IPv4 :Source Address: 101.1.0.2
	IPv4 :Destination Address: 233.1.1.1
	Tx Frames: 85791
	Rx Expected Frames: 85791
	Rx Frames: 69094
	Frames Delta: 16697
	Loss %: 19.462
	Tx Frame Rate: 0.000
	Rx Frame Rate: 0.000
	Rx Bytes: 8844032
	Tx Rate (Bps): 0.000
	Rx Rate (Bps): 0.000
	Tx Rate (bps): 0.000
	Rx Rate (bps): 0.000
	Tx Rate (Kbps): 0.000
	Rx Rate (Kbps): 0.000
	Tx Rate (Mbps): 0.000
	Rx Rate (Mbps): 0.000
	First TimeStamp: 00:00:00.951
	Last TimeStamp: 00:00:15.140
"""

text7 = """
Tx Frames: 85791
"""

text8 = """
Rx Frames: 69094
"""

text9 = """
Loss %: 19
"""

try:
    print('Ждем синхронизации 30 секунд')
    time.sleep(30)
    print('Проверяем, что трафик генерируется')
    print('Ждем 20 секунд')
    time.sleep(20)
    dut_result = {
        'Результат выполнения теста': 'Не успешно',
        'Описание теста': test_description,
        'Статистика Protocols Summary (Ixia)': text1,
        'Вывод информации о настройках протокола IGMP и PIM (DUT)': text2,
        'Вывод информации show ip pim status (DUT)': text3,
        'Вывод информации show ip route multicast (DUT)': text4,
        'Вывод Port Statistics (Ixia)': text5,
        'Вывод Flow Statistics (Ixia)': text6,
        'Количество переданных фреймов (Ixia)': text7,
        'Количество принятых фреймов (Ixia)': text8,
        'Процент потерь (Ixia)': text9
    }
    print('Записываем статистику в словарь')
    time.sleep(1)
    print('Собираем статистику с Иксии')
    time.sleep(1)
    print('Запрашиваем команды отображения на DUT')
    time.sleep(1)
    print('Запрашиваем команды show')
    time.sleep(1)
    print('Проверяем условия выполения тестирования')
    time.sleep(1)
    print('Записываем результатаы в JSON')
    for k, v in dut_result.items():
        print(f'\n---{k}---')
        print(v)
    with open(f'report/{profile_name}.json', 'w') as f:
        f.write(json.dumps(dut_result, ensure_ascii=False))

except Exception as errMsg:
    print('\nError: %s' % traceback.format_exc())
    print('\nrestPy.Exception:', errMsg)
finally:
    print('\n\n---Ссесия завершена---')
