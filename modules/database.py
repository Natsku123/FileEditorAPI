import pymysql
import json


def get_conf():
    with open('config.json', 'r') as conf_file:
        return json.load(conf_file)


def get_secret():
    """
    Get secret from config.
    :return:
    """
    with open("config.json", "r") as conf:
        data = json.load(conf)

    return data['secret']


# Work around for working with Flask-JWT.
class User:
    def __init__(self, user_id, username, access_token):
        self.id = user_id
        self.username = username
        self.access_token = access_token


config = get_conf()


def insert(sql, values=None):
    """
    Insert data into database.
    :param sql:
    :param values:
    :return:
    """
    db = pymysql.connect(
        config['host'],
        config['username'],
        config['password'],
        config['name'],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with db.cursor() as cursor:
            if values is not None:
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)

        db.commit()
        db.close()
        return True
    except pymysql.MySQLError as e:
        db.rollback()
        db.close()
        print(e, e.args)
        return False


def get(sql, values=None, everything=True):
    """
    Get data from database.
    :param sql:
    :param values:
    :param everything:
    :return:
    """
    db = pymysql.connect(
        config['host'],
        config['username'],
        config['password'],
        config['name'],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with db.cursor() as cursor:
            if values is not None:
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)

            if everything:
                data = cursor.fetchall()
            else:
                data = cursor.fetchone()

        db.close()
        return data
    except pymysql.MySQLError:
        db.close()
        return None


def auth(username: str, password: str):
    sql = "SELECT * FROM `users` WHERE `username`=%s AND `password`=ENCRYPT(%s, `password`);"
    return get(sql, (username, password), False)


def get_user_by_id(user_id):
    sql = "SELECT * FROM `users` WHERE `id`=%s;"
    return get(sql, (user_id,), False)


def all_users():
    sql = "SELECT users.id, users.id FROM `users`;"
    return get(sql)


def create_user(username: str, password: str):
    sql = "INSERT INTO `users` (`username`, `password`) VALUES (%s, ENCRYPT(%s, CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))));"
    if insert(sql, (username, password)):
        return {'Status': 'success'}
    else:
        return {'Status': 'Error, unable to create user.'}


def update_user(id, username: str, password: str):
    sql = "UPDATE `users` SET `password`=ENCRYPT('%s', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), `username`=%s WHERE `id`='%s';"
    if insert(sql, (password, username, id)):
        return {'Status': 'success'}
    else:
        return {'Status': 'Error, unable to update user.'}
