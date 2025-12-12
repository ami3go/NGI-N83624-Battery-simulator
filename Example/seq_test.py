import N83624.n83624_06_05_class as bat_sim
import time

global ngi, s_ch, e_ch
ngi = bat_sim.n83624_06_05_class_tcp()
ngi.init("COM12")
s_ch = 1 # start channel
e_ch = 16 # end channel


def str2aray(txt_array):
    value_list = txt_array.split(',')
    numeric_values = list(map(float, value_list))
    return numeric_values


def ngi_set_voltages(vout):
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, vout))


def ngi_output_on():
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.output.on.ch_range(s_ch, e_ch))
    time.sleep(0.5)


def ngi_output_off():
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.output.off.ch_range(s_ch, e_ch))


def ngi_set_current(iout):
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.source.current.ch_range(s_ch, e_ch, iout))

def ngi_get_voltage():
    txt_array = ngi.query(ngi.cmd.measure.voltage.ch_range(s_ch, e_ch))
    return str2aray(txt_array)  

def ngi_get_current():
    txt_array = ngi.query(ngi.cmd.measure.current.ch_range(s_ch, e_ch))
    return str2aray(txt_array)

def ngi_close():
    global ngi, s_ch, e_ch
    ngi.close()

if __name__ == '__main__':
    cmd_list = [
        "OUTPut1:ONOFF 0", #  turn off the output for present channel
        "OUTPut1:MODE 128", #  set operation mode to SEQ mode
        "SEQuence1:EDIT:FILE 1", #  set SEQ file No. to 1
        "SEQuence1:EDIT:LENGth 3", #  set total steps to 3
        "SEQuence1:EDIT:CYCle 1", #  set file cycle times to 1
        "SEQuence1:EDIT:STEP 1", #  set step No. to 1
        "SEQuence1:EDIT:VOLTage 1.0", #  set CV Value for step No. 1 to 1.0V
        "SEQuence1:EDIT:OUTCURRent 2000", #  set output current limit for step No. 1 to 2000mA
        "SEQuence1:EDIT:Res 0.0", #  set resistance for step No. 1 to 0mΩ
        "SEQuence1:EDIT:RUNTime 5", #  set running time for step No. 1 to 5s
        "SEQuence1:EDIT:LINKStart -1", #  set link start step for step No. 1 to -1
        "SEQuence1:EDIT:LINKEnd -1", #  set link stop step for step No. 1 to -1
        "SEQuence1:EDIT:LINKCycle 0", #  set link cycle times to 0
        "SEQuence1:EDIT:STEP 2", #  set step No. to 2
        "SEQuence1:EDIT:VOLTage 2.0", #  set CV Value for step No. 2 to 2.0V
        "SEQuence1:EDIT:OUTCURRent 2000", #  set output current limit for step No. 2 to 2000mA
        "SEQuence1:EDIT:Res 0.1", #  set resistance for step No. 2 to 0.1mΩ
        "SEQuence1:EDIT:RUNTime 10", #  set running time for step No. 2 to 10s
        "SEQuence1:EDIT:LINKStart -1", #  set link start step for step No. 2 to -1
        "SEQuence1:EDIT:LINKEnd -1", #  set link stop step for step No. 2 to -1
        "SEQuence1:EDIT:LINKCycle 0", #  set link cycle times to 0
        "SEQuence1:EDIT:STEP 3", #  set step No. to 3
        "SEQuence1:EDIT:VOLTage 3.0", #  set CV Value for step No. 3 to 3.0V
        "SEQuence1:EDIT:OUTCURRent 2000", #  set output current limit for step No. 3 to 2000mA
        "SEQuence1:EDIT:Res 0.2", #  set resistance for step No. 3 to 0.2mΩ
        "SEQuence1:EDIT:RUNTime 20", #  set running time for step No. 3 to 20s
        "SEQuence1:EDIT:LINKStart -1", #  set link start step for step No. 3 to -1
        "SEQuence1:EDIT:LINKEnd -1", #  set link stop step for step No. 3 to -1
        "SEQuence1:EDIT:LINKCycle 0", #  set link cycle times to 0
        "SEQuence1:RUN:FILE 1", #  set the running SEQ file No. to 1
        "OUTPut1:ONOFF 1", #  turn on the output for channel 1
        "SEQuence1: RUN:STEP?", #  read the present running step No.
        "SEQuence1: RUN:T?", #  read running time for present SEQ file No.
    ]
    cmd_list2 = [
        "OUTPut:ONOFF 0(@1,2,3)",  # turn off the output for present channel
        "OUTPut:MODE 128(@1,2,3)",  # set operation mode to SEQ mode
        "SEQuence:EDIT:FILE 1(@1,2,3)",  # set SEQ file No. to 1
        "SEQuence:EDIT:LENGth 3(@1,2,3)",  # set total steps to 3
        "SEQuence:EDIT:CYCle 5(@1,2,3)",  # set file cycle times to 1

        "SEQuence:EDIT:STEP 1(@1,2,3)",  # set step No. to 1
        "SEQuence:EDIT:VOLTage 1.125(@1,2,3)",  # set CV Value for step No. 1 to 1.0V
        "SEQuence:EDIT:OUTCURRent 2000(@1,2,3)",  # set output current limit for step No. 1 to 2000mA
        "SEQuence:EDIT:Res 0.0(@1,2,3)",  # set resistance for step No. 1 to 0mΩ
        "SEQuence:EDIT:RUNTime 2(@1,2,3)",  # set running time for step No. 1 to 5s
        "SEQuence:EDIT:LINKStart -1(@1,2,3)",  # set link start step for step No. 1 to -1
        "SEQuence:EDIT:LINKEnd -1(@1,2,3)",  # set link stop step for step No. 1 to -1
        "SEQuence:EDIT:LINKCycle 0(@1,2,3)",  # set link cycle times to 0

        "SEQuence:EDIT:STEP 2(@1,2,3)",  # set step No. to 2
        "SEQuence:EDIT:VOLTage 4.2(@1,2,3)",  # set CV Value for step No. 2 to 2.0V
        "SEQuence:EDIT:OUTCURRent 2000(@1,2,3)",  # set output current limit for step No. 2 to 2000mA
        "SEQuence:EDIT:Res 0.1(@1,2,3)",  # set resistance for step No. 2 to 0.1mΩ
        "SEQuence:EDIT:RUNTime 2(@1,2,3)",  # set running time for step No. 2 to 10s
        "SEQuence:EDIT:LINKStart -1(@1,2,3)",  # set link start step for step No. 2 to -1
        "SEQuence:EDIT:LINKEnd -1(@1,2,3)",  # set link stop step for step No. 2 to -1
        "SEQuence:EDIT:LINKCycle 0(@1,2,3)",  # set link cycle times to 0

        "SEQuence:EDIT:STEP 3(@1,2,3)",  # set step No. to 3
        "SEQuence:EDIT:VOLTage 1.125(@1,2,3)",  # set CV Value for step No. 3 to 3.0V
        "SEQuence:EDIT:OUTCURRent 2000(@1,2,3)",  # set output current limit for step No. 3 to 2000mA
        "SEQuence:EDIT:Res 0.2(@1,2,3)",  # set resistance for step No. 3 to 0.2mΩ
        "SEQuence:EDIT:RUNTime 2(@1,2,3)",  # set running time for step No. 3 to 20s
        "SEQuence:EDIT:LINKStart -1(@1,2,3)",  # set link start step for step No. 3 to -1
        "SEQuence:EDIT:LINKEnd -1(@1,2,3)",  # set link stop step for step No. 3 to -1
        "SEQuence:EDIT:LINKCycle 0(@1,2,3)",  # set link cycle times to 0


    ]

    for cmd in cmd_list2:
        ngi.send(cmd)
        time.sleep(0.1)
    time.sleep(1)
    ngi.send("SEQuence:RUN:FILE 1(@1,2,3)")
    ngi.send("OUTPut:ONOFF 1(@1,2,3)")
    print(ngi.query("SEQuence: RUN:STEP?(@1,2,3)"))
    print(ngi.query("SEQuence: RUN:T?(@1,2,3)"))
