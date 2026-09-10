import streamlit as st
import requests
import hashlib
import hmac
import urllib.parse
import time
import uuid
from datetime import datetime, timedelta
from google import genai


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce Internet Services",
    page_icon="🛍️",
    layout="wide"
)


# ============================================================
# 2. SECRETS
# ============================================================

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

SAFE_BROWSING_API_KEY = st.secrets.get(
    "SAFE_BROWSING_API_KEY", ""
)

ABUSEIPDB_API_KEY = st.secrets.get(
    "ABUSEIPDB_API_KEY", ""
)

VIRUSTOTAL_API_KEY = st.secrets.get(
    "VIRUSTOTAL_API_KEY", ""
)

VNP_TMN_CODE = st.secrets.get(
    "VNP_TMN_CODE", ""
)

VNP_HASH_SECRET = st.secrets.get(
    "VNP_HASH_SECRET", ""
)

VNP_URL = st.secrets.get(
    "VNP_URL",
    "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
)

GHN_TOKEN = st.secrets.get(
    "GHN_TOKEN", ""
)

GHN_SHOP_ID = st.secrets.get(
    "GHN_SHOP_ID", ""
)


# ============================================================
# 3. SESSION STATE
# ============================================================

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content":
            "Xin chào! Tôi là trợ lý AI của cửa hàng. "
            "Bạn muốn tìm sản phẩm nào?"
        }
    ]


if "orders" not in st.session_state:
    st.session_state.orders = {}


# ============================================================
# 4. CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 25px;
}

.box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 5. UTILITY
# ============================================================

def money(value):
    return f"{value:,.0f}".replace(",", ".") + " VNĐ"


def generate_order_id():
    return (
        "ORD"
        + datetime.now().strftime("%Y%m%d%H%M%S")
        + uuid.uuid4().hex[:4].upper()
    )


def normalize_ip(ip):
    return ip.strip()


# ============================================================
# 6. GEMINI
# ============================================================

def gemini_chat(question):

    if not GEMINI_API_KEY:
        return "❌ Chưa cấu hình GEMINI_API_KEY."

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        history = ""

        for message in st.session_state.chat_messages[-8:]:
            history += (
                f"{message['role']}: "
                f"{message['content']}\n"
            )

        prompt = f"""
Bạn là trợ lý bán hàng của một sàn thương mại điện tử.

Hãy:
- Tư vấn sản phẩm.
- So sánh sản phẩm.
- Giải thích ưu nhược điểm.
- Trả lời bằng tiếng Việt.
- Ngắn gọn, dễ hiểu.
- Không tự bịa giá sản phẩm.

Lịch sử:
{history}

Câu hỏi:
{question}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"❌ Gemini API lỗi: {str(e)}"


# ============================================================
# 7. GOOGLE SAFE BROWSING
# ============================================================

def check_safe_browsing(url):

    if not SAFE_BROWSING_API_KEY:
        return {
            "success": False,
            "safe": None,
            "message": "Chưa cấu hình Safe Browsing API Key"
        }

    endpoint = (
        "https://safebrowsing.googleapis.com/"
        "v4/threatMatches:find"
    )

    params = {
        "key": SAFE_BROWSING_API_KEY
    }

    payload = {
        "client": {
            "clientId": "ecommerce-demo",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": [
                "ANY_PLATFORM"
            ],
            "threatEntryTypes": [
                "URL"
            ],
            "threatEntries": [
                {
                    "url": url
                }
            ]
        }
    }

    try:

        response = requests.post(
            endpoint,
            params=params,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            return {
                "success": False,
                "safe": None,
                "message":
                    f"HTTP {response.status_code}: "
                    f"{response.text[:300]}"
            }

        data = response.json()

        matches = data.get("matches", [])

        if matches:

            return {
                "success": True,
                "safe": False,
                "score": 40,
                "message":
                    f"⚠️ Phát hiện {len(matches)} mối đe dọa"
            }

        return {
            "success": True,
            "safe": True,
            "score": 0,
            "message": "✅ URL an toàn"
        }

    except Exception as e:

        return {
            "success": False,
            "safe": None,
            "message": f"Lỗi Safe Browsing: {str(e)}"
        }


# ============================================================
# 8. ABUSEIPDB
# ============================================================

def check_abuse_ip(ip):

    if not ABUSEIPDB_API_KEY:
        return {
            "success": False,
            "score": 0,
            "confidence": None,
            "message": "Chưa cấu hình AbuseIPDB API Key"
        }

    endpoint = (
        "https://api.abuseipdb.com/api/v2/check"
    )

    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": normalize_ip(ip),
        "maxAgeInDays": 90
    }

    try:

        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code != 200:

            return {
                "success": False,
                "score": 0,
                "confidence": None,
                "message":
                    f"HTTP {response.status_code}: "
                    f"{response.text[:300]}"
            }

        data = response.json().get(
            "data",
            {}
        )

        confidence = int(
            data.get(
                "abuseConfidenceScore",
                0
            )
        )

        # Chuyển 0-100 thành tối đa 30 điểm
        risk_score = round(
            confidence * 0.30
        )

        return {
            "success": True,
            "score": risk_score,
            "confidence": confidence,
            "country": data.get("countryCode"),
            "total_reports":
                data.get("totalReports", 0),
            "message":
                "⚠️ IP có dấu hiệu đáng ngờ"
                if confidence >= 50
                else
                "✅ IP có mức rủi ro thấp"
        }

    except Exception as e:

        return {
            "success": False,
            "score": 0,
            "confidence": None,
            "message": f"Lỗi AbuseIPDB: {str(e)}"
        }


# ============================================================
# 9. VIRUSTOTAL URL
# ============================================================

def check_virustotal_url(url):

    if not VIRUSTOTAL_API_KEY:
        return {
            "success": False,
            "score": 0,
            "malicious": 0,
            "suspicious": 0,
            "message": "Chưa cấu hình VirusTotal API Key"
        }

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        # Gửi URL
        response = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=30
        )

        if response.status_code not in [200, 201]:

            return {
                "success": False,
                "score": 0,
                "malicious": 0,
                "suspicious": 0,
                "message":
                    f"HTTP {response.status_code}: "
                    f"{response.text[:300]}"
            }

        analysis_id = response.json()[
            "data"
        ]["id"]

        # Chờ phân tích
        result = None

        for _ in range(10):

            time.sleep(2)

            analysis_response = requests.get(
                f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                headers=headers,
                timeout=30
            )

            if analysis_response.status_code != 200:
                continue

            result = analysis_response.json()

            status = (
                result
                .get("data", {})
                .get("attributes", {})
                .get("status")
            )

            if status == "completed":
                break

        if not result:

            return {
                "success": False,
                "score": 0,
                "malicious": 0,
                "suspicious": 0,
                "message": "Không nhận được kết quả VirusTotal"
            }

        stats = (
            result
            .get("data", {})
            .get("attributes", {})
            .get("stats", {})
        )

        malicious = int(
            stats.get("malicious", 0)
        )

        suspicious = int(
            stats.get("suspicious", 0)
        )

        # Tối đa 30 điểm
        vt_score = min(
            30,
            malicious * 3 + suspicious
        )

        return {
            "success": True,
            "score": vt_score,
            "malicious": malicious,
            "suspicious": suspicious,
            "message":
                "🚨 Phát hiện dấu hiệu độc hại"
                if malicious > 0
                else
                "✅ Không phát hiện mã độc"
        }

    except Exception as e:

        return {
            "success": False,
            "score": 0,
            "malicious": 0,
            "suspicious": 0,
            "message":
                f"Lỗi VirusTotal: {str(e)}"
        }


# ============================================================
# 10. RISK ENGINE
# ============================================================

def calculate_risk(
    safe_result,
    abuse_result,
    vt_result
):

    safe_score = safe_result.get(
        "score", 0
    )

    abuse_score = abuse_result.get(
        "score", 0
    )

    vt_score = vt_result.get(
        "score", 0
    )

    total = (
        safe_score
        + abuse_score
        + vt_score
    )

    total = min(100, total)

    if total >= 70:
        level = "HIGH"

    elif total >= 30:
        level = "MEDIUM"

    else:
        level = "LOW"

    return total, level


# ============================================================
# 11. VNPAY
# ============================================================

import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
import pytz
import requests
import streamlit as st


def sort_dict(data):
    return dict(sorted(data.items(), key=lambda x: x[0]))


def build_vnpay_url(
    order_id, amount, order_info, return_url, client_ip="127.0.0.1"
):
    if not VNP_TMN_CODE:
        raise Exception("Thiếu VNP_TMN_CODE")

    if not VNP_HASH_SECRET:
        raise Exception("Thiếu VNP_HASH_SECRET")

    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(tz)

    create_date = now.strftime("%Y%m%d%H%M%S")
    expire_date = (now + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S")

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNP_TMN_CODE,
        "vnp_Amount": str(int(amount * 100)),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": str(order_id),
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": return_url,
        "vnp_IpAddr": client_ip,
        "vnp_CreateDate": create_date,
        "vnp_ExpireDate": expire_date,
    }

    params = sort_dict(params)

    query_string = urllib.parse.urlencode(
        params, quote_via=urllib.parse.quote_plus
    )

    secure_hash = hmac.new(
        VNP_HASH_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    payment_url = f"{VNP_URL}?{query_string}&vnp_SecureHash={secure_hash}"

    return payment_url


# ============================================================
# 12. VNPAY VERIFY RETURN
# ============================================================


def verify_vnpay_response(query_params):
    if hasattr(query_params, "to_dict"):
        query_params = query_params.to_dict()
    else:
        query_params = dict(query_params)

    data = {}

    for key, value in query_params.items():
        if key.startswith("vnp_"):
            if isinstance(value, list):
                value = value[0] if len(value) > 0 else ""

            if value is not None and str(value) != "":
                data[key] = str(value)

    received_hash = data.pop("vnp_SecureHash", "")
    data.pop("vnp_SecureHashType", None)

    data = sort_dict(data)

    query_string = urllib.parse.urlencode(
        data, quote_via=urllib.parse.quote_plus
    )

    calculated_hash = hmac.new(
        VNP_HASH_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    valid = hmac.compare_digest(
        calculated_hash.lower(), str(received_hash).lower()
    )

    return valid, data


# ============================================================
# 13. GHN CREATE ORDER (ĐÃ SỬA LỖI COD & ORDER CODE)
# ============================================================


def create_ghn_order(
    client_order_code,  # Khóa chính để đồng bộ với VNPay (order_id)
    customer_name,
    customer_phone,
    customer_address,
    ward_name,
    district_name,
    province_name,
    product_name,
    amount,
    weight,
    is_paid=True,  # Đánh dấu đơn hàng đã thanh toán VNPay hay chưa
):
    if not GHN_TOKEN:
        return {"success": False, "message": "Thiếu GHN_TOKEN"}

    if not GHN_SHOP_ID:
        return {"success": False, "message": "Thiếu GHN_SHOP_ID"}

    endpoint = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create"

    headers = {
        "Content-Type": "application/json",
        "Token": GHN_TOKEN,
        "ShopId": str(GHN_SHOP_ID),
    }

    # Đã thanh toán VNPay thì COD = 0, ngược lại thì thu COD
    cod_amount = 0 if is_paid else int(amount)

    payload = {
        "payment_type_id": 1,  # 1: Bên gửi trả phí dịch vụ vận chuyển
        "note": f"Đơn hàng VNPay #{client_order_code}",
        "required_note": "KHONGCHOXEMHANG",
        "client_order_code": str(client_order_code),
        # THÔNG TIN SHOP
        "from_name": "E-Commerce Shop",
        "from_phone": "0900000000",
        "from_address": "39 Nguyen Thi Thap",
        "from_ward_name": "Phuong Tan Phu",
        "from_district_name": "Quan 7",
        "from_province_name": "Ho Chi Minh",
        # THÔNG TIN KHÁCH HÀNG
        "to_name": customer_name,
        "to_phone": customer_phone,
        "to_address": customer_address,
        "to_ward_name": ward_name,
        "to_district_name": district_name,
        "to_province_name": province_name,
        # THÔNG TIN HÀNG HÓA
        "cod_amount": cod_amount,
        "content": product_name,
        "weight": int(weight),
        "length": 20,
        "width": 15,
        "height": 10,
        "service_type_id": 2,
    }

    try:
        response = requests.post(
            endpoint, headers=headers, json=payload, timeout=30
        )
        data = response.json()

        if response.status_code == 200 and data.get("code") == 200:
            result = data.get("data", {})
            return {
                "success": True,
                "order_code": result.get("order_code"),
                "total_fee": result.get("total_fee"),
                "expected_delivery_time": result.get("expected_delivery_time"),
                "message": data.get("message", "Success"),
            }

        return {
            "success": False,
            "message": data.get("message", response.text),
        }

    except Exception as e:
        return {"success": False, "message": f"Lỗi GHN: {str(e)}"}


# ============================================================
# 14. LOGIC TỰ ĐỘNG HỨNG VNPAY & TẠO ĐƠN GHN TRÊN STREAMLIT
# ============================================================


def process_vnpay_return_and_ghn():
    query_params = dict(st.query_params)

    # Khi VNPay trả kết quả về URL
    if "vnp_ResponseCode" in query_params:
        is_valid, vnp_data = verify_vnpay_response(query_params)

        if is_valid:
            response_code = vnp_data.get("vnp_ResponseCode")
            order_id = vnp_data.get("vnp_TxnRef")

            if response_code == "00":
                st.success(
                    f"🎉 Thanh toán VNPay thành công cho đơn hàng `{order_id}`!"
                )

                # Lấy dữ liệu đơn hàng đã lưu trong session trước khi đi thanh toán
                pending_order = st.session_state.get(f"pending_order_{order_id}")

                if pending_order:
                    if not pending_order.get("ghn_created"):
                        with st.spinner("Đang tự động đẩy đơn sang GHN..."):
                            ghn_res = create_ghn_order(
                                client_order_code=order_id,
                                customer_name=pending_order["customer_name"],
                                customer_phone=pending_order["customer_phone"],
                                customer_address=pending_order[
                                    "customer_address"
                                ],
                                ward_name=pending_order["ward_name"],
                                district_name=pending_order["district_name"],
                                province_name=pending_order["province_name"],
                                product_name=pending_order["product_name"],
                                amount=pending_order["amount"],
                                weight=pending_order["weight"],
                                is_paid=True,  # Đơn đã thanh toán thành công
                            )

                            if ghn_res["success"]:
                                st.session_state[f"pending_order_{order_id}"][
                                    "ghn_created"
                                ] = True
                                st.session_state[f"pending_order_{order_id}"][
                                    "ghn_order_code"
                                ] = ghn_res["order_code"]
                                st.balloons()
                                st.success(
                                    f"✅ Đã tạo đơn GHN thành công! Mã vận đơn GHN: **{ghn_res['order_code']}**"
                                )
                            else:
                                st.error(
                                    f"❌ Lỗi tạo đơn GHN: {ghn_res['message']}"
                                )
                    else:
                        st.info(
                            f"Đơn hàng đã được tạo GHN trước đó. Mã vận đơn: **{pending_order.get('ghn_order_code')}**"
                        )
                else:
                    st.warning(
                        "Không tìm thấy thông tin chi tiết đơn hàng tạm trong Session."
                    )
            else:
                st.error(
                    f"Thanh toán không thành công. Mã lỗi VNPay: {response_code}"
                )
        else:
            st.error("Chữ ký VNPay không hợp lệ!")

     





# ============================================================
# 14. HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🛍️ SÀN THƯƠNG MẠI ĐIỆN TỬ'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI + Security 3 lớp + Risk Engine + VNPay + GHN'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 15. SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ SYSTEM STATUS")

    st.write(
        "🤖 Gemini:",
        "🟢"
        if GEMINI_API_KEY
        else "🔴"
    )

    st.write(
        "🌐 Safe Browsing:",
        "🟢"
        if SAFE_BROWSING_API_KEY
        else "🔴"
    )

    st.write(
        "📍 AbuseIPDB:",
        "🟢"
        if ABUSEIPDB_API_KEY
        else "🔴"
    )

    st.write(
        "🛡️ VirusTotal:",
        "🟢"
        if VIRUSTOTAL_API_KEY
        else "🔴"
    )

    st.write(
        "💳 VNPay:",
        "🟢"
        if VNP_TMN_CODE
        and VNP_HASH_SECRET
        else "🔴"
    )

    st.write(
        "🚚 GHN:",
        "🟢"
        if GHN_TOKEN
        and GHN_SHOP_ID
        else "🔴"
    )

    st.divider()

    st.markdown("### 📊 Risk Policy")

    st.write("🟢 0–29 → LOW")
    st.write("🟡 30–69 → MEDIUM")
    st.write("🔴 70–100 → HIGH")


# ============================================================
# 16. TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "💬 Gemini AI",
        "🚀 Đặt hàng & Security",
        "📋 Lịch sử đơn hàng"
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.subheader(
        "🤖 Gemini AI - Tư vấn khách hàng"
    )

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Nhập câu hỏi..."
    )

    if prompt:

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "Gemini đang tư vấn..."
            ):

                answer = gemini_chat(
                    prompt
                )

            st.markdown(answer)

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.subheader(
        "🚀 Đặt hàng & kiểm soát rủi ro"
    )

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    st.markdown(
        "### 📦 1. Thông tin đơn hàng"
    )

    col1, col2 = st.columns(2)

    with col1:

        product_name = st.text_input(
            "Tên sản phẩm",
            "Giày Sneaker Thể Thao Pro"
        )

        price_text = st.text_input(
            "Giá sản phẩm (VNĐ)",
            "1200000"
        )

    with col2:

        customer_name = st.text_input(
            "Họ tên khách hàng",
            "Đỗ Trung Kiên"
        )

        customer_phone = st.text_input(
            "Số điện thoại",
            "0900000000"
        )

        customer_address = st.text_input(
            "Địa chỉ",
            "39 Nguyen Thi Thap"
        )

    col3, col4, col5 = st.columns(3)

    with col3:

        province_name = st.text_input(
            "Tỉnh / Thành phố",
            "Ho Chi Minh"
        )

    with col4:

        district_name = st.text_input(
            "Quận / Huyện",
            "Quan 7"
        )

    with col5:

        ward_name = st.text_input(
            "Phường / Xã",
            "Phuong Tan Phu"
        )

    try:

        price = float(
            price_text
            .replace(".", "")
            .replace(",", "")
            .replace(" ", "")
        )

    except:

        price = 0

    st.info(
        f"💰 Giá trị đơn hàng: "
        f"**{money(price)}**"
    )

    # --------------------------------------------------------
    # SECURITY INPUT
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "### 🛡️ 2. Security Check"
    )

    url_to_check = st.text_input(
        "🌐 URL cần kiểm tra",
        "https://example.com"
    )

    ip_to_check = st.text_input(
        "📍 IP cần kiểm tra",
        "8.8.8.8"
    )

    uploaded_file = st.file_uploader(
        "🛡️ File cần kiểm tra bằng VirusTotal",
        type=None
    )

    st.caption(
        "Bản này hiện dùng VirusTotal để kiểm tra URL. "
        "File upload sẽ được bổ sung ở bước tiếp theo nếu cần."
    )

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    if st.button(
        "🔥 KÍCH HOẠT SECURITY + RISK ENGINE",
        type="primary",
        use_container_width=True
    ):

        if price <= 0:

            st.error(
                "❌ Giá sản phẩm không hợp lệ."
            )

            st.stop()

        if not customer_phone:

            st.error(
                "❌ Vui lòng nhập số điện thoại."
            )

            st.stop()

        order_id = generate_order_id()

        st.markdown(
            f"## 🆔 Order ID: `{order_id}`"
        )

        progress = st.progress(0)

        # ====================================================
        # SAFE BROWSING
        # ====================================================

        with st.status(
            "🌐 Google Safe Browsing...",
            expanded=True
        ) as status:

            safe_result = check_safe_browsing(
                url_to_check
            )

            if safe_result["success"]:

                st.write(
                    safe_result["message"]
                )

            else:

                st.error(
                    safe_result["message"]
                )

            status.update(
                label="🌐 Safe Browsing hoàn tất",
                state="complete"
            )

        progress.progress(25)

        # ====================================================
        # ABUSEIPDB
        # ====================================================

        with st.status(
            "📍 AbuseIPDB...",
            expanded=True
        ) as status:

            abuse_result = check_abuse_ip(
                ip_to_check
            )

            st.write(
                abuse_result["message"]
            )

            if abuse_result.get(
                "confidence"
            ) is not None:

                st.write(
                    "Abuse Confidence Score: "
                    f"**{abuse_result['confidence']}%**"
                )

                st.write(
                    "Reports: "
                    f"**{abuse_result.get('total_reports', 0)}**"
                )

            status.update(
                label="📍 AbuseIPDB hoàn tất",
                state="complete"
            )

        progress.progress(50)

        # ====================================================
        # VIRUSTOTAL
        # ====================================================

        with st.status(
            "🛡️ VirusTotal...",
            expanded=True
        ) as status:

            vt_result = check_virustotal_url(
                url_to_check
            )

            st.write(
                vt_result["message"]
            )

            if vt_result["success"]:

                st.write(
                    f"Malicious: "
                    f"**{vt_result['malicious']}**"
                )

                st.write(
                    f"Suspicious: "
                    f"**{vt_result['suspicious']}**"
                )

            status.update(
                label="🛡️ VirusTotal hoàn tất",
                state="complete"
            )

        progress.progress(75)

        # ====================================================
        # RISK ENGINE
        # ====================================================

        risk_score, risk_level = calculate_risk(
            safe_result,
            abuse_result,
            vt_result
        )

        st.markdown(
            "### 📊 3. RISK ENGINE"
        )

        r1, r2, r3, r4 = st.columns(4)

        with r1:

            st.metric(
                "Safe Browsing",
                f"+{safe_result.get('score', 0)}"
            )

        with r2:

            st.metric(
                "AbuseIPDB",
                f"+{abuse_result.get('score', 0)}"
            )

        with r3:

            st.metric(
                "VirusTotal",
                f"+{vt_result.get('score', 0)}"
            )

        with r4:

            st.metric(
                "RISK SCORE",
                f"{risk_score}/100"
            )

        st.progress(
            risk_score / 100
        )

        # ====================================================
        # HIGH
        # ====================================================

        if risk_level == "HIGH":

            st.error(
                f"🔴 HIGH RISK — {risk_score}/100"
            )

            st.error(
                "⛔ ĐƠN HÀNG BỊ CHẶN."
            )

            st.warning(
                "Hệ thống phát hiện mức rủi ro cao. "
                "Không chuyển sang VNPay."
            )

            status = "BLOCKED"

        # ====================================================
        # MEDIUM
        # ====================================================

        elif risk_level == "MEDIUM":

            st.warning(
                f"🟡 MEDIUM RISK — {risk_score}/100"
            )

            st.info(
                "Yêu cầu xác minh OTP trước khi thanh toán."
            )

            otp = st.text_input(
                "🔐 OTP Demo",
                type="password"
            )

            if st.button(
                "Xác thực OTP"
            ):

                if otp != "123456":

                    st.error(
                        "❌ OTP không chính xác."
                    )

                    status = "BLOCKED"

                else:

                    st.success(
                        "✅ OTP xác minh thành công."
                    )

                    status = "OTP_VERIFIED"

            else:

                status = "WAITING_OTP"

        # ====================================================
        # LOW
        # ====================================================

        else:

            st.success(
                f"🟢 LOW RISK — {risk_score}/100"
            )

            st.success(
                "Có thể tiếp tục thanh toán VNPay."
            )

            status = "APPROVED"


        # ====================================================
        # SAVE ORDER
        # ====================================================

        st.session_state.orders[
            order_id
        ] = {

            "order_id":
                order_id,

            "created_at":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),

            "customer":
                customer_name,

            "phone":
                customer_phone,

            "product":
                product_name,

            "amount":
                price,

            "risk_score":
                risk_score,

            "risk_level":
                risk_level,

            "status":
                status
        }


        # ====================================================
        # PAYMENT
        # ====================================================

        if status in [
            "APPROVED",
            "OTP_VERIFIED"
        ]:

            st.divider()

            st.markdown(
                "### 💳 4. VNPay Sandbox"
            )

            # Streamlit URL hiện tại
            return_url = (
                "https://"
                + st.context.headers.get(
                    "Host",
                    ""
                )
            )

            if return_url.endswith(".streamlit.app"):

                return_url = (
                    "https://"
                    + st.context.headers.get(
                        "Host"
                    )
                )

            try:

                payment_url = build_vnpay_url(
                    order_id,
                    price,
                    f"Thanh toan don hang {order_id}",
                    return_url
                )

                st.success(
                    "✅ Đã tạo URL thanh toán VNPay."
                )

                st.link_button(
                    "💳 THANH TOÁN QUA VNPAY",
                    payment_url,
                    use_container_width=True
                )

                st.info(
                    "Sau khi thanh toán, VNPay sẽ "
                    "redirect về Return URL."
                )

            except Exception as e:

                st.error(
                    f"❌ Không tạo được VNPay URL: {e}"
                )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.subheader(
        "📋 Lịch sử đơn hàng"
    )

    if not st.session_state.orders:

        st.info(
            "Chưa có đơn hàng."
        )

    else:

        for order_id, order in reversed(
            list(
                st.session_state.orders.items()
            )
        ):

            with st.expander(
                f"{order_id} — "
                f"{order['risk_level']} — "
                f"{money(order['amount'])}"
            ):

                st.write(
                    "👤 Khách hàng:",
                    order["customer"]
                )

                st.write(
                    "📦 Sản phẩm:",
                    order["product"]
                )

                st.write(
                    "💰 Giá:",
                    money(order["amount"])
                )

                st.write(
                    "📊 Risk Score:",
                    f"{order['risk_score']}/100"
                )

                st.write(
                    "🚦 Risk Level:",
                    order["risk_level"]
                )

                st.write(
                    "📌 Status:",
                    order["status"]
                )

                st.write(
                    "🕒 Thời gian:",
                    order["created_at"]
                )
