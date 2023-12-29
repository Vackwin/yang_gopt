#!/bin/bash

# git clone https://github.com/Vackwin/yang_gopt.git
cd yang_gopt/ || exit
# ln -sf /opt/kaldi/ kaldi
# cp src/ezai-lexicon.txt cmudict/new.txt
# sed -i 's/\s/\t/' cmudict/new.txt
# sed -i '/\tSPN\|\tSIL/d' cmudict/new.txt
./src/shell_scripts/dl_libri_model.sh
cd kaldi/egs/gop_speechocean762/s5/ || exit
cp ~/notebooks/yang_gopt/src/shell_scripts/first_run.sh .
cp ~/notebooks/yang_gopt/src/shell_scripts/run.sh .
chmod +x first_run.sh run.sh
./first_run.sh
cd ~/notebooks/yang_gopt || exit
rm -rf kaldi/egs/gop_speechocean762/s5/exp/gop_test
cp src/extract_kaldi_gop/extract_gop_feats.py kaldi/egs/gop_speechocean762/s5/local/
pip install -r requirements.txt
apt update
apt install -y ffmpeg
cd src
python app.py