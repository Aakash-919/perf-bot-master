import numpy as np
import re
from word2number import w2n
from ..Db import query
from flask import jsonify, Response
# if __name__ == '__main__':
#     from model_predict import (word_to_vec, predict, intents, slots, model)
# else:
from .model_predict import (word_to_vec, predict, intents, slots, model)
from .core import gen_report

responses = {
    "update_attribute": "Updating attribute %s to %s",
    "inc_attr": "Incrementing attribute %s by %s",
    "dec_attr": "Decrementing attribute %s by %s",
    "internship": "Great! incrementing your number of internships comleted by 1",
    "participated_hack": "Great! incrementing your number of hackathons participated in by 1",
    "won_hack": "Congratulations! incrementing your number of hackathons won by 1",
    "learnt_tech": "Great! incrementing your number of technologies learnt by 1",
    "send_report": ""
}
attr_index_to_name = {
    4: "num_internships",
    5: "num_hacks_part",
    7: "comp_coding",
    8: "num_hrs",
    9: "num_tech",
    12: "sports_part",
    13: "debate_part"
}


def clean(ip):
    ip = ip.lower()
    ip = re.sub("\+", " ", ip)
    ip = re.sub("\.", " .", ip)
    ip = re.sub(",", " ,", ip)
    ip = re.sub("\?", " ?", ip)
    ip = re.sub("!", " !", ip)
    ip = re.sub("'s", " is", ip)
    words = ip.split()
    words_to_num = {}
    for word in words:
        try:
            num = w2n.word_to_num(word)
            words_to_num[word] = num
        except ValueError as ve:
            pass
    for word in words_to_num:
        ip = ip.replace(word, str(words_to_num[word]))
    return ip


def proc_slots(slots, ip):
    ret = {}
    ip = ip.split()
    for i, slot in enumerate(slots):
        if not slot == "o":
            ret[slot] = ip[i]
    return ret


def check_num(s):
    try:
        float(s)
        return True
    except Exception as e:
        return False


def response(ip, id, model):
    ip = clean(ip)
    ip_intent, ip_slots, ip_intents_probs = predict(ip, model)
    # print(ip_intent)
    # print(ip_slots)
    # print(ip_intents_probs)
    ip_slots = proc_slots(ip_slots, ip)
    if ip_intent == "update_attribute":
        if "attr_name" in ip_slots and "attr_newval" in ip_slots:
            if ip_slots["attr_name"] in ["cgpa", "iq"]:
                if check_num(ip_slots["attr_newval"]):
                    if query.insert_update("UPDATE attrs set %s = %s WHERE student_id = %s;", (
                            ip_slots["attr_name"], ip_slots["attr_newval"], id)):
                        return responses["update_attribute"] % (ip_slots["attr_name"], ip_slots["attr_newval"])
                    else:
                        return "Unable to access the database"

    elif ip_intent == "inc_attr":
        if "attr_name" in ip_slots and "attr_incval" in ip_slots:
            if ip_slots["attr_name"] in ["cgpa", "iq"]:
                if check_num(ip_slots["attr_incval"]):
                    if query.insert_update(
                            "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + %s WHERE student_id = %s;",
                            (ip_slots["attr_name"], ip_slots["attr_name"], id, ip_slots["attr_incval"], id)):
                        return responses["inc_attribute"] % (ip_slots["attr_name"], ip_slots["attr_newval"])
                    else:
                        return "Unable to access the database"

    elif ip_intent == "dec_attr":
        if "attr_name" in ip_slots and "attr_incval" in ip_slots:
            if ip_slots["attr_name"] in ["cgpa", "iq"]:
                if check_num(ip_slots["attr_incval"]):
                    if query.insert_update(
                            "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + %s WHERE student_id = %s;",
                            (ip_slots["attr_name"], ip_slots["attr_name"], id, ip_slots["attr_incval"], id)):
                        return responses["dec_attribute"] % (ip_slots["attr_name"], ip_slots["attr_newval"])
                    else:
                        return "Unable to access the database"

    elif ip_intent == "internship":
        if query.insert_update(
                "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + 1 WHERE student_id = %s;", (
                        "num_internships", "num_internships", id, id)):
            return responses["internship"]
        else:
            return "Unable to access the database"

    elif ip_intent == "participated_hack":
        if query.insert_update(
                "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + 1 WHERE student_id = %s;", (
                        "num_hacks_part", "num_hacks_part", id, id)):
            return responses["participated_hack"]
        else:
            return "Unable to access the database"

    elif ip_intent == "won_hack":
        if query.insert_update(
                "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + 1 WHERE student_id = %s;", (
                        "num_hacks_won", "num_hacks_won", id, id)):
            return responses["won_hack"]
        else:
            return "Unable to access the database"

    elif ip_intent == "learnt_tech":
        if query.insert_update(
                "UPDATE attrs set %s = (SELECT %s from attrs WHERE student_id = %s) + 1 WHERE student_id = %s;", (
                        "num_tech", "num_tech", id, id)):
            return responses["won_hack"]
        else:
            return "Unable to access the database"

    elif ip_intent == "send_report":
        vals = query.select("SELECT * FROM students, attrs WHERE id=student_id and id=%s", (id,), dict_ret=False)[0]
        print(vals)
        predicted_cgpa, predicted_class, req_attrs = gen_report(vals[6:], id, vals[2],
                                                                [{"attr_index": 4, "ub": 10, "inc": 1},
                                                                 {"attr_index": 5, "ub": 10, "inc": 1},
                                                                 {"attr_index": 9, "ub": 15, "inc": 1},
                                                                 {"attr_index": 7, "ub": 1, "inc": 1},
                                                                 {"attr_index": 8, "ub": 5, "inc": 0.5},
                                                                 {"attr_index": 12, "ub": 1, "inc": 1},
                                                                 {"attr_index": 13, "ub": 1, "inc": 1}])

        n_req = {}
        for k in req_attrs:
            n_req[attr_index_to_name[k]] = float(str(req_attrs[k]))
        return jsonify({"predicted_cgpa": predicted_cgpa,
                        "predicted_class": predicted_class,
                        "req_attrs": n_req})

    return "Err"

# while True:
#     response(input("Enter\n"))
