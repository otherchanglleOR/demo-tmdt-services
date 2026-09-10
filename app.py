import streamlit as st
import requests
import time
import os
from google import genai

# Lấy Gemini API Key từ cấu hình Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

st.set_page_config(page_title="Demo Internet Services - Sàn TMĐT", layout="wide")
st.title("🛒 DEMO TÍCH HỢP 5 INTERNET SERVICES CHO SÀN TMĐT")

# Thanh bên hông (Sidebar)
st.sidebar.header("🔌 TRẠNG THÁI KẾT NỐI SERVICES")
st.sidebar.success("1. AI Service: Google Gemini API (Flash-8B Ultra-Light)")
st.sidebar.success("2. Security WAF: Cloudflare (Proxy)")
st.sidebar.success("3. Security Fraud: vKey / Device Check (Active)")
st.sidebar.success("4. Payment Service: VNPay Gateway (Sandbox)")
st.sidebar.success("5. Shipping/Notify: GHN API & Zalo ZNS (Sandbox)")

tab1, tab2 = st.tabs(["🤖 1. AI Tư Vấn Khách Hàng", "📦 2. Workflow Tự Động Hóa Đặt Hàng"])

# ---------------------------------------------------------
# TAB 1: AI SERVICE (GOOGLE GEMINI 2.5 FLASH LITE - SIÊU NHẸ)
# ---------------------------------------------------------
with tab1:
    st.subheader("Trải nghiệm AI Service tư vấn bán hàng")
    user_query = st.text_input("Nhập câu hỏi của khách hàng:", "Tư vấn cho tôi tai nghe bluetooth giá dưới 1 triệu")
    
    if st.button("Gửi cho AI Tư Vấn"):
        if GEMINI_API_KEY:
            with st.spinner("Google AI đang xử lý..."):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    # Dùng gemini-2.5-flash-lite theo đúng bảng Quota trong tài khoản của bạn
                    response = client.models.generate_content(
                        model='gemini-2.5-flash-lite',
                        contents=f"Bạn là AI tư vấn bán hàng TMĐT. Trả lời ngắn gọn dưới 3 câu, thân thiện: {user_query}"
                    )
                    st.info(f"**Phản hồi từ Google Gemini AI:**\n\n{response.text}")
                except Exception as e:
                    st.error(f"Lỗi gọi AI API: {e}")
        else:
            st.warning("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit Cloud!")

# ---------------------------------------------------------
# TAB 2: WORKFLOW TỰ ĐỘNG HÓA
# ---------------------------------------------------------
with tab2:
    st.subheader("Luồng tự động hóa kết nối Security -> Payment -> Shipping -> Notification")
    
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("Tên sản phẩm", "Áo Polo Unisex Local Brand")
        price = st.number_input("Giá tiền (VND)", value=250000)
        customer_name = st.text_input("Tên khách hàng", "Đỗ Trung Kiên")
        customer_phone = st.text_input("Số điện thoại", "0901234567")
        customer_address = st.text_input("Địa chỉ giao hàng", "Quận 1, TP. Hồ Chí Minh")
        
    with col2:
        st.write("**Kích hoạt đơn hàng & Chạy Workflow:**")
        if st.button("🚀 BẤM ĐẶT HÀNG (KÍCH HOẠT WORKFLOW)"):
            st.write("---")
            
            # 1. SECURITY CHECK
            st.write("🔍 **Bước 1: Gọi Security API (Cloudflare / vKey Check Risk Score)...**")
            time.sleep(1)
            st.success("✅ Security Passed! (IP Check: OK | Device Risk Score: 10/100 - An toàn)")

            # 2. PAYMENT API
            st.write("🔍 **Bước 2: Gọi Payment API (VNPay Gateway)...**")
            time.sleep(1)
            trans_id = f"VNPAY_{int(time.time())}"
            st.success(f"✅ Thanh toán thành công qua VNPay API! Mã GD: **{trans_id}** | Số tiền: **{price:,} VND**")

            # 3. SHIPPING API
            st.write("🔍 **Bước 3: Gọi Shipping API (Giao Hàng Nhanh - GHN)...**")
            time.sleep(1)
            tracking_code = f"GHN_EXPRESS_{int(time.time())}"
            st.success(f"✅ Đã tự động tạo đơn trên hệ thống GHN API! Mã vận đơn: **{tracking_code}**")

            # 4. NOTIFICATION API
            st.write("🔍 **Bước 4: Gọi Notification API (Zalo ZNS / SMS Service)...**")
            time.sleep(1)
            st.success(f"📲 Đã gửi tin nhắn Zalo/SMS đến {customer_phone}: 'Đơn hàng {tracking_code} đã tạo thành công!'")

            st.balloons()
            st.subheader("🎉 QUY TRÌNH TỰ ĐỘNG HÓA HOÀN TẤT 100%!")
