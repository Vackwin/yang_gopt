#!/bin/bash

awk -F'\t' '
NR==FNR{ a[$1]=1; next }
{ if(!($1 in a)){print "new.txt lacks "$0; error=123} }
' cmudict/new.txt /root/notebooks/yang_gopt/kaldi/egs/gop_speechocean762/s5/data/speechocean762/resource/lexicon.txt