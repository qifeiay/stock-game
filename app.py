import streamlit as st
import random
import pandas as pd
# >>> 新增内容 <<<
import plotly.graph_objects as go 
# >>> 新增内容结束 <<<

# --- 新闻事件库定义 --- (保持不变，省略中间内容...)
NEWS_EVENTS = [
    # 重大利好 (Positive Shock)
    {"title": "🚀【特大喜讯】AI芯片技术取得革命性突破！", "impact": 0.18, "color": "green"},
    # ... (其他事件省略)
    {"title": "☁️【成本上升】原材料价格暴涨，公司利润空间被压缩。", "impact": -0.06, "color": "red"},
]


# --- 1. 设置网页标题和布局 ---
st.set_page_config(page_title="模拟炒股大亨", layout="wide")
st.title("📈 模拟炒股大亨 v3.0 - K线专业版")

# --- 2. 初始化“记忆库” (Session State) ---
initial_price = 100.0
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
    st.session_state.shares = 0
    st.session_state.price = initial_price       # 记录最新的收盘价
    st.session_state.day = 1
    st.session_state.log = ["游戏开始！初始资金 $100,000"]
    st.session_state.current_news = None
    
    # >>> 关键改动：初始化 OHLC 历史数据 <<<
    # K线图需要 OHLCV 数据，我们用 Pandas DataFrame 存储历史数据
    st.session_state.history = pd.DataFrame([{
        'Day': 0, 
        'Open': initial_price, 
        'High': initial_price, 
        'Low': initial_price, 
        'Close': initial_price 
    }])
    # >>> 新增内容结束 <<<

ss = st.session_state 

# --- 3. 定义游戏逻辑函数 ---
def next_day():
    """进入下一天，股价波动并生成 OHLC 数据"""
    
    # 获取前一天的收盘价作为今天的开盘价
    last_close = ss.price
    
    # 1. 决定是否触发重大新闻事件 (20% 概率)
    ss.current_news = None
    news_impact = 0.0      
    
    if random.random() < 0.20:
        event = random.choice(NEWS_EVENTS)
        ss.current_news = event
        news_impact = event['impact']
        ss.log.append(f"🔥 【新闻】{event['title']}")
    
    # 2. 计算基础波动和总冲击
    base_volatility = random.uniform(-0.03, 0.03)
    total_change = base_volatility + news_impact  
    
    # 3. 计算并更新今天的收盘价 (Close)
    new_close = last_close * (1 + total_change)
    if new_close < 1: new_close = 1.0
    ss.price = new_close # 更新 session state 里的最新价格
    
    # >>> 关键改动：生成当天的高点和低点 <<<
    # 最高价：至少要高于 Open 和 Close，并加上一个随机波动
    day_high = max(last_close, new_close) * random.uniform(1.002, 1.01)
    # 最低价：至少要低于 Open 和 Close，并减去一个随机波动
    day_low = min(last_close, new_close) * random.uniform(0.99, 0.998)
    
    # 4. 记录 OHLC 数据
    new_day_data = pd.DataFrame([{
        'Day': ss.day, 
        'Open': last_close, 
        'High': day_high, 
        'Low': day_low, 
        'Close': new_close 
    }])
    
    # 合并到历史数据中
    ss.history = pd.concat([ss.history, new_day_data], ignore_index=True)
    # >>> 新增内容结束 <<<
    
    ss.day += 1
    
    # 5. 记录日志 
    if not ss.current_news:
        ss.log.append(f"📅 第 {ss.day} 天：基础波动 {total_change*100:.2f}%")

def buy(amount):
    # ... (保持不变)
    cost = amount * ss.price
    if amount <= 0:
        st.error("数量必须大于0！")
    elif ss.balance >= cost:
        ss.balance -= cost
        ss.shares += amount
        ss.log.append(f"🟢 买入 {amount} 股，花费 ${cost:.2f}")
        st.success("买入成功！")
    else:
        st.error("余额不足！")

def sell(amount):
    # ... (保持不变)
    revenue = amount * ss.price
    if amount <= 0:
        st.error("数量必须大于0！")
    elif ss.shares >= amount:
        ss.shares -= amount
        ss.balance += revenue
        ss.log.append(f"🔴 卖出 {amount} 股，获得 ${revenue:.2f}")
        st.success("卖出成功！")
    else:
        st.error("持仓不足！")

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
# 将盈亏百分比作为 delta 显示
col4.metric("总资产", f"${total_asset:.2f}", delta=f"${asset_delta:.2f} ({asset_delta_pct})") 

# B. 重大新闻展示区
if ss.current_news:
    event = ss.current_news
    st.markdown(
        f"<h3 style='color:{event['color']};'>{event['title']}</h3>"
        f"<h5>市场预估波动幅度: {abs(event['impact'])*100:.0f}% </h5>", 
        unsafe_allow_html=True
    )
else:
    st.info("今日市场平静，无重大突发新闻。")

# >>> 关键改动：替换 line_chart 为 Plotly K线图 <<<
st.subheader("📊 股价走势 - K线图")

# 移除第一天（Day 0）的初始数据，不显示在图表上
df_chart = ss.history[ss.history['Day'] > 0] 

# 使用 Plotly 绘制 Candlestick 图
fig = go.Figure(data=[go.Candlestick(
    x=df_chart['Day'],
    open=df_chart['Open'],
    high=df_chart['High'],
    low=df_chart['Low'],
    close=df_chart['Close'],
    increasing_line_color='green', 
    decreasing_line_color='red'
)])

# 优化图表布局
fig.update_layout(
    xaxis_rangeslider_visible=False, # 隐藏底部的滑动条
    xaxis_title='天数',
    yaxis_title='价格 ($)',
    height=500
)

st.plotly_chart(fig, use_container_width=True)
# >>> 新增内容结束 <<<

# D. 操作控制区 (Controls)
st.markdown("---")
c1, c2 = st.columns([1, 2])

# ... (操作面板和交易日记保持不变，省略中间内容)

with c1:
    st.subheader("🕹️ 操作面板")
    trade_amount = st.number_input("交易数量", min_value=0, value=100, step=100)
    
    if st.button("🟢 买入股票", use_container_width=True):
        buy(trade_amount)
        st.rerun()
        
    if st.button("🔴 卖出股票", use_container_width=True):
        sell(trade_amount)
        st.rerun()

    st.markdown("###")
    if st.button(f"🌙 进入下一天 (当前第 {ss.day} 天)", type="primary", use_container_width=True):
        next_day()
        st.rerun()

with c2:
    st.subheader("📝 交易日记")
    for record in ss.log[::-1][:8]:
        st.text(record)
