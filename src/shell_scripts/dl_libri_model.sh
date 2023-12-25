#!/usr/bin/bash

model_url='https://kaldi-asr.org/models/13/0013_librispeech_v1_chain.tar.gz'
lm_url='https://kaldi-asr.org/models/13/0013_librispeech_v1_lm.tar.gz'
extractor_url='https://kaldi-asr.org/models/13/0013_librispeech_v1_extractor.tar.gz'

if [ ! -f 0013_librispeech_v1_chain.tar.gz ]; then
    wget $model_url
    wget $lm_url
    wget $extractor_url
fi

tar -xvzf 0013_librispeech_v1_chain.tar.gz -C kaldi/egs/librispeech/s5/
tar -xvzf 0013_librispeech_v1_extractor.tar.gz -C kaldi/egs/librispeech/s5/
tar -xvzf 0013_librispeech_v1_lm.tar.gz -C kaldi/egs/librispeech/s5/