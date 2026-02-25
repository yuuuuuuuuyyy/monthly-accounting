import streamlit as st
import time
from streamlit_cookies_controller import CookieController

# 1. 網頁基本設定
st.set_page_config(page_title="每月記帳", page_icon="💰", layout="centered")
st.title("每月待繳金額計算 💰")

# 2. 初始化 Cookie 控制器 (用來把資料存在你的手機裡)
controller = CookieController()

# 給系統一點點時間去讀取手機裡的 Cookie 紀錄
time.sleep(0.1)

# 3. 讀取之前的紀錄 (我們把這個記憶欄位命名為 'saved_total')
saved_total = controller.get('saved_total')

# 如果找不到紀錄（代表是第一次用，或是被清除了），預設為 0.0
if saved_total is None:
    saved_total = 0.0
else:
    saved_total = float(saved_total)

# 4. 輸入區塊
item_name = st.text_input("繳費項目 (例如：車貸、學貸)")

# 總金額的預設值，會自動帶入我們讀取到的記憶數字
total_amount = st.number_input("總金額", value=saved_total, step=100.0)
add_amount = st.number_input("本月增加金額", value=0.0, step=100.0)
pay_amount = st.number_input("本月已繳金額", value=0.0, step=100.0)

# 5. 計算與按鈕
if st.button("開始計算並結轉下個月", type="primary", use_container_width=True):
    # 核心公式
    new_total = total_amount + add_amount - pay_amount
    
    # 🌟 重點：把最新的金額存進手機的 Cookie 裡！(max_age 是保存秒數，這裡設為 365 天)
    controller.set('saved_total', new_total, max_age=31536000)
    
    # 暫存進 session_state 以便畫面立刻更新
    st.session_state.remaining_amount = new_total
    
    st.success(f"✅ 計算完成！已自動記憶下個月總金額：$ {new_total:,.0f}")
    time.sleep(1) # 暫停 1 秒讓使用者看到成功訊息
    st.rerun()    # 重新整理畫面

# 6. 顯示結果
st.markdown("---")
display_name = item_name if item_name else "該項目"
st.subheader(f"🏷️ {display_name} 的剩下待繳金額：")

# 判斷要顯示剛算好的，還是剛讀取到的舊資料
if 'remaining_amount' in st.session_state:
    display_amount = st.session_state.remaining_amount
else:
    display_amount = saved_total

st.metric(label="目前待繳", value=f"$ {display_amount:,.0f}")
