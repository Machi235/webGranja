import mysql.connector

class Registro_datos():

    def __init__(self):
        self.conexion = mysql.connector.connect( host='localhost',
                                                database='base_datos',
                                                user='root',
                                                password='12345678')
    def busca_users(self, users):
        cur = self.conexion.cursor()
        sql = "SELECT * FROM login_datos WHERE Users = %s".format(users)
        cur.execute(sql, (users,))
        usersx = cur.fetchall()
        cur.close()
        return usersx
    
    def busca_password(self, password):
        cur = self.conexion.cursor()
        sql = "SELECT * FROM login_datos WHERE Password = %s".format(password)
        cur.execute(sql, (password,))
        passwordx = cur.fetchall()
        cur.close()
        return passwordx
    
    def validar_usuario(self, user, password):
        cur = self.conexion.cursor()
        sql = "SELECT * FROM login_datos WHERE Users = %s AND Password = %s"
        cur.execute(sql, (user, password))
        result = cur.fetchone()   
        cur.close()
        return result