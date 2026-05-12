import pymysql

mydb = pymysql.connect(
host ='127.0.0.1',
user ='root',
password ='Shankar@123',
database ='call_book',
port=3306,
)

cursor=mydb.cursor()
# print("Connection Done Successfully!!!")