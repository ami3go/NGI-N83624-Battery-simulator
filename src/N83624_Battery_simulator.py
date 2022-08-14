# import pyvisa # PyVisa info @ http://PyVisa.readthedocs.io/en/stable/
import serial.tools.list_ports
import serial
import time


#****************************************************
# Purpose: Establish communication
#
# Inputs:  Ip adress
#
# Returns: Visa object
#
#****************************************************

class com_interface:
    def __init__(self):
        # Commands Subsystem
        # this is the list of Subsystem commands
        # super(communicator, self).__init__(port="COM10",baudrate=115200, timeout=0.1)
        print("communicator init")
        self.cmd = None
        self.ser = None

    def init(self, com_port, baudrate_var=115200):
        com_port_list = [comport.device for comport in serial.tools.list_ports.comports()]
        if com_port not in com_port_list:
            print("COM port is not found")
            print("Please ensure that USB is connected")
            print(f"Please check COM port Number. Currently it is {com_port} ")
            print(f'Founded COM ports:{com_port_list}')
            return False
        else:
            self.ser = serial.Serial(
                port=com_port,
                baudrate=baudrate_var,
                timeout=0.1
            )
            if not self.ser.isOpen:
                self.ser.open()

            txt = '*IDN?'

            read_back = self.query(txt)
            print(f"Connected to: {read_back}")
            return True

    def send(self, txt):
        # will put sending command here
        txt = f'{txt}\r\n'
        # print(f'Sending: {txt}')
        self.ser.write(txt.encode())

    def query(self, cmd_srt):
        txt = f'{cmd_srt}\r\n'
        self.ser.reset_input_buffer()
        self.ser.write(txt.encode())
        # print(f'Query: {txt}')
        return_val = self.ser.readline().decode()
        return return_val

    def close(self):
        self.ser.close()
        self.ser = None


#****************************************************
#
#     Service functions
#
#****************************************************


def range_check(val, min, max, val_name):
    if val > max:
        print(f"Wrong {val_name}: {val}. Max value should be less then {max}")
        val = max
    if val < min:
        print(f"Wrong {val_name}: {val}. Should be >= {min}")
        val = min
    return val


def ch_list_from_list(*argv):
    txt = ""
    for items in argv:
        txt = f'{txt}{items},'
    txt = txt[:-1]
    return f'(@{txt})'


def ch_list_from_range(min, max, channels_num=24):
    channels = channels_num

    min = range_check(min, 1, channels_num, "ch_list_from_range , min")
    max = range_check(max, 1, channels_num, "ch_list_from_range , max")
    txt = f"{min},"
    l = [f"{min},"]
    for z in range(0, (max - min)):
        l.append(f'{min + z + 1},')
    txt = "".join(l)
    txt = txt[:-1]
    return f"(@{txt})"

#****************************************************
#
#     Service Classes
#
#****************************************************


class select_channel2:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def list(self, *argv):
        ch_list_txt = ch_list_from_list2(*argv)
        txt = f'{self.cmd}{ch_list_txt}'
        return txt

    def range(self, min, max, channels_num=24):
        ch_list_txt = ch_list_from_range2(min, max, channels_num)
        txt = f"{self.cmd}{ch_list_txt}"
        return txt


class req3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self):
        return self.cmd + "?"

class req_ch_num:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self, ch_num):
        ch_num = range_check(ch_num, 1, 24, "req ch number")
        ind = self.cmd.find(":")
        txt = f"{self.cmd[:ind]}{ch_num}{self.cmd[ind:]}"
        return txt + "?"

class str_ch_num:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def cmd(self, ch_num):
        ch_num = range_check(ch_num, 1, 24, "req ch number")
        ind = self.cmd.find(":")
        return f"{self.cmd[:ind]}{ch_num}{self.cmd[ind:]}"


class str_and_req:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self, ):
        return self.cmd

    def req(self):
        return self.cmd + "?"


class sel_ch_with_param:
    def __init__(self, prefix, min, max):
        self.prefix = prefix
        self.cmd = self.prefix
        self.max = max
        self.min = min

    def list(self,var, *argv):
        var = range_check(var, self.min, self.max, self.cmd)
        ch_list_txt = ch_list_from_list2(*argv)
        txt = f'{self.cmd} {var},{ch_list_txt}'
        return txt

    def range(self, var, ch_min, ch_max, ch_num=20):
        var = range_check(var, self.min, self.max, self.cmd)
        ch_list_txt = ch_list_from_range2(ch_min, ch_max, ch_num)
        txt = f"{self.cmd} {var},{ch_list_txt}"
        return txt


class dig_param3:
    def __init__(self, prefix, min, max):
        self.prefix = prefix
        self.cmd = self.prefix
        self.max = max
        self.min = min

    def val(self, ch_num, count=0):
        count = range_check(count, self.min, self.max, "MAX count")
        ch_num = range_check(ch_num, 1, 24, "req ch number")
        ind = self.cmd.find(":")
        txt = f"{self.cmd[:ind]}{ch_num}{self.cmd[ind:]} {count}"
        return txt


class str3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self, ):
        return self.cmd

#****************************************************
#
#     Main command storage classes
#
#****************************************************


class storage:
    def __init__(self):
        self.cmd = None
        self.prefix = None
        self.idn = req3("*IDN")
        self.opc = str3("*OPC")
        self.reset = str3("*RST")

        self.measure = measure()
        self.output = output()
        self.source = source()
        # self.charge = charge()
        # self.seq = seq()





class measure:
    # command list :
    # MEASure < n >: CURRent?
    # MEASure < n >: VOLTage?
    # MEASure < n >: POWer?
    # MEASure < n >: MAH?
    # MEASure < n >: Res?

    def __init__(self):
        # print("INIT Measure")
        self.cmd = "MEASure"
        self.prefix = "MEASure"
        self.current = current(self.prefix)
        self.voltage = voltage(self.prefix)
        self.power = power(self.prefix)
        self.mah = mah(self.prefix)
        self.resist = resist(self.prefix)

class req_on_off_ch_select:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix
        self.req = req2(self.prefix)
        self.on = conf2(self.prefix + " ON,")
        self.off = conf2(self.prefix + " OFF,")


class voltage(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "VOLTage"
        self.cmd = self.prefix



class current(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "CURRent"
        self.cmd = self.prefix


class power(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "POWer"
        self.cmd = self.prefix


class mah(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "MAH"
        self.cmd = self.prefix


class resist(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "Res"
        self.cmd = self.prefix



class source:
    # command list :
    # SOURce < n >: VOLTage
    # SOUR1: VOLT?
    # SOURce < n >: OUTCURRent
    # SOUR1: OUTCURR?
    # SOURce < n >: RANGe < NR1 >

    def __init__(self):
        # print("INIT Measure")
        self.cmd = "SOURce"
        self.prefix = "SOURce"
        self.current = scurrent(self.prefix)
        self.voltage = svoltage(self.prefix)
        self.range = srange(self.prefix)


class srange(req_ch_num):
    def __init__(self, prefix):
        self.min = 0
        self.max = 3
        self.prefix = prefix + ":" + "RANGe"
        self.cmd = self.prefix
        self._int_cmd = dig_param3(self.prefix, 0, 3)
    def high(self, ch_num):
        return self._int_cmd.val(0)

    def low(self, ch_num):
        return self._int_cmd.val(2)

    def auto(self, ch_num):
        return self._int_cmd.val(3)


class svoltage(voltage, dig_param3):
    def __init__(self, prefix):
        self.min = 0
        self.max = 10
        self.prefix = prefix + ":" + "VOLTage"
        self.cmd = self.prefix

class scurrent(current, dig_param3):
    def __init__(self, prefix):
        self.min = 0
        self.max = 10
        self.prefix = prefix + ":" + "OUTCURR"
        self.cmd = self.prefix

class output:
    # command list :
    # OUTPut < n >: MODE < NR1 >
    # OUTPut < n >: ONOFF < NR1 >
    # OUTPut < n >: STATe?

    def __init__(self):
        # print("INIT Measure")
        self.cmd = "OUTP"
        self.prefix = "OUTP"
        self.mode = mode(self.prefix)
        self._internal = dig_param3(self.prefix + ":ONOFF", 0, 1)
        self.onoff = req_ch_num(self.prefix + ":ONOFF")
        self.state = req_ch_num(self.prefix + ":STATe")

    def off(self, ch_num):
        return self._internal.val(ch_num, 0)

    def on(self, ch_num):
        return self._internal.val(ch_num, 1)


class mode(req_ch_num):
    def __init__(self, prefix):
        self.prefix = prefix + ":" + "MODE"
        self.cmd = self.prefix
        self._internal = dig_param3(self.prefix, 0, 128)

    def source(self, ch_num):
        return self._internal.val(ch_num, 0)

    def charge(self, ch_num):
        return self._internal.val(ch_num, 1)

    def soc(self, ch_num):
        return self._internal.val(ch_num, 3)

    def seq(self, ch_num):
        return self._internal.val(ch_num, 128)

class charge:
    CHARge < n >: VOLTage
    CHARge < n >: OUTCURRent < NRf >
    CHARge < n >: Res
    CHARge < n >: ECHO:VOLTage


if __name__ == '__main__':
    # dev = LOG_34970A()
    # dev.init("COM10")
    # dev.send("COM10 send")
    cmd = storage()
    print("")
    print("TOP LEVEL")
    print("*" * 150)
    print(cmd.idn.req())
    print(cmd.opc.str())
    print(cmd.reset.str())
    print(cmd.measure.voltage.req(1))
    print(cmd.measure.current.req(2))
    print(cmd.measure.power.req(10))
    print(cmd.measure.mah.req(20))
    print(cmd.measure.resist.req(24))

    print(cmd.source.range.req(10))
    print(cmd.source.range.auto(10))
    print(cmd.source.voltage.req(23))
    print(cmd.source.voltage.val(12, 2.54))
    print(cmd.source.current.val(12, 3.6))
    print(cmd.source.voltage.req(12))

    print(cmd.output.mode.source(10))
    print(cmd.output.mode.seq(5))
    print(cmd.output.mode.req(10))
    print(cmd.output.on(10))
    print(cmd.output.off(20))
    print(cmd.output.onoff.req(10))
    print(cmd.output.state.req(1))




