import streamlit as st
import time
import os
from google import genai

# Cấu hình trang Web
st.set_page_config(
    page_title="E-Commerce Internet Services - Automated Risk Flow",
    page_icon="🛍️",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("🛍️ Sàn Thương Mại Điện Tử - Demo Tích Hợp Internet Services")
st.caption("Quy trình tự động hóa 100%: Tư vấn AI -> Đặt hàng -> Kiểm tra An ninh ngầm -> Phân nhánh Risk Score -> Thanh toán/Vận chuyển/Cảnh báo")

# Lấy API Key Gemini từ Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Khởi tạo các Tab theo Quy trình
tab1, tab2 = st.tabs([
    "💬 1. Tư Vấn Khách Hàng (Gemini AI)", 
    "🚀 2. Luồng Đặt Hàng & Kiểm Soát Rủi Ro Tự Động"
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
# BƯỚC 3 -> 12: CHỌN SẢN PHẨM & XỬ LÝ RỦI RO TỰ ĐỘNG
# ==========================================
with tab2:
    st.subheader("🛒 Khách Hàng Chọn Sản Phẩm & Đặt Hàng")
    st.markdown("Chọn 1 trong 3 sản phẩm thử nghiệm đại diện cho các kịch bản an ninh khác nhau để xem hệ thống xử lý tự động ngầm:")

    # 3 Sản phẩm tương ứng với 3 kịch bản
    products = {
        "🟢 Sản phẩm A: Giày Thể Thao Pro (Kịch bản: An Toàn / Rủi Ro Thấp)": {
            "name": "Giày Thể Thao Pro",
            "price": "1.200.000 VNĐ",
            "risk": "LOW",
            "url_status": "✅ Google Safe Browsing: Clean URL (An toàn)",
            "ip_status": "🟢 AbuseIPDB: IP Sạch (Risk Score: 0%)",
            "file_status": "🛡️ VirusTotal: 0/72 Clean (Không có mã độc)"
        },
        "🟡 Sản phẩm B: Đồng Hồ Thông Minh (Kịch bản: Nghi Vấn / Rủi Ro Trung Bình)": {
            "name": "Đồng Hồ Thông Minh",
            "price": "3.500.000 VNĐ",
            "risk": "MEDIUM",
            "url_status": "✅ Google Safe Browsing: Clean URL (An toàn)",
            "ip_status": "🟡 AbuseIPDB: IP Nghi vấn / Proxy (Risk Score: 45%)",
            "file_status": "🛡️ VirusTotal: 0/72 Clean (Không có mã độc)"
        },
        "🔴 Sản phẩm C: Mã Giảm Giá Độc Quyền (Kịch bản: Độc Hại / Rủi Ro Cao)": {
            "name": "Mã Giảm Giá Độc Quyền 99%",
            "price": "50.000 VNĐ",
            "risk": "HIGH",
            "url_status": "🚨 Google Safe Browsing: Phishing / Scam Site Detected!",
            "ip_status": "🔴 AbuseIPDB: Blacklisted IP (Risk Score: 95%)",
            "file_status": "⚠️ VirusTotal: 12/72 Flagged Malware!"
        }
    }

    selected_product_key = st.radio("Chọn sản phẩm đặt hàng:", list(products.keys()))
    selected_prod = products[selected_product_key]

    st.divider()
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.text_input("Sản phẩm đã chọn:", selected_prod["name"], disabled=True)
        st.text_input("Giá thanh toán:", selected_prod["price"], disabled=True)
    with col_info2:
        st.text_input("Người mua:", "Đỗ Trung Kiên", disabled=True)
        st.text_input("Địa chỉ giao hàng:", "TP. Hồ Chí Minh", disabled=True)

    if st.button("🔥 BẤM ĐẶT HÀNG (KÍCH HOẠT QUY TRÌNH TỰ ĐỘNG)", type="primary"):
        st.divider()
        st.markdown("## 🔄 QUY TRÌNH KIỂM TRA & ĐIỀU PHỐI TỰ ĐỘNG (API GATEWAY)")

        # ----------------------------------------------------
        # BƯỚC: KIỂM TRA BẢO MẬT TỰ ĐỘNG
        # ----------------------------------------------------
        with st.status("🔍 1. Hệ thống đang tự động quét an ninh ngầm qua 3 Security Services...", expanded=True) as status_sec:
            time.sleep(0.8)
            st.write(selected_prod["url_status"])
            time.sleep(0.6)
            st.write(selected_prod["ip_status"])
            time.sleep(0.6)
            st.write(selected_prod["file_status"])
            status_sec.update(label="✅ Đã hoàn tất phân tích an ninh!", state="complete", expanded=False)

        # ----------------------------------------------------
        # BƯỚC: PHÂN NHÁNH RISK SCORE TỰ ĐỘNG
        # ----------------------------------------------------
        st.markdown("---")
        st.markdown("### 📊 PHÂN LOẠI MỨC ĐỘ RỦI RO (RISK SCORE)")

        risk_type = selected_prod["risk"]

        # NHÁNH 1: RỦI RO CAO -> CHẶN ĐƠN HÀNG
        if risk_type == "HIGH":
            st.error("🔴 **MỨC RỦI RO: CAO (High Risk Score)**")
            st.warning("🚨 Phát hiện mối đe dọa an ninh nghiêm trọng (URL lừa đảo hoặc IP bị blacklist)!")
            time.sleep(0.5)
            st.error("⛔ **KẾT QUẢ: CHẶN ĐƠN HÀNG!** Hệ thống đã tự động dừng giao dịch để bảo vệ an toàn.")

        # NHÁNH 2: RỦI RO TRUNG BÌNH -> CẢNH BÁO -> XÁC MINH
        elif risk_type == "MEDIUM":
            st.warning("🟡 **MỨC RỦI RO: TRUNG BÌNH (Medium Risk Score)**")
            st.info("⚠️ **CẢNH BÁO**: Địa chỉ IP truy cập bất thường. Yêu cầu khách hàng xác minh danh tính (OTP).")
            
            st.markdown("#### 🔐 BƯỚC XÁC MINH KHÁCH HÀNG")
            user_otp = st.text_input("Nhập mã OTP gửi về điện thoại (Thử nhập mã đúng là '123456'):", key="otp_input")
            
            if st.button("Xác thực OTP"):
                if user_otp == "123456":
                    st.success("✅ **Xác minh thành công!** Cho phép chuyển tiếp sang luồng Thanh toán & Vận chuyển.")
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        with st.status("💳 THANH TOÁN (VNPay)", expanded=True):
                            time.sleep(0.6)
                            st.write("Cổng: VNPay Sandbox")
                            st.write("Mã GD: `VNP-M88219`")
                            st.write("Trạng thái: **Thành công**")
                    with col_m2:
                        with st.status("🚚 VẬN CHUYỂN (GHN)", expanded=True):
                            time.sleep(0.6)
                            st.write("Đơn vị: GHN Express")
                            st.write("Mã VĐ: `GHN-VN-88219`")
                            st.write("Trạng thái: **Đã tạo đơn**")
                    with col_m3:
                        with st.status("🔔 THÔNG BÁO (Twilio/Zalo)", expanded=True):
                            time.sleep(0.6)
                            st.write("Kênh: Twilio SMS / Zalo ZNS")
                            st.write("Trạng thái: **Đã gửi SMS**")
                    st.balloons()
                else:
                    st.error("❌ **Xác minh thất bại!** Mã OTP không chính xác.")
                    st.error("⛔ **KẾT QUẢ: CHẶN ĐƠN HÀNG!**")

        # NHÁNH 3: RỦI RO THẤP -> CHẠY TỰ ĐỘNG THẲNG ĐẾN HOÀN TẤT
        else:
            st.success("🟢 **MỨC RỦI RO: THẤP (Low Risk Score)**")
            st.markdown("Hệ thống tự động kích hoạt liên hoàn các dịch vụ:")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                with st.status("💳 THANH TOÁN (VNPay)", expanded=True):
                    time.sleep(0.8)
                    st.write("Cổng: VNPay Sandbox")
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
                    st.write("Kênh: Twilio SMS / Zalo ZNS")
                    st.write("Nội dung: *Đơn hàng đã xác nhận*")
                    st.write("Trạng thái: **Đã gửi tin nhắn**")

            st.balloons()
            st.success("🎉 **ĐƠN HÀNG HOÀN TẤT THÀNH CÔNG THEO ĐÚNG LUỒNG RỦI RO THẤP!**")
