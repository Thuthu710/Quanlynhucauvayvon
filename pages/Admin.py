import pandas as pd
from database import get_connection
import streamlit as st

st.set_page_config(page_title="Trang quản trị", page_icon="🔐")

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

password = st.text_input("Mật khẩu", type="password")

login = st.button("Đăng nhập")

# --------------------------
# Kiểm tra đăng nhập
# --------------------------
if login:
  if username == USERNAME and password == PASSWORD:
    st.success("Đăng nhập thành công!")

    conn = get_connection()

    # Đã sửa lại từ dangky_dulich thành bảng quản lý nhu cầu vay vốn
    sql = """
        SELECT *
        FROM quanly_nhucau_vayvon
        ORDER BY id DESC
        """

    try:
      df = pd.read_sql(sql, conn)
      conn.close()

      st.subheader("📋 Danh sách hồ sơ nhu cầu vay vốn đã tiếp nhận")

      if not df.empty:
        st.dataframe(df, use_container_width=True)
      else:
        st.info("Chưa có hồ sơ nào trong cơ sở dữ liệu.")

    except Exception as e:
      st.error(
          "Lỗi truy vấn cơ sở dữ liệu. Hãy đảm bảo bạn đã tạo bảng"
          " 'quanly_nhucau_vayvon' trên MySQL."
      )
      # In chi tiết lỗi nếu cần debug (có thể ẩn đi khi chạy production)
      # st.write(e)
      if conn:
        conn.close()

  else:
    st.error("Sai tên đăng nhập hoặc mật khẩu.")
