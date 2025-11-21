import streamlit as st
import random
import pandas as pd

# --- 1. 设置网页标题和布局 ---
st.set_page_config(page_title="模拟炒股大亨", layout="wide")
st.title("📈 模拟炒股大亨 v1.0")

# --- 2. 初始化“记忆库” (Session State) ---
# Streamlit 每次交互都会重跑代码，所以必须把数据存进 session_state 里
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0  # 初始资金
    st.session_state.shares = 0          # 初始持仓
    st.session_state.price = 100.0       # 初始股价
    st.session_state.day = 1             # 天数
    st.session_state.history = [100.0]   # 股价历史记录(用于画图)
    st.session_state.log = ["游戏开始！初始资金 $100,000"] # 交易日志

# 为了方便，我们把长变量名简化一下
ss = st.session_state 

# --- 3. 定义游戏逻辑函数 ---
def next_day():
    """进入下一天，股价波动"""
    change = random.uniform(-0.10, 0.10) # ±10% 波动
    ss.price = ss.price * (1 + change)
    if ss.price < 1: ss.price = 1.0 # 保底逻辑
    
    ss.day += 1
    ss.history.append(ss.price) # 记录历史股价
    ss.log.append(f"📅 第 {ss.day} 天：股价波动 {change*100:.2f}%")

def buy(amount):
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
col4.metric("总资产", f"${total_asset:.2f}", delta=total_asset-100000)

# B. 股价走势图 (Chart)
st.subheader("📉 股价走势")
chart_data = pd.DataFrame(ss.history, columns=['股价'])
st.line_chart(chart_data)

# C. 操作控制区 (Controls)
st.markdown("---")
c1, c2 = st.columns([1, 2]) # 左窄右宽

with c1:
    st.subheader("🕹️ 操作面板")
    trade_amount = st.number_input("交易数量", min_value=0, value=100, step=100)
    
    # 放置三个按钮
    if st.button("🟢 买入股票", use_container_width=True):
        buy(trade_amount)
        st.rerun() # 强制刷新页面以更新数据
        
    if st.button("🔴 卖出股票", use_container_width=True):
        sell(trade_amount)
        st.rerun()

    st.markdown("###") # 空行
    if st.button("🌙 进入下一天 (股价波动)", type="primary", use_container_width=True):
        next_day()
        st.rerun()

# D. 交易日志 (Log)
with c2:
    st.subheader("📝 交易日记")
    # 显示最近的 5 条记录
    for record in ss.log[::-1][:8]:
        st.text(record)