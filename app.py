import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go 
import json
from io import BytesIO 

# --- 交易费率定义 ---
TRANSACTION_FEE_RATE = 0.001 

# --- 新闻事件库定义 --- (保持不变，省略中间内容...)
NEWS_EVENTS = [
    {"title": "🚀【特大喜讯】AI芯片技术取得革命性突破！", "impact": 0.18, "color": "green"},
    # ... (其他事件省略)
    {"title": "☁️【成本上升】原材料价格暴涨，公司利润空间被压缩。", "impact": -0.06, "color": "red"},
]

# (所有函数 next_day, buy, sell, save_game, load_game 保持不变)
# (Session State 初始化也保持不变)
# (为了代码简洁，中间函数省略，请确保你的文件里有这些函数)

ss = st.session_state

# >>> 关键改动：CSS 注入 <<<
# 注入 CSS 代码，定义一个固定在底部的容器样式
st.markdown("""
<style>
/* Streamlit 默认是深色主题，使用深色背景 */
.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    /* 使用 Streamlit 的主题背景色 */
    background-color: #0e1117; 
    padding: 10px 30px; /* 增加左右内边距，避免贴边 */
    box-shadow: 0px -4px 12px rgba(0, 0, 0, 0.7); /* 底部阴影，看起来有“浮动”感 */
    z-index: 1000; /* 确保它在最上层 */
}

/* 隐藏侧边栏的页脚（如果存在） */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)
# >>> CSS 注入结束 <<<

# --- 4. 搭建界面 (Dashboard) ---

# A. 顶部指标栏 (Metrics)
total_asset = ss.balance + (ss.shares * ss.price)
col1, col2, col3, col4 = st.columns(4)
col1.metric("当前股价", f"${ss.price:.2f}")
col2.metric("持有现金", f"${ss.balance:.2f}")
col3.metric("持仓股数", f"{ss.shares} 股")

initial_asset = 100000.0
asset_delta = total_asset - initial_asset
asset_delta_pct = f"{asset_delta / initial_asset * 100:.2f}%" if initial_asset != 0 else "0.00%"
col4.metric("总资产", f"${total_asset:.2f}", delta=f"${asset_delta:.2f} ({asset_delta_pct})") 

# B. 重大新闻展示区 (保持不变)
if ss.current_news:
    event = ss.current_news
    st.markdown(
        f"<h3 style='color:{event['color']};'>{event['title']}</h3>"
        f"<h5>市场预估波动幅度: {abs(event['impact'])*100:.0f}% </h5>", 
        unsafe_allow_html=True
    )
else:
    st.info("今日市场平静，无重大突发新闻。")

# C. 股价走势图 (K线图) (保持不变)
st.subheader("📊 股价走势 - K线图")
df_chart = ss.history[ss.history['Day'] > 0] 

fig = go.Figure(data=[go.Candlestick(
    x=df_chart['Day'],
    open=df_chart['Open'],
    high=df_chart['High'],
    low=df_chart['Low'],
    close=df_chart['Close'],
    increasing_line_color='green', 
    decreasing_line_color='red'
)])

fig.update_layout(
    xaxis_rangeslider_visible=False,
    xaxis_title='天数',
    yaxis_title='价格 ($)',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# D. 存档/读档 (保持在滚动区域)
st.subheader("📁 存档/读档")
save_col, load_col = st.columns(2)

# (存档和读档组件代码不变，省略)
save_col.download_button(
    label="⬇️ 保存进度 (下载 SaveFile.json)",
    data=save_game(),
    file_name="StockGame_SaveFile.json",
    mime="application/json",
    use_container_width=True
)

uploaded_file = load_col.file_uploader(
    "⬆️ 加载进度 (上传 SaveFile.json)", 
    type=['json'], 
    accept_multiple_files=False, 
    key="file_uploader"
)

if uploaded_file is not None:
    if st.button("点击确认加载进度"):
        load_game(uploaded_file)

# >>> 关键改动：交易日记提前 <<<
# 将交易日记放在滚动区域，靠近图表
st.subheader("📝 交易日记")
for record in ss.log[::-1][:8]:
    st.text(record)
    
st.markdown("---")
# >>> 交易日记提前结束 <<<


# >>> 关键改动：固定底部面板区域 <<<
# 1. 插入一个空的占位符，防止页面内容被固定底栏遮挡
st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True) 

# 2. 创建固定的底栏容器
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
st.markdown(f"**交易成本：** 买入/卖出均收取 **{TRANSACTION_FEE_RATE*100:.1f}%** 手续费。")

# 3. 在固定底栏内设置操作列
fixed_c1, fixed_c2, fixed_c3 = st.columns([1, 1, 1])

with fixed_c1:
    trade_amount = st.number_input("交易数量", min_value=0, value=100, step=100, key="fixed_amount_input", label_visibility="collapsed")
    st.markdown("交易数量")

with fixed_c2:
    st.markdown("---") # 占位
    if st.button("🟢 买入", use_container_width=True):
        buy(trade_amount)
        st.rerun()
    if st.button("🔴 卖出", use_container_width=True):
        sell(trade_amount)
        st.rerun()

with fixed_c3:
    st.markdown("---") # 占位
    if st.button(f"🌙 进入下一天 (第 {ss.day} 天)", type="primary", use_container_width=True):
        next_day()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # 关闭固定底栏容器
# >>> 固定底部面板区域结束 <<<
