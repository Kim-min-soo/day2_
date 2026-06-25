import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# ── 페이지 설정 ────────────────────────────────────────────────────
st.set_page_config(page_title="주문·리뷰 통합 대시보드", layout="wide", page_icon="📊")

# ── 전역 CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── 전역 텍스트 색상 ── */
html, body, [class*="css"], .stApp, .main, .block-container,
p, span, div, li, label, h1, h2, h3, h4, h5, h6,
[data-testid="stText"], [data-testid="stMarkdown"],
[data-testid="stCaptionContainer"] {
    color: #1e1e2e !important;
}
/* Streamlit 기본 위젯 텍스트 */
.stSelectbox label, .stMultiSelect label,
.stFileUploader label, .stCheckbox label,
.stRadio label, .stSlider label,
.stTextInput label, .stNumberInput label,
[data-testid="stWidgetLabel"] { color: #1e1e2e !important; }
/* 선택 입력 내부 텍스트 */
[data-baseweb="select"] [data-testid="stMarkdown"],
[data-baseweb="input"] { color: #1e1e2e !important; }
/* info / warning / success 배너 */
[data-testid="stAlert"] p,
[data-testid="stAlert"] { color: #1e1e2e !important; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4ff 0%, #fafbff 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: #ffffff;
    color: #1e1e2e;
}
/* 사이드바 일반 텍스트 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] label {
    color: #1e1e2e !important;
}
/* 멀티셀렉트 선택 태그 텍스트는 흰색 유지 */
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-baseweb="tag"] span {
    color: #ffffff !important;
}
/* 파일 업로더 드래그 영역: 배경을 밝게, 텍스트를 어둡게 */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #f0f4ff;
    border-radius: 10px;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #1e1e2e !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: #f0f4ff !important;
    border: 2px dashed #4f6ef7 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
    color: #1e1e2e !important;
}
/* Browse files 버튼 텍스트 */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
    background-color: #4f6ef7 !important;
    border: none !important;
}
[data-testid="stSidebar"] hr {
    border-color: #e0e0e0;
}
.block-container { padding-top: 2rem; padding-bottom: 3rem; }

.hero-card {
    background: linear-gradient(120deg, #4f6ef7 0%, #7c3aed 100%);
    border-radius: 18px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.hero-card h1 { margin: 0 0 .25rem 0; font-size: 2rem; font-weight: 700; color: white !important; }
.hero-card p  { margin: 0; opacity: .9; font-size: .95rem; color: white !important; }

.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    box-shadow: 0 2px 12px rgba(79,110,247,.10);
    border-left: 5px solid #4f6ef7;
}
.kpi-label {
    font-size: .8rem; color: #555 !important; font-weight: 600;
    text-transform: uppercase; letter-spacing: .05em; margin-bottom: .3rem;
}
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #1e1e2e !important; line-height: 1; }
.kpi-sub   { font-size: .8rem; color: #4f6ef7 !important; margin-top: .3rem; }

.section-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    box-shadow: 0 2px 12px rgba(79,110,247,.08);
    margin-bottom: 1.2rem;
}
.section-title {
    font-size: 1rem; font-weight: 700; color: #1e1e2e !important;
    margin-bottom: 1rem; display: flex; align-items: center; gap: .4rem;
}
[data-baseweb="tag"] { background-color: #4f6ef7 !important; }
[data-testid="stDataFrame"] thead th {
    background-color: #f0f4ff !important;
    color: #4f6ef7 !important;
    font-weight: 700 !important;
}
/* 데이터프레임 셀 텍스트 */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] { color: #1e1e2e !important; }
/* 다운로드 버튼 */
[data-testid="stDownloadButton"] button { color: #1e1e2e !important; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ──────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
  <h1>📊 주문·리뷰 통합 대시보드</h1>
  <p>주문 기본 정보와 리뷰 데이터를 업로드하면 자동으로 병합하여 분석합니다.</p>
</div>
""", unsafe_allow_html=True)

# ── 서울 날씨 (Open-Meteo) ────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_seoul_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=37.5665&longitude=126.9780"
        "&current=temperature_2m"
        "&hourly=temperature_2m"
        "&timezone=Asia%2FSeoul"
        "&forecast_days=1"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

try:
    weather = fetch_seoul_weather()
    current_temp = weather["current"]["temperature_2m"]
    hours = weather["hourly"]["time"]          # "2025-06-25T00:00" 형식
    temps = weather["hourly"]["temperature_2m"]

    now_hour = datetime.now().hour
    hour_labels = [h.split("T")[1] for h in hours]   # "00:00" ~ "23:00"
    x_indices = list(range(len(hour_labels)))         # 0 ~ 23 (숫자 축)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🌡️ 서울 현재 날씨 (Open-Meteo)</div>", unsafe_allow_html=True)

    w_col1, w_col2 = st.columns([1, 3], gap="large")

    with w_col1:
        st.markdown(f"""
        <div style="text-align:center; padding: 1.5rem 0;">
            <div style="font-size:3.5rem; font-weight:800; color:#4f6ef7;">{current_temp}°C</div>
            <div style="font-size:.9rem; color:#444; margin-top:.4rem;">서울 현재 기온</div>
            <div style="font-size:.8rem; color:#666; margin-top:.2rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')} 기준</div>
        </div>
        """, unsafe_allow_html=True)

    with w_col2:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=x_indices, y=temps,
            mode="lines+markers",
            line=dict(color="#4f6ef7", width=2.5),
            marker=dict(size=5, color="#4f6ef7"),
            fill="tozeroy",
            fillcolor="rgba(79,110,247,0.08)",
            customdata=hour_labels,
            hovertemplate="%{customdata}<br>%{y}°C<extra></extra>",
        ))
        fig_w.add_vline(
            x=now_hour,
            line_dash="dot", line_color="#f03e3e", line_width=1.5,
            annotation_text="현재", annotation_position="top",
        )
        fig_w.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=20, b=20, l=0, r=0),
            xaxis=dict(
                title="시간", gridcolor="#f0f0f0", tickangle=-45,
                tickvals=x_indices[::2], ticktext=hour_labels[::2],
            ),
            yaxis=dict(title="기온 (°C)", gridcolor="#f0f0f0"),
            height=260,
        )
        st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.warning(f"날씨 데이터를 불러오지 못했습니다: {e}")

st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

# ── 사이드바: 파일 업로드 ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 파일 업로드")
    st.markdown("두 엑셀 파일을 모두 업로드하면 `주문번호` 기준으로 자동 병합됩니다.")
    st.markdown("---")

    file_basic  = st.file_uploader("📦 주문 기본 정보 (orders_basic)", type=["xlsx", "xls"], key="basic")
    file_review = st.file_uploader("⭐ 리뷰 데이터 (orders_review)",   type=["xlsx", "xls"], key="review")

    st.markdown("---")
    st.caption("더미데이터 폴더의 두 파일을 그대로 올려보세요.")

# ── 파일 미업로드 안내 ────────────────────────────────────────────
if file_basic is None or file_review is None:
    missing = []
    if file_basic  is None: missing.append("📦 **주문 기본 정보** (orders_basic.xlsx)")
    if file_review is None: missing.append("⭐ **리뷰 데이터** (orders_review.xlsx)")

    st.info("왼쪽 사이드바에서 두 엑셀 파일을 모두 업로드해 주세요.")
    for m in missing:
        st.warning(f"{m} 파일이 필요합니다.")
    st.stop()

# ── 데이터 로드 & 병합 ────────────────────────────────────────────
@st.cache_data
def load_and_merge(basic_bytes, review_bytes):
    df_basic  = pd.read_excel(basic_bytes)
    df_review = pd.read_excel(review_bytes)
    df = pd.merge(df_basic, df_review, on="주문번호", how="inner")
    df["주문일자"] = pd.to_datetime(df["주문일자"], errors="coerce")
    return df, df_basic, df_review

df, df_basic, df_review = load_and_merge(file_basic, file_review)

st.success(f"✅ 병합 완료 — 주문 기본 {len(df_basic)}건 × 리뷰 {len(df_review)}건 → 매칭 {len(df)}건")

# ── 사이드바: 필터 ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 필터")

    categories = sorted(df["상품카테고리"].dropna().unique())
    sel_cat = st.multiselect("상품카테고리", categories, default=categories)

    grades = sorted(df["회원등급"].dropna().unique())
    sel_grade = st.multiselect("회원등급", grades, default=grades)

    channels = sorted(df["접속채널"].dropna().unique())
    sel_channel = st.multiselect("접속채널", channels, default=channels)

filtered = df[
    df["상품카테고리"].isin(sel_cat) &
    df["회원등급"].isin(sel_grade) &
    df["접속채널"].isin(sel_channel)
]

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# ── KPI 카드 ──────────────────────────────────────────────────────
total_orders   = len(filtered)
total_revenue  = filtered["결제금액(원)"].sum()
avg_rating     = filtered["별점"].mean()
return_rate    = (filtered["반품여부"] == "Y").mean() * 100
repurchase_rate = (filtered["재구매의향"] == "있음").mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "총 주문 건수",    f"{total_orders:,} 건",          "병합 기준"),
    (k2, "총 결제 금액",    f"₩ {total_revenue:,}",          "할인 후 합산"),
    (k3, "평균 별점",       f"⭐ {avg_rating:.2f}",           "5점 만점"),
    (k4, "반품율",          f"{return_rate:.1f} %",           "반품여부 Y 기준"),
    (k5, "재구매 의향율",   f"{repurchase_rate:.1f} %",       "'있음' 응답 비율"),
]
for col, label, value, sub in kpis:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Row 1: 카테고리별 매출 / 별점 분포 ───────────────────────────
col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💰 카테고리별 결제 금액</div>", unsafe_allow_html=True)
    cat_rev = (
        filtered.groupby("상품카테고리", as_index=False)["결제금액(원)"].sum()
        .sort_values("결제금액(원)", ascending=False)
    )
    fig = px.bar(
        cat_rev, x="상품카테고리", y="결제금액(원)",
        color="상품카테고리",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        text_auto=True,
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(title=""), yaxis=dict(title="결제금액 (원)", gridcolor="#f0f0f0"),
    )
    fig.update_traces(texttemplate="₩%{y:,.0f}", textposition="outside", marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>⭐ 별점 분포</div>", unsafe_allow_html=True)
    rating_dist = filtered["별점"].value_counts().sort_index().reset_index()
    rating_dist.columns = ["별점", "건수"]
    rating_dist["별점"] = rating_dist["별점"].astype(str) + "점"
    fig2 = px.bar(
        rating_dist, x="별점", y="건수",
        color="별점",
        color_discrete_sequence=["#ff6b6b","#ffa94d","#ffd43b","#a9e34b","#4f6ef7"],
        text_auto=True,
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(title=""), yaxis=dict(title="건수", gridcolor="#f0f0f0"),
    )
    fig2.update_traces(textposition="outside", marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 2: 결제수단 / 회원등급별 평균 별점 ───────────────────────
col_c, col_d = st.columns(2, gap="large")

with col_c:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💳 결제수단 비율</div>", unsafe_allow_html=True)
    pay_dist = filtered["결제수단"].value_counts().reset_index()
    pay_dist.columns = ["결제수단", "건수"]
    fig3 = px.pie(
        pay_dist, names="결제수단", values="건수",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.45,
    )
    fig3.update_layout(
        paper_bgcolor="white", margin=dict(t=10, b=10, l=0, r=0),
        legend=dict(orientation="v", x=1, y=0.5),
    )
    fig3.update_traces(textinfo="percent+label")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_d:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>👑 회원등급별 평균 별점 & 반품율</div>", unsafe_allow_html=True)
    grade_stats = (
        filtered.groupby("회원등급", as_index=False)
        .agg(평균별점=("별점", "mean"), 반품율=("반품여부", lambda x: (x == "Y").mean() * 100))
        .sort_values("평균별점", ascending=False)
    )
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=grade_stats["회원등급"], y=grade_stats["평균별점"],
        name="평균 별점", marker_color="#4f6ef7",
        text=grade_stats["평균별점"].round(2), textposition="outside",
        yaxis="y1",
    ))
    fig4.add_trace(go.Scatter(
        x=grade_stats["회원등급"], y=grade_stats["반품율"],
        name="반품율(%)", mode="lines+markers",
        marker=dict(color="#f03e3e", size=8),
        line=dict(color="#f03e3e", width=2),
        yaxis="y2",
    ))
    fig4.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10, l=0, r=60),
        xaxis=dict(title=""),
        yaxis=dict(title="평균 별점", gridcolor="#f0f0f0", range=[0, 6]),
        yaxis2=dict(title="반품율 (%)", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 3: 쿠폰 사용 여부 / 재구매 의향 ──────────────────────────
col_e, col_f = st.columns(2, gap="large")

with col_e:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🎟️ 쿠폰 사용 여부별 평균 결제금액</div>", unsafe_allow_html=True)
    coupon_stats = (
        filtered.groupby("쿠폰사용여부", as_index=False)["결제금액(원)"].mean()
    )
    coupon_stats["쿠폰사용여부"] = coupon_stats["쿠폰사용여부"].map({"Y": "쿠폰 사용", "N": "미사용"})
    fig5 = px.bar(
        coupon_stats, x="쿠폰사용여부", y="결제금액(원)",
        color="쿠폰사용여부",
        color_discrete_map={"쿠폰 사용": "#4f6ef7", "미사용": "#adb5bd"},
        text_auto=True,
    )
    fig5.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(title=""), yaxis=dict(title="평균 결제금액 (원)", gridcolor="#f0f0f0"),
    )
    fig5.update_traces(texttemplate="₩%{y:,.0f}", textposition="outside", marker_line_width=0)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_f:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔄 재구매 의향 vs 반품여부</div>", unsafe_allow_html=True)
    cross = (
        filtered.groupby(["재구매의향", "반품여부"]).size()
        .reset_index(name="건수")
    )
    cross["반품여부"] = cross["반품여부"].map({"Y": "반품 있음", "N": "반품 없음"})
    fig6 = px.bar(
        cross, x="재구매의향", y="건수", color="반품여부",
        barmode="group",
        color_discrete_map={"반품 있음": "#f03e3e", "반품 없음": "#4f6ef7"},
        text_auto=True,
    )
    fig6.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10, l=0, r=0),
        xaxis=dict(title="재구매 의향"),
        yaxis=dict(title="건수", gridcolor="#f0f0f0"),
        legend=dict(orientation="h", y=-0.2),
    )
    fig6.update_traces(textposition="outside", marker_line_width=0)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── 병합 데이터 테이블 ────────────────────────────────────────────
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📋 병합 데이터 전체 보기</div>", unsafe_allow_html=True)

display_cols = [
    "주문번호", "주문일자", "상품카테고리", "상품명",
    "단가(원)", "수량", "할인금액(원)", "결제금액(원)",
    "결제수단", "회원등급", "별점", "반품여부", "재구매의향", "쿠폰사용여부",
]
display_cols = [c for c in display_cols if c in filtered.columns]

st.dataframe(
    filtered[display_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "주문일자": st.column_config.DateColumn("주문일자", format="YYYY-MM-DD"),
        "단가(원)": st.column_config.NumberColumn("단가(원)", format="₩%d"),
        "할인금액(원)": st.column_config.NumberColumn("할인금액(원)", format="₩%d"),
        "결제금액(원)": st.column_config.NumberColumn("결제금액(원)", format="₩%d"),
        "별점": st.column_config.NumberColumn("별점", format="⭐ %d"),
    },
)
st.markdown("</div>", unsafe_allow_html=True)

# ── 다운로드 버튼 ─────────────────────────────────────────────────
csv = filtered.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="⬇️ 병합 데이터 CSV 다운로드",
    data=csv,
    file_name="merged_orders_review.csv",
    mime="text/csv",
)
