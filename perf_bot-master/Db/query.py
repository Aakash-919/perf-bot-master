import psycopg2 as psg
from psycopg2 import pool

conn_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, user="postgres",
                                      password="postgres@123",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="perf_bot")


def select(query, params, dict_ret=True):
    if type(params) is not tuple:
        params = (params,)
    cursor = None
    conn = None
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        descr = cursor.description
        fa = cursor.fetchall()
        if dict_ret:
            res = []
            for i, row in enumerate(fa):
                res.append({})
                for col, val in zip(descr, row):
                    res[i][col.name] = val
            if len(res) == 1:
                res = res[0]
            return res
        else:
            return fa
    except Exception as e:
        print("Db access exception")
        print(e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn_pool.putconn(conn)


def insert_update(query, params):
    cursor = None
    conn = None
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
    except Exception as e:
        print("Db access exception")
        print(e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn_pool.putconn(conn)
    return True

# print(select("Select * from students;", None))
