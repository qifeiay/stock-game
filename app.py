import streamlit as st
import random
import pandas as pd

# >>> 新增内容 <<<
# --- 新闻事件库定义 ---
NEWS_EVENTS = [
    # 重大利好 (Positive Shock)
    {"title": "🚀【特大喜讯】AI芯片技术取得革命性突破！", "impact": 0.18, "color": "green"},
    {"title": "📈【政府订单】获得国家能源局巨额采购合同！", "impact": 0.15, "color": "green"},
    
    # 一般利好 (Mild Positive)
    {"title": "✅【财报超预期】季度营收增长超出市场预期！", "impact": 0.08, "color": "green"},
    {"title": "🤝【战略合作】与行业巨头签署长期战略合作协议。", "impact": 0.05, "color": "green"},
    
    # 重大利空 (Negative Shock)
    {"title": "🔥【重大丑闻】CEO涉嫌内幕交易，被监管机构调查！", "impact": -0.25, "color": "red"},
    {"title": "📉【市场监管】新政出台，公司核心业务面临巨大挑战。", "impact": -0.18, "color": "red"},
    
    # 一般利空 (Mild Negative)
    {"title": "⚠️【产品召回】主力产品出现严重质量问题，宣布召回。", "impact": -0.10, "color": "red"},
    {"title": "☁️【成本上升】原材料价格暴涨，公司利润空间被压缩。", "impact": -0.06, "color": "red"},
]
# >>> 新增内容结束 <<<


# --- 1. 设置网页标题和布局 ---
st.set_page_config(page_title="模拟炒股大亨", layout="wide")
st.title("📈 模拟炒股大亨 v2.0 - 新闻驱动版")

# --- 2. 初始化“记忆库” (Session State) ---
if 'balance' not in st.session_state:
    st.session_state.balance = 100000.0
    st.session_state.shares = 0
    st.session_state.price = 100.0
    st.session_state.day = 1
    st.session_state.history = [100.0]
    st.session_state.log = ["游戏开始！初始资金 $100,000"]
    # >>> 新增内容 <<<
    st.session_state.current_news = None  # 用于存储当前日期的重大新闻
    # >>> 新增内容结束 <<<

# 为了方便，我们把长变量名简化一下
ss = st.session_state 

# --- 3. 定义游戏逻辑函数 ---
def next_day():
    """进入下一天，股价波动"""
    
    # >>> 新增内容 <<<
    # 1. 决定是否触发重大新闻事件 (20% 概率)
    ss.current_news = None # 重置新闻
    news_impact = 0.0      # 新闻冲击默认为 0
    
    if random.random() < 0.20: # 20% 概率触发新闻
        event = random.choice(NEWS_EVENTS)
        ss.current_news = event
        news_impact = event['impact']
        ss.log.append(f"🔥 【新闻】{event['title']}")
    # >>> 新增内容结束 <<<
    
    # 2. 计算基础波动和总冲击
    base_volatility = random.uniform(-0.03, 0.03) # 基础波动 ±3%
    total_change = base_volatility + news_impact   # 总变化率 = 基础波动 + 新闻冲击
    
    # 3. 更新股价
    ss.price = ss.price * (1 + total_change)
    if ss.price < 1: ss.price = 1.0 # 保底逻辑
    
    ss.day += 1
    ss.history.append(ss.price) # 记录历史股价
    
    # 4. 记录日志 (如果只是基础波动，记录简易日志)
    if not ss.current_news:
        ss.log.append(f"📅 第 {ss.day} 天：基础波动 {base_volatility*100:.2f}%")


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

# 计算总资产盈亏百分比
initial_asset = 100000.0
asset_delta = total_asset - initial_asset
asset_delta_pct = f"{asset_delta / initial_asset * 100:.2f}%" if initial_asset != 0 else "0.00%"
col4.metric("总资产", f"${total_asset:.2f}", delta=f"${asset_delta:.2f} ({asset_delta_pct})")

# >>> 新增内容 <<<
# B. 重大新闻展示区
if ss.current_news:
    event = ss.current_news
    # 使用 Markdown 突出显示新闻，颜色根据利好/利空变化
    st.markdown(
        f"<h3 style='color:{event['color']};'>{event['title']}</h3>"
        f"<h5>市场预估波动幅度: {abs(event['impact'])*100:.0f}% </h5>", 
        unsafe_allow_html=True
    )
    # 如果是利好，播放庆祝声音，如果是利空，播放警报声音 (Streamlit暂不支持，这里只是文本提示)
else:
    st.info("今日市场平静，无重大突发新闻。")
# >>> 新增内容结束 <<<

# C. 股价走势图 (Chart)
st.subheader("📉 股价走势")
chart_data = pd.DataFrame(ss.history, columns=['股价'])
st.line_chart(chart_data)

# D. 操作控制区 (Controls)
st.markdown("---")
c1, c2 = st.columns([1, 2]) # 左窄右宽

with c1:
    st.subheader("🕹️ 操作面板")
    trade_amount = st.number_input("交易数量", min_value=0, value=100, step=100)
    
    # 放置三个按钮
    if st.button("🟢 买入股票", use_container_width=True):
        buy(trade_amount)
        st.rerun()
        
    if st.button("🔴 卖出股票", use_container_width=True):
        sell(trade_amount)
        st.rerun()

    st.markdown("###") # 空行
    # 在按钮上显示当前是第几天
    if st.button(f"🌙 进入下一天 (当前第 {ss.day} 天)", type="primary", use_container_width=True):
        next_day()
        st.rerun()

# E. 交易日志 (Log)
with c2:
    st.subheader("📝 交易日记")
    # 显示最近的 8 条记录
    for record in ss.log[::-1][:8]:
        st.text(record)
