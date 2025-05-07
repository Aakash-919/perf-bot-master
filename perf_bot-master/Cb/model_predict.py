import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
import io
from tensorflow.python.keras.backend import set_session

model_file = "data/mp_cb-e10-nd400k.h5"
word_vec_file = "data/wiki-news-300d-1M.vec"
cb_data_file = "data/ncb.csv"


def vocab(embf=None, n=100000, req=()):
    if not embf:
        embf = word_vec_file

    def load_vectors(fname, n):
        print("Loading word vectors")
        fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
        # n, d = map(int, fin.readline().split())
        data = {}
        for i, line in enumerate(fin):
            if i == 0:
                continue
            if len(data) % 10 ** 5 == 0:
                print("Loaded ", len(data), " words...")
            if i % 10 ** 5 == 0:
                print("iterating through word vecs, i=", i)
            tokens = line.rstrip().split(' ')
            if i < n:
                data[tokens[0]] = list(map(float, tokens[1:]))
            elif not req:
                break
            if tokens[0] in req:
                data[tokens[0]] = list(map(float, tokens[1:]))
        return data

    word_to_vec = {}
    unk = [0] * 300
    word_to_vec = load_vectors(embf, n)
    print("words loaded ", len(word_to_vec))
    return word_to_vec


def predict(sent, model):
    global graph, sess
    tokens = sent.split()
    ip = np.zeros((1, len(tokens), 300))
    for i, token in enumerate(tokens):
        if token in word_to_vec:
            ip[0, i] = word_to_vec[token]
        else:
            ip[0, i] = [0] * 300
    with graph.as_default():
        set_session(sess)
        pred = model.predict(ip)
    intents_pred = pred[0]
    intents_pred = list(np.squeeze(intents_pred))
    # print("Intent:", intents[intents_pred.index(max(intents_pred))])
    intent = intents[intents_pred.index(max(intents_pred))]
    slots_pred = pred[1]
    slots_pred = np.squeeze(slots_pred)
    ret_slots = []
    for pred in slots_pred:
        pred = list(pred)
        ret_slots.append(slots[pred.index(max(pred))])
    print("Sentence:", sent)
    print("Slots:", ret_slots)
    print("Intent:", intent)
    return intent, ret_slots, intents_pred


df = pd.read_csv(cb_data_file)
n = df.to_numpy()
intents = []
slots = []
for row in n:
    for i, val in enumerate(row):
        if i == 3:
            if val not in intents:
                intents.append(val)
        elif i == 2:
            for slot in val.split():
                if slot not in slots:
                    slots.append(slot)


sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)
model = keras.models.load_model(model_file)
# model._make_predict_function()
# graph = tf.get_default_graph()
word_to_vec = vocab(n=1 * 10 ** 5)

print("Intents length:", len(intents))
print(intents)
print("Slots length:", len(slots))
print(slots)
print(model.summary())
