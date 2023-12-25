import asyncio
from query_db.get_log_document import *
import test_eval
from my_logging import *
import play
import time
import requests
import os
from fastapi import FastAPI
import uvicorn
import logging

app = FastAPI()

GOPT_PATH = "/root/notebooks/yang_gopt/"
log_dir = GOPT_PATH + "logs/"
save_dir = GOPT_PATH + "wav_dir"
for dir in log_dir, save_dir:
    if not os.path.isdir(dir):
        os.mkdir(dir)

def set_query_by_id(ids):
    where = {
        "id": ids,
        "source": ["chapters_sentence","homework","video"],
    }
    query_dict = {
        "db_name": "capt_logs",
        "select": ["id","result","audio_url"],
        "collection_name": "capt_logs",
        "where": where,
        "skip": 0,
        "limit": 0,
        "sort": {
            "field": "id",
            "order": 1
        }
    }
    query = Query(**query_dict)
    return query

@app.post("/gopt")
def main(ids: List[int]):
    whole_start_time = time.time()
    query = set_query_by_id(ids)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    task = loop.create_task(query_capt_logs(query))
    loop.run_until_complete(task)
    documents= task.result()
    utt_dim = ["acc","com","flu","pro","tot"]
    returned_dict = {}
    for el in utt_dim:
        returned_dict[el] = []

    logger = logging.getLogger("")
    logger.info(documents)
    sum_score_by_dim = [0,0,0,0,0]
    returned_dict['avg'] = {}
    if len(documents) == 0:
        returned_dict['status'] = 'all ids error, maybe older than 3 months'
        return returned_dict
    for document in documents:
        play.reflush()
        result_dict = json.loads(document["result"])
        audio_url = document["audio_url"]
        if audio_url is None:
            logger.debug(document['id'], "audio_url is null")
            continue
        skip_utt = False
        ## get word prompt after nltk
        prompt_list = []
        for word_result in result_dict["hyp"]:
            word = word_result["input_word"].upper()
            prompt_list.append(word)
        text = " ".join(prompt_list)
        response = requests.get(audio_url)
        response.raise_for_status()
        save_path = f"{save_dir}/{document['id']}.wav"
        with open(save_path, "wb") as file:
            file.write(response.content)

        check, list_len_phn = play.prepare_gop(save_path, text)
        logger.debug(f"list_len_phn: {list_len_phn}")
        num_phns = 0
        for word_len in list_len_phn:
            num_phns += word_len
            if num_phns >= 60:
                skip_utt = True
                break
        if skip_utt:
            logger.debug(f"{document['id']}, Sentence too long. Not running gopt.")
            continue

        if check != "OK":
            print("\033[91m!!!!gop error!!!!!\033[0m")
            print(check)
            returned_dict['status'] = 'get gop error'
            return returned_dict
        utter, w_acc, w_st, w_total, phn = play.run_gopt(list_len_phn)
        if utter == 0:
            print("\033[91m!!!!infer error!!!!!\033[0m")
            # return "\033[91m!!!!error!!!!\033[0m"
            returned_dict['status'] = 'run gopt error'
            return returned_dict
        for i in range(5):
            dim_score = int(utter[i])
            sum_score_by_dim[i] += dim_score
            returned_dict[utt_dim[i]].append(dim_score)
    for i in range(5):
        returned_dict['avg'][utt_dim[i]] = sum_score_by_dim[i]/len(returned_dict[utt_dim[i]])
    returned_dict['status'] = 'ok'
    logger.debug(returned_dict)
    whole_end_time = time.time()
    logger.info(f"whole time: {whole_end_time - whole_start_time}")
    return returned_dict

@app.post("/batch_gopt")
def batch_main(ids: List[int]):
    whole_start_time = time.time()
    query = set_query_by_id(ids)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    task = loop.create_task(query_capt_logs(query))
    loop.run_until_complete(task)
    documents= task.result()
    utt_dim = ["acc","com","flu","pro","tot"]
    returned_dict = {}
    for el in utt_dim:
        returned_dict[el] = []

    logger = logging.getLogger("")
    logger.debug(documents)
    returned_dict['avg'] = {}
    play.batch_reflush()
    fetched_num = len(documents)
    # gop_start_time = time.time()
    for ind, document in enumerate(documents):
        result_dict = json.loads(document["result"])
        audio_url = document["audio_url"]
        if audio_url is None:
            logger.debug(document['id'], "audio_url is null")
            continue
        ## get word prompt after nltk
        prompt_list = []
        for word_result in result_dict["hyp"]:
            word = word_result["input_word"].upper()
            prompt_list.append(word)
        text = " ".join(prompt_list)
        response = requests.get(audio_url)
        response.raise_for_status()
        save_path = f"{save_dir}/{document['id']}.wav"
        with open(save_path, "wb") as file:
            file.write(response.content)

        check, list_len_phn = play.batch_prepare_gop(save_path, text, ind)
        logger.debug(f"{document['id']}: list_len_phn: {list_len_phn}")

        if check != "OK":
            print("\033[91m!!!!gop error!!!!!\033[0m")
            returned_dict['status'] = 'get gop error'
            return returned_dict
            # return "bugs"
    # gop_end_time = time.time()
    # logger.info(f"gop time:  {gop_end_time - gop_start_time}")
    # gopt_start_time = time.time()
    check, ret = play.batch_run_gopt()
    # gopt_end_time = time.time()
    # logger.info(f"gopt time: {gopt_end_time - gopt_start_time}")
    logger.debug('ret:')
    logger.debug(ret)
    if check == 0:
        print("\033[91m!!!!infer error!!!!!\033[0m")
        returned_dict['status'] = 'run gopt error'
        return returned_dict
    returned_dict['avg'] = dict(zip(utt_dim, ret[1].tolist()))
    for i in range(ret[0].shape[0]):
        for j, el in enumerate(utt_dim):
            returned_dict[el].append(ret[0][i][j].tolist())
    whole_end_time = time.time()
    logger.info(f"whole time: {whole_end_time - whole_start_time}")
    returned_dict['status'] = 'ok'
    
    return returned_dict

    
# uvicorn run on port 5021
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5021, reload=True, log_config=LOGGING_CONFIG)