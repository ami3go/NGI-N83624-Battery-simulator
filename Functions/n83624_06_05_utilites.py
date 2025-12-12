import N83624.n83624_06_05_class as bat_sim


def set_voltage(s_ch=1, e_ch=18, cell_volt=4.3):
    '''
    This script check connection
    It make following algorithm:
    1. Switch Off output voltage
    2. Set current limit to 20 mA
    3. Set voltage to 4.3 V
    4. Switch on output voltage
    5. Read each channel voltage
    6. if at list one channel measure below 1 V, this mean that channel shorter
        Or usually  connector swapped
        in this case it terminate execution indicates which channel is shorted
    7. if all channel are >=4.2 V this mean that connection is ok
    '''
    # initiate NGI battery simulator via LAN network
    # NGI default IP is 192.168.0.111:7000
    # check ping in OK, in case of any error here

    error_description = {}
    error_status = 0
    # detecting if any short circuit or wrong connection
    ngi = bat_sim.n83624_06_05_class_tcp()
    ngi.init(bat_sim.default_ip_port)
    # execute list
    ngi_init_list = [
        ngi.cmd.output.off.ch_range(s_ch, e_ch),
        ngi.cmd.output.mode_source.ch_range(s_ch, e_ch),
        ngi.cmd.source.voltage.ch_range(s_ch, e_ch, cell_volt),
        ngi.cmd.source.current.ch_range(s_ch, e_ch, 20),
        ngi.cmd.source.range_auto.ch_range(s_ch, e_ch),
        ngi.cmd.output.on.ch_range(s_ch, e_ch),
    ]
    for ngi_cmd in ngi_init_list:
        ngi.send(ngi_cmd)
        time.sleep(0.9)

    ngi_voltage = ngi.query(ngi.cmd.measure.voltage.ch_range(s_ch, e_ch)) # read voltage, shorted channel will have low voltage
    ngi_voltage = ngi_voltage.split(",")

    # checking logic and rise error in case of any channel is shorted
    for i in range(len(ngi_voltage)):
        volt = round(float(ngi_voltage[i]), 2)
        key = f"CH{i+1}"
        if volt >= 4.2:
            error_description[key] = f"OK , VOLT: {volt}"
        if volt <= 1:
            error_description[key] = f" *** Shorted ***, VOLT: {volt} *** Shorted *** "
            error_status = 1
    if error_status != 0:
        print(f"{Fore.BLACK}{Back.YELLOW}Something shorted, please check cell connection{Style.RESET_ALL}")
        print()
        for key, value in error_description.items():
            if value.find("Shorted") != -1:
                print(f"{Fore.BLACK}{Back.RED}Key: {key}: {value}{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLACK}{Back.YELLOW}Key: {key}: {value}{Style.RESET_ALL}")
        raise Exception("Sorry, Something shorted. ")
    ngi.send(ngi.cmd.source.current.ch_range(s_ch, e_ch, 500))
    print(f"{Fore.BLACK}{Back.GREEN} **** CMC cell connection OK{Style.RESET_ALL}")
    ngi.close()