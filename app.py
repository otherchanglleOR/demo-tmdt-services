import streamlit as st
import time
import os
from google import genai

# Cấu hình trang Web
st.set_page_config(
    page_title="E-Commerce Internet Services - Interactive Flow",
    page_icon="🛍️",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("🛍️ Sàn Thương Mại Điện Tử - Demo Tích Hợp Internet Services")
st.caption("Quy trình tự động hóa tích hợp AI, Kiểm tra An ninh 3 Lớp, Phân loại Risk Score, Thanh toán & Vận chuyển")

# Lấy các API Keys từ Streamlit Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Khởi tạo các Tab theo đúng Quy trình
tab1, tab2 = st.tabs([
    "💬 1. Tư Vấn Khách Hàng (Gemini AI)", 
    "🚀 2. Quy Trình Đặt Hàng & Kiểm Soát Rủi Ro (Full Workflow)"
])

# ==========================================
# BƯỚC 1 & 2: KHÁCH HÀNG & TƯ VẤN KHÁCH HÀNG (GEMINI AI)
# ==========================================
with tab1:
    st.subheader("🤖 Tư Vấn Khách Hàng - Google Gemini AI")
    st.markdown("Chức năng: *Hỗ trợ khách hàng tìm kiếm và chọn lựa sản phẩm trước khi đặt hàng*")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Xin chào! Tôi là trợ lý AI. Bạn đang muốn tìm sản phẩm nào hôm nay?"}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hỏi AI tư vấn sản phẩm..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if GEMINI_API_KEY:
            with st.chat_message("assistant"):
                with st.spinner("Gemini AI đang tư vấn..."):
                    try:
                        client = genai.Client(api_key=GEMINI_API_KEY)
                        context = "Bạn là trợ lý tư vấn bán hàng TMĐT. Trả lời thân thiện, ngắn gọn dưới 3 câu. Lịch sử:\n"
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
                        st.error(f"Lỗi gọi Gemini API: {e}")
        else:
            st.warning("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets!")

# ==========================================
# BƯỚC 3 -> 12: ĐẶT HÀNG & MÔ HÌNH XỬ LÝ RỦI RO THEO SƠ ĐỒ
# ==========================================
with tab2:
    st.subheader("🛒 Quy Trình Đặt Hàng & Kiểm Soát Rủi Ro Phân Nhánh")
    
    st.markdown("### 📦 1. Khách hàng chọn sản phẩm & Đặt hàng")
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Tên sản phẩm:", "Giày Snaker Thể Thao Pro")
        product_price = st.text_input("Giá tiền:", "1.200.000 VNĐ")
    with col2:
        customer_name = st.text_input("Họ tên khách hàng:", "Đỗ Trung Kiên")
        customer_address = st.text_input("Địa chỉ giao hàng:", "TP. Hồ Chí Minh")

    st.divider()
    st.markdown("### 🛡️ 2. Mô phỏng tham số Kiểm tra An ninh (Dành cho Demo)")
    st.caption("Thay đổi các giá trị bên dưới để test các nhánh Rủi ro Thấp / Trung bình / Cao theo sơ đồ:")
    
    col_sec1, col_sec2, col_sec3 = st.columns(3)
    with col_sec1:
        input_url = st.selectbox("Safe Browsing (Quét URL):", ["URL An toàn (Clean)", "URL Độc hại / Phishing (Danger)"])
    with col_sec2:
        input_ip = st.selectbox("AbuseIPDB (Mức độ rủi ro IP):", ["IP Sạch (Risk 0%)", "IP Nghi vấn (Risk 45%)", "IP Spam/Tấn công (Risk 90%)"])
    with col_sec3:
        input_file = st.selectbox("VirusTotal (Quét File/Mã độc):", ["File Sạch (0/72 Clean)", "Phát hiện Mã độc (Malware Flagged)"])

    if st.button("🔥 KÍCH HOẠT QUY TRÌNH XỬ LÝ ĐƠN HÀNG", type="primary"):
        st.divider()
        st.markdown("## 🔄 LUỒNG XỬ LÝ TỰ ĐỘNG THEO SƠ ĐỒ KIẾN TRÚC")

        # ----------------------------------------------------
        # BƯỚC: SECURITY CHECK (Safe Browsing, AbuseIPDB, VirusTotal)
        # ----------------------------------------------------
        with st.status("🔍 1. Đang thực hiện Kiểm tra An ninh 3 lớp...", expanded=True) as status_sec:
            time.sleep(0.6)
            st.write(f"🌐 **Safe Browsing**: {input_url}")
            time.sleep(0.6)
            st.write(f"📍 **AbuseIPDB**: {input_ip}")
            time.sleep(0.6)
            st.write(f"🛡️ **VirusTotal**: {input_file}")
            status_sec.update(label="✅ Hoàn tất kiểm tra 3 lớp an ninh!", state="complete", expanded=False)

        # ----------------------------------------------------
        # BƯỚC: RISK SCORE (Tính toán điểm rủi ro)
        # ----------------------------------------------------
        risk_level = "LOW"
        if "Phishing" in input_url or "90%" in input_ip or "Malware" in input_file:
            risk_level = "HIGH"
        elif "45%" in input_ip:
            risk_level = "MEDIUM"

        st.markdown("---")
        st.markdown("### 📊 RISK SCORE - DÙNG NGUYÊN TẮC PHÂN NHÁNH")

        # NHÁNH 1: RỦI RO CAO (HIGH RISK) -> CHẶN ĐƠN HÀNG
        if risk_level == "HIGH":
            st.error("🔴 **MỨC RỦI RO: CAO (High Risk Score)**")
            st.warning("🚨 Phát hiện mối đe dọa an ninh nghiêm trọng (URL độc hại, IP nằm trong danh sách đen hoặc có mã độc)!")
            time.sleep(0.5)
            st.error("⛔ **KẾT QUẢ: CHẶN ĐƠN HÀNG!** Hệ thống đã hủy giao dịch để bảo vệ an toàn.")

        # NHÁNH 2: RỦI RO TRUNG BÌNH (MEDIUM RISK) -> CẢNH BÁO -> XÁC MINH
        elif risk_level == "MEDIUM":
            st.warning("🟡 **MỨC RỦI RO: TRUNG BÌNH (Medium Risk Score)**")
            st.info("⚠️ **CẢNH BÁO**: Yêu cầu xác minh danh tính khách hàng trước khi cho phép thanh toán.")
            
            st.markdown("#### 🔐 XÁC MINH KHÁCH HÀNG (OTP / Captcha)")
            user_otp = st.text_input("Nhập mã OTP xác minh gửi về điện thoại (Thử nhập '123456'):", key="otp_input")
            
            if st.button("Xác thực OTP"):
                if user_otp == "123456":
                    st.success("✅ **Xác minh đạt!** Cho phép tiếp tục luồng thanh toán.")
                    
                    # Tiến hành Thanh toán -> Vận chuyển -> Thông báo
                    with st.spinner("💳 1. Kết nối VNPay..."):
                        time.sleep(1)
                        st.success("💳 **Thanh toán VNPay**: Giao dịch thành công (Mã: VNP99823)")
                    with st.spinner("🚚 2. Kết nối GHN..."):
                        time.sleep(1)
                        st.success("🚚 **Vận chuyển GHN**: Khởi tạo đơn hàng thành công (Mã: GHN-VN-99823)")
                    with st.spinner("🔔 3. Kết nối Notification API..."):
                        time.sleep(1)
                        st.success("🔔 **Thông báo (Twilio/Zalo ZNS)**: Đã gửi SMS xác nhận đơn hàng thành công đến khách hàng!")
                    st.balloons()
                else:
                    st.error("❌ **Xác minh không đạt!** Mã OTP sai.")
                    st.error("⛔ **KẾT QUẢ: CHẶN ĐƠN HÀNG!**")

        # NHÁNH 3: RỦI RO THẤP (LOW RISK) -> THANH TOÁN -> VẬN CHUYỂN -> THÔNG BÁO
        else:
            st.success("🟢 **MỨC RỦI RO: THẤP (Low Risk Score)**")
            st.markdown("Chuyển thẳng sang luồng xử lý tự động:")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                with st.status("💳 THANH TOÁN (VNPay)", expanded=True):
                    time.sleep(0.8)
                    st.write("Cổng thanh toán: VNPay Sandbox")
                    st.write("Số tiền: 1.200.000 VNĐ")
                    st.write("Trạng thái: **Thành công (00)**")
            
            with col_b:
                with st.status("🚚 VẬN CHUYỂN (GHN)", expanded=True):
                    time.sleep(0.8)
                    st.write("Đơn vị: Giao Hàng Nhanh")
                    st.write("Mã vận đơn: `GHN-VN-102938`")
                    st.write("Trạng thái: **Đã tiếp nhận**")

            with col_c:
                with st.status("🔔 THÔNG BÁO (Twilio/Zalo)", expanded=True):
                    time.sleep(0.8)
                    st.write("Kênh gửi: Twilio SMS / Zalo ZNS")
                    st.write("Nội dung: *Đơn hàng đã được xác nhận*")
                    st.write("Trạng thái: **Đã gửi**")

            st.balloons()
            st.success("🎉 **ĐƠN HÀNG HOÀN TẤT THÀNH CÔNG THEO ĐÚNG TIẾN TRÌNH RỦI RO THẤP!**")
