import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self):
        self.host = 'localhost'
        self.database = 'quanlycuahang' # Tên database bạn vừa tạo
        self.user = 'root'                 # Tên đăng nhập 
        self.password = 'admin'                 # Mật khẩu 

    def connect(self):
        """Tạo kết nối đến MySQL"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            print(f"Lỗi kết nối MySQL: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Dùng để chạy lệnh SELECT lấy dữ liệu"""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"Lỗi truy vấn: {e}")
                return []
            finally:
                cursor.close()
                conn.close()

    def execute_query(self, query, params=None):
        """Dùng để chạy lệnh INSERT, UPDATE, DELETE"""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit() # Bắt buộc phải có commit() để lưu thay đổi
                return True
            except Error as e:
                print(f"Lỗi thực thi: {e}")
                return False
            finally:
                cursor.close()
                conn.close()