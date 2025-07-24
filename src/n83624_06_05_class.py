import serial.tools.list_ports
import serial
import pyvisa
import time
from colorama import Back, Style, Fore
import numpy as np

default_ip_port = "TCPIP0::192.168.0.111::7000::SOCKET"
default_com = "COM5"

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# It is recommended to use a minimum delay of 250ms between two commands
def delay(time_in_sec=0.25):
    """
    Time delay based on time.sleep().
    It is recommended to use a minimum delay of 250ms between two GPIB commands

    :param time_in_sec: delay time
    :return: None
    """
    time.sleep(time_in_sec)


def range_check(val, min_val, max_val, val_name):
    if val > max_val:
        print(f"Wrong {val_name}: {val}. Max output should be less then {max_val} V")
        val = max_val
    if val < min_val:
        print(f"Wrong {val_name}: {val}. Should be >= {min_val}")
        val = min_val
    return val

# n83624_06_05
max_ch_number = 24


class n83624_06_05_class:
    def __init__(self):
        self.inst = None
        self.cmd = storage()

    def init_ser(self, com_port, max_ch = max_ch_number):
        max_ch = range_check(max_ch, 1, max_ch_number, "Maximum number of channels")
        com_port_list = [comport.device for comport in serial.tools.list_ports.comports()]
        if com_port not in com_port_list:
            print("COM port connected")
            print("Please ensure that USB is connected")
            print(f"Please check COM port Number. Currently it is {com_port} ")
            print(f'Founded COM ports:{com_port_list}')
            return False
        else:
            self.inst = serial.Serial(
                port=com_port,
                baudrate=115200,
                timeout=0.1
            )
            self.max_ch = max_ch
            if not self.inst.isOpen():
                self.inst.open()
            # tmp = self.ser.isOpen()
            # print("is open:", tmp)
            # return_value = self.get_status()
            return True


    def close(self):
        self.inst.close()
        self.inst = None

    def send(self, cmd_str):
        txt = f'{cmd_str}\r\n'
        # print("Send:", txt)

        self.inst.write(txt.encode())

    def query(self, cmd_srt):
        txt = f'{cmd_srt}\r\n'
        print("Query: ",txt)
        self.inst.write(txt.encode())
        time.sleep(0.1)
        return_val = self.inst.readline().decode()
        # print(return_val)
        return return_val

    def send_list(self, cmd_list, send_delay=0.5):
        for item in cmd_list:
            self.send(item)
            time.sleep(send_delay)



class n83624_06_05_class_tcp:
    def __init__(self):
        self.inst = None
        self.cmd = storage()
        self._s_ch = 1 # operational channels
        self._e_ch = 24 # operational channels
        self._s_ch_all = 1 # used in methods with prefix all
        self._e_ch_all = 24 # used in methods with prefix all
        self.key_prefix = "NGI_"  # return a list of NGI1V or NGI1I keys for CSV
        self.key_end_curr = "I"  # prefix for current
        self.key_end_volt = "V"  # prefix for voltage
        self._send_delay = 0.3

    def init(self, ip_port=default_ip_port, max_ch=max_ch_number):
        max_ch = range_check(max_ch, 1, max_ch_number, "Maximum number of channels")
        rm = pyvisa.ResourceManager()
        # print(rm.list_resources())
        # Visa specific settings
        self.inst = rm.open_resource(ip_port)
        self.inst.set_visa_attribute(pyvisa.constants.VI_ATTR_SEND_END_EN, 1)
        # self.inst.write_termination = "\n"
        self.inst.read_termination = '\r\n'
        self.inst.timeout = 5000  # timeout in ms
        self.inst.query_delay = 1  # write/read delay

        self.inst.chunk_size = 102400
        self._e_ch = max_ch
        self._e_ch_all = max_ch
        print(f"**** Connected to: {self.get_idn()} ****")


    @property
    def working_channels(self):
        return self._s_ch, self._e_ch

    @working_channels.setter
    def working_channels(self, first_last_ch=None):
        """
        set working channels by array [First,Last]
        Assumed that series connected battery simulated
        default: First=1, Last = 24
        @param first_last_ch: [1,10]
        """
        if first_last_ch is None:
            first_last_ch = [1, self._e_ch_all]
        self._s_ch = int(first_last_ch[0])
        self._e_ch = int(first_last_ch[1])

    @property
    def send_delay(self):
        return self._send_delay

    # Setter for _send_delay with validation
    @send_delay.setter
    def send_delay(self, delay_val):
        if isinstance(delay_val, (int, float)) and delay_val >= 0:
            var = range_check(delay_val, 0.001, 2, "NGI send_delay")
            self._send_delay = delay
        else:
            raise ValueError("send_delay must be a non-negative number.")

    def send(self, cmd_str):
        # print("Send:", cmd_str)
        # if self.send_delay != 0:
        time.sleep(self._send_delay)
        self.inst.write(cmd_str)

    def send_list(self, cmd_list, send_delay=0.5):
        """
        methods takes list of command and send it one-by-one with delay
        @param cmd_list:
        @param send_delay:
        """
        for item in cmd_list:
            self.send(item)
            time.sleep(send_delay)

    def query(self, cmd_str):
        """
        NGI firmware have slow processing time for some command.
        Regular query have frequently fails with "TMO" error
        Retry strategy is implemented
        :param cmd_str: VISA string command
        :type cmd_str: str
        :return: VISA string replay
        """
        return_str = ""
        for i in range(100):
            try:
                # debug print to check how may tries
                # print("trying",i)

                return_str = self.inst.query(cmd_str)
                delay()  # regular delay according to datasheet before next command
                return return_str

            except Exception as e:
                print(f"query[{i}]: {cmd_str}, Reply: {return_str}, Error: {e}")
                delay(5)

    def close(self):
        self.inst.close()
        self.inst = None

    def set_voltage(self,  cell_volt):
        """
        Setting output voltage.
        :param cell_volt: 0V to 6V
        """
        cmd_var = self.cmd.source.voltage.ch_range(self._s_ch, self._e_ch, cell_volt)
        self.send(cmd_var)


    def set_current(self, cell_current):
        cmd_var = self.cmd.source.current.ch_range(self._s_ch, self._e_ch, cell_current)
        self.send(cmd_var)

    def set_current_range(self, value="auto"):
        """Current range of internal current sensor: "low" for uA, "high" for mA or auto.
        "Low" may cause short power loss if device start suddenly consume high current.
        :param value: "low", "high", "auto"
        :type: vale str
        """
        auto_cmd = self.cmd.source.range_auto.ch_range(self._s_ch, self._e_ch)
        ranges = {
            "low": self.cmd.source.range_low.ch_range(self._s_ch, self._e_ch),
            "high": self.cmd.source.range_high.ch_range(self._s_ch, self._e_ch),
            "auto": auto_cmd,
        }
        self.send(ranges.get(value, auto_cmd))
        # set minimum current of 1mA because by default it is 0 when switching ranges
        if value in ["auto", "low"]:
            self.set_current(1)

    def out_on(self):
        """Turn output ON for pre-defined cells"""
        cmd_var = self.cmd.output.on.ch_range(self._s_ch, self._e_ch)
        self.send(cmd_var)

    def out_off(self):
        """Turn output OFF for pre-defined cells"""
        cmd_var = self.cmd.output.off.ch_range(self._s_ch, self._e_ch)
        self.send(cmd_var)

    def out_on_all(self):
        """ Turn output of all channels ON"""
        cmd_var = self.cmd.output.off.ch_range(self._s_ch_all, self._e_ch_all)
        self.send(cmd_var)

    def out_off_all(self):
        """ Turn output of all channels OFF"""
        cmd_var = self.cmd.output.off.ch_range(self._s_ch_all, self._e_ch_all)
        self.send(cmd_var)

    def get_voltage(self, ret_as_dict=False):
        """
        Read Voltages for pre-defined channels
        :param ret_as_dict: True - return dictionary,
                            False - return array
        :return:  dictionary or array float
        """
        # read voltage, shorted channel will have low voltage
        txt_val = self.query(self.cmd.measure.voltage.ch_range(self._s_ch, self._e_ch))
        return_val = self.__txt_array_to_digit_array(self.__txt_to_array(txt_val))

        if ret_as_dict:
            return_val = self.__array_to_dict(return_val, self.key_end_volt)
        return return_val

    def get_current(self, ret_as_dict=False):
        """

        :param ret_as_dict:
        :return: array dictionary or array float
        """
        # read voltage, shorted channel will have low voltage
        self.inst.query_delay = 4.5  # write/read delay
        txt_val = self.query(self.cmd.measure.current.ch_range(self._s_ch, self._e_ch))
        return_val = self.__txt_array_to_digit_array(self.__txt_to_array(txt_val))
        self.inst.query_delay = 1  # write/read delay
        if ret_as_dict:
            return_val = self.__array_to_dict(return_val, self.key_end_curr)
        return return_val

    def get_current_avr(self, ret_as_dict=False, n_samples=5):
        n_samples = range_check(n_samples, 2, 16, "get average current")
        i_cells_array = []
        for i in range(n_samples):
            i_cells_array.append(self.get_current())
            time.sleep(3)
        np_array = np.mean(np.array(i_cells_array))
        return  np_array.tolist()

        if ret_as_dict:
            return_val = self.__array_to_dict(return_val, self.key_end_curr)
        return return_val

    def get_idn(self):
        return self.query(self.cmd.idn.req())


    #
    # service functions
    #
    @staticmethod
    def __txt_to_array(txt):
        txt = txt.split(",")
        array_var = []
        for i in range(len(txt)):
            array_var.append(round(float(txt[i]), 4))
        return array_var


    def __array_to_dict(self, array_var, prefix="I"):
        dict_var = {}
        for i, val in enumerate(array_var):
            key = f"{self.key_prefix}{i + 1}{prefix.capitalize()}"
            dict_var[key] = val
        return dict_var

    @staticmethod
    def __txt_array_to_digit_array(txt_array, round_dig=6):
        dig_array = []
        round_dig = range_check(round_dig, 0, 10, "__txt_array_to_digit_array")
        for item in txt_array:
            dig_array.append(round(float(item), round_dig))
        return dig_array

    def get_csv_keys(self):
        """
        Returns CSV keys for Voltage and Current for pr-defined channels
        @return: string array of keys [Voltage, Current]
        """
        current_keys = []
        voltage_keys = []
        for z in range(self._e_ch):
            i_key = f"{self.key_prefix}{z + 1}{self.key_end_curr}"
            v_key = f"{self.key_prefix}{z + 1}{self.key_end_volt}"
            current_keys.append(i_key)
            voltage_keys.append(v_key)
        return [voltage_keys, current_keys]



    def short_circuit_test(self, cell_volt=4.3):
        """
        This script check connection
        It makes following algorithm:
        1. Switch Off output voltage
        2. Set current limit to 20 mA
        3. Set voltage to 4.3 V
        4. Switch on output voltage
        5. Read each channel voltage
        6. if at list one channel measure below 1 V, this mean that channel shorter
            Or usually connector swapped
            in this case it terminate execution indicates which channel is shorted
        7. if all channel are >=4.2 V this mean that connection is ok
        """
        # initiate NGI battery simulator via LAN network
        # NGI default IP is 192.168.0.111:7000
        # check ping in OK, in case of any error here
        cell_volt = range_check(cell_volt, 0.1, 6, "short_circuit_test" )
        s_ch, e_ch = self.working_channels
        error_description = {}
        error_status = False
        # detecting if any short circuit or wrong connection
        # execute list
        ngi_init_list = [
            self.cmd.output.off.ch_range(s_ch, e_ch),
            self.cmd.source.current.ch_range(s_ch, e_ch, 20),
            self.cmd.source.range_high.ch_range(s_ch, e_ch),
            self.cmd.source.voltage.ch_range(s_ch, e_ch, cell_volt),
            self.cmd.output.on.ch_range(s_ch, e_ch),
        ]
        self.send_list(ngi_init_list, 1)
        ngi_voltage = self.get_voltage()

        # checking logic and rise error in case of any channel is shorted
        for i, volt in enumerate(ngi_voltage):
            key = f"CH{i + 1}"
            if volt >= (cell_volt - 0.1):
                error_description[key] = f"OK , VOLT: {volt}"
            if volt <= (cell_volt - 0.3):
                error_description[key] = f" *** Shorted ***, VOLT: {volt} *** Shorted *** "
                error_status = True



        # for i in range(len(ngi_voltage)):
        #     volt = round(float(ngi_voltage[i]), 2)
        #     key = f"CH{i + 1}"
        #     if volt >= (cell_volt - 0.1):
        #         error_description[key] = f"OK , VOLT: {volt}"
        #     if volt <= (cell_volt - 0.3):
        #         error_description[key] = f" *** Shorted ***, VOLT: {volt} *** Shorted *** "
        #         error_status = True
        if error_status:
            print(f"{Fore.BLACK}{Back.YELLOW}Something shorted, please check cell connection{Style.RESET_ALL}")
            print()
            for key, value in error_description.items():
                if value.find("Shorted") != -1:
                    print(f"{Fore.BLACK}{Back.RED}Key: {key}: {value}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.BLACK}{Back.YELLOW}Key: {key}: {value}{Style.RESET_ALL}")
            raise Exception("Sorry, Something shorted. ")
        self.out_off()
        # self.send(self.cmd.output.off.ch_range(s_ch, e_ch))
        print(f"{Fore.BLACK}{Back.GREEN} **** CMC cell connection OK{Style.RESET_ALL}")
        return None

    def cmc_set_voltage(self,  all_cell_volt=4.3,  ilim=5000):
        s_ch, e_ch = self.working_channels
        ngi_init_list = [
            self.cmd.output.off.ch_range(s_ch, e_ch),
            self.cmd.output.mode_source.ch_range(s_ch, e_ch),
            self.cmd.source.voltage.ch_range(s_ch, e_ch, all_cell_volt),
            self.cmd.source.current.ch_range(s_ch, e_ch, ilim),
            self.cmd.source.range_high.ch_range(s_ch, e_ch),
            self.cmd.output.on.ch_range(s_ch, e_ch),

        ]
        self.send_list(ngi_init_list,1)


###############################################
###############################################
###############################################
# Service classes for inheritance
# they just help to reduce amount of linear code

class Req3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self):
        return self.cmd + "?"


class Str3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self, ):
        return self.cmd


class StrAndReq(Str3, Req3):
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix


class _ch_range:
    def __init__(self, prefix, ending, max_ch=max_ch_number):
        self.prefix = prefix
        self.max_ch = max_ch
        self.ending = ending
        self.cmd = prefix + ending

    def ch_range(self, ch_start, ch_end, param):
        ch_start = range_check(ch_start, 1, self.max_ch, "CH selection range")
        ch_end = range_check(ch_end, 1, self.max_ch, "CH selection range")
        txt = ""
        for k in range(ch_start, ch_end + 1):
            txt = txt + f"{k},"
            # print(txt)
        txt = f"{param}(@{txt[0:-1]})"
        return f"{self.prefix}{self.ending} {txt}"



class ch_str_param(_ch_range):
    def __init__(self, prefix, ending, min_v=0, max_v=6, max_ch=max_ch_number):
        self.prefix = prefix
        self.max_ch = max_ch
        self.cmd = ""
        self.ending = ":" + ending
        self.min_val = min_v
        self.max_val = max_v
    def ch_num(self, ch_num, param):
        param = range_check(param,self.min_val, self.max_val, "ch_str_param")
        ch_num = range_check(ch_num, 1, self.max_ch, "CH selection")
        return f"{self.prefix}{ch_num}{self.ending} {param}"

    def ch_num_req(self, ch_num):
        ch_num = range_check(ch_num, 1, max_ch_number, "CH selection")
        return f"{self.prefix}{ch_num}{self.ending}?"


class req_ch_num():
    def __init__(self, prefix, ending):
        self.ending = ":" + ending
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.__range = _ch_range(prefix, ":" + ending + "?", max_ch=max_ch_number)

    def ch_num(self, ch_num):
        return self.__range.ch_range(ch_num , ch_num, "")

    def ch_range(self, ch_start, ch_end):
        return self.__range.ch_range(ch_start, ch_end, "")



class str_ch_num():
    def __init__(self, prefix, ending):
        self.ending = ":" + ending
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.__range = _ch_range(prefix, ":" + ending, max_ch=max_ch_number)

    def ch_num(self, ch_num):
        return self.__range.ch_range(ch_num , ch_num, "")

    def ch_range(self, ch_start, ch_end):
        return self.__range.ch_range(ch_start, ch_end, "")


class storage:
    """
    Class organize hierarchical Visa command list.
    Methods acts as command constructors with code suggestion if IDE supports it
    """
    def __init__(self):
        self.cmd = None
        self.prefix = None
        # super(communicator, self).__init__()
        # super(storage,self).__init__()
        # communicator.init(self, "COM10")
        # this is the list of Subsystem commands
        self.sequence = sequence()
        self.charge = charge()
        self.source = source()
        self.output = output()
        self.measure = measure()
        self.idn = Req3("*IDN")
        self.opc = StrAndReq("*OPС")
        self.rst = Str3("*RST")

#
#  Main classes
#


class measure:
    # command list :
    # MEASure1:CURRent? //Read the readback current for channel 1
    # MEASure1:VOLTage? //Read the readback voltage for channel 1
    # MEASure1:POWer? //Read the real-time power for channel 1
    # MEASure1:TEMPerature? //Read the real-time temperature for channel 1
    # MEAS2:CURR? //Read the readback current for channel 2
    # MEAS2:VOLT? //Read the readback voltage for channel 2
    # MEAS2:POW? //Read the real-time power for channel 2
    # MEAS2:TEMP? //Read the real-time temperature for channel 2

    def __init__(self):
        # print("INIT Measure")
        self.cmd = "MEAS"
        self.prefix = "MEAS"
        self.current = req_ch_num(self.prefix, "CURR" )
        self.voltage = req_ch_num(self.prefix, "VOLT" )
        self.power = req_ch_num(self.prefix, "POW" )
        self.temp = req_ch_num(self.prefix, "TEMP" )
        self.mah = req_ch_num(self.prefix, "MAH")
        self.resistance = req_ch_num(self.prefix, "R")


class output:

    def __init__(self):
        # print("INIT Output")
        self.cmd = "OUTP"
        self.prefix = "OUTP"
        self.mode_source = str_ch_num(self.prefix, "MODE 0")
        self.mode_charge = str_ch_num(self.prefix, "MODE 1")
        self.mode_SOC = str_ch_num(self.prefix, "MODE 3")
        self.mode_SEQ = str_ch_num(self.prefix, "MODE 128")
        self.mode_req = req_ch_num(self.prefix, "MODE")
        self.on = str_ch_num(self.prefix, "ONOFF 1")
        self.off = str_ch_num(self.prefix, "ONOFF 0")
        self.on_off_req = req_ch_num(self.prefix, "ONOFF")


class source:

    def __init__(self):
        # print("INIT Source")
        self.cmd = "SOUR"
        self.prefix = "SOUR"
        self.voltage = ch_str_param(self.prefix, "VOLT", 0, 6, max_ch_number)
        self.current = ch_str_param(self.prefix, "OUTCURR", 0, 1000, max_ch_number)
        self.range_high = str_ch_num(self.prefix, "RANG 0")
        self.range_low = str_ch_num(self.prefix, "RANG 2")
        self.range_auto = str_ch_num(self.prefix, "RANG 3")


class charge:

    def __init__(self):
        # print("INIT CHARrge")
        self.cmd = "CHAR"
        self.prefix = "CHAR"
        self.voltage = ch_str_param(self.prefix, "VOLT", 0, 6, max_ch_number)
        self.current = ch_str_param(self.prefix, "OUTCURR", 0, 5000, max_ch_number)
        self.current_req = req_ch_num(self.prefix, "OUTCURR")
        self.resistance = ch_str_param(self.prefix, "R", 0, 100, max_ch_number) # milli ohm
        self.echo_voltages = req_ch_num(self.prefix, "ECHO:VOLT")
        self.echo_capacity = req_ch_num(self.prefix, "ECHO:Q")


class sequence:

    def __init__(self):
        # print("INIT SEQuence")
        self.cmd = "SEQ"
        self.prefix = "SEQ"
        # This command is used to set sequence file number.
        self.edit_file = ch_str_param(self.prefix, ":EDIT:FILE", 0, 10, max_ch_number)

        # This command is used to set total steps in the sequence file.
        self.edit_length = ch_str_param(self.prefix, ":EDIT:LENG", 0, 200, max_ch_number)

        # This command is used to set the specific step number.
        self.edit_step = ch_str_param(self.prefix, ":EDIT:STEP", 0, 200, max_ch_number)

        # This command is used to set the cycle times for the file under editing.
        self.edit_cycle = ch_str_param(self.prefix, ":EDIT:CYC", 0, 100, max_ch_number)

        # This command is used to set the output voltage for the step under editing.
        self.edit_voltage = ch_str_param(self.prefix, ":EDIT:VOLT", 0, 6, max_ch_number)

        # This command is used to set the output current limit for the step under editing.
        self.edit_current = ch_str_param(self.prefix, ":EDIT:OUTCURR", 0, 5000, max_ch_number)

        # This command is used to set the resistance for the step under editing.
        self.edit_resistance = ch_str_param(self.prefix, ":EDIT:R", 0, 100, max_ch_number)

        # This command is used to set the running time for the step under editing.
        self.set_running_time = ch_str_param(self.prefix, ":EDIT:RUNT", 0, 1000, max_ch_number)

        # This command is used to set the required link start step after the present step is completed.
        self.set_link_start = ch_str_param(self.prefix, ":EDIT:LINKS", -1, 200, max_ch_number)

        # This command is used to set the link stop step for the step under editing.
        self.set_link_end = ch_str_param(self.prefix, ":EDIT:LINKE", -1, 200, max_ch_number)

        # This command is used to set cycle times for the link.
        self.set_cycle_time = ch_str_param(self.prefix, ":EDIT:LINKC", 0, 100, max_ch_number)

        # This command is used to set the sequence test file number.
        self.run_file = ch_str_param(self.prefix, ":RUN:FILE", 0, 10, max_ch_number)

        # This command is used to query the present running step number.
        self.run_steps_req = req_ch_num(self.prefix, ":RUN:STEP")

        # This command is used to query the running time for the sequence test file.
        self.run_steps_req = req_ch_num(self.prefix, ":RUN:T")

#
# Testing code
#
if __name__ == '__main__':
    cmd = storage()
    bat_sim = n83624_06_05_class_tcp()
    bat_sim.init()
    # bat_sim.init("COM12")
    # bat_sim.send(cmd.source.voltage.ch_range(1, 16, 3))
    # bat_sim.send(cmd.output.on.ch_range(1, 16))
    # # bat_sim.send(cmd.rst.str())
    # vcell = 1
    # for z in range(5):
    #     bat_sim.send(cmd.source.voltage.ch_range(1, 16, vcell))
    #     time.sleep(0.5)
    #     print("3: ", bat_sim.query(cmd.measure.voltage.ch_range(1, 16)))
    #     time.sleep(1)
    #     vcell = vcell + 0.5
    # # bat_sim.send(cmd.source.voltage.ch_range(1, 1, 3.25))
    # # bat_sim.send(cmd.source.voltage.ch_range(2, 2, 3.45))
    # bat_sim.send(cmd.source.current.ch_range(1, 16, 500))
    # bat_sim.send(cmd.output.on.ch_range(1, 16))
    # time.sleep(0.1)
    # print("1: ", bat_sim.query(cmd.measure.voltage.ch_num(1)))
    # print("2: ", bat_sim.query(cmd.measure.voltage.ch_range(1,5)))
    #
    # print("4: ", bat_sim.query(cmd.measure.voltage.ch_num(1)))
    # print(bat_sim.query(cmd.measure.voltage.ch_ra))
    # bat_sim.close()
    print(cmd.measure.voltage.ch_num(5))
    print(cmd.measure.temp.ch_num(10))
    print(cmd.measure.mah.ch_num(20))
    print(cmd.output.mode_source.ch_num(10))
    print(cmd.output.mode_SEQ.ch_num(24))
    print(cmd.output.mode_req.ch_num(12))
    print(cmd.output.on.ch_num(6))
    print(cmd.source.voltage.ch_num(10, 10))
    print(cmd.source.voltage.ch_num_req(10))
    print(cmd.source.current.ch_num(20, 500))
    print(cmd.charge.echo_capacity.ch_num(13))
    print(cmd.source.voltage.ch_range(1, 1, 5))