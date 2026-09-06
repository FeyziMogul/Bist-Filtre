import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="BIST Hisse Filtresi",
    page_icon="📈",
    layout="wide"
)

st.title("📈 BIST Hisse Filtreleme Uygulaması")

dosya = st.file_uploader(
    "Hisse verilerini yükle",
    type=["csv", "xlsx"]
)

if dosya is not None:
    try:
        if dosya.name.endswith(".csv"):
            df = pd.read_csv(dosya)
        else:
            df = pd.read_excel(dosya)
    except Exception as e:
        st.error(f"Dosya okunurken bir hata oluştu: {e}")
        st.stop()

    st.sidebar.header("🔎 Filtreler")

    hedef_kolonlar = [
        "Fiyat", "FK", "PD/DD", "FD/FAVÖK", "Temettu",
        "ROE", "ROIC", "Ciro Buyume", "Kar Buyume", "Borç/Ozsermaye"
    ]

    mevcut = [x for x in hedef_kolonlar if x in df.columns]

    # Veri tiplerini sayısal tipe dönüştürme (string/virgül hatalarına karşı)
    for col in mevcut:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.replace(",", ".").str.replace("%", "")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    filtreler = {}

    for kolon in mevcut:
        seri = df[kolon].dropna()

        # Sütun tamamen boşsa atla
        if seri.empty:
            continue

        min_val = float(seri.min())
        max_val = float(seri.max())

        # Min ve Max eşitse slider yerine sabit bilgi ver veya ufak pay ekle
        if min_val == max_val:
            st.sidebar.caption(f"*{kolon}*: Sabit Değer ({min_val})")
            continue

        filtreler[kolon] = st.sidebar.slider(
            label=kolon,
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=(max_val - min_val) / 100 if max_val != min_val else 0.1
        )

    # NaN değerleri korumak isteyip istemediğini sor
    nan_dahil_et = st.sidebar.checkbox("Eksik (NaN) Verili Hisseleri Koru", value=False)

    # Filtreleme mantığı
    sonuc = df.copy()
    for kolon, aralik in filtreler.items():
        kriter = (sonuc[kolon] >= aralik[0]) & (sonuc[kolon] <= aralik[1])
        if nan_dahil_et:
            kriter = kriter | sonuc[kolon].isna()
        sonuc = sonuc[kriter]

    st.subheader(f"📊 {len(sonuc)} hisse bulundu")

    # Sonuç ekranı
    st.dataframe(
        sonuc,
        use_container_width=True,
        hide_index=True
    )

    # İndirme Butonu
    csv_cikti = sonuc.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Filtrelenmiş Listeyi İndir (CSV)",
        data=csv_cikti,
        file_name="filtrelenmis_hisseler.csv",
        mime="text/csv"
    )

else:
    st.info("Başlamak için hisse verilerini CSV veya Excel dosyası olarak yükle.")
    st.markdown("""
    ### Örnek Veri Formatı
    Yükleyeceğiniz tabloda şu sütun isimlerinin yer alması filtrenin otomatik algılamasını sağlar:
    * Hisse, Fiyat, FK, PD/DD, FD/FAVÖK
    * Temettu, ROE, ROIC, Ciro Buyume, Kar Buyume, Borç/Ozsermaye
    """)