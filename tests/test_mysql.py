import pytest 
import pymysql


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