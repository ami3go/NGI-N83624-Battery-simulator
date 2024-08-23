ch_start = 1
ch_end = 10
txt = ""
for z in range(ch_start, ch_end + 1):
    txt = txt + f"{z},"
    print(txt)
txt = f"(@{txt[0:-1]})"
print(txt)

# class str_ch_num(ch_str):
#     def __init__(self, prefix, ending):
#         super().__init__(prefix, max_ch=max_ch_number) # will make universal latter
#         self.ending = ":" + ending
#         self.cmd = prefix + self.ending
#         self.prefix = prefix
#         self.__range = _ch_range(prefix, ":" + ending, max_ch=max_ch_number)
#     def ch_range(self, ch_start, ch_end):
#         return self.__range.ch_range(ch_start, ch_end, "")