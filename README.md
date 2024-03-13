# GOPT: Transformer-Based Multi-Aspect Multi-Granularity Non-Native English Speaker Pronunciation Assessment
 - [Train and evaluate GOPT with speechocean 762 dataset](#Train-and-evaluate-GOPT-with-speechocean-762-dataset)



## (Local Scripts) Train and evaluate GOPT with speechocean 762 dataset

**Step 0. Init environment.**

If you run the project first time, you need to 
set path of kaldi and lexicon.

You need to get lexicon from twcc.

Just edit 'src/shell_scripts/init.sh'
```
init.sh

1.#!/bin/bash
2.
3.KALDI_PATH=/opt/kaldi/ >>>>> change this
4.LEXICON_TXT=src/ezai-lexicon.txt >>>>> change this
```
This script will do:
<ol>
<li>Clone from original repo
<li>Download librispeech models
<li>Install required packages
<li>Run app.py
</ol>


**Step 1. Run the app**

After first run, you can just run 'src/app.py'
```
shell

>cd src
>python app.py

```
**Step 2. Connect the api**

You can test it locally using 'src/client.py', or by fastapi docs if you want to do it from remote.

The post request body is a list of id.<br>e.g. [19204394, 19204396, 19204397]

Select ids from documents in (mongodb)capt_logs

Note. Selected documents can't be too old, or the audio will be deleted.
