import streamlit as st
import time
import json
from streamlit_cookies_controller import CookieController

# 1. 網頁基本設定 (準備好側邊欄)
st.set_page_config(page_title="每月記帳", page_icon="💰", layout="centered")

# 2. 初始化 Cookie 控制器
controller = CookieController()
time.sleep(0.1) # 給系統一點點時間讀取手機裡的 Cookie

# 3. 讀取之前的紀錄 (把存檔的文字轉換回 Python 的字典格式)
saved_items_str = controller.get('saved_items')

if saved_items_str:
    try:
        saved_items = json.loads(saved_items_str)
    except:
        saved_items = {}
else:
    saved_items = {}

# ================= 左側欄 (Sidebar) =================
st.sidebar.title("📁 已存檔項目")

if not saved_items:
    st.sidebar.info("目前沒有存檔的項目。")
else:
    # 把它存的項目一個一個列出來
    for item, amount in saved_items.items():
        st.sidebar.metric(label=item, value=f"$ {int(amount):,}")
    
    st.sidebar.markdown("---")
    
    # 貼心功能：提供刪除項目的按鈕，不然打錯字會一直留在左邊
    st.sidebar.subheader("🗑️ 管理項目")
    item_to_delete = st.sidebar.selectbox("選擇要刪除的項目", ["無"] + list(saved_items.keys()))
    if st.sidebar.button("刪除此項目"):
        if item_to_delete != "無":
            del saved_items[item_to_delete]
            # 存回 Cookie
            controller.set('saved_items', json.dumps(saved_items), max_age=31536000)
            st.sidebar.success(f"已刪除 {item_to_delete}")
            time.sleep(1)
            st.rerun()

# ================= 主畫面 =================
st.title("每月待繳金額計算 💰")

# 4. 輸入區塊
st.markdown("💡 **提示：** 只要輸入與左側相同的「繳費項目」名稱，就會自動載入總金額！")
item_name = st.text_input("繳費項目名稱 (例如：車貸、學貸)")

# 根據你打的名稱，去記憶卡裡面找錢。如果找不到(新項目)就預設為 0
default_total = int(saved_items.get(item_name, 0)) if item_name else 0

# 金額輸入框 (全部改為整數，拿掉小數點)
total_amount = st.number_input("總金額", value=default_total, step=100, format="%d")
add_amount = st.number_input("本月增加金額", value=0, step=100, format="%d")
pay_amount = st.number_input("本月已繳金額", value=0, step=100, format="%d")

# 5. 計算與按鈕
if st.button("開始計算並結轉下個月", type="primary", use_container_width=True):
    if not item_name.strip():
        st.error("⚠️ 請先輸入「繳費項目」名稱！")
    else:
        # 核心公式 (確保是整數)
        new_total = int(total_amount + add_amount - pay_amount)
        
        # 把算好的新金額，更新到字典裡面
        saved_items[item_name] = new_total
        
        # 🌟 重點：把包含多個項目的清單，打包存進手機的 Cookie 裡！
        controller.set('saved_items', json.dumps(saved_items), max_age=31536000)
        
        # 暫存進 session_state 以便畫面立刻更新顯示
        st.session_state.current_item = item_name
        st.session_state.current_total = new_total
        
        st.success(f"✅ 計算完成！已更新【{item_name}】的紀錄。")
        time.sleep(1) # 暫停 1 秒讓使用者看到成功訊息
        st.rerun()    # 重新整理畫面

# 6. 顯示當次計算結果
st.markdown("---")
if 'current_item' in st.session_state and 'current_total' in st.session_state:
    st.subheader(f"🏷️ {st.session_state.current_item} 的剩下待繳金額：")
    st.metric(label="目前待繳", value=f"$ {st.session_state.current_total:,}")
else:
    display_name = item_name if item_name else "該項目"
    st.subheader(f"🏷️ {display_name} 的剩下待繳金額：")
    st.metric(label="目前待繳", value=f"$ {default_total:,}")
