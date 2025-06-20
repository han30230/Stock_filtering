import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="52주 신고가 종목 필터링")

# 💄 CSS 삽입
st.markdown(
    """
    <style>
        .dataframe th, .dataframe td {
            text-align: center !important;
            font-size: 14px !important;
        }
        .stDataFrame {
            background-color: white;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 데이터 로드
df = pd.read_excel("52week_high_combined_with_summary.xlsx")
original_df = df.copy()

# 컬럼 설정
price_column = '종가' if '종가' in df.columns else '현재가'
eps_column = '최근 1년 주당순이익 (TTM EPS)' if '최근 1년 주당순이익 (TTM EPS)' in df.columns else None
peg_column = 'PEG (PER/EPS)' if 'PEG (PER/EPS)' in df.columns else None

# 🎛️ 사이드바: 필터링 UI
st.sidebar.title("🎛️ 필터 옵션")
apply_filter = st.sidebar.checkbox("🔎 필터 적용", value=False)

filtered_df = df.copy()

if apply_filter:
    # 📉 주가 필터
    st.sidebar.markdown("### 💲 주가 범위")
    if price_column in df.columns:
        numeric_prices = pd.to_numeric(df[price_column], errors='coerce')
        price_min, price_max = int(numeric_prices.min()), int(numeric_prices.max())
        price_slider = st.sidebar.slider("주가 슬라이더", price_min, price_max, (price_min, price_max), step=10)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            price_input_min = st.number_input("최소 주가", value=price_slider[0], step=10)
        with col2:
            price_input_max = st.number_input("최대 주가", value=price_slider[1], step=10)
        filtered_df = filtered_df[numeric_prices.between(price_input_min, price_input_max)]

    # EPS 필터
    st.sidebar.markdown("### 📘 EPS")
    if eps_column and eps_column in df.columns:
        eps_numeric = pd.to_numeric(df[eps_column], errors='coerce')
        eps_min, eps_max = float(eps_numeric.min()), float(eps_numeric.max())
        eps_slider = st.sidebar.slider("EPS 슬라이더", eps_min, eps_max, (eps_min, eps_max), step=0.5)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            eps_input_min = st.number_input("최소 EPS", value=eps_slider[0], step=0.5)
        with col2:
            eps_input_max = st.number_input("최대 EPS", value=eps_slider[1], step=0.5)
        filtered_df = filtered_df[eps_numeric.between(eps_input_min, eps_input_max)]

    # PEG 필터
    st.sidebar.markdown("### 🧮 PEG")
    if peg_column and peg_column in df.columns:
        peg_numeric = pd.to_numeric(df[peg_column], errors='coerce')
        peg_min, peg_max = float(peg_numeric.min()), float(peg_numeric.max())
        peg_slider = st.sidebar.slider("PEG 슬라이더", peg_min, peg_max, (peg_min, peg_max), step=0.1)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            peg_input_min = st.number_input("최소 PEG", value=peg_slider[0], step=0.1)
        with col2:
            peg_input_max = st.number_input("최대 PEG", value=peg_slider[1], step=0.1)
        filtered_df = filtered_df[peg_numeric.between(peg_input_min, peg_input_max)]

    # 성장률 계산
    def calc_growth(current, previous):
        try:
            current, previous = float(current), float(previous)
            if previous == 0:
                return None
            return ((current - previous) / abs(previous)) * 100
        except:
            return None

    filtered_df['1→2Q 매출증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('1분기 총매출'), x.get('2분기 총매출')), axis=1)
    filtered_df['2→3Q 매출증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('2분기 총매출'), x.get('3분기 총매출')), axis=1)

    st.sidebar.markdown("### 📊 매출 증가율")
    for col in ['1→2Q 매출증가율', '2→3Q 매출증가율']:
        if col in filtered_df.columns:
            g_min, g_max = float(filtered_df[col].min()), float(filtered_df[col].max())
            g_slider = st.sidebar.slider(f"{col} 슬라이더", g_min, g_max, (g_min, g_max), step=1.0)
            col1, col2 = st.sidebar.columns(2)
            with col1:
                g_input_min = st.number_input(f"{col} 최소", value=g_slider[0], step=1.0)
            with col2:
                g_input_max = st.number_input(f"{col} 최대", value=g_slider[1], step=1.0)
            filtered_df = filtered_df[filtered_df[col].between(g_input_min, g_input_max)]

    # 순이익 증가율
    filtered_df['1→2Q 순이익증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('1분기 순이익'), x.get('2분기 순이익')), axis=1)
    st.sidebar.markdown("### 💰 순이익 증가율")
    pg_min, pg_max = float(filtered_df['1→2Q 순이익증가율'].min()), float(filtered_df['1→2Q 순이익증가율'].max())
    pg_slider = st.sidebar.slider("1→2Q 순이익증가율 슬라이더", pg_min, pg_max, (pg_min, pg_max), step=1.0)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        pg_input_min = st.number_input("최소 순이익 증가율", value=pg_slider[0], step=1.0)
    with col2:
        pg_input_max = st.number_input("최대 순이익 증가율", value=pg_slider[1], step=1.0)
    filtered_df = filtered_df[filtered_df['1→2Q 순이익증가율'].between(pg_input_min, pg_input_max)]

# 💡 본문 출력
st.title("📈 미국주식 52주 신고가 종목 리스트")
st.markdown(f"**총 종목 수:** `{len(original_df)}` | **필터링 후:** `{len(filtered_df)}`")

if apply_filter:
    st.info("필터가 적용되었습니다. 사이드바에서 조건을 변경할 수 있습니다.")

st.dataframe(filtered_df, use_container_width=True, height=800)
st.markdown("---")
st.caption("📊 데이터 출처:  Investing.com의 52주 최고가 리스트 및 YFinance API를 통한 실시간 시세 정보")
