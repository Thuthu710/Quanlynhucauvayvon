import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Trang Quản Trị - Thẩm Định Vốn",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Khu Vực Quản Trị & Thẩm Định Hồ Sơ (Admin Portal)")
st.markdown("Dành riêng cho bộ phận quản lý và nhân viên thẩm định nguồn vốn.")

# Mock database riêng cho Admin (hoặc kết nối chung file DB/Cloud Database nếu triển khai thật)
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
            "notes": "Hồ sơ đầy đủ, cần xác minh tài sản bảo đảm."
        }
    ]

# Sidebar chọn chức năng trong Admin
admin_menu = st.sidebar.radio("Chức năng Admin:", ["📊 Dashboard Tổng Quan", "👥 Quản Lý & Thẩm Định Hồ Sơ"])

if admin_menu == "📊 Dashboard Tổng Quan":
    st.subheader("📊 Thống Kê Tổng Quan Hoạt Động Vốn")
    
    df = pd.DataFrame(st.session_state.admin_applications)
    
    if len(df) == 0:
        st.info("Chưa có dữ liệu hồ sơ.")
    else:
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
            avg_score = int(df['credit_score'].mean())
            st.metric(label="Điểm CIC trung bình", value=avg_score)
            
        st.markdown("---")
        st.subheader("📋 Bảng Danh Sách Hồ Sơ Hệ Thống")
        st.dataframe(df[['id', 'name', 'phone', 'purpose', 'requested_amount', 'has_collateral', 'status', 'eligibility']], use_container_width=True)

elif admin_menu == "👥 Quản Lý & Thẩm Định Hồ Sơ":
    st.subheader("👥 Quản Lý Hồ Sơ & Phê Duyệt Tín Dụng")
    
    df = pd.DataFrame(st.session_state.admin_applications)
    
    if len(df) == 0:
        st.info("Chưa có hồ sơ nào.")
    else:
        status_filter = st.selectbox("Lọc trạng thái:", ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
        filtered_df = df if status_filter == "Tất cả" else df[df['status'] == status_filter]
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📁 [{row['id']}] - KH: {row['name']} | Nhu cầu: {row['requested_amount']:,.0f} VNĐ | Trạng thái: **{row['status']}**"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("#### 👤 Thông tin")
                    st.write(f"**Họ tên:** {row['name']}")
                    st.write(f"**Điện thoại:** {row['phone']}")
                    st.write(f"**Mục đích:** {row['purpose']}")
                    st.write(f"**Ngày nộp:** {row['date']}")
                    
                with c2:
                    st.markdown("#### 🛡️ Tài chính & TSBD")
                    st.write(f"**Thu nhập:** {row['monthly_income']:,.0f} VNĐ")
                    st.write(f"**Điểm CIC:** {row['credit_score']}")
                    st.write(f"**TS thế chấp:** {row['has_collateral']} ({row['collateral_type']})")
                    if row['has_collateral'] == "Có":
                        st.write(f"**Giá trị TS:** {row['collateral_value']:,.0f} VNĐ")
                    st.info(f"Đánh giá gợi ý: {row['eligibility']}")
                    
                with c3:
                    st.markdown("#### 🎯 Thao tác duyệt")
                    st.write(f"Hạn mức đề xuất: **{row['suggested_limit']:,.0f} VNĐ**")
                    
                    real_idx = next(i for i, item in enumerate(st.session_state.admin_applications) if item["id"] == row['id'])
                    
                    new_status = st.selectbox(
                        "Cập nhật trạng thái",
                        ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"],
                        index=["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"].index(row['status']),
                        key=f"adm_status_{row['id']}"
                    )
                    
                    notes = st.text_input("Ghi chú nội bộ", value=row['notes'], key=f"adm_notes_{row['id']}")
                    
                    if st.button(f"Lưu duyệt {row['id']}", key=f"adm_btn_{row['id']}" ):
                        st.session_state.admin_applications[real_idx]['status'] = new_status
                        st.session_state.admin_applications[real_idx]['notes'] = notes
                        st.success("Cập nhật thành công!")
                        st.rerun()
