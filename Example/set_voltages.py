import N83624.n83624_06_05_class as bat_sim
import time
import pandas as pd
global ngi, s_ch, e_ch
from colorama import Style, Fore, Back
ngi = bat_sim.n83624_06_05_class_tcp()
ngi.init()

ehv7_csvfile = 'EHV-7_PPE41C.csv'

global v_max_hv, v_ov_2, v_ov_1, v_opmax_hv, v_op_unlim_max_hv, v_n, v_op_unlim_min_hv, v_opmin_hv, v_m, v_min_hv,v_zero


v_max_hv = 5.5
v_ov_2 = 5
v_ov_1 = 4.5
v_opmax_hv = 4.3
v_op_unlim_max_hv = 4.2
v_n = 3.4
v_op_unlim_min_hv = 2.4
v_opmin_hv = 2.3
v_m = 1.7125
v_min_hv = 1.125
v_zero = 0

SoC_100 = 4.334
SoC_0 = 2.416

s_ch = 1 # start channel
e_ch = 16 # end channel


def str2aray(txt_array):
    if txt_array != "":
        value_list = txt_array.split(',')
        numeric_values = list(map(float, value_list))
        return numeric_values

def ngi_ini_conf():
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.rst.str())
    time.sleep(5)
    ngi.send(ngi.cmd.output.mode_source.ch_range(s_ch, e_ch, ))


def ngi_set_voltages(vout):
    global ngi, s_ch, e_ch
    ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, vout))
    time.sleep(0.05)


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


def ngi_level(v_out, t_del_sec):
    global ngi, s_ch, e_ch
    print(f"{Fore.BLUE}Flat line, V={v_out:.3f} V, Time={t_del_sec} sec {Style.RESET_ALL}")
    ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, v_out))
    time.sleep(t_del_sec)


def ngi_slope(v_start,v_end, t_tran_sec):
     global ngi, s_ch, e_ch
     v_start = round(v_start, 4)
     v_end = round(v_end, 4)
     v_step = 0.1
     vout = v_start
     n_steps = (int(round((v_end - v_start)/v_step)))
     tdelay = round(t_tran_sec / abs(n_steps), 2)

     cond = 0
     if tdelay < 0.3:
         v_step = 0.2
         n_steps = (int(round((v_end - v_start)/v_step)))
         tdelay = round(t_tran_sec / abs(n_steps), 2)
         tdelay = round(tdelay - 0.05, 3)
         cond = 0
     elif tdelay < 1:
          v_step = 0.1
          n_steps = (int(round((v_end - v_start)/v_step)))
          tdelay = round(t_tran_sec / abs(n_steps), 2)
          tdelay = round(tdelay - 0.055,3)
          cond = 1
     elif tdelay < 2:
         v_step = 0.05
         n_steps = (int(round((v_end - v_start)/v_step)))
         tdelay = round(t_tran_sec / abs(n_steps), 2)
         tdelay = round(tdelay - 0.05, 3)
         cond = 2
     elif tdelay < 5:
         v_step = 0.01
         n_steps = (int(round((v_end - v_start)/v_step)))
         tdelay = round(t_tran_sec / abs(n_steps), 2)        
         tdelay = round(tdelay - 0.07, 3)
         cond = 3
     else:
        v_step = 0.005
        n_steps = (int(round((v_end - v_start)/v_step)))
        tdelay = round(t_tran_sec / abs(n_steps), 2)
        tdelay = round(tdelay - 0.07, 3)
        cond = 4
     print(f"Slope from {v_start} V to {v_end}, Time = {t_tran_sec} sec, *** "
           f" Vstep: {v_step}, steps: {n_steps}, tdealy: {tdelay},  Cond: {cond },  ")
           
     for v in range(abs(n_steps)):
         ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, vout))
         time.sleep(tdelay)
         time.sleep(0.05)
         if n_steps > 0:
             vout = round((vout + v_step),4)
         else:
             vout = round((vout - v_step), 4)
     ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, v_end))

def ngi_slope_n_level(s_v, s_time, l_v, l_time):
    '''
    create slop and then keep the level
    '''
    ngi_slope(s_v,l_v,s_time)
    ngi_level(l_v, l_time)




def EHV01a():

    t_hold = 60*5
    t_h = 60*5
    t_r = 60*5

    ngi_set_voltages(v_opmax_hv)
    ngi_output_on()

    ngi_level(v_opmax_hv, t_h)

    ngi_slope(v_opmax_hv,  v_n, t_r)
    ngi_level( v_n, t_h)


    ngi_slope( v_n, v_opmin_hv, t_r)
    ngi_level(v_opmin_hv, t_h)

    ngi_level( v_n, t_h)

    ngi_slope(v_opmin_hv, v_n, t_r)
    ngi_level(v_n, t_h)

    ngi_slope(v_n,v_opmax_hv, t_r)
    ngi_level(v_opmax_hv, t_h)
     # END OF EHV01 test


def DeratingCurve(base, max_min):
   t_h = 5 # seconds
   t_r = 5
   n_times = int(240/20)
   ngi_level(base, 60)
   for i in range(n_times):
       ngi_slope(base,max_min, t_r)
       ngi_level(max_min, t_h)

       ngi_slope(max_min, base, t_r)
       ngi_level(max_min, base)




def EHV01b():

     n_cycles = 1
     t_hold = 60*5
     t_h1=t_h3=t_h4=t_h5=t_h6 = 60*5
     t_r1=t_r2 = 60*5
     t_h2=t_h3 = 60*5
     t_f1=t_f2 = 60*5

     ngi_set_voltages(v_op_unlim_max_hv)
     ngi_output_on()

     for z in range(n_cycles):
          ngi_level(v_op_unlim_max_hv, t_h1)
          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv)
          ngi_level(v_op_unlim_max_hv, t_h1)

          ngi_slope(v_op_unlim_max_hv,  v_n, t_f1)
          ngi_level(v_n, t_h2)

          ngi_slope(v_n, v_op_unlim_min_hv, t_f2)

          ngi_level(v_op_unlim_min_hv, t_h3)
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv)

          ##### Middle point, mirrored curve
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv, n_pulses)
          ngi_level(v_op_unlim_min_hv, t_h4)

          ngi_slope(v_op_unlim_min_hv, v_n, t_r1)
          ngi_level(v_n, t_h5)

          ngi_slope(v_n, v_op_unlim_max_hv, t_r2)
          ngi_level(v_op_unlim_max_hv, t_h6)

          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv, n_pulses)
          ngi_level(v_op_unlim_max_hv, t_h1)
     # END OF EHV01 test



def EHV_02():
    '''
    EHV 02 test for PPE41C
    '''

    t_hold = 60*5
    t_h = 60
    t_r = 60
    vcell = 3.4
    ngi_set_voltages(vcell)
    ngi_output_on()
    time.sleep(t_hold)
    for z in range(3):
         ngi_level(v_n_hv, t_h)

         ngi_slope(v_n_hv, v_opmax_hv, t_r)
         ngi_level(v_opmax_hv, t_h)

         ngi_slope(v_opmax_hv, v_ov_1, t_r)
         ngi_level(v_ov_1, t_h)

         ngi_slope(v_ov_1, v_opmax_hv, t_r)
         ngi_level(v_opmax_hv, t_h)

         ngi_slope(v_opmax_hv, v_ov_2, t_r)
         ngi_level(v_ov_2, t_h)

         ngi_slope(v_ov_2, v_opmax_hv, t_r)
         ngi_level(v_opmax_hv, t_h)

         ngi_slope(v_opmax_hv, v_max_hv, t_r)
         ngi_level(v_max_hv, t_h)

         ngi_slope(v_max_hv, v_n_hv,  t_r)
         ngi_level(v_n_hv, t_h)

    # END OF EHV02 test


def EHV03():
     n_cycles = 3
     t_hold = 60
     t_h1=t_h2=t_h3=t_h4= 60
     t_h5=t_h6=t_h7=t_h8= 60
     t_r1=t_r2=t_r3=t_r4 = 60
     t_f1=t_f2=t_f3=t_f4 = 60

     ngi_set_voltages(v_n)
     ngi_output_on()

     for z in range(n_cycles):
          ngi_level(v_n, t_h1)

          ngi_slope_n_level(v_n, t_r1, v_opmax_hv, t_h2)

          ngi_slope_n_level(v_opmax_hv, t_r2, v_ov_1, t_h3)

          ngi_slope_n_level(v_ov_1, t_f1, v_opmax_hv, t_h4)

          ngi_slope_n_level(v_opmax_hv, t_r3, v_ov_2, t_h5)

          ngi_slope_n_level(v_ov_2, t_f2, v_opmax_hv, t_h6)

          ngi_slope_n_level(v_opmax_hv, t_r4, v_max_hv, t_h7)

          ngi_slope_n_level(v_max_hv, t_f3, v_n, t_h8)

     # END OF EHV03 test

# def EHV07(temp_from_csv):
#
#     data = pd.read_csv(ehv7_csvfile)
#     test_mask = data["Temp, degC"] == temp_from_csv
#     test_case = data[test_mask]
#     t_h = 5  # seconds
#     for z in range(len(test_case)):
#         print()
#         SoC_0 = test_case.iloc[z]["0%"]
#         SoC_20 = test_case.iloc[z]["20%"]
#         SoC_40 = test_case.iloc[z]["40%"]
#         SoC_60 = test_case.iloc[z]["60%"]
#         SoC_80 = test_case.iloc[z]["80%"]
#         SoC_100 = test_case.iloc[z]["100%"]
#         txt_SoC = test_case.iloc[z]["SOC"]
#         txt_Process = test_case.iloc[z]["Process"]
#         txt_TestID = test_case.iloc[z]["Test_ID"]
#         txt_Temp = test_case.iloc[z]["Temp, degC"]
#         txt = f"[{z+1}/{len(test_case)}]: "
#               f"TestId: {txt_TestID} "
#               f"Temp: {txt_Temp} "
#               f"Process: {txt_Process} "
#               f"SoC: {txt_SoC} "
#               f"0%: {SoC_0} "
#               f"100%: {SoC_100} "
#     print(txt)
#
#         SoC_list = [SoC_0,
#                     SoC_100,
#                     SoC_0,
#                     SoC_20,
#                     SoC_80,
#                     SoC_20,
#                     SoC_40,
#                     SoC_100,
#                     SoC_40,
#                     SoC_80,
#                     SoC_40,
#                     SoC_60,
#                     SoC_0,
#                     SoC_40,
#                     SoC_20,
#                     SoC_0
#                     ]
#
#         n_cycles = 3
#         ngi_level(SoC_0, 15)
#         for zz in range(n_cycles):
#             for SoC in SoC_list:
#                 ngi_level(SoC, t_h)


def OnOff_test():
    n_cycles = 3
    t_on = 10
    v_on = 4.2
    t_slope = 10
    t_off = 5
    v_off = 0

    n_cycles = 200000
    for z in range(n_cycles):
        ngi_slope_n_level(v_off, t_slope, v_on, t_on)
        ngi_level(v_off, t_off)
        time.sleep(3)
        ngi_slope_n_level(v_off, t_slope, v_on, t_on)
        ngi_slope_n_level(v_on, t_slope, v_off, t_off)
        time.sleep(3)

if __name__ == '__main__':
    ngi_ini_conf()
    ngi_set_voltages(4.2)
    ngi_output_on()
    # OnOff_test()
    # EHV01a()
    # ngi_level(2.25, 10*60)
    # time.sleep()
    # EHV01b()
    #
    # EHV_02()
    #
    # EHV03()
    #
    # EHV07(-25)
    # EHV07(55)
    # EHV07(20)




























    ngi_close()