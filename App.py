import numpy as np
import pandas as pd
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Quản Lý Nhu Cầu Vay Vốn & Rủi Ro", page_icon="🏦", layout="wide"
)

st.title("🏦 Hệ Thống Quản Lý & Phân Tích Nhu Cầu Vay Vốn Thông Minh")
st.markdown(
    "Ứng dụng phân tích chỉ số rủi ro, mô phỏng kịch bản vĩ mô và đánh giá chuẩn mực ESG trong tín dụng."
)
st.divider()

# --- KHỞI TẠO SESSION STATE (LƯU TẠM DỮ LIỆU ĐỂ TEST GIAO DIỆN) ---
if "df_customers" not in st.session_state:
  st.session_state["df_customers"] = pd.DataFrame(
      columns=[
          "Tên khách hàng",
          "Loại KH",
          "Số điện thoại",
          "Phòng ban phụ trách",
          "Nhu cầu vay (Tỷ)",
          "Lĩnh vực",
          "Điểm ESG",
          "Trạng thái duyệt",
      ]
  )

# --- SIDEBAR: NHẬP LIỆU HỒ SƠ MỚI ---
st.sidebar.header("📝 Gửi yêu cầu vay vốn mới")

with st.sidebar.form("customer_form"):
  ten_kh = st.text_input("Tên khách hàng / Doanh nghiệp")
  loai_kh = st.selectbox(
      "Loại khách hàng", ["Doanh nghiệp (SME/Corporate)", "Cá nhân (Retail)"]
  )
  sdt = st.text_input("Số điện thoại liên hệ")
  phong_ban = st.selectbox(
      "Phòng ban / RM phụ trách",
      ["Phòng Khách hàng Doanh nghiệp", "Phòng Bán lẻ", "Phòng Quản lý Rủi ro"],
  )
  nhu_cau = st.number_input(
      "Nhu cầu vay vốn (Tỷ VNĐ)", min_value=0.5, max_value=500.0, value=10.0
  )
  linh_vuc = st.selectbox(
      "Lĩnh vực ngành nghề",
      [
          "Bất động sản & Xây dựng",
          "SME / Sản xuất tiêu dùng",
          "Nông nghiệp công nghệ cao / Xanh",
          "Bán lẻ cá nhân",
      ],
  )

  st.markdown("**Đánh giá tiêu chuẩn ESG & Đạo đức:**")
  esg_env = st.checkbox("🌿 Công nghệ thân thiện môi trường", value=True)
  esg_social = st.checkbox("👥 Đảm bảo phúc lợi lao động & an toàn", value=True)
  esg_animal_welfare = st.checkbox(
      "🐾 Tuân thủ nhân đạo / Không hại động vật", value=True
  )

  submit_button = st.form_submit_button(
      label="➕ Gửi hồ sơ lên hệ thống", type="primary"
  )

  if submit_button and ten_kh:
    score_esg = sum([esg_env, esg_social, esg_animal_welfare])
    trang_thai = (
        "Đã phê duyệt"
        if score_esg >= 2
        else ("Chờ thẩm định" if score_esg == 1 else "Từ chối")
    )

    new_row = {
        "Tên khách hàng": ten_kh,
        "Loại KH": loai_kh,
        "Số điện thoại": sdt,
        "Phòng ban phụ trách": phong_ban,
        "Nhu cầu vay (Tỷ)": nhu_cau,
        "Lĩnh vực": linh_vuc,
        "Điểm ESG": f"{score_esg}/3",
        "Trạng thái duyệt": trang_thai,
    }

    st.session_state["df_customers"] = pd.concat(
        [st.session_state["df_customers"], pd.DataFrame([new_row])],
        ignore_index=True,
    )
    st.sidebar.success(f"Đã gửi hồ sơ của **{ten_kh}** thành công!")

# Lấy tổng nhu cầu
if not st.session_state["df_customers"].empty:
  total_demand = st.session_state["df_customers"]["Nhu cầu vay (Tỷ)"].sum()
else:
  total_demand = 500.0

st.sidebar.divider()
st.sidebar.header("⚙️ Thiết lập vĩ mô & Chỉ tiêu")
kpi_target = st.sidebar.number_input(
    "Chỉ tiêu giải ngân KPI chung (Tỷ VNĐ)",
    min_value=10.0,
    max_value=10000.0,
    value=max(450.0, total_demand * 0.9),
    step=50.0,
)
current_npl = (
    st.sidebar.slider("Tỷ lệ nợ xấu chung hiện tại (%)", 0.0, 10.0, 2.5, 0.1)
    / 100
)

# --- SÁNG KIẾN MỚI: DASHBOARD TỔNG QUAN THAY CHO BẢNG THÔ ---
st.subheader("📊 Dashboard Tổng Quan Nhu Cầu & Tác động")
d_col1, d_col2, d_col3, d_col4 = st.columns(4)
d_col1.metric("Tổng nhu cầu đăng ký", f"{total_demand:,.1f} Tỷ")
d_col2.metric("Chỉ tiêu KPI giải ngân", f"{kpi_target:,.1f} Tỷ")
d_col3.metric(
    "Tổng số hồ sơ tiếp nhận", len(st.session_state["df_customers"])
)
d_col4.metric(
    "Tỷ lệ hoàn thành KPI",
    f"{(total_demand/kpi_target)*100:.1f}%" if kpi_target > 0 else "0%",
)

st.divider()

# --- CHIA LAYOUT 3 CỘT CHO 3 TÍNH NĂNG PHÂN TÍCH ---
col1, col2, col3 = st.columns(3)

with col1:
  st.subheader("🚦 1. Trạng thái KPI & Rủi ro")
  achievement_rate = (
      (total_demand / kpi_target) * 100 if kpi_target > 0 else 0
  )

  if current_npl > 0.04 or achievement_rate > 150:
    status_color = "🔴"
    status_text = "RỦI RO CAO / QUÁ TẢI"
    advice = "Cần thắt chặt thẩm định, dừng nới lỏng chỉ tiêu."
  elif current_npl > 0.02 or achievement_rate < 80:
    status_color = "🟡"
    status_text = "CẦN THEO DÕI SÁT"
    advice = "Dư địa còn nhưng cần cân đối lại danh mục cho vay."
  else:
    status_color = "🟢"
    status_text = "AN TOÀN / TỐI ƯU"
    advice = "Hoạt động giải ngân và kiểm soát chất lượng đang ổn định."

  st.markdown(f"### {status_color} **{status_text}**")
  st.metric(label="Tỷ lệ đạt KPI giải ngân", value=f"{achievement_rate:.1f}%")
  st.metric(label="Tỷ lệ nợ xấu (NPL)", value=f"{current_npl*100:.1f}%")
  st.info(f"💡 **Khuyến nghị:** {advice}")

with col2:
  st.subheader("🌪️ 2. Mô phỏng Stress Test")
  st.markdown("Giả định các biến động vĩ mô ảnh hưởng:")

  rate_shock = st.slider("Biên độ tăng lãi suất (%)", 0.0, 5.0, 1.0, 0.5)
  macro_downturn = st.slider(
      "Mức suy giảm kinh tế khách hàng (%)", 0.0, 50.0, 10.0, 5.0
  )

  simulated_npl = min(
      100.0,
      (current_npl * 100) + (rate_shock * 0.8) + (macro_downturn * 0.15),
  )
  simulated_demand = total_demand * (1 - macro_downturn / 100)

  st.markdown("---")
  st.write("📊 **Kết quả sau kịch bản giả định:**")
  st.metric(
      label="Nợ xấu dự phóng (Simulated NPL)",
      value=f"{simulated_demand and f'{simulated_npl:.2f}%' or '0.00%'}",
      delta=f"{simulated_npl - (current_npl*100):+.2f}%",
  )
  st.metric(
      label="Nhu cầu vay khả dụng", value=f"{simulated_demand:.1f} Tỷ VNĐ"
  )

with col3:
  st.subheader("🌱 3. Thẩm định ESG Danh Mục")
  st.markdown("Đánh giá tổng quan tiêu chuẩn ESG chung:")

  esg_env_all = st.checkbox(
      "🌿 Ưu tiên danh mục xanh / Giảm phát thải", value=True
  )
  esg_soc_all = st.checkbox("👥 Đảm bảo an sinh xã hội toàn hệ thống", value=True)
  esg_anim_all = st.checkbox("🐾 Tuân thủ bảo vệ phúc lợi động vật", value=True)

  score_all = sum([esg_env_all, esg_soc_all, esg_anim_all])

  st.markdown("---")
  if score_all == 3:
    st.success(
        "🌟 **Xếp hạng ESG Toàn hệ thống: HẠNG A**\nDanh mục phát triển bền"
        " vững đạt chuẩn quốc tế."
    )
  elif score_all == 2:
    st.warning(
        "⚠️ **Xếp hạng ESG Toàn hệ thống: HẠNG B**\nCần tối ưu hóa các tiêu"
        " chí xã hội/môi trường."
    )
  else:
    st.error(
        "🛑 **Xếp hạng ESG Toàn hệ thống: HẠNG C**\nRủi ro pháp lý và danh"
        " tiếng cao."
    )

st.divider()
st.caption(
    "🔒 *Lưu ý: Danh sách chi tiết hồ sơ khách hàng đã được chuyển bảo mật sang"
    " trang Quản trị (Admin) để phục vụ công tác thẩm định.*"
)
