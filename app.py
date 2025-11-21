import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go 

# >>> 新增内容 <<<
# --- 交易费率定义 ---
TRANSACTION_FEE_RATE = 0.001 # 0.1% 手续费率 (买入和卖出均收取)
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
st.title("📈 模拟炒股大亨 v4.0 - 交易深度版") # 版本号升级

# --- 2. 初始化“记忆库” (Session State) ---
initial_price = 100.0
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
    st.session_state.shares = 0
    st.session_state.price = initial_price       
    st.session_state.day = 1
    st.session_state.log = [f"游戏开始！初始资金 ${100000.0:.2f} | 手续费率: {TRANSACTION_FEE_RATE*100:.1f}%"] # 增加费率显示
    st.session_state.current_news = None
    
    st.session_state.history = pd.DataFrame([{
        'Day': 0, 
        'Open': initial_price, 
        'High': initial_price, 
        'Low': initial_price, 
        'Close': initial_price 
    }])

ss = st.session_state 

# --- 3. 定义游戏逻辑函数 ---
def next_day():
    # ... (next_day 函数保持不变)
    
    last_close = ss.price
    ss.current_news = None
    news_impact = 0.0      
    
    if random.random() < 0.20:
        event = random.choice(NEWS_EVENTS)
        ss.current_news = event
        news_impact = event['impact']
        ss.log.append(f"🔥 【新闻】{event['title']}")
    
    base_volatility = random.uniform(-0.03, 0.03)
    total_change = base_volatility + news_impact  
    
    new_close = last_close * (1 + total_change)
    if new_close < 1: new_close = 1.0
    ss.price = new_close
    
    day_high = max(last_close, new_close) * random.uniform(1.002, 1.01)
    day_low = min(last_close, new_close) * random.uniform(0.99, 0.998)
    
    new_day_data = pd.DataFrame([{
        'Day': ss.day, 
        'Open': last_close, 
        'High': day_high, 
        'Low': day_low, 
        'Close': new_close 
    }])
    
    ss.history = pd.concat([ss.history, new_day_data], ignore_index=True)
    ss.day += 1
    
    if not ss.current_news:
        ss.log.append(f"📅 第 {ss.day} 天：基础波动 {total_change*100:.2f}%")

# >>> 关键改动：买入逻辑 <<<
def buy(amount):
    """计算买入手续费，并检查余额"""
    share_cost = amount * ss.price
    fee = share_cost * TRANSACTION_FEE_RATE  # 计算手续费
    total_cost = share_cost + fee            # 实际总花费
    
    if amount <= 0:
        st.error("数量必须大于0！")
    elif ss.balance >= total_cost:
        ss.balance -= total_cost
        ss.shares += amount
        ss.log.append(f"🟢 买入 {amount} 股，花费 ${share_cost:.2f} (手续费 ${fee:.2f})")
        st.success(f"买入成功！扣除手续费 ${fee:.2f}")
    else:
        st.error(f"余额不足！总花费 (含手续费 ${fee:.2f}) 为 ${total_cost:.2f}")
# >>> 关键改动结束 <<<

# >>> 关键改动：卖出逻辑 <<<
def sell(amount):
    """计算卖出手续费，并结算净收入"""
    share_revenue = amount * ss.price
    fee = share_revenue * TRANSACTION_FEE_RATE  # 计算手续费
    net_revenue = share_revenue - fee           # 实际净收入
    
    if amount <= 0:
        st.error("数量必须大于0！")
    elif ss.shares >= amount:
        ss.shares -= amount
        ss.balance += net_revenue
        ss.log.append(f"🔴 卖出 {amount} 股，收入 ${share_revenue:.2f} (扣除手续费 ${fee:.2f})")
        st.success(f"卖出成功！净收入 ${net_revenue:.2f}")
    else:
        st.error("持仓不足！")
# >>> 关键改动结束 <<<

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

# D. 操作控制区 (Controls)
st.markdown("---")

# >>> 新增内容：显示费率信息 <<<
st.markdown(f"**交易成本：** 买入/卖出均收取 **{TRANSACTION_FEE_RATE*100:.1f}%** 手续费。")
# >>> 新增内容结束 <<<

c1, c2 = st.columns([1, 2])

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
