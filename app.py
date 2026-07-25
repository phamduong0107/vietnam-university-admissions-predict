import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import time

st.set_page_config(page_title="Dự báo Điểm chuẩn 2026", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS (Hiệu ứng & Giao diện Premium) ---
st.markdown("""
<style>
    /* Fade-in animation cho toàn trang */
    .block-container {
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Title Gradient */
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    
    /* Thẻ Metric Card Hover */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        border: 1px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title-gradient">🎯 Hệ thống Dự báo Điểm chuẩn 2026</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ứng dụng AI phân tích phổ điểm, chỉ tiêu và xu hướng ngành nghề tại Hà Nội.</p>', unsafe_allow_html=True)

import json
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('results/predictions_2026.csv')
        try:
            # Xóa cache để load lại file JSON
            with open('results/school_mapping.json', 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            df['ten_truong'] = df['ma_truong'].map(mapping).fillna(df['ma_truong'])
            df['truong_display'] = df['ma_truong'] + " - " + df['ten_truong']
        except:
            df['truong_display'] = df['ma_truong']
        return df
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Chưa có dữ liệu dự báo. Vui lòng chạy pipeline huấn luyện mô hình trước!")
else:
    # --- Trợ lý Tư vấn Chọn Trường ---
    st.header("🧑‍🎓 Trợ lý Tư vấn Chọn Trường")
    st.markdown("Nhập điểm thi thực tế và tổ hợp môn của bạn để nhận danh sách trường phù hợp.")
    
    with st.container(border=True):
        col_diem, col_khoi = st.columns(2)
        with col_diem:
            user_score = st.number_input("Điểm xét tuyển của bạn (Đã cộng ưu tiên):", min_value=0.0, max_value=30.0, value=24.0, step=0.1)
        
        with col_khoi:
            all_blocks = set()
            for b in df['ma_xet_tuyen'].dropna().unique():
                all_blocks.update([x.strip() for x in str(b).split(',')])
            khoi_list = sorted(list(all_blocks))
            user_block = st.selectbox("Khối thi (Tổ hợp môn):", khoi_list, index=khoi_list.index("A00") if "A00" in khoi_list else 0)

        col_truong, col_nganh = st.columns(2)
        with col_truong:
            truong_list_adv = sorted(df['truong_display'].unique().tolist())
            search_truong = st.multiselect("🔍 Lọc Trường (Tùy chọn):", truong_list_adv)
        with col_nganh:
            search_nganh = st.text_input("🔍 Tìm Tên Ngành (Tùy chọn):", "", placeholder="VD: Máy tính, Kinh tế...")

    # Nút bấm có hiệu ứng
    analyze_btn = st.button("✨ Bắt đầu Phân tích Phù hợp ✨", use_container_width=True, type="primary")

    if analyze_btn:
        with st.spinner('AI đang quét và phân loại hàng ngàn dữ liệu...'):
            time.sleep(1) # Tạo cảm giác AI đang suy nghĩ
            st.balloons() # Hiệu ứng bóng bay nổ tung
            
    # Lọc data theo Khối
    df_filtered_block = df[df['ma_xet_tuyen'].fillna('').str.contains(user_block)].copy()
    
    if search_truong:
        df_filtered_block = df_filtered_block[df_filtered_block['truong_display'].isin(search_truong)]
    if search_nganh.strip():
        df_filtered_block = df_filtered_block[df_filtered_block['chuong_trinh_dao_tao'].str.contains(search_nganh.strip(), case=False, na=False)]
        
    if df_filtered_block.empty:
        st.info("Không tìm thấy dữ liệu phù hợp với bộ lọc của bạn.")
    else:
        # Phân loại 3 nhóm
        safe_df = df_filtered_block[user_score >= df_filtered_block['diem_chuan_du_bao'] + 0.5]
        appr_df = df_filtered_block[(user_score >= df_filtered_block['diem_chuan_du_bao'] - 0.5) & (user_score < df_filtered_block['diem_chuan_du_bao'] + 0.5)]
        risk_df = df_filtered_block[(user_score >= df_filtered_block['diem_chuan_du_bao'] - 2.0) & (user_score < df_filtered_block['diem_chuan_du_bao'] - 0.5)]
        
        tab1, tab2, tab3 = st.tabs(["✅ Nhóm An Toàn", "🎯 Nhóm Vừa Sức", "⚠️ Nhóm Thử Thách (Rủi ro)"])
        
        def display_advisory_table(data_df, sort_asc=True):
            if data_df.empty:
                st.write("Không có trường nào trong nhóm này với mức điểm của bạn.")
            else:
                show_df = data_df[['truong_display', 'chuong_trinh_dao_tao', 'ma_xet_tuyen', 'diem_chuan_du_bao']].copy()
                show_df['diem_chenh_lech'] = (user_score - show_df['diem_chuan_du_bao']).round(2)
                show_df.columns = ['Trường', 'Tên Ngành', 'Tổ Hợp', 'Điểm Dự Báo', 'Chênh Lệch']
                show_df['abs_chenh_lech'] = show_df['Chênh Lệch'].abs()
                show_df = show_df.sort_values(by='abs_chenh_lech', ascending=sort_asc)
                show_df = show_df.drop(columns=['abs_chenh_lech'])
                
                show_df['Điểm Dự Báo'] = show_df['Điểm Dự Báo'].apply(lambda x: f"{x:.2f}")
                show_df['Chênh Lệch'] = show_df['Chênh Lệch'].apply(lambda x: f"+{x:.2f}" if x > 0 else f"{x:.2f}")
                
                st.dataframe(show_df, use_container_width=True, hide_index=True)

        with tab1:
            st.markdown("**Nhóm An Toàn:** Khả năng đỗ cực cao. Đang hiển thị các ngành sát điểm bạn nhất lên đầu.")
            display_advisory_table(safe_df, sort_asc=True)
            
        with tab2:
            st.markdown("**Nhóm Vừa Sức:** Điểm của bạn nằm trong vùng cạnh tranh khốc liệt. Hãy ưu tiên nguyện vọng 1, 2.")
            display_advisory_table(appr_df, sort_asc=True)
            
        with tab3:
            st.markdown("**Nhóm Thử Thách:** Thấp hơn dự báo tối đa 2 điểm. Dành cho nguyện vọng may rủi.")
            display_advisory_table(risk_df, sort_asc=True)
            
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    # --- Tra cứu truyền thống ---
    st.header("📊 Bảng Tra Cứu Toàn Bộ")
    
    # Move filters to main page
    col_filter_1, col_filter_2 = st.columns([1, 2])
    with col_filter_1:
        truong_list = sorted(df['truong_display'].unique().tolist())
        selected_truong = st.multiselect("Lọc nhanh trường:", truong_list, default=[])
    
    if selected_truong:
        filtered_df = df[df['truong_display'].isin(selected_truong)]
    else:
        filtered_df = df
        
    filtered_df['delta'] = (filtered_df['diem_chuan_du_bao'] - filtered_df['diem_nam_ngoai']).round(2)
    
    display_df = filtered_df[['truong_display', 'chuong_trinh_dao_tao', 'ma_xet_tuyen', 'diem_nam_ngoai', 'diem_chuan_du_bao', 'delta']].copy()
    display_df.columns = ['Trường', 'Tên Ngành', 'Tổ Hợp', 'Điểm 2025', 'Dự Báo 2026', 'Mức Tăng/Giảm']
    
    st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Thống kê Biến động Thị trường")
    col1, col2, col3 = st.columns(3)
    
    tang = len(filtered_df[filtered_df['delta'] > 0.1])
    giam = len(filtered_df[filtered_df['delta'] < -0.1])
    di_ngang = len(filtered_df[(filtered_df['delta'] >= -0.1) & (filtered_df['delta'] <= 0.1)])
    
    col1.metric("🔥 Ngành TĂNG điểm", tang, f"{tang/len(filtered_df)*100:.1f}%")
    col2.metric("📉 Ngành GIẢM điểm", giam, f"-{giam/len(filtered_df)*100:.1f}%")
    col3.metric("⚖️ Ngành ĐI NGANG", di_ngang, f"{di_ngang/len(filtered_df)*100:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Phân bố Điểm Dự Báo")
    fig = px.histogram(filtered_df, x="diem_chuan_du_bao", nbins=30, 
                       labels={'diem_chuan_du_bao': 'Điểm chuẩn', 'count': 'Số lượng ngành'},
                       color_discrete_sequence=['#4ECDC4'])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
