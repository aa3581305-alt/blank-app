import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ページ設定
st.set_page_config(page_title="USD/JPY & Interest Rates", layout="wide")
st.title("🇺🇸🇺🇳 米ドル/円レートと日米政策金利の推移")

# 2. サイドバーでの設定
st.sidebar.header("設定")
years = st.sidebar.slider("表示期間（過去何年）", 1, 20, 5)
end_date = datetime.today()
start_date = end_date - timedelta(days=years * 365)

# 3. データの取得
@st.cache_data
def get_data(start, end):
    # 為替レート (USD/JPY)
    fx_data = yf.download("JPY=X", start=start, end=end)['Close']
    
    # 政策金利 (FREDから取得)
    # FEDFUNDS: 米国フェデラル・ファンド実効金利
    # INTDSRJPM193N: 日本の政策金利（割引率）または代替指標
    us_rate = web.DataReader("FEDFUNDS", "fred", start, end)
    jp_rate = web.DataReader("IRSTCB01JPM156N", "fred", start, end) # 日本政策金利（短期）
    
    return fx_data, us_rate, jp_rate

try:
    fx, us_ir, jp_ir = get_data(start_date, end_date)

    # 4. グラフ作成 (Plotly)
    # 為替チャート
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Scatter(x=fx.index, y=fx.values.flatten(), name="USD/JPY", line=dict(color="#1f77b4")))
    fig_fx.update_layout(title="USD/JPY 為替レート", xaxis_title="日付", yaxis_title="円", height=400)
    st.plotly_chart(fig_fx, use_container_width=True)

    # 政策金利チャート
    fig_ir = go.Figure()
    fig_ir.add_trace(go.Scatter(x=us_ir.index, y=us_ir['FEDFUNDS'], name="米国政策金利 (FFレート)", line=dict(color="#d62728")))
    fig_ir.add_trace(go.Scatter(x=jp_ir.index, y=jp_ir['IRSTCB01JPM156N'], name="日本政策金利", line=dict(color="#2ca02c")))
    fig_ir.update_layout(title="日米政策金利の推移", xaxis_title="日付", yaxis_title="%", height=400, hovermode="x unified")
    st.plotly_chart(fig_ir, use_container_width=True)

    # 5. 最新データの表示
    col1, col2, col3 = st.columns(3)
    col1.metric("最新 USD/JPY", f"{fx.values[-1][0]:.2f} 円")
    col2.metric("米国金利", f"{us_ir.iloc[-1, 0]:.2f} %")
    col3.metric("日本金利", f"{jp_ir.iloc[-1, 0]:.2f} %")

except Exception as e:
    st.error(f"データの取得中にエラーが発生しました: {e}")
    st.info("※FRED（政策金利）のデータ取得にはネットワーク制限がある場合があります。")
