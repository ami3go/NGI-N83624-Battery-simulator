# def set_voltage_from_array( v_array, start_ch=1):
#     for z, cell_volt in enumerate(v_array):
#         # z = range_check(z, self._s_ch, self._e_ch, "set_voltage_from_array VAR: z")
#         # cell_volt = range_check(cell_volt, ngi_min_voltage, ngi_max_voltage, "set_voltage_from_array VAR: item")
#         # cmd_var = self.cmd.source.voltage.ch_num(z + start_ch, cell_volt)
#         # self.send(cmd_var)
#         print(z + start_ch, cell_volt)
#
# set_voltage_from_array([10,5,6,7,8,9,0], 20)
from bms_browser_scripts.SimpleScripts.ADBMS6842_multiple_init import cell_volt

cell_volt=[0]*16
names = []
for z,k in enumerate(cell_volt):
    names.append(f"V{z}C_Set")
print(names)