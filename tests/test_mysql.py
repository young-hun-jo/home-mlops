import pytest 
import pymysql
import json


@pytest.fixture
def db_connection():
    db = pymysql.connect(host="localhost", port=3306, user="root", passwd="zedd-ai", db="mlflow_db", charset="utf8")
    return db


def test_select_from_table(db_connection):
    cursor = db_connection.cursor()
    sql = "select count(*) from training_history"
    cursor.execute(sql)
    rows = cursor.fetchall()
    assert rows[0][0] > 1, "there is no records in `mlflow_db.training_history` in MySQL DB"


def test_insert_json_to_db(db_connection):
    experiment_id = "test-experiment"
    run_id = "test-run"
    problem = "regression"
    model_type = "pytorch"
    params = {"epochs": 10, "batch_size": 256}
    metrics = {"rmse": 0.95, "mae": 0.8}
    signature = {"x1": "np.float32", "x2": "np.int32"}

    sql = """
        insert into training_history(experiment_id, run_id, problem, model_type, params, metrics, signature)
        values(%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql, (experiment_id, run_id, problem, model_type, json.dumps(params), json.dumps(metrics), json.dumps(signature)))
        db_connection.commit()
    finally:
        db_connection.close()
    