import pyvisa

default_ip_port = "TCPIP0::192.168.0.111::7000::SOCKET"

# rm = pyvisa.ResourceManager()
# for item in rm.list_resources():
#     print(item)

rm = pyvisa.ResourceManager()
inst = rm.open_resource(default_ip_port )
inst.set_visa_attribute(pyvisa.constants.VI_ATTR_SEND_END_EN, 1)
# self.inst.write_termination = "\n"
inst.read_termination = '\r\n'
inst.timeout = 5000  # timeout in ms
inst.query_delay = 1  # write/read delay

inst.chunk_size = 102400
print(f"**** Connected to: {inst.query("*IDN?")} ****")


