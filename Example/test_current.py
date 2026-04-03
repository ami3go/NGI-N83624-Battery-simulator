import N83624.n83624_06_05_class as bat_sim
import time
import functools
import inspect


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] executed in {elapsed:.4f}s")
        return result
    return wrapper

s_ch = 1
e_ch = 16
sleep_i_avr = 5  # how many measurements for sleep current averaging
ball_i_avr = 3  # how many measurements for balancing current averaging
retry_cnt = 5  # retry counter for reading SID
cmc_cmd_delay = 0.1
# setup NIG
ngi = bat_sim.n83624_06_05_class_tcp()
ngi.init(bat_sim.default_ip_port)
ngi.working_channels = [s_ch, e_ch]
ngi.out_off()
ngi.set_current_range("high")
ngi.set_voltage(3)
ngi.out_on()
# for i in range(16):
#     print(i)
#     ngi.fault_simulation(value="open_pos", start_ch=i+1, end_ch=i+1)
#     ngi.fault_simulation(value="open_neg", start_ch=i+2, end_ch=i+2)
#     time.sleep(2)
#     ngi.fault_simulation(value="normal", start_ch=i + 1, end_ch=i + 1)


ngi.set_sampling_rate("medium")  # setup 10ms measurement time per channel.
start = time.perf_counter()
current = ngi.get_current()
end = time.perf_counter()
elapsed = end - start
print(current)
print(f"Elapsed: {elapsed:.4f}s")
ngi.close()