import numpy as np
import pandas as pd
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Quản Lý Nhu Cầu Vay Vốn & Rủi Ro",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Hệ Thống Quản Lý & Phân Tích Nhu Cầu Vay Vốn Thông Minh")
st.markdown(
    "Ứng dụng tích hợp phân tích chỉ số rủi ro, mô phỏng kịch bản và đánh giá chuẩn mực ESG trong tín dụng."
)
st.divider()

# --- KHU VỰC NHẬP LIỆU DỮ LIỆU ĐẦU VÀO ---
st.sidebar.header("⚙️ Thiết lập dữ liệu đầu vào")
total_demand = st.sidebar.number_input(
    "Tổng nhu cầu vay vốn hiện tại (Tỷ VNĐ)",
    min_value=10.0,
    max_value=10000.0,
    value=500.0,
    step=50.0,
)
kpi_target = st.sidebar.number_input(
    "Chỉ tiêu giải ngân KPI (Tỷ VNĐ)",
    min_value=10.0,
    max_value=10000.0,
    value=450.0,
    step=50.0,
)
current_npl = (
    st.sidebar.slider("Tỷ lệ nợ xấu hiện tại (%)", 0.0, 10.0, 2.5, 0.1) / 100
)

# Phân khúc khách hàng mẫu
sector = st.sidebar.selectbox(
    "Lĩnh vực cho vay chủ lực",
    [
        "Bất động sản & Xây dựng",
        "SME / Sản xuất tiêu dùng",
        "Nông nghiệp công nghệ cao / Xanh",
        "Bán lẻ cá nhân",
    ],
)

# Chia layout thành 3 cột chính tương ứng với 3 tính năng hay ho
col1, col2, col3 = st.columns(3)

# ==========================================
# TÍNH NĂNG 1: ĐÈN GIAO THÔNG CẢNH BÁO KPI & RỦI RO
# ==========================================
with col1:
    st.subheader("🚦 1. Trạng thái KPI & Rủi ro")

    # Tính toán chỉ số căng thẳng (Stress Index)
    achievement_rate = (
        (total_demand / kpi_target) * 100 if kpi_target > 0 else 0
    )

    # Đánh giá trạng thái Đèn giao thông
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
    st.metric(
        label="Tỷ lệ đạt KPI giải ngân", value=f"{achievement_rate:.1f}%"
    )
    st.metric(label="Tỷ lệ nợ xấu (NPL)", value=f"{current_npl*100:.1f}%")
    st.info(f"💡 **Khuyến nghị:** {advice}")


# ==========================================
# TÍNH NĂNG 2: MÔ PHỎNG KỊCH BẢN CĂNG THẲNG (STRESS TEST)
# ==========================================
with col2:
    st.subheader("🌪️ 2. Mô phỏng Stress Test")
    st.markdown("Giả định các biến động vĩ mô ảnh hưởng đến danh mục:")

    rate_shock = st.slider("Biên độ tăng lãi suất (%)", 0.0, 5.0, 1.0, 0.5)
    macro_downturn = st.slider(
        "Mức suy giảm kinh tế của khách hàng (%)", 0.0, 50.0, 10.0, 5.0
    )

    # Tính toán mô phỏng đơn giản
    simulated_npl = min(
        100.0,
        (current_npl * 100) + (rate_shock * 0.8) + (macro_downturn * 0.15),
    )
    simulated_demand = total_demand * (1 - macro_downturn / 100)

    st.markdown("---")
    st.write("📊 **Kết quả sau kịch bản giả định:**")
    st.metric(
        label="Nợ xấu dự phóng (Simulated NPL)",
        value=f"{simulated_npl:.2f}%",
        delta=f"{simulated_npl - (current_npl*100):+.2f}%",
    )
    st.metric(
        label="Nhu cầu vay khả dụng", value=f"{simulated_demand:.1f} Tỷ VNĐ"
    )


# ==========================================
# TÍNH NĂNG 3: BỘ LỌC ĐẠO ĐỨC & TRÁCH NHIỆM XÃ HỘI (ESG)
# ==========================================
with col3:
    st.subheader("🌱 3. Thẩm định ESG & Đạo đức")
    st.markdown("Đánh giá tác động xã hội và môi trường của danh mục:")

    # Checklist đánh giá nhanh ESG
    esg_env = st.checkbox(
        "🌿 Doanh nghiệp áp dụng công nghệ thân thiện môi trường", value=True
    )
    esg_social = st.checkbox(
        "👥 Đảm bảo phúc lợi lao động & tiêu chuẩn an toàn", value=True
    )
    esg_animal_welfare = st.checkbox(
        "🐾 Tuân thủ nhân đạo / Không thử nghiệm / Không hại động vật",
        value=True,
    )

    # Tính điểm ESG Score giả lập
    score = sum([esg_env, esg_social, esg_animal_welfare])

    st.markdown("---")
    if score == 3:
        st.success(
            "🌟 **Xếp hạng ESG: HẠNG A (Bền vững tuyệt đối)**\nĐược ưu tiên hạn mức và cộng điểm ưu đãi lãi suất."
        )
    elif score == 2:
        st.warning(
            "⚠️ **Xếp hạng ESG: HẠNG B (Cần cải thiện)**\nCần bổ sung cam kết cải thiện tiêu chuẩn xã hội/môi trường."
        )
    else:
        st.error(
            "🛑 **Xếp hạng ESG: HẠNG C (Rủi ro cao)**\nCân nhắc từ chối cấp tín dụng theo chuẩn mực phát triển bền vững."
        )

st.divider()
st.caption(
    "💡 *Gợi ý: Bạn có thể tùy chỉnh thêm các trọng số tính toán hoặc kết nối trực tiếp với cơ sở dữ liệu thật của ứng dụng Streamlit hiện tại.*"
)
