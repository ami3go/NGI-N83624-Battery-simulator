import n83624_06_05_class as bat_sim
import time
import datetime
from colorama import Fore, Back, Style

global ngi, s_ch, e_ch
s_ch = 1
e_ch = 16
ngi = bat_sim.n83624_06_05_class_tcp()
ngi.init(bat_sim.default_ip_port)
ngi.send(ngi.cmd.rst.str())
time.sleep(2)
ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, 4.300))
# print(ngi.cmd.measure.voltage.ch_range(1,16)))
# voltage = ngi.query("MEASure:VOLTage?(@1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)")
# voltage = ngi.query(ngi.cmd.measure.voltage.ch_range(1,16))
# current = ngi.query(ngi.cmd.measure.current.ch_range(1,16))
ngi.send(ngi.cmd.source.current.ch_range(s_ch, e_ch, 500))
ngi.send(ngi.cmd.output.on.ch_range(s_ch,e_ch))
# time.sleep(1)
# ngi.send(ngi.cmd.source.voltage.ch_range(s_ch,e_ch,4.333))
time.sleep(1)
voltage = ngi.query(ngi.cmd.measure.voltage.ch_range(s_ch,e_ch))
print(voltage)
# time.sleep(2)
# ngi.send(ngi.cmd.source.voltage.ch_range(s_ch,e_ch,2.555))
# time.sleep(1)
# voltage = ngi.query(ngi.cmd.measure.voltage.ch_range(s_ch,e_ch))
# print(voltage)
# ngi.send(ngi.cmd.output.off.ch_range(s_ch,e_ch))
delay = 0.5
n = 100
for i in range(n):
    # print(f"{Fore.YELLOW}{datetime.datetime.now()}, request volatge {Style.RESET_ALL}")
    # voltage = ngi.query(ngi.cmd.measure.voltage.ch_range(s_ch,e_ch))
    # print(datetime.datetime.now(),voltage)
    # time.sleep(delay)
    # print(f"{Fore.YELLOW}{datetime.datetime.now()}, request current {Style.RESET_ALL}")
    current = ngi.query(ngi.cmd.measure.current.ch_range(s_ch, e_ch))
    txt = f"{Fore.YELLOW}{datetime.datetime.now()}{Style.RESET_ALL} {current}"
    print(txt)
    time.sleep(delay)


ngi.send(ngi.cmd.output.off.ch_range(s_ch,e_ch))



