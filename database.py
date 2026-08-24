import pymysql


def get_connection():

    conn = pymysql.connect(

        host="mysql-11a8761d-dlu-47b.a.aivencloud.com",

        port=27162,

        user="avnadmin",

        password="AVNS_6ykmeDg6U2dI2gt_hX5",

        database="managecapital",

        ssl={
            "ca": "ca.pem"
        }

    )

    return conn
