import streamlit as st # 'Import' kelimesindeki 'I' harfi küçültüldü
import requests

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

API_URL = "https://api.bist-api.com/api/v1"

# API anahtarını buraya yaz
API_KEY = st.secrets.get("API_KEY", "BURAYA_API_KEY_YAZ") # API anahtarı güvenliği için st.secrets kullanıldı, bulamazsa string'i alır

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# --------------------------------------------------
# API'DEN HİSSE VERİSİ
# --------------------------------------------------

def get_stock(symbol):

    symbol = symbol.upper().strip()

    url = f"{API_URL}/stocks/{symbol}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
        return None


# --------------------------------------------------
# TEKNİK GÖSTERGE
# --------------------------------------------------

def get_indicator(symbol, indicator):

    url = f"{API_URL}/indicators/{symbol}/{indicator}"

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


# --------------------------------------------------
# PUANLAMA
# --------------------------------------------------

def calculate_score(data):

    score = 0
    total = 0

    results = []

    # ---------------------------
    # F/K
    # ---------------------------

    pe = data.get("pe")

    if pe is not None:

        total += 1

        if pe < 10:
            score += 1
            results.append(("F/K", pe, "GEÇTİ"))
        else:
            results.append(("F/K", pe, "KALDI"))

    # ---------------------------
    # PD/DD
    # ---------------------------

    pb = data.get("pb")

    if pb is not None:

        total += 1

        if pb < 2:
            score += 1
            results.append(("PD/DD", pb, "GEÇTİ"))
        else:
            results.append(("PD/DD", pb, "KALDI"))

    # ---------------------------
    # PİYASA DEĞERİ
    # ---------------------------

    market_cap = data.get("market_cap")

    if market_cap is not None:

        results.append(
            ("Piyasa Değeri", market_cap, "-")
        )

    return score, total, results


# --------------------------------------------------
# ARAYÜZ
# --------------------------------------------------

st.set_page_config(
    page_title="BIST Hisse Analiz",
    page_icon="📈",
    layout="wide"
)

st.title("📈 BIST Hisse Filtreleme & Analiz")

st.write(
    "Hisse kodunu girerek fiyat, finansal veriler "
    "ve filtreleme sonuçlarını görüntüleyebilirsin."
)

# --------------------------------------------------
# HİSSE ARAMA
# --------------------------------------------------

symbol = st.text_input(
    "Hisse kodu",
    placeholder="Örn: TUPRS, THYAO, ASELS"
)

analyze = st.button(
    "🔎 HİSSEYİ ANALİZ ET",
    use_container_width=True
)

# --------------------------------------------------
# ANALİZ
# --------------------------------------------------

if analyze:

    if not symbol:

        st.warning("Lütfen bir hisse kodu gir.")

    else:

        with st.spinner("Hisse verileri alınıyor..."):

            data = get_stock(symbol)

        if data is None:

            st.error(
                "Hisse bulunamadı veya API verisi alınamadı."
            )

        else:

            # --------------------------------------------------
            # TEMEL BİLGİLER
            # --------------------------------------------------

            st.subheader(
                f"📊 {symbol.upper()} Analizi"
            )

            col1, col2, col3, col4 = st.columns(4)

            price = data.get(
                "current_price",
                data.get("price", "-")
            )

            change = data.get(
                "change_percent",
                data.get("change", "-")
            )

            volume = data.get(
                "volume",
                "-"
            )

            market_cap = data.get(
                "market_cap",
                "-"
            )

            col1.metric(
                "Anlık Fiyat",
                f"{price} TL"
            )

            col2.metric(
                "Değişim",
                f"%{change}"
            )

            col3.metric(
                "Hacim",
                str(volume)
            )

            col4.metric(
                "Piyasa Değeri",
                str(market_cap)
            )

            # --------------------------------------------------
            # FİNANSAL ORANLAR
            # --------------------------------------------------

            st.subheader("📌 Finansal Oranlar")

            pe = data.get("pe", "-")
            pb = data.get("pb", "-")
            eps = data.get("eps", "-")
            beta = data.get("beta", "-")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("F/K", pe)
            c2.metric("PD/DD", pb)
            c3.metric("EPS", eps)
            c4.metric("Beta", beta)

            # --------------------------------------------------
            # PUANLAMA
            # --------------------------------------------------

            score, total, results = calculate_score(data)

            st.subheader("🎯 Filtre Sonucu")

            if total > 0:

                percentage = (
                    score / total
                ) * 100

                st.progress(
                    percentage / 100
                )

                st.metric(
                    "Genel Skor",
                    f"{score}/{total}"
                )

                if percentage >= 80:

                    st.success(
                        "🟢 Hisse kriterlere büyük ölçüde uyuyor."
                    )

                elif percentage >= 50:

                    st.warning(
                        "🟡 Hisse orta seviyede uygun."
                    )

                else:

                    st.error(
                        "🔴 Hisse belirlenen kriterleri karşılamıyor."
                    )

            # --------------------------------------------------
            # KRİTERLER
            # --------------------------------------------------

            st.subheader("🔍 Kriter Detayları")

            for name, value, result in results:

                if result == "GEÇTİ":

                    st.success(
                        f"✅ {name}: {value}"
                    )

                elif result == "KALDI":

                    st.error(
                        f"❌ {name}: {value}"
                    )

                else:

                    st.info(
                        f"ℹ️ {name}: {value}"
                    )

            st.caption(
                "Bu uygulama yatırım tavsiyesi değildir."
            )
