import play
def print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text):
    ret = f"Accuracy:{utter[0]:.0f}, Completeness:{utter[1]:.0f}, Fluency:{utter[2]:.0f}, Prosodic:{utter[3]:.0f}, Total:{utter[4]:.0f}\n"
    word = text.split()
    time, index = 0, 0
    for len_phn in list_len_phn:
        p = "[ "
        for i in range(len_phn):
            p += f"{phn[index]:.0f} "
            index += 1
        
        ret = ret + f"{word[time]:10}" + f": accuracy:{w_acc[time]:.0f}, " \
                + f"stress:{w_st[time]:.0f}, " + f"score:{w_total[time]:.0f}  {p} ]\n"

        time += 1
    print(ret)
    return ret

def gopt_score(voice, text):
    play.reflush()
    check, list_len_phn = play.prepare_gop(voice, text)
    if check != "OK":
        return "bugs"
    utter, w_acc, w_st, w_total, phn = play.run_gopt(list_len_phn)
    if utter == 0:
        print("infer error!")
        return "error"
    ret = print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text)
    return ret

gopt_score("/data/master/yangming3/gopt/lttc_dir/112020303011/112020303011_10013.wav" ,"for another lining up this way helps them stay together".upper())
