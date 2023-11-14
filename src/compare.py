import csv
from scipy.stats import pearsonr
def main(fileA = '../data/wav/capt_logs_gt90_with_phone_gop.csv', fileB = "output.csv"):
    with open(fileA, 'r', newline='') as fileA, open(fileB, 'r', newline='') as fileB:        
        readerA = csv.DictReader(fileA)
        readerB = csv.DictReader(fileB)
        word_acc, word_st, word_total = [], [], []

        for f1, f2 in zip(readerA, readerB):
            utt_acc = int(f1["sentence_accuracy"]) - int(f2['utt_acc'])
            utt_comp = float(f1["sentence_completeness"])*100  - float(f2['utt_comp'])
            utt_flu = int(f1["sentence_fluency"]) - int(f2['utt_flu'])
            utt_pros = int(f1["sentence_prosodic"]) - int(f2['utt_pros'])
            utt_total = int(f1["sentence_total"]) - int(f2['utt_total'])

            # 将比较结果存储到另一个CSV文件
            with open('comparison_result.csv', 'a', newline='') as result_file:
                fieldnames = ['id', 'sentence', 
                              'utt_acc', 'utt_comp', 'utt_flu', 'utt_pros', 'utt_total',
                              'gop', 'aver_phn',
                ]
                writer = csv.DictWriter(result_file, fieldnames=fieldnames)
                writer.writerow({'id': f1["id"], 'sentence': f1["sentence"], 
                                 'utt_acc': utt_acc, 'utt_comp': int(utt_comp), 'utt_flu': utt_flu, 'utt_pros': utt_pros, 'utt_total': utt_total,
                                 'gop': f2["gop"], 'aver_phn': f2['aver_phn'],                                
                                })
                
def print_pcc(filename = "output.csv"):
    with open(filename, 'r', newline='') as file:        
        f_reader = csv.DictReader(file)
        x, y = [], []
        for f in f_reader:
            x.append(float(f['gop']))
            # y.append(float(f['gop']))
            y.append(float(f['aver_phn']))
        pccs = pearsonr(x, y)
        print(pccs)

    return 

if __name__ == "__main__":
    with open('comparison_result.csv', 'w', newline='') as result_file:
        fieldnames = ['id', 'sentence', 
                      'utt_acc', 'utt_comp', 'utt_flu', 'utt_pros', 'utt_total',
                      'gop', 'aver_phn',
        ]

        writer = csv.DictWriter(result_file, fieldnames=fieldnames)
        writer.writeheader()

    main()
    print_pcc()