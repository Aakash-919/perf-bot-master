import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
from tensorflow.python.keras.backend import set_session
import matplotlib.pyplot as plt

sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)

cgpa_model = keras.models.load_model("data/cgpa_e1900.h5")
print("loaded cgpa model")
class_model = keras.models.load_model("data/class_e1600.h5")
print("loaded class model")


def gen_report(attrs, uid, name, attrs_incl):  # attrs should be (1,14)
    global graph, sess
    with graph.as_default():
        set_session(sess)
        attrs = np.array(attrs)
        attrs = np.reshape(attrs, (1, 14))
        predicted_cgpa = float(cgpa_model.predict(attrs)[0, 0])
        predicted_class = list(class_model.predict(attrs, batch_size=1)[0])
        predicted_class_prob = max(predicted_class)
        predicted_class = predicted_class.index(max(predicted_class))
        attr_req_amts = {}
        if predicted_class != 2:
            for attr in attrs_incl:
                attr_req_amts[attr["attr_index"]] = -1
                temp_attrs = attrs.copy()
                for i in np.arange(attrs[0, attr["attr_index"]], attr["ub"] + 0.1, attr["inc"]):
                    i = float(i)
                    temp_attrs[0, attr["attr_index"]] = i
                    new_pred_class = class_model.predict(temp_attrs)[0, 0]
                    if new_pred_class > predicted_cgpa:
                        attr_req_amts[attr["attr_index"]] = i
                        break

    return predicted_cgpa, predicted_class, attr_req_amts


def predict(prediction):
    for i, p in enumerate(prediction):
        p = list(p)
        print("i=", i, " class=", p.index(max(p)))


if __name__ == '__main__':
    train_df = pd.read_csv("../data/data.csv")
    X = train_df.loc[:, :"Debate participation(1/0)"].to_numpy()
    print(X.shape)
    input("Contine....\n")
    y_cgpa = train_df.loc[:, "Future CGPA"].to_numpy()
    t_y_class = train_df.iloc[:, -1].to_numpy()
    y_class = np.zeros((t_y_class.shape[0], 3))
    for i, y in enumerate(t_y_class):
        y = int(y)
        y_class[i, y] = 1
    # print(y_class[:2,:])

    ip = keras.layers.Input(shape=X.shape[1], batch_size=None)
    dense_cgpa = keras.layers.Dense(units=10, name="cgpa_1", )(ip)
    cgpa_op = keras.layers.Dense(units=1, name="cgpa")(dense_cgpa)
    cgpa_model = keras.models.Model(inputs=ip, outputs=cgpa_op, name="CGPA")
    print(cgpa_model.summary())
    input("Contine....\n")

    cgpa_model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(0.005))
    cgpa_model.fit(X, y_cgpa, epochs=1900)
    input("Contine....\n")

    dense_class = keras.layers.Dense(units=10, name="class_1")(ip)
    class_op = keras.layers.Dense(units=3, activation="softmax", name="class")(dense_class)
    class_model = keras.models.Model(inputs=ip, outputs=class_op, name="CLASS")
    print(class_model.summary())
    input("Contine....\n")

    class_model.compile(loss="categorical_crossentropy", optimizer=keras.optimizers.Adam(0.001), metrics=["acc"])
    class_model.fit(X, y_class, epochs=1600)
    input("Contine....\n")

    filepath = input("Enter filename to save cgpa model, -1 to cancel\n")
    if not filepath == "-1":
        cgpa_model.save("../data/" + filepath)

    filepath = input("Enter filename to save class model, -1 to cancel\n")
    if not filepath == "-1":
        cgpa_model.save("../data/" + filepath)

    # test_df = pd.read_csv("../data/data.csv")
    # test_df = test_df.iloc[50:, :]
    # X = test_df.loc[:, :"Debate participation(1/0)"].to_numpy()
    # print(X.shape)
    # input()
    # y_cgpa = test_df.loc[:, "Future CGPA"].to_numpy()
    # t_y_class = test_df.iloc[:, -1].to_numpy()
    # print(cgpa_model.predict(X))
    # predict(class_model.predict(X))
    #
    # while True:
    #     t = np.zeros((1, 14))
    #     for i in range(14):
    #         t[0, i] = float(input())
    #     print(t)
    #     print(cgpa_model.predict(t))
    #     print(class_model.predict(t))
