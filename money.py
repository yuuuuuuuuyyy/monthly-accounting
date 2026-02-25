import streamlit as st

# 1. 網頁基本設定
st.set_page_config(page_title="每月記帳", page_icon="💰", layout="centered")
st.title("每月待繳金額計算 💰")

# 2. 初始化 Session State (讓 Streamlit 記住結轉後的金額)
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0.0
if 'remaining_amount' not in st.session_state:
    st.session_state.remaining_amount = 0.0

# 3. 輸入區塊
item_name = st.text_input("繳費項目 (例如：車貸、學貸)")

# 總金額會自動讀取 session_state 裡面的值，達成自動結轉的效果
total_amount = st.number_input("總金額", value=st.session_state.total_amount, step=100.0)
add_amount = st.number_input("本月增加金額", value=0.0, step=100.0)
pay_amount = st.number_input("本月已繳金額", value=0.0, step=100.0)

# 4. 計算與按鈕
if st.button("開始計算並結轉下個月", type="primary", use_container_width=True):
    # 核心公式：總金額 + 增加金額 - 繳費金額
    new_total = total_amount + add_amount - pay_amount
    
    # 將計算結果存起來
    st.session_state.remaining_amount = new_total
    
    # 自動結轉：把新總額設定為下一次的總金額
    st.session_state.total_amount = new_total
    
    # 強制重新整理畫面，讓輸入框顯示新的總金額
    st.rerun()

# 5. 顯示結果
st.markdown("---")
display_name = item_name if item_name else "該項目"
st.subheader(f"🏷️ {display_name} 的剩下待繳金額：")

# 使用 Streamlit 內建的漂亮的數據顯示元件
st.metric(label="目前待繳", value=f"$ {st.session_state.remaining_amount:,.0f}")