import gradio as gr
import os
import torch
import play
import models

def class_HL(str_score, score):
    # if score <1.0:
    #     return [str_score, "bad"] 
    # elif score >1.65:
    #     return [str_score, "great"]
    # else:
    #     return [str_score, "good"]
    if score <50.0:
        if score < 0:
            return ["0", "bad"] 
        return [f"{score:.0f}", "bad"] 
    elif score >75.0:
        if score > 100.0:
            return ["100", "great"]
        return [f"{score:.0f}", "great"] 
    else:
        return [f"{score:.0f}", "good"]

def print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text):
    # print(phn)
    ret = []
    word = text.split()
    time, index = 0, 0
    for len_phn in list_len_phn:
        ret.append([f"【{word[time]:^10}】 Accuracy: ", None])
        ret.append(class_HL(f"{w_acc[time]:.3f}", w_acc[time]))
        ret.append([f"Stress: ", None])
        ret.append(class_HL(f"{w_st[time]:.3f}", w_st[time]))
        ret.append([f"Score: ", None])
        ret.append(class_HL(f"{w_total[time]:.3f}", w_total[time]))
        ret.append([f" [ ", None])

        for i in range(len_phn):
            ret.append(class_HL(f"{phn[index]:.3f} ", phn[index]))
            ret.append([f" ", None])
            index += 1
        ret.append([f" ]\n", None])
        time += 1

    ret.append(["\n Accuracy: ", None])
    ret.append(class_HL(f"{utter[0]:.3f}", utter[0]))
    ret.append([", Completeness: ", None])
    ret.append(class_HL(f"{utter[1]:.3f}", utter[1]))
    ret.append([", Fluency: ", None])
    ret.append(class_HL(f"{utter[2]:.3f}", utter[2]))
    ret.append([", Prosodic: ", None])
    ret.append(class_HL(f"{utter[3]:.3f}", utter[3]))
    ret.append([", Total: ", None])
    ret.append(class_HL(f"{utter[4]:.3f}", utter[4]))
    # print(ret)
    return ret

def gopt_score(text, audio):
    play.reflush()
    check, list_len_phn = play.prepare_gop(audio, text)
    if check != "OK":
        return "bugs"
    utter, w_acc, w_st, w_total, phn = play.run_gopt(list_len_phn)
    ret = print_form(utter, w_acc, w_st, w_total, phn, list_len_phn, text)
    return ret

# save your HF API token from https:/hf.co/settings/tokens as an env variable to avoid rate limiting
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
auth_token = os.getenv("auth_token")

def find_speaker(file_id):
    filename = "/data/master/yangming3/gopt/src/speechocean762/train/utt2spk"
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) == 2 and parts[0] == file_id:
                    return parts[1]
            return None  # 如果找不到對應的id則返回None
    except FileNotFoundError:
        print("檔案不存在")
        return None

example_list = []

example_list.append(["for another lining up this way helps them stay together", f"/data/master/yangming3/gopt/lttc_dir/112020303011/112020303011_10013.wav"])
example_list.append(["today such equipment is no longer in use", f"/data/master/yangming3/gopt/lttc_dir/112020303011/112020303011_1002.wav"])
for i in range(30):
    text, file_id = play.choose_text()
    speaker_id = find_speaker(file_id)
    example_list.append([text.lower(), f"/data/master/yangming3/gopt/src/speechocean762/WAVE/SPEAKER{speaker_id}/{file_id}.WAV"])
text = example_list[-1][0]

mydescription = f"""
<h2>1. Choose one sentence. </h2>
<h2>2. Record your voice or use the example file.</h2>
<h2>3. Press the submit button.</h2>
"""

inputs = [
    gr.Textbox(
        value=example_list[-1][0], 
        label="Prompt Text"),
    gr.Audio(source="microphone", type="filepath", label="Input File"),
]

output = gr.HighlightedText(label="Score",
        color_map={"bad": "red", "good": "yellow", "great": "green"},   
        combine_adjacent=True,      
        show_legend=True,
        # theme=gr.themes.Base(), 
        )

interface = gr.Interface(
    fn=gopt_score,
    inputs=inputs,
    outputs=output,
    live=False,
    allow_flagging='never',
    title="GOPT demo",
    cache_examples=False,
    examples=example_list,
    description=mydescription
)

interface.launch(debug=True, show_error=True, share=True)
