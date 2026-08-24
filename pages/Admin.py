import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Trang Quản Trị Admin - Thẩm Định Vốn",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo mock database quản trị admin
if "admin_applications" not in st.session_state:
    st.session_state.admin_applications = [
        {
            "id": "HD-2026-1001",
            "name": "Nguyễn Văn An",
            "phone": "0912345678",
            "purpose": "Kinh doanh mở rộng xưởng",
            "requested_amount": 500000000,
            "monthly_income": 35000000,
            "credit_score": 740,
            "has_collateral": "Có",
            "collateral_type": "Bất động sản (Nhà/Đất)",
            "collateral_value": 800000000,
            "status": "Chờ thẩm định",
            "eligibility": "Đạt (Đủ điều kiện)",
            "suggested_limit": 450000000,
            "date": "2026-08-24",
            "notes": "Hồ sơ mẫu, cần xác minh tài sản bảo đảm."
        }
    ]

# --- Sidebar Navigation (Chỉ bao gồm phần 3 & 4) ---
st.sidebar.title("🔒 Khu Vực Admin")
st.sidebar.markdown("---")
admin_menu = st.sidebar.radio(
    "Chọn chức năng Admin:",
    [
        "🔒 Quản Lý Hồ Sơ & Thẩm Định", 
        "📊 Dashboard Tổng Quan Vốn"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Khu vực nội bộ dành riêng cho cấp quản lý và nhân viên thẩm định duyệt hồ sơ.")

# ==========================================
# 3. TRANG ADMIN: QUẢN LÝ HỒ SƠ & THẨM ĐỊNH
# ==========================================
if admin_menu == "🔒 Quản Lý Hồ Sơ & Thẩm Định":
    st.title("🔒 Quản Lý Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng (Admin)")
    st.markdown("Xem danh sách, kiểm tra tài sản thế chấp và cập nhật trạng thái phê duyệt hồ sơ.")
    
    if len(st.session_state.admin_applications) == 0:
        st.info("📭 Chưa có hồ sơ nào trong hệ thống.")
    else:
        df = pd.DataFrame(st.session_state.admin_applications)
        
        status_filter = st.selectbox("Lọc theo trạng thái hồ sơ:", ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
        filtered_df = df if status_filter == "Tất cả" else df[df['status'] == status_filter]
        
        st.write(f"Tìm thấy **{len(filtered_df)}** hồ sơ phù hợp.")
        st.markdown("---")
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📁 [{row['id']}] - KH: {row['name']} | Nhu cầu: {row['requested_amount']:,.0f} VNĐ | Trạng thái: **{row['status']}**"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("#### 👤 Thông tin khách hàng")
                    st.write(f"**Họ tên:** {row['name']}")
                    st.write(f"**Điện thoại:** {row['phone']}")
                    st.write(f"**Mục đích vay:** {row['purpose']}")
                    st.write(f"**Ngày tiếp nhận:** {row['date']}")
                    
                with c2:
                    st.markdown("#### 💳 Tài chính & Tài sản đảm bảo")
                    st.write(f"**Thu nhập tháng:** {row['monthly_income']:,.0f} VNĐ")
                    st.write(f"**Điểm CIC:** {row['credit_score']}")
                    st.write(f"**Tài sản thế chấp:** {row['has_collateral']} ({row['collateral_type']})")
                    if row['has_collateral'] == "Có":
                        st.write(f"**Định giá TS:** {row['collateral_value']:,.0f} VNĐ")
                    
                    if "Đạt" in row['eligibility']:
                        st.success(f"Hệ thống gợi ý: **{row['eligibility']}**")
                    elif "Cần" in row['eligibility']:
                        st.warning(f"Hệ thống gợi ý: **{row['eligibility']}**")
                    else:
                        st.error(f"Hệ thống gợi ý: **{row['eligibility']}**")
                        
                with c3:
                    st.markdown("#### 🎯 Phê duyệt & Cập nhật")
                    st.info(f"💡 Hạn mức đề xuất: **{row['suggested_limit']:,.0f} VNĐ**")
                    
                    real_idx = next(i for i, item in enumerate(st.session_state.admin_applications) if item["id"] == row['id'])
                    
                    new_status = st.selectbox(
                        "Cập nhật trạng thái",
                        ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"],
                        index=["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"].index(row['status']),
                        key=f"adm_status_{row['id']}"
                    )
                    
                    notes = st.text_input("Ghi chú thẩm định nội bộ", value=row['notes'], key=f"adm_notes_{row['id']}")
                    
                    if st.button(f"Lưu thay đổi {row['id']}", key=f"adm_btn_{row['id']}"):
                        st.session_state.admin_applications[real_idx]['status'] = new_status
                        st.session_state.admin_applications[real_idx]['notes'] = notes
                        st.success("Đã cập nhật hồ sơ thành công!")
                        st.rerun()

# ==========================================
# 4. TRANG ADMIN: DASHBOARD TỔNG QUAN
# ==========================================
elif admin_menu == "📊 Dashboard Tổng Quan Vốn":
    st.title("📊 Dashboard Tổng Quan Hoạt Động Vốn (Admin)")
    st.markdown("Thống kê số liệu thời gian thực toàn bộ danh mục hồ sơ vay vốn trong hệ thống.")
    
    if len(st.session_state.admin_applications) == 0:
        st.info("📭 Chưa có dữ liệu thống kê.")
    else:
        df = pd.DataFrame(st.session_state.admin_applications)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Tổng số hồ sơ", value=len(df))
        with col2:
            total_req = df['requested_amount'].sum()
            st.metric(label="Tổng nhu cầu vốn", value=f"{total_req:,.0f} VNĐ")
        with col3:
            approved_count = len(df[df['status'].isin(['Đã phê duyệt', 'Đã giải ngân'])])
            st.metric(label="Đã duyệt / Giải ngân", value=approved_count)
        with col4:
            avg_score = int(df['credit_score'].mean()) if len(df) > 0 else 0
            st.metric(label="Điểm tín dụng CIC TB", value=avg_score)
            
        st.markdown("---")
        st.subheader("📋 Bảng Dữ Liệu Tổng Hợp")
        st.dataframe(
            df[['id', 'name', 'phone', 'purpose', 'requested_amount', 'has_collateral', 'status', 'eligibility']], 
            use_container_width=True
        )
                        st.session_state.admin_applications[real_idx]['notes'] = notes
                        st.success("Cập nhật thành công!")
                        st.rerun()
