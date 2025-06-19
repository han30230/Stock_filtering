import streamlit as st
import pandas as pd

# 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# 엑셀 파일 읽기
df = pd.read_excel("52week_high_combined.xlsx")

# 컬럼 확인 후 이름 정리 (예: 종가 컬럼 존재 여부)
price_column = '종가' if '종가' in df.columns else '현재가'
eps_column = 'EPS' if 'EPS' in df.columns else None  # EPS 없을 수 있음

# ----- 사이드바 필터링 -----
st.sidebar.header("🔍 필터링 옵션")

# 업종 필터링
if '업종' in df.columns:
    industry_options = df['업종'].dropna().unique()
    selected_industries = st.sidebar.multiselect("업종 선택", sorted(industry_options), default=industry_options)
    df = df[df['업종'].isin(selected_industries)]

# PER 필터링
if 'PER' in df.columns:
    min_per, max_per = float(df['PER'].min()), float(df['PER'].max())
    per_range = st.sidebar.slider("PER 범위", min_value=0.0, max_value=max_per, value=(min_per, max_per))
    df = df[df['PER'].between(per_range[0], per_range[1])]

# 종가 10달러 이상 필터링
if price_column in df.columns:
    df = df[pd.to_numeric(df[price_column], errors='coerce') >= 10]

# EPS 기반 적자 기업 제외 (가능한 경우만)
if eps_column and eps_column in df.columns:
    df = df[pd.to_numeric(df[eps_column], errors='coerce') > 0]
# 주가 필터링 (사이드바에서 직접 설정)
if price_column in df.columns:
    numeric_prices = pd.to_numeric(df[price_column], errors='coerce')
    min_price = 0.0
    max_price = float(numeric_prices.max())

    st.sidebar.markdown("**주가 범위 (달러)**")

    price_slider = st.sidebar.slider(
        "슬라이더로 주가 범위 선택",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=0.1
    )

    input_min_price = st.sidebar.number_input(
        "최소 주가 입력", min_value=min_price, max_value=max_price, value=price_slider[0], step=0.1
    )
    input_max_price = st.sidebar.number_input(
        "최대 주가 입력", min_value=min_price, max_value=max_price, value=price_slider[1], step=0.1
    )

    effective_min = max(input_min_price, price_slider[0])
    effective_max = min(input_max_price, price_slider[1])

    df = df[numeric_prices.between(effective_min, effective_max)]

# EPS 필터링 (EPS 컬럼이 있는 경우)
if eps_column and eps_column in df.columns:
    min_eps = float(pd.to_numeric(df[eps_column], errors='coerce').min())
    max_eps = float(pd.to_numeric(df[eps_column], errors='coerce').max())
    eps_range = st.sidebar.slider("EPS 범위", min_value=min_eps, max_value=max_eps, value=(0.01, max_eps))
    df = df[pd.to_numeric(df[eps_column], errors='coerce').between(eps_range[0], eps_range[1])]

# ----- 메인 콘텐츠 -----
st.title("📈 미국주식 52주 신고가 종목 리스트")

with st.container():
    st.markdown(
        """
        <style>
        .centered-table {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="centered-table">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=800)
    st.markdown('</div>', unsafe_allow_html=True)
