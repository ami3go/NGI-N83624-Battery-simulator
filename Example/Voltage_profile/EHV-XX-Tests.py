import src.n83624_06_05_class as bat_sim
import time

global ngi, s_ch, e_ch
ngi = bat_sim.n83624_06_05_class()
ngi.init("COM12")

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
    ngi.send(ngi.cmd.output.mode_source.ch_range(s_ch, e_ch,))

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
    print(f"flat line, V={v_out} V, Time = {t_del_sec} sec")
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
     print(f"Slope, Vstart={v_start} V, Vend={v_end}, Time = {t_tran_sec} sec, *** "
           f"Condition {cond }, tdealy: {tdelay}, steps: {n_steps}, Vstep: {v_step}")   
           
     for v in range(abs(n_steps)):
         ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, vout))
         time.sleep(tdelay)
         time.sleep(0.05)
         if n_steps > 0:
             vout = round((vout + v_step),4)
         else:
             vout = round((vout - v_step), 4)
     ngi.send(ngi.cmd.source.voltage.ch_range(s_ch, e_ch, v_end))

def EHV_02():
    '''
    EHV 02 test for PPE41C
    '''
    v_max_hv = 5.5
    v_ov_2 = 5
    v_ov_1 =4.5
    v_opmax_hv = 4.2
    v_n_hv = 3.4
    t_hold = 60*4
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

def EHV01a():
     v_opmax_hv = 4.2
     v_n = 3.4
     v_opmin_hv = 2.416

     t_hold = 60*4
     t_h = 60                                       
     t_r = 60

     ngi_set_voltages(v_opmax_hv)
     ngi_output_on()                                
     ngi_level(v_opmax_hv, t_hold)

     for z in range(3):
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


def DeratingCurve(base, max_min, n_times = 2):
       t_h = 5 # seconds
       for i in range(n_times):
           ngi_level(base, t_h)
           ngi_slope(base,max_min, t_h)

           ngi_level(max_min, t_h)
           ngi_slope(max_min, base, t_h)




def EHV01a():                                                 
     v_opmax_hv = 4.2                                         
     v_n = 3.4                                                
     v_opmin_hv = 2.416                                       
                                                              
     t_hold = 60*4                                            
     t_h = 60                                                 
     t_r = 60                                                 
                                                              
     ngi_set_voltages(v_opmax_hv)                             
     ngi_output_on()                                          
     ngi_level(v_opmax_hv, t_hold)                            
                                                              
     for z in range(3):                                       
          ngi_level(v_opmax_hv, t_h)                          
                                                              
          ngi_slope(v_opmax_hv,  v_n, t_r)                    
          ngi_level( v_n, t_h)                                
                                                              
                                                              
          ngi_slope( v_n, v_opmin_hv, t_r)                    
          ngi_level(v_opmin_hv, t_h)                          
          # middle point
          ngi_level(v_opmin_hv, t_h)
                                                              
          ngi_slope(v_opmin_hv, v_n, t_r)                     
          ngi_level(v_n, t_h)                                 
                                                              
          ngi_slope(v_n,v_opmax_hv, t_r)                      
          ngi_level(v_opmax_hv, t_h)                          
     # END OF EHV01 test                                      

def EHV01b():
     v_opmax_hv = 5.5
     v_op_unlim_max_hv = 4.2
     v_n = 3.4
     v_op_unlim_min_hv = 2.416
     v_opmin_hv = 1.5

     n_pulses = 2

     t_hold = 60*3
     t_h1=t_h3=t_h4=t_h5=t_h6 = 60
     t_r1=t_r2 = 5
     t_h2=t_h3 = 5
     t_f1=t_f2 = 5

     ngi_set_voltages(v_op_unlim_max_hv)
     ngi_output_on()
     ngi_level(v_op_unlim_max_hv, t_hold)

     for z in range(3):
          ngi_level(v_op_unlim_max_hv, t_h1)
          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv, n_pulses)
          ngi_level(v_op_unlim_max_hv, t_h1)

          ngi_slope(v_op_unlim_max_hv,  v_n, t_f1)
          ngi_level(v_n, t_h2)

          ngi_slope(v_n, v_op_unlim_min_hv, t_f2)

          ngi_level(v_op_unlim_min_hv, t_h3)
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv, n_pulses)
          ngi_level(v_op_unlim_min_hv, t_h3)

          ##### Middle point, mirrored curve
          ngi_level(v_op_unlim_min_hv, t_h3)
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv, n_pulses)
          ngi_level(v_op_unlim_min_hv, t_h4)

          ngi_slope(v_op_unlim_min_hv, v_n, t_r1)
          ngi_level(v_n, t_h5)

          ngi_slope(v_n, v_op_unlim_max_hv, t_r2)
          ngi_level(v_op_unlim_max_hv, t_h6)

          ngi_level(v_op_unlim_max_hv, t_h1)
          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv, n_pulses)
          ngi_level(v_op_unlim_max_hv, t_h1)
     # END OF EHV01 test

def EHV03():


     v_n_hv = 3.4
     v_opmin_hv = 2.416
     v_m  =    1.5
     v_min_hv =  1.125
     v_zero = 0
     n_pulses = 2

     t_hold = 60*3
     t_h1=t_h3=t_h4=t_h5=t_h6 = 60
     t_r1=t_r2 = 5
     t_h2=t_h3 = 5
     t_f1=t_f2 = 5

     ngi_set_voltages(v_op_unlim_max_hv)
     ngi_output_on()
     ngi_level(v_op_unlim_max_hv, t_hold)

     for z in range(3):
          ngi_level(v_op_unlim_max_hv, t_h1)
          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv, n_pulses)
          ngi_level(v_op_unlim_max_hv, t_h1)

          ngi_slope(v_op_unlim_max_hv,  v_n, t_f1)
          ngi_level(v_n, t_h2)

          ngi_slope(v_n, v_op_unlim_min_hv, t_f2)

          ngi_level(v_op_unlim_min_hv, t_h3)
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv, n_pulses)
          ngi_level(v_op_unlim_min_hv, t_h3)

          ##### Middle point, mirrored curve
          ngi_level(v_op_unlim_min_hv, t_h3)
          DeratingCurve(v_op_unlim_min_hv, v_opmin_hv, n_pulses)
          ngi_level(v_op_unlim_min_hv, t_h4)

          ngi_slope(v_op_unlim_min_hv, v_n, t_r1)
          ngi_level(v_n, t_h5)

          ngi_slope(v_n, v_op_unlim_max_hv, t_r2)
          ngi_level(v_op_unlim_max_hv, t_h6)

          ngi_level(v_op_unlim_max_hv, t_h1)
          DeratingCurve(v_op_unlim_max_hv, v_opmax_hv, n_pulses)
          ngi_level(v_op_unlim_max_hv, t_h1)
     # END OF EHV01 test



if __name__ == '__main__':
    # ngi_ini_conf()
    # EHV_02()
    # EHV01a()
    EHV01b()






























    ngi_close()