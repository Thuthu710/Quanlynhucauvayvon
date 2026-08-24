import pandas as pd
from database import get_connection
import streamlit as st

st.set_page_config(page_title="Trang quản trị", page_icon="🔐", layout="wide")

st.title("🔐 TRANG QUẢN TRỊ & THẨM ĐỊNH HỒ SƠ")

# --------------------------
# Đăng nhập bảo mật đơn giản
# --------------------------
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
  username = st.text_input("Tên đăng nhập")
  password = st.text_input("Mật khẩu", type="password")
  if st.button("Đăng nhập"):
    if username == "admin" and password == "123456":
      st.session_state["authenticated"] = True
      st.rerun()
    else:
      st.error("Sai tên đăng nhập hoặc mật khẩu.")
else:
  st.success("Đăng nhập thành công với quyền Quản trị viên!")
  if st.button("Đăng xuất"):
    st.session_state["authenticated"] = False
    st.rerun()

  st.divider()
  st.subheader("📋 Quản lý toàn bộ danh sách hồ sơ nhu cầu vay vốn")

  try:
    conn = get_connection()
    sql = """
        SELECT *
        FROM quanly_nhucau_vayvon
        ORDER BY id DESC
        """
    df = pd.read_sql(sql, conn)
    conn.close()

    if not df.empty:
      # Thêm tính năng lọc theo trạng thái duyệt
      status_filter = st.selectbox(
          "Lọc theo trạng thái duyệt",
          ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Từ chối"],
      )
      if status_filter != "Tất cả":
        df_filtered = df[df["trang_thai_duyet"] == status_filter]
      else:
        df_filtered = df

      st.dataframe(df_filtered, use_container_width=True)
      st.info(f"Tổng số bản ghi hiển thị: {len(df_filtered)}")
    else:
      st.info("Chưa có hồ sơ nào trong cơ sở dữ liệu MySQL.")

  except Exception as e:
    st.error(
        "Không thể kết nối hoặc truy vấn dữ liệu từ MySQL. Hãy kiểm tra lại"
        " cấu hình cơ sở dữ liệu!"
    )
