import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="52주 신고가 종목 필터링")

# 💄 테이블 시각화 개선용 CSS 삽입
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

# 원본 데이터 로드
df = pd.read_excel("52week_high_combined_with_summary.xlsx")
original_df = df.copy()

# 컬럼 지정
price_column = '종가' if '종가' in df.columns else '현재가'
eps_column = '최근 1년 주당순이익 (TTM EPS)' if '최근 1년 주당순이익 (TTM EPS)' in df.columns else None
peg_column = 'PEG (PER/EPS)' if 'PEG (PER/EPS)' in df.columns else None

# 🎛️ 사이드바: 필터링 UI
st.sidebar.title("🎛️ 필터 옵션")
apply_filter = st.sidebar.checkbox("🔎 필터 적용", value=False)

filtered_df = df.copy()

if apply_filter:


    st.sidebar.markdown("### 💲 주가 범위")
    if price_column in df.columns:
        numeric_prices = pd.to_numeric(df[price_column], errors='coerce')
        price_min, price_max = numeric_prices.min(), numeric_prices.max()
        price_min = round(float(price_min), -1)
        price_max = round(float(price_max), -1)
        price_range = st.sidebar.slider("주가 범위", min_value=price_min, max_value=price_max, value=(price_min, price_max))
        filtered_df = filtered_df[numeric_prices.between(price_range[0], price_range[1])]

    st.sidebar.markdown("### 📘 EPS")
    if eps_column and eps_column in df.columns:
        eps_numeric = pd.to_numeric(df[eps_column], errors='coerce')
        eps_min, eps_max = eps_numeric.min(), eps_numeric.max()
        if pd.notna(eps_min) and pd.notna(eps_max):
            eps_min = round(float(eps_min), 1)
            eps_max = round(float(eps_max), 1)
            eps_range = st.sidebar.slider("EPS 범위", min_value=eps_min, max_value=eps_max, value=(eps_min, eps_max))
            filtered_df = filtered_df[eps_numeric.between(eps_range[0], eps_range[1])]

    st.sidebar.markdown("### 🧮 PEG")
    if peg_column and peg_column in df.columns:
        peg_numeric = pd.to_numeric(df[peg_column], errors='coerce')
        peg_min, peg_max = peg_numeric.min(), peg_numeric.max()
        if pd.notna(peg_min) and pd.notna(peg_max):
            peg_min = round(float(peg_min), 2)
            peg_max = round(float(peg_max), 2)
            peg_range = st.sidebar.slider("PEG 범위", min_value=peg_min, max_value=peg_max, value=(peg_min, peg_max))
            filtered_df = filtered_df[peg_numeric.between(peg_range[0], peg_range[1])]

    # 성장률 계산 함수
    def calc_growth(current, previous):
        try:
            current, previous = float(current), float(previous)
            if previous == 0:
                return None
            return ((current - previous) / abs(previous)) * 100
        except:
            return None

    # 매출 증가율 계산
    filtered_df['1→2Q 매출증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('1분기 총매출'), x.get('2분기 총매출')), axis=1)
    filtered_df['2→3Q 매출증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('2분기 총매출'), x.get('3분기 총매출')), axis=1)

    st.sidebar.markdown("### 📊 매출 증가율")
    for col in ['1→2Q 매출증가율', '2→3Q 매출증가율']:
        if col in filtered_df.columns:
            min_g, max_g = filtered_df[col].min(), filtered_df[col].max()
            if pd.notna(min_g) and pd.notna(max_g):
                min_g = round(min_g, 1)
                max_g = round(max_g, 1)
                growth_range = st.sidebar.slider(f"{col} (%)", min_value=min_g, max_value=max_g, value=(min_g, max_g))
                filtered_df = filtered_df[filtered_df[col].between(growth_range[0], growth_range[1])]

    # 순이익 증가율
    filtered_df['1→2Q 순이익증가율'] = filtered_df.apply(lambda x: calc_growth(x.get('1분기 순이익'), x.get('2분기 순이익')), axis=1)
    st.sidebar.markdown("### 💰 순이익 증가율")
    min_pg, max_pg = filtered_df['1→2Q 순이익증가율'].min(), filtered_df['1→2Q 순이익증가율'].max()
    if pd.notna(min_pg) and pd.notna(max_pg):
        min_pg = round(min_pg, 1)
        max_pg = round(max_pg, 1)
        profit_growth_range = st.sidebar.slider("1→2Q 순이익증가율 (%)", min_value=min_pg, max_value=max_pg, value=(min_pg, max_pg))
        filtered_df = filtered_df[filtered_df['1→2Q 순이익증가율'].between(profit_growth_range[0], profit_growth_range[1])]



# 💡 본문 출력
st.title("📈 미국주식 52주 신고가 종목 리스트")
st.markdown(f"**총 종목 수:** `{len(original_df)}` | **필터링 후:** `{len(filtered_df)}`")

if apply_filter:
    st.info("필터가 적용되었습니다. 사이드바에서 조건을 변경할 수 있습니다.")

# 📋 표 출력
st.dataframe(filtered_df, use_container_width=True, height=800)

# 하단 정보
st.markdown("---")
st.caption("📊 데이터 출처:  Investing.com의 52주 최고가 리스트 및 YFinance API를 통한 실시간 시세 정보")
