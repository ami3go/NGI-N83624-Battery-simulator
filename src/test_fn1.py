def ch_list_from_list2(*argv):
    txt = ""
    for items in argv:
        txt = f'{txt}{items},'
    txt = txt[:-1]
    return f'(@{txt})'


def ch_list_from_range(min, max, channels_num=24):
    channels = channels_num

    # min = range_check(min, 1, channels_num, "ch_list_from_range , min")
    # max = range_check(max, 1, channels_num, "ch_list_from_range , max")
    txt = f"{min},"
    l = [f"{min},"]
    for z in range(0, (max - min)):
        l.append(f'{min + z + 1},')
    txt = "".join(l)
    txt = txt[:-1]
    return f"(@{txt})"


txt = ch_list_from_list2(1,2,3,4,5)
print(txt)

txt = ch_list_from_range(1,24)
print(txt)