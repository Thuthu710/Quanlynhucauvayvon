import streamlit as st
import pandas as pd
from database import get_connection

st.set_page_config(
    page_title="Trang quản trị",
    page_icon="🔐"
)

st.title("🔐 ĐĂNG NHẬP QUẢN TRỊ")

# --------------------------
# Tài khoản quản trị
# --------------------------
USERNAME = "admin"
PASSWORD = "123456"

# --------------------------
# Đăng nhập
# --------------------------
username = st.text_input("Tên đăng nhập")

password = st.text_input(
    "Mật khẩu",
    type="password"
)

login = st.button("Đăng nhập")

# --------------------------
# Kiểm tra đăng nhập
# --------------------------
if login:

    if username == USERNAME and password == PASSWORD:

        st.success("Đăng nhập thành công!")

        conn = get_connection()

        sql = """
        SELECT *
        FROM dangky_dulich
        ORDER BY id DESC
        """

        df = pd.read_sql(sql, conn)

        conn.close()

        st.subheader("Danh sách nhân viên đăng ký")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:
        st.error("Sai tên đăng nhập hoặc mật khẩu.")
