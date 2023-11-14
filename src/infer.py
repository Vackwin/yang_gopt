import eval_score
import play
import csv
import subprocess
import numpy as np
from tqdm import tqdm

def print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text, gop_phone):
    ret = f"Accuracy:{utter[0]:.0f}, Completeness:{utter[1]:.0f}, Fluency:{utter[2]:.0f}, Prosodic:{utter[3]:.0f}, Total:{utter[4]:.0f}\n"
    word = text.split()
    
    word_acc, word_st, word_total = "", "", ""
    str_phn = ""
    time, index, aver_phn = 0, 0, 0.0
    str_phn = "[ "
    p = ""
    for len_phn in list_len_phn:
        for i in range(len_phn):
            p += f"{phn[index]:.0f} "
            aver_phn += float(phn[index])
            str_phn += f"{phn[index]:.0f} "
            index += 1
        
        ret = ret + f"{word[time]:10}" + f": accuracy:{w_acc[time]:.0f}, " \
                + f"stress:{w_st[time]:.0f}, " + f"score:{w_total[time]:.0f}  {p} ]\n"
        word_acc += f"{w_acc[time]:.0f} "
        word_st += f"{w_st[time]:.0f} "
        word_total += f"{w_total[time]:.0f} "
        time += 1
    aver_phn = aver_phn / index
    str_phn += "]"
    print(ret)
    return word_acc, word_st, word_total, str_phn , f"{aver_phn: .0f}"


def infer(audio, text, id, gop, phone_gop):
    play.reflush()
    check, list_len_phn = play.prepare_gop(audio, text)
    if check != "OK":
        print("\033[91m!!!!gop error!!!!!\033[0m")
        return "bugs"
    utter, w_acc, w_st, w_total, phn = play.run_gopt(list_len_phn)
    if utter == 0:
        print("\033[91m!!!!infer error!!!!!\033[0m")
        return "\033[91m!!!!error!!!!\033[0m"
    print(len(phn), len(phone_gop))
    if len(phn) == len(phone_gop):
        # 使用numpy的corrcoef計算相關係數矩陣
        correlation_matrix = np.corrcoef(phn, phone_gop)
        # 得到相關係數
        correlation_coefficient = correlation_matrix[0, 1]
        print(f"相關係數: {correlation_coefficient}")
    
    word_acc, word_st, word_total, str_phn, aver_phn = print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text, phone_gop)
    with open('output.csv', 'a', newline='') as csvfile:
        # 建立 CSV 檔寫入器
        fieldnames = ['speaker', 'sentence', 'gop', 'utt_acc', 'utt_comp', 'utt_flu', 'utt_pros', 'utt_total',
                        'word_acc', 'word_stress', 'word_total',
                        'aver_phn',
                        'cof',
                        'phn', 'gop_phn',
                      ]

        # # 將 dictionary 寫入 CSV 檔
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if len(phn) == len(phone_gop):
            # 寫入資料
            writer.writerow({'speaker': id, 'sentence': text, 'gop': gop,
                        'utt_acc': int(utter[0]), 'utt_comp': int(utter[1]), 'utt_flu': int(utter[2]), 'utt_pros': int(utter[3]), 'utt_total': int(utter[4]),
                        'word_acc':word_acc, 'word_stress':word_st, 'word_total':word_total,
                        'aver_phn': aver_phn,
                        'cof': correlation_coefficient,
                        'phn': str_phn, 
                        'gop_phn': phone_gop,
                         })
        else:
            writer.writerow({'speaker': id, 'sentence': text, 'gop': gop,
                        'utt_acc': int(utter[0]), 'utt_comp': int(utter[1]), 'utt_flu': int(utter[2]), 'utt_pros': int(utter[3]), 'utt_total': int(utter[4]),
                        'word_acc':word_acc, 'word_stress':word_st, 'word_total':word_total,
                        'aver_phn': aver_phn,
                        'cof': f"{len(phn)}, {len(phone_gop)}",
                        'phn': str_phn, 
                        'gop_phn': phone_gop,
                         })

        
    return 

def main(filename, wav_path):
    # 開啟 CSV 檔案
    with open(filename, newline='') as csvfile:
        # 讀取 CSV 檔案內容
        rows = csv.DictReader(csvfile)
        rows_list = list(rows)

        for i, row in enumerate(tqdm(rows_list)):
            text = take_off(row['sentence'])
            wav_file_name = row['audio_url'][40:]

            run_wget(wav_path, row['audio_url'])

            print(row['id'], text)
            # print(text, wav_path + wav_file_name)
            list_of_numbers = [float(num) for num in row['phone_gop'].strip('[]').split(', ')]
            ret = infer(wav_path + wav_file_name, text, row['id'], row['gop'], list_of_numbers)
            if ret == "bugs":
                return 

def run_wget(wav_path, audio_url):
    # 定义wget命令
    wget_command = f"wget -nc -P {wav_path} {audio_url}"

    # 执行wget命令
    completed_process = subprocess.run(wget_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 檢查子進程的返回碼
    if completed_process.returncode == 0:
        print("Command executed successfully")
    else:
        print("Command failed with return code:", completed_process.returncode)
        stderr_output = completed_process.stderr
        print("stderr output:", stderr_output)


def take_off(text):
    # 要清除的字符列表
    characters_to_remove = ['?', '.', ',', '"', '!', ":",
                            '1', '2', '3', '4', '5'
                            '6', '7', '8', '9', '0'
                            ]
    # 清除字符
    for char in characters_to_remove:
        text = text.replace(char, '')
    return text


if __name__ == "__main__":
    with open('output.csv', 'w', newline='') as csvfile:
        # 建立 CSV 檔寫入器
        fieldnames = ['speaker', 'sentence', 'gop', 'utt_acc', 'utt_comp', 'utt_flu', 'utt_pros', 'utt_total',
                        'word_acc', 'word_stress', 'word_total',
                        'aver_phn',
                        'cof',
                        'phn', 'gop_phn',
                      ]
        # # 將 dictionary 寫入 CSV 檔
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 寫入第一列的欄位名稱
        writer.writeheader()

    main('../data/wav/capt_logs_gt90_with_phone_gop.csv', "../data/wav/")