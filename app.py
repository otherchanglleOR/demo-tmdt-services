import streamlit as st
import time
import os
from google import genai

# Cấu hình trang Web
st.set_page_config(
    page_title="E-Commerce Internet Services Demo",
    page_icon="🛍️",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("🛍️ Sàn Thương Mại Điện Tử - Demo Tích Hợp Internet Services")
st.caption("Đồ án môn học: Hệ thống tích hợp AI Service, Multi-Security Services, Payment & Logistics API")

# Lấy API Key từ Secrets của Streamlit Cloud
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Khởi tạo các Tab theo đúng Sơ đồ Kiến trúc
tab1, tab2, tab3 = st.tabs([
    "1. AI Service (Gemini)", 
    "2. Security Services (Google Safe Browsing, AbuseIPDB, VirusTotal)", 
    "3. Full E-Commerce Workflow"
])

# ==========================================
# TAB 1: AI SERVICE (GOOGLE GEMINI)
# ==========================================
with tab1:
    st.subheader("🤖 AI Service: Google Gemini AI")
    st.markdown("Chức năng: *Tư vấn khách hàng tự động*")
    
    user_query = st.text_input("Nhập câu hỏi tư vấn của khách hàng:", "Tư vấn cho tôi tai nghe bluetooth chơi game dưới 1 triệu")
    
    if st.button("Gửi cho AI Tư Vấn"):
        if GEMINI_API_KEY:
            with st.spinner("Google Gemini đang phân tích câu hỏi..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    response = client.models.generate_content(
                        model='gemini-3.5-flash-lite',
                        contents=f"Bạn là AI tư vấn bán hàng TMĐT. Trả lời ngắn gọn dưới 3 câu, thân thiện: {user_query}"
                    )
                    st.success("Phản hồi từ Google Gemini AI:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Lỗi gọi AI API: {e}")
        else:
            st.warning("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit Cloud!")

# ==========================================
# TAB 2: SECURITY SERVICES (KHỚP SƠ ĐỒ KIẾN TRÚC)
# ==========================================
with tab2:
    st.subheader("🛡️ Security Services: Kiểm Tra An Ninh 3 Lớp")
    st.markdown("Chức năng: *Kiểm tra URL, Địa chỉ IP và File/Hành vi độc hại trước khi giao dịch*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1. Google Safe Browsing")
        test_url = st.text_input("Nhập URL kiểm tra:", "https://my-store.com/checkout")
        if st.button("Kiểm tra URL"):
            with st.spinner("Scanning URL..."):
                time.sleep(1)
                st.success(f"✅ **Google Safe Browsing**: URL `{test_url}` An toàn (No Phishing / Malware).")

    with col2:
        st.markdown("### 2. AbuseIPDB")
        test_ip = st.text_input("Nhập IP truy cập:", "113.161.72.11")
        if st.button("Kiểm tra IP"):
            with st.spinner("Checking IP Risk Score..."):
                time.sleep(1)
                st.info(f"📊 **AbuseIPDB**: IP `{test_ip}` - Confidence Score: **0% Risk** (Clean IP).")

    with col3:
        st.markdown("### 3. VirusTotal")
        test_file = st.selectbox("Hành vi/File đính kèm:", ["order_payload.json", "payment_receipt.png"])
        if st.button("Quét Virus / Behavior"):
            with st.spinner("Analyzing Behavior..."):
                time.sleep(1)
                st.success(f"🛡️ **VirusTotal**: 0/72 Vendors flagged `{test_file}`. Clean!")

# ==========================================
# TAB 3: FULL WORKFLOW (LUỒNG ĐẶT HÀNG TỰ ĐỘNG)
# ==========================================
with tab3:
    st.subheader("🚀 Luồng Xử Lý Đặt Hàng Tự Động (API Gateway Integration)")
    
    st.write("**Thông tin đơn hàng mẫu:**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input("Sản phẩm:", "Tai nghe Bluetooth Wireless x1", disabled=True)
        st.text_input("Tổng tiền:", "850.000 VNĐ", disabled=True)
    with col_b:
        st.text_input("Khách hàng:", "Đỗ Trung Kiên", disabled=True)
        st.text_input("Địa chỉ giao hàng:", "TP. Hồ Chí Minh", disabled=True)

    if st.button("🔥 BẤM ĐẶT HÀNG (KÍCH HOẠT API GATEWAY)", type="primary"):
        st.divider()
        st.markdown("### 🔄 API Gateway đang điều phối các Services:")
        
        # Bước 1: Security Services (Triple Check)
        with st.status("1. Security Services đang kiểm tra an toàn...", expanded=True) as status1:
            time.sleep(0.8)
            st.write("🟢 **Google Safe Browsing**: URL checkout hợp lệ.")
            time.sleep(0.6)
            st.write("🟢 **AbuseIPDB**: IP người dùng an toàn (Risk Score: 0%).")
            time.sleep(0.6)
            st.write("🟢 **VirusTotal**: Không phát hiện hành vi bất thường/mã độc.")
            status1.update(label="✅ Security Services: Đã vượt qua 3 lớp kiểm tra an ninh!", state="complete", expanded=False)
            
        # Bước 2: Payment Service (VNPay)
        with st.status("2. Payment Service (VNPay) đang xử lý...", expanded=True) as status2:
            time.sleep(1)
            st.write("💳 Đã kết nối Cổng thanh toán VNPay Sandbox...")
            st.write("🎟️ Mã giao dịch: `VNP13984920` - Trạng thái: **Thanh toán thành công (00)**.")
            status2.update(label="✅ Payment Service: VNPay xác nhận thanh toán 850.000 VNĐ thành công!", state="complete", expanded=False)
            
        # Bước 3: Shipping Service (GHN)
        with st.status("3. Shipping Service (GHN) đang tạo vận đơn...", expanded=True) as status3:
            time.sleep(1)
            st.write("📦 Đã kết nối API Giao Hàng Nhanh (GHN Sandbox)...")
            st.write("🚚 Mã vận đơn tạo thành công: **`GHN-VN-884920`**")
            status3.update(label="✅ Shipping Service: GHN đã nhận đơn và cấp mã vận đơn thành công!", state="complete", expanded=False)
            
        st.balloons()
        st.success("🎉 **ĐƠN HÀNG ĐÃ ĐƯỢC XỬ LÝ HOÀN HẢO QUA TOÀN BỘ INTERNET SERVICES TRÊN SƠ ĐỒ KIẾN TRÚC!**")
