import subprocess
import random
import time
import eval_score
import os
from pydub import AudioSegment
from alive_progress import alive_bar
import logging

logger = logging.getLogger("")


def clear_file_content(file_path):
    """
    清空文件的内容。
    
    Args:
        file_path (str): 要清空内容的文件路径。
    """
    with open(file_path, 'w') as file:
        pass

def cp_file(src_file, dst_file = "output.txt"):
    # 构建Shell命令
    command = ["cp", "-r", src_file, dst_file]
    dst_dir = os.path.dirname(dst_file)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    # 执行Shell命令
    try:
        subprocess.run(command, check=True)
        # print(f"Created {dst_file}: copyed by {src_file}.")
    except subprocess.CalledProcessError:
        print("cp_file() error.")
        pass

def del_file(file_path):
    # 构建Shell命令
    command = ["rm", "-rf" , file_path]
    # 执行Shell命令
    print("in del_file")
    try:
        subprocess.run(command, check=True)
        print(f" {file_path} deleted successfully.")
    except subprocess.CalledProcessError:
        print(f"Error executing {file_path}.")
        pass

def run_script(pre_path, script_path):
    # 构建Shell命令
    # command = ["./" + script_path]
    # get_current_directory()
    script = f"""
                #!/bin/bash
                cd {pre_path}
                ./{script_path}
            """
    # 执行Shell命令

    # subprocess.run(command, check=True)
    result = subprocess.run(script, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"{script_path}執行成功")
        # print(result.stdout)
        return 0
    else:
        print(f"{script_path}執行失敗，錯誤輸出: ")
        print(result.stdout)
        print(result.stderr)
        return "error"

def get_current_directory():
    script = """
    #!/bin/bash

    current_directory=$(pwd)
    echo "$current_directory"
    """

    result = subprocess.run(script, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        # print(result.stdout.strip())
        return result.stdout.strip()
    else:
        return "脚本执行失败，错误输出：" + result.stderr

def run_python(pre_path, python_path):
    # 构建Shell命令
    # command = ["python3", python_path]
    # get_current_directory()
    script = f"""
                #!/bin/bash
                cd {pre_path}
                python3 {python_path}
            """
    # 执行Shell命令
    try:
        # subprocess.run(command, check=True)
        result = subprocess.run(script, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"{python_path}執行成功")
            print(result.stdout)
        else:
            print(f"{python_path}執行失敗，錯誤輸出: ")
            print(result.stdout)
            print(result.stderr)
    except subprocess.CalledProcessError:
        print(f"Error executing {python_path}.")

def load_lexicon(filename):
    lexicon = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    word, pronunciation = parts[0], parts[1]
                    lexicon[word] = pronunciation
    return lexicon

def process_phone(phone):
    phonemes = phone.split()
    processed_phones = []
    len_phone = len(phonemes)
    if len_phone == 1:
        processed_phones.append(phonemes[0] + "_S")
    else:
        processed_phones.append(phonemes[0] + "_B")
        for phoneme in phonemes[1:-1]:
            processed_phones.append(phoneme + "_I")
        processed_phones.append(phonemes[-1] + "_E")

    return " ".join(processed_phones), len_phone

def find_phone(word):
    lexicon_file = 'lexicon.txt'

    lexicon = load_lexicon(lexicon_file)
    lexicon2 = load_lexicon('../cmudict/new.txt')

    if word in lexicon:
        pronunciation = lexicon[word]
        pronunciation, len = process_phone(pronunciation)
        return pronunciation, len
    elif word in lexicon2:
        pronunciation = lexicon2[word]
        write_new_lexicon(word, pronunciation)
        pronunciation, len = process_phone(pronunciation)
        return pronunciation, len
    else:
        return "error", 0

def write_new_lexicon(new_key, new_value, dst_path = 'lexicon.txt'):
    existing_data = {}
    with open(dst_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('\t')
            # print(key + " +++ " + value)
            existing_data[key] = value

    # 添加新的 key-value 對
    # new_key = 'ACCEPT'
    # new_value = 'AH0 K S EH1 P T'
    existing_data[new_key] = new_value

    # 按字典序排序 key
    sorted_keys = sorted(existing_data.keys())

    # 寫回檔案
    with open(dst_path, 'w') as file:
        for key in sorted_keys:
            file.write(f'{key}\t{existing_data[key]}\n')

def read_random_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        total_lines = len(lines)
        
        if total_lines == 0:
            return None
        
        random_line_number = random.randint(1, total_lines)
        random_line = lines[random_line_number - 1].strip()
        
        return random_line

def write_text(filename, text):
    try:
        with open(filename, 'a') as file:
            file.write(text)
        return "成功寫入檔案。"
    except Exception as e:
        print(f"寫入檔案時發生錯誤：{str(e)}")
        return "error"

def choose_text():
    speechOcean = "/home/yu_hsiu/forked/yang_gopt/kaldi/egs/gop_speechocean762/s5/data/train/"
    file = "text"
    text = read_random_line(speechOcean + file)
    if text is None:
        print("生成文字發生錯誤。")
        return "error"
    file_id = text[:9]
    text = text[10:]
    return f"{text}", file_id

def convert_phone(text, id):
    words = text.upper().split(" ")
    ret = ""
    words_len_phn = []
    for index, word in enumerate(words):
        phones, len_phn = find_phone(word)
        if len_phn == 0:
            print(word)
            print(phones)
            return "error", [0]
        words_len_phn.append(len_phn)
        ret = ret + f"{id}.{index} {phones}\n"
    return ret, words_len_phn

def resampleAndSave(wav, new_sample_rate, path_name):
    audio = AudioSegment.from_wav(wav)

    # 重新采样
    resampled_audio = audio.set_frame_rate(new_sample_rate)

    # 将重新采样的音频保存为新的文件
    resampled_audio.export(path_name, format='wav')
    return 

def run_gopt(list_len_phn):
    with alive_bar(len(range(4))) as bar:
        bar()  # 顯示進度
        kaldi_start_time = time.time()
        ret = run_script("../kaldi/egs/gop_speechocean762/s5/", "run.sh")
        kaldi_end_time = time.time()
        logger.debug(f"kaldi time: {kaldi_end_time - kaldi_start_time}")
        if ret != 0:
            print("run.sh error")
            return 0, 0, 0, 0, 0
        bar()  # 顯示進度
        os.environ['KALDI_ROOT']='/home/yu_hsiu/kaldi'
        run_python("../kaldi/egs/gop_speechocean762/s5/", "local/extract_gop_feats.py")
        print("extract gop ok")
        cp_file("../kaldi/egs/gop_speechocean762/s5/gopt_feats/", "../data/raw_kaldi_gop/mydataset/")
        print("cp ok")
        bar()  # 顯示進度
        run_python("prep_data/", "gen_seq_data_phn_demo.py")
        print("gen seq data ok")
        bar()  # 顯示進度
        gopt_start_time = time.time()
        ret = eval_score.gopt_score(list_len_phn)
        gopt_end_time = time.time()
        logger.debug(f"gopt time: {gopt_end_time - gopt_start_time}")
        return ret

def prepare_gop(audio, text):
    spk = "9999"
    voice_name = f"0{spk}8787_{spk}"

    socean_dst_path = "../kaldi/egs/gop_speechocean762/s5/data/speechocean762/"
    resource_file = "resource/text-phone"
    test_file = ["test/spk2utt", "test/text", "test/utt2spk", "test/wav.scp"]
    wave_file = f"WAVE/SPEAKER{spk}/{voice_name}.wav"
    SAMPLE_RATE = 16000

    if not os.path.isdir(os.path.dirname(socean_dst_path+wave_file)):
        os.makedirs(os.path.dirname(socean_dst_path+wave_file))
    if not os.path.isdir(os.path.dirname(socean_dst_path+test_file[0])):
        os.makedirs(os.path.dirname(socean_dst_path+test_file[0]))

    resampleAndSave(audio, SAMPLE_RATE, socean_dst_path+wave_file)
    write_text(socean_dst_path+test_file[0], f"{spk} {voice_name}\n")             # spk2utt
    write_text(socean_dst_path+test_file[1], f"{voice_name} {text.upper()}\n")    # text
    write_text(socean_dst_path+test_file[2], f"{voice_name} {spk}\n")             # utt2spk
    write_text(socean_dst_path+test_file[3], f"{voice_name} {wave_file}\n")       # wav.scp

    a_list_of_text_phone, list_len_phn = convert_phone(text.upper(), voice_name)
    if a_list_of_text_phone == "error":
        return "convert phone error", [0]
    cp_file(socean_dst_path+resource_file, socean_dst_path+resource_file+"a")

    ret = write_text(socean_dst_path+resource_file, f"{a_list_of_text_phone}")      # text-phone
    if ret == "error":
        return "write_text text-phone error", [0]
    return "OK", list_len_phn

def reflush():
    spk = "9999"
    voice_name = f"0{spk}8787_{spk}"

    socean_dst_path = "../kaldi/egs/gop_speechocean762/s5/data/speechocean762/"
    resource_file = "resource/text-phone"
    test_file = ["test/spk2utt", "test/text", "test/utt2spk", "test/wav.scp"]
    wave_file = f"WAVE/SPEAKER{spk}/{voice_name}.wav"

    del_file(socean_dst_path+wave_file)
    del_file("../kaldi/egs/gop_speechocean762/s5/data/test")
    # del_file("../kaldi/egs/gop_speechocean762/s5/data/local")
    # del_file("../kaldi/egs/gop_speechocean762/s5/data/lang_nosp")
    del_file(socean_dst_path+"test/spk2age")
    del_file(socean_dst_path+"test/spk2gender")
    clear_file_content(socean_dst_path+test_file[0])    # spk2utt
    clear_file_content(socean_dst_path+test_file[1])    # text
    clear_file_content(socean_dst_path+test_file[2])    # utt2spk
    clear_file_content(socean_dst_path+test_file[3])    # wav.scp   
    try: 
        with open(socean_dst_path+resource_file, 'w') as file_a, open(socean_dst_path+resource_file+"a", 'r') as file_b:
            # 讀取檔案B的內容
            content_b = file_b.read()
            
            # 將檔案B的內容寫入檔案A
            file_a.write(content_b)
    except:
        print("no replace text-phone")
        pass

    print("reflush OK")

def batch_run_gopt():
    with alive_bar(len(range(4))) as bar:
        write_text("../kaldi/egs/gop_speechocean762/s5/data/speechocean762/test/spk2utt", f"\n")
        bar()  # 顯示進度
        kaldi_start_time = time.time()
        ret = run_script("../kaldi/egs/gop_speechocean762/s5/", "run.sh")
        kaldi_end_time = time.time()
        logger.debug(f"kaldi time: {kaldi_end_time - kaldi_start_time}")
        if ret != 0:
            print("run.sh error")
            return 0, 0
        bar()  # 顯示進度
        os.environ['KALDI_ROOT']='/home/yu_hsiu/kaldi'
        run_python("../kaldi/egs/gop_speechocean762/s5/", "local/extract_gop_feats.py")
        print("extract gop ok")
        cp_file("../kaldi/egs/gop_speechocean762/s5/gopt_feats/", "../data/raw_kaldi_gop/mydataset/")
        print("cp ok")
        bar()  # 顯示進度
        run_python("prep_data/", "gen_seq_data_phn_demo.py")
        print("gen seq data ok")
        bar()  # 顯示進度
        gopt_start_time = time.time()
        ret = eval_score.batch_gopt_score()
        gopt_end_time = time.time()
        logger.debug(f"gopt time: {gopt_end_time - gopt_start_time}")
        return 1, ret

def batch_prepare_gop(audio, text, id):
    spk = "9999"
    voice_name = f"0{spk}{id:04d}"

    socean_dst_path = "../kaldi/egs/gop_speechocean762/s5/data/speechocean762/"
    resource_file = "resource/text-phone"
    test_file = ["test/spk2utt", "test/text", "test/utt2spk", "test/wav.scp"]
    wave_file = f"WAVE/SPEAKER{spk}/{voice_name}.wav"
    SAMPLE_RATE = 16000

    if not os.path.isdir(os.path.dirname(socean_dst_path+wave_file)):
        os.makedirs(os.path.dirname(socean_dst_path+wave_file))
    if not os.path.isdir(os.path.dirname(socean_dst_path+test_file[0])):
        os.makedirs(os.path.dirname(socean_dst_path+test_file[0]))

    a_list_of_text_phone, list_len_phn = convert_phone(text.upper(), voice_name)
    if a_list_of_text_phone == "error":
        return "convert phone error", [0]
    num_phns = 0
    for word_len in list_len_phn:
            num_phns += word_len
            if num_phns >= 60:
                return "sentence too long", [0]
    resampleAndSave(audio, SAMPLE_RATE, socean_dst_path+wave_file)
    if read_random_line(socean_dst_path+test_file[0]) == None:
        write_text(socean_dst_path+test_file[0], f"{spk} {voice_name}")             # spk2utt
    else:
        write_text(socean_dst_path+test_file[0], f" {voice_name}")
    write_text(socean_dst_path+test_file[1], f"{voice_name} {text.upper()}\n")    # text
    write_text(socean_dst_path+test_file[2], f"{voice_name} {spk}\n")             # utt2spk
    write_text(socean_dst_path+test_file[3], f"{voice_name} {wave_file}\n")       # wav.scp

    cp_file(socean_dst_path+resource_file, socean_dst_path+resource_file+"a")

    ret = write_text(socean_dst_path+resource_file, f"{a_list_of_text_phone}")      # text-phone
    if ret == "error":
        return "write_text text-phone error", [0]
    return "OK", list_len_phn

def batch_reflush():
    spk = "9999"

    socean_dst_path = "../kaldi/egs/gop_speechocean762/s5/data/speechocean762/"
    resource_file = "resource/text-phone"
    test_file = ["test/spk2utt", "test/text", "test/utt2spk", "test/wav.scp"]
    wave_dir = f"WAVE/SPEAKER{spk}/"

    del_file(socean_dst_path+wave_dir)
    del_file("../kaldi/egs/gop_speechocean762/s5/data/test")
    # del_file("../kaldi/egs/gop_speechocean762/s5/data/local")
    # del_file("../kaldi/egs/gop_speechocean762/s5/data/lang_nosp")
    del_file(socean_dst_path+"test/spk2age")
    del_file(socean_dst_path+"test/spk2gender")
    clear_file_content(socean_dst_path+test_file[0])    # spk2utt
    clear_file_content(socean_dst_path+test_file[1])    # text
    clear_file_content(socean_dst_path+test_file[2])    # utt2spk
    clear_file_content(socean_dst_path+test_file[3])    # wav.scp   
    try: 
        with open(socean_dst_path+resource_file, 'w') as file_a, open(socean_dst_path+resource_file+"a", 'r') as file_b:
            # 讀取檔案B的內容
            content_b = file_b.read()
            
            # 將檔案B的內容寫入檔案A
            file_a.write(content_b)
    except:
        print("no replace text-phone")
        pass

    print("reflush OK")