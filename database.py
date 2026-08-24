import pymysql

def get_connection():
    """Tạo kết nối tới cơ sở dữ liệu MySQL trên Aiven Cloud"""
    conn = pymysql.connect(
        host="mysql-11a8761d-dlu-47b.a.aivencloud.com",
        port=27162,
        user="avnadmin",
        password="AVNS_6ykmeDg6U2dI2gt_hX5",
        database="managecapital",
        ssl={
            "ca": "ca.pem"
        },
        cursorclass=pymysql.cursors.DictCursor  # Giúp trả kết quả dạng dictionary dễ thao tác với pandas
    )
    return conn

def init_db():
    """Khởi tạo bảng lưu trữ hồ sơ đăng ký vay vốn trên MySQL nếu chưa tồn tại"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dangky_vayvon (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255),
                phone VARCHAR(50),
                purpose TEXT,
                requested_amount DECIMAL(18,2),
                monthly_income DECIMAL(18,2),
                credit_score INT,
                has_collateral TINYINT(1),
                collateral_type VARCHAR(255),
                collateral_value DECIMAL(18,2),
                notes TEXT,
                date VARCHAR(50),
                status VARCHAR(50)
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Lỗi khởi tạo bảng MySQL: {e}")

# Tự động chạy tạo bảng khi gọi module database
init_db()
