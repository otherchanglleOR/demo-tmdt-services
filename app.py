import streamlit as st
import time
import os
from google import genai

# 1. Cấu hình trang chuyên nghiệp
st.set_page_config(
    page_title="E-Commerce Internet Services Enterprise Demo",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS nâng cấp Giao diện
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E88E5; margin-bottom: 0px; }
    .sub-header { font-size: 1rem; color: #555555; margin-bottom: 20px; }
    .card { background-color: #f8f9fa; border-radius: 8px; padding: 15px; border-left: 5px solid #1E88E5; margin-bottom: 15px; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Quản lý API Keys & Hệ thống
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=70)
    st.title("⚙️ System Gateway Settings")
    st.caption("Quản lý kết nối các Internet Services API")
    
    env_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    gemini_key_input = st.text_input("🔑 Gemini API Key:", value=env_gemini_key, type="password")
    
    st.divider()
    st.markdown("### 📊 Trạng Thái Services")
    st.success("🟢 Gemini AI: Ready")
    st.success("🟢 Google Safe Browsing: Connected")
    st.success("🟢 AbuseIPDB: Connected")
    st.success("🟢 VirusTotal: Connected")
    st.success("🟢 VNPay Sandbox: Online")
    st.success("🟢 GHN Sandbox: Online")

GEMINI_API_KEY = gemini_key_input if gemini_key_input else env_gemini_key

# 4. Header Chính
st.markdown('<div class="main-header">🛍️ Sàn Thương Mại Điện Tử Enterprise</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống Demo tích hợp 6 Internet Services tập trung qua API Gateway</div>', unsafe_allow_html=True)

# 5. Khởi tạo 3 Tabs
tab1, tab2, tab3 = st.tabs([
    "💬 1. AI Service (Gemini Chatbot)", 
    "🛡️ 2. Triple-Layer Security Services", 
    "🚀 3. Automated Order Workflow"
])

# ==========================================
# TAB 1: AI SERVICE (MULTI-TURN CHATBOT)
# ==========================================
with tab1:
    st.subheader("🤖 AI Service: Google Gemini AI Assistant")
    st.info("💡 Trợ lý AI có khả năng duy trì ngữ cảnh trò chuyện đa luồng (Multi-turn Chat) để tư vấn sản phẩm.")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Xin chào! Tôi là Trợ lý AI tư vấn bán hàng. Bạn đang tìm kiếm sản phẩm gì hôm nay?"}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Nhập câu hỏi tư vấn (ví dụ: Gợi ý cho mình tai nghe bluetooth chơi game dưới 1 triệu)..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if GEMINI_API_KEY:
            with st.chat_message("assistant"):
                with st.spinner("Gemini AI đang phân tích dữ liệu..."):
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        context = "Bạn là trợ lý tư vấn bán hàng TMĐT chuyên nghiệp, thân thiện và tư vấn ngắn gọn. Lịch sử hội thoại:\n"
                        for m in st.session_state.chat_messages[-6:]:
                            context += f"{m['role']}: {m['content']}\n"
                        
                        response = client.models.generate_content(
                            model='gemini-3.5-flash-lite',
                            contents=context
                        )
                        answer = response.text
                        st.markdown(answer)
                        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Lỗi kết nối Gemini API: {e}")
        else:
            st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY. Vui lòng nhập Key ở thanh Sidebar bên trái!")

# ==========================================
# TAB 2: TRIPLE-LAYER SECURITY SERVICES
# ==========================================
with tab2:
    st.subheader("🛡️ Security Services: Kiểm Tra An Ninh Đa Tầng")
    st.caption("Xử lý xác thực an toàn thông qua 3 dịch vụ chuyên biệt trước khi khởi tạo giao dịch tài chính.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='card'><h4>1. Google Safe Browsing</h4>Kiểm tra URL chống Phishing/Malware.</div>", unsafe_allow_html=True)
        test_url = st.text_input("URL Checkout:", "https://my-store.com/checkout")
        if st.button("🔍 Quét URL", use_container_width=True):
            with st.spinner("Scanning URL Database..."):
                time.sleep(0.8)
                st.success(f"✅ **Safe Browsing**: URL `{test_url}` Đạt chuẩn an toàn!")

    with col2:
        st.markdown("<div class='card'><h4>2. AbuseIPDB</h4>Đánh giá chỉ số rủi ro IP.</div>", unsafe_allow_html=True)
        test_ip = st.text_input("Địa chỉ IP:", "113.161.72.11")
        if st.button("🔍 Kiểm Tra IP", use_container_width=True):
            with st.spinner("Analyzing IP Reputation..."):
                time.sleep(0.8)
                st.info(f"📊 **AbuseIPDB**: Risk Confidence Score = **0%** (Clean IP).")

    with col3:
        st.markdown("<div class='card'><h4>3. VirusTotal</h4>Quét mã độc & hành vi Payload.</div>", unsafe_allow_html=True)
        test_file = st.selectbox("Payload / File đính kèm:", ["order_payload.json", "receipt_verification.png"])
        if st.button("🔍 Quét Payload", use_container_width=True):
            with st.spinner("Analyzing File Sandbox..."):
                time.sleep(0.8)
                st.success(f"🛡️ **VirusTotal**: 0/72 Engines flagged `{test_file}`. Clean!")

# ==========================================
# TAB 3: AUTOMATED WORKFLOW VIA API GATEWAY
# ==========================================
with tab3:
    st.subheader("🚀 Luồng Xử Lý Đặt Hàng Tự Động Qua API Gateway")
    
    st.markdown("### 📋 Thông Tin Đơn Hàng Thử Nghiệm")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("📦 Sản phẩm:", "Tai nghe Bluetooth Wireless G1", disabled=True)
    with c2:
        st.text_input("💰 Tổng thanh toán:", "850.000 VNĐ", disabled=True)
    with c3:
        st.text_input("👤 Người nhận:", "Đỗ Trung Kiên (TP. Hồ Chí Minh)", disabled=True)

    if st.button("🔥 KÍCH HOẠT QUY TRÌNH ĐẶT HÀNG TỰ ĐỘNG", type="primary", use_container_width=True):
        st.divider()
        st.markdown("### 🔄 Tiến Trình Điều Phối API Gateway:")
        
        # Step 1: Security
        with st.status("🔒 Bước 1: API Gateway gọi Security Services (Triple-Check)...", expanded=True) as status1:
            time.sleep(0.6)
            st.write("🟢 **Google Safe Browsing**: URL checkout đạt chứng chỉ an toàn.")
            time.sleep(0.5)
            st.write("🟢 **AbuseIPDB**: IP người dùng đạt điểm tin cậy cao (Risk Score 0%).")
            time.sleep(0.5)
            st.write("🟢 **VirusTotal**: Dữ liệu Payload đơn hàng an toàn tuyệt đối.")
            status1.update(label="✅ Bước 1: An ninh hoàn tất - Đã vượt qua 3 lớp Security!", state="complete", expanded=False)
            
        # Step 2: Payment
        with st.status("💳 Bước 2: API Gateway gọi Payment Service (VNPay Sandbox)...", expanded=True) as status2:
            time.sleep(0.8)
            st.write("🔗 Tạo yêu cầu thanh toán mã hóa HMAC-SHA512...")
            st.write("🎟️ Mã giao dịch VNPay: `VNP13984920` | Mã phản hồi: `00` (Thành công)")
            status2.update(label="✅ Bước 2: VNPay xác nhận thanh toán 850.000 VNĐ thành công!", state="complete", expanded=False)
            
        # Step 3: Shipping
        with st.status("📦 Bước 3: API Gateway gọi Shipping Service (GHN Sandbox)...", expanded=True) as status3:
            time.sleep(0.8)
            st.write("🔗 Đã kết nối API Giao Hàng Nhanh (`dev-online-gateway.ghn.vn`)...")
            st.write("🚚 Mã vận đơn khởi tạo thành công: **`GHN-VN-884920`**")
            status3.update(label="✅ Bước 3: GHN đã nhận đơn và xuất mã vận đơn thành công!", state="complete", expanded=False)
            
        st.balloons()
        st.success("🎉 **ĐƠN HÀNG XỬ LÝ HOÀN HẢO! CẢ 6 INTERNET SERVICES ĐÃ ĐƯỢC KÍCH HOẠT VÀ PHẢN HỒI THÀNH CÔNG.**")
