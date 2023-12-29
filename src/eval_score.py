import torch
import sys
import os
# sys.path.append(os.path.abspath('../src/'))
import models
from pynvml import *


def print_gpu_utilization():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")

def feature_normalize(input_feat):
    norm_mean, norm_std = 3.203, 4.045
    feat_norm = torch.zeros_like(input_feat)
    for i in range(input_feat.shape[0]):
        for j in range(input_feat.shape[1]):
            if input_feat[i, j, 0] != 0:
                feat_norm[i, j, :] = (input_feat[i, j, :] - norm_mean) / norm_std
            else:
                break
    return feat_norm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gopt = models.GOPT(embed_dim=24, num_heads=1, depth=3, input_dim=84)
# print('running on ' + str(device))
# GOPT is trained with dataparallel, so it need to be wrapped with dataparallel even you have a single gpu or cpu
gopt = torch.nn.DataParallel(gopt)
sd = torch.load('../pretrained_models/gopt_librispeech/test/best_audio_model.pth', map_location='cpu')
gopt.load_state_dict(sd, strict=True)
gopt = gopt.to(device)

def gopt_score(list_len_phn):
    from eval_score import gopt

    import numpy as np
    input_feat = np.load("../data/seq_data_mydataset/te_feat.npy")
    input_phn = np.load("../data/seq_data_mydataset/te_label_phn.npy")
    gopt = gopt.float()
    gopt.eval()
    with torch.no_grad():
        t_input_feat = torch.from_numpy(input_feat[:,:,:])
        t_input_feat = feature_normalize(t_input_feat)
        t_phn = torch.from_numpy(input_phn[:,:,0])
        u1, u2, u3, u4, u5, p, w1, w2, w3 = gopt(t_input_feat.float(),t_phn.float())
        
        index, index_word = 0, 0
        w_acc, w_st, w_total, phn = [], [], [], []
        utter = [u1.item(), u2.item(), u3.item(), u4.item(), u5.item()]
        
        for len_phn in list_len_phn:
            w1_mean_score, w2_mean_score, w3_mean_score = 0, 0, 0
            for i in range(len_phn):
                w1_mean_score += w1.data.cpu().numpy()[0][index].item()
                w2_mean_score += w2.data.cpu().numpy()[0][index].item()
                w3_mean_score += w3.data.cpu().numpy()[0][index].item()
                phn.append(p.data.cpu().numpy()[0][index].item())
                index += 1
            w1_mean_score, w2_mean_score, w3_mean_score = w1_mean_score/len_phn, w2_mean_score/len_phn, w3_mean_score/len_phn
            w_acc.append(w1_mean_score)
            w_st.append(w2_mean_score)
            w_total.append(w3_mean_score)
            # print(f"{index_word}: w1:{w1_mean_score:.2f}, w2:{w2_mean_score:.2f}, w3:{w3_mean_score:.2f}.")
            index_word += 1

        # print(list_len_phn)

        return utter, w_acc, w_st, w_total, phn
    
def batch_gopt_score():
    from eval_score import gopt

    import numpy as np
    input_feat = np.load("../data/seq_data_mydataset/te_feat.npy")
    input_phn = np.load("../data/seq_data_mydataset/te_label_phn.npy")
    gopt = gopt.float()
    gopt.eval()
    with torch.no_grad():
        t_input_feat = torch.from_numpy(input_feat[:,:,:])
        t_input_feat = feature_normalize(t_input_feat)
        t_phn = torch.from_numpy(input_phn[:,:,0])
        print_gpu_utilization()
        u1, u2, u3, u4, u5, p, w1, w2, w3 = gopt(t_input_feat.float(),t_phn.float())
        print_gpu_utilization()
        
        utter = torch.cat((u1,u2,u3,u4,u5), dim=1)
        utt_avg = torch.mean(utter, dim=0)

        return utter, utt_avg

if __name__ == "__main__":
    gopt_score()