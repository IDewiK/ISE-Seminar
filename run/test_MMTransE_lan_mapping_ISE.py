import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/MMTransE'))

from MMTransE import MMTransE
import time
import multiprocessing
from multiprocessing import Process, Value, Lock, Manager, Array
import numpy as np
from numpy import linalg as LA

fmap = os.path.join(os.path.dirname(__file__), '../data/y2db.csv')
fmap2 = os.path.join(os.path.dirname(__file__), '../data/db2y.csv')
fmodel = os.path.join(os.path.dirname(__file__), '../models/model_MMtransE_person_ISE.bin')
ofile1 = os.path.join(os.path.dirname(__file__), '../results/P_test_y2db_score_MM_ISE.txt')
ofile4 = os.path.join(os.path.dirname(__file__), '../results/P_test_db2y_score_MM_ISE.txt')



ef_map = {}
fe_map = {}

vocab_e = []
vocab_f = []

topK = 10

model = MMTransE()
model.load(fmodel)

def seem_hit(x, y):
    for i in y:
        if x.find(i) > -1 or i.find(x) > -1:
            return True
    return False

for line in open(fmap):
    line = line.rstrip('\n').split('@@@')
    if len(line) != 2:
        continue
    vocab_e.append(line[0])
    if ef_map.get(line[0]) == None:
        ef_map[line[0]] = [line[1]]
    else:
        ef_map[line[0]].append(line[1])
for line in open(fmap2):
    line = line.rstrip('\n').split('@@@')
    if len(line) != 2:
        continue
    vocab_f.append(line[0])
    if fe_map.get(line[1]) == None:
        fe_map[line[1]] = [line[0]]
    else:
        fe_map[line[1]].append(line[0])

print "Loaded dbpedia_yago yago_dbpedia mappings."

#en:...
manager = Manager()
lock1 = Lock()

past_num = Value('i', 0, lock=True)
score = manager.list()#store hit @ k

rank = Value('d', 0.0, lock=True)
rank_num = Value('i', 0, lock=True)

cpu_count = multiprocessing.cpu_count()
t0 = time.time()
def test(model, vocab, index, src_lan, tgt_lan, map, score, past_num):
    while index.value < len(vocab):
        id = index.value
        index.value += 1
        word = vocab[id]
        if id % 100 == 0:
            print id ,'/', len(vocab), ' time used ',time.time() - t0
            print score
            print rank.value
        tgt = map.get(word)
        cand = model.kNN_entity_name(word, src_lan, tgt_lan, topK)
        cand = [x[0] for x in cand]
        tmp_score = np.zeros(topK)
        hit = False
        last_i = 0
        cur_rank = None
        if tgt == None:
            continue
        for i in range(len(cand)):
            last_i = i
            tmp_cand = cand[i]
            if hit == False and (seem_hit(tmp_cand, tgt) == True):
                hit = True
            if hit == True:
                tmp_score[i] = 1.0
                if cur_rank == None:
                    cur_rank = i
        while last_i < topK:
            if hit:
                tmp_score[last_i] = 1.0
            last_i += 1
        if len(score) == 0:
            score.append(tmp_score)
        else:
            with lock1:
                score[0] = (score[0] * past_num.value + tmp_score) / (past_num.value + 1.0)
        past_num.value += 1
        if cur_rank != None:
            rank.value = (rank.value * rank_num.value + cur_rank) / (rank_num.value + 1)
            rank_num.value += 1
            continue
        tmp_dist = 2
        vec_t = None
        vec_s = model.entity_transfer_vec(word, src_lan, tgt_lan)
        for tmp_vec in tgt:
            tmp_vec_t = model.entity_vec(tmp_vec, tgt_lan)
            if tmp_vec_t is None:
                continue
            cur_dist = LA.norm(tmp_vec_t - vec_s)
            if cur_dist < tmp_dist:
                tmp_dist = cur_dist
                vec_t = tmp_vec_t
        if vec_t is None:
            continue
        cur_rank = model.entity_rank(vec_s, vec_t, tgt_lan)
        rank.value = (rank.value * rank_num.value + cur_rank) / (rank_num.value + 1)
        rank_num.value += 1

index = Value('i',0,lock=True)
processes = [Process(target=test, args=(model, vocab_e, index, 'en', 'fr', ef_map, score, past_num)) for x in range(cpu_count - 1)]
for p in processes:
    p.start()
for p in processes:
    p.join()

with open(ofile1, 'w') as fp:
    fp.write(str(rank.value) + '\n')
    for s in score[0]:
        fp.write(str(s) + '\t')

print 'Finished testing dbpedia to yago'

#fr:...
manager = Manager()
past_num = Value('i', 0, lock=True)
score = manager.list()#store hit @ k
rank = Value('d', 0.0, lock=True)
rank_num = Value('i', 0, lock=True)

index = Value('i',0,lock=True)
processes = [Process(target=test, args=(model, vocab_f, index, 'fr', 'en', fe_map, score, past_num)) for x in range(cpu_count - 1)]
for p in processes:
    p.start()
for p in processes:
    p.join()

with open(ofile4, 'w') as fp:
    fp.write(str(rank.value) + '\n')
    for s in score[0]:
        fp.write(str(s) + '\t')

print 'Finished testing yago to dbpedia'