import pyvisa
battery_sim_adr = "TCPIP0::192.168.0.111::inst::INSTR"

rm = pyvisa.ResourceManager()
# print(rm.list_resources())
# for items in rm.list_resources():
#     print(items)
app = rm.open_resource(battery_sim_adr)
print(app)
# IDN = str(app.query("*IDN?"))
# print(f': Connected to: {IDN}')
