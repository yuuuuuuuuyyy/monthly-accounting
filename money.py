import streamlit as st
import time
import json
from streamlit_cookies_controller import CookieController

# 1. 網頁基本設定
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

# 定義按鈕行為：點擊左側項目時，把該項目名稱填入主畫面的輸入框
if 'item_input' not in st.session_state:
    st.session_state.item_input = ""

def select_item(item_name):
    st.session_state.item_input = item_name

def clear_selection():
    st.session_state.item_input = ""

# ================= 左側欄 (Sidebar) =================
st.sidebar.title("📁 已存檔項目")

if not saved_items:
    st.sidebar.info("目前沒有存檔的項目。")
else:
    st.sidebar.markdown("👇 **點擊下方項目可載入修改**")
    
    # 將存檔項目變成「可點擊的按鈕」
    for item, amount in saved_items.items():
        st.sidebar.button(
            f"📂 {item} : $ {int(amount):,}", 
            key=f"btn_{item}", 
            on_click=select_item,  # 點擊時觸發的動作
            args=(item,),          # 傳遞項目名稱給動作
            use_container_width=True
        )
    
    st.sidebar.markdown("---")
    
    # 刪除功能
    st.sidebar.subheader("🗑️ 刪除項目")
    item_to_delete = st.sidebar.selectbox("選擇要刪除的項目", ["無"] + list(saved_items.keys()))
    if st.sidebar.button("刪除此項目", type="secondary"):
        if item_to_delete != "無":
            del saved_items[item_to_delete]
            # 存回 Cookie
            controller.set('saved_items', json.dumps(saved_items), max_age=31536000)
            # 如果刪除的剛好是現在畫面上的項目，就清空畫面
            if st.session_state.item_input == item_to_delete:
                st.session_state.item_input = ""
            st.sidebar.success(f"已刪除 {item_to_delete}")
            time.sleep(1)
            st.rerun()

# ================= 主畫面 =================
st.title("每月待繳金額計算 💰")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("💡 輸入名稱可**新增**，或從左側點選以**載入修改**")
with col2:
    # 點擊此按鈕會清空輸入框，方便建立新項目
    st.button("➕ 建立新項目", on_click=clear_selection, use_container_width=True)

# 輸入區塊 (綁定 session_state.item_input，達成連動效果)
item_name = st.text_input("繳費項目名稱 (例如：車貸、學貸)", key="item_input")

# 根據你打的名稱或點擊的名稱，去記憶卡裡面找錢。如果找不到(新項目)就預設為 0
default_total = int(saved_items.get(item_name, 0)) if item_name else 0

# 金額輸入框
total_amount = st.number_input("總金額", value=default_total, step=100, format="%d")
add_amount = st.number_input("本月增加金額", value=0, step=100, format="%d")
pay_amount = st.number_input("本月已繳金額", value=0, step=100, format="%d")

# 5. 計算與按鈕
if st.button("開始計算並存檔", type="primary", use_container_width=True):
    if not item_name.strip():
        st.error("⚠️ 請先輸入「繳費項目」名稱！")
    else:
        # 核心公式
        new_total = int(total_amount + add_amount - pay_amount)
        
        # 更新到字典裡面
        saved_items[item_name] = new_total
        
        # 存進手機的 Cookie 裡
        controller.set('saved_items', json.dumps(saved_items), max_age=31536000)
        
        # 暫存進 session_state 以便畫面立刻更新
        st.session_state.current_item = item_name
        st.session_state.current_total = new_total
        
        st.success(f"✅ 已更新【{item_name}】！目前剩下待繳：$ {new_total:,}")
        time.sleep(1) # 暫停 1 秒讓使用者看到成功訊息
        st.rerun()    # 重新整理畫面

# 6. 顯示當次計算結果
st.markdown("---")
display_name = item_name if item_name else "該項目"
st.subheader(f"🏷️ {display_name} 的剩下待繳金額：")

# 判斷要顯示剛算好的，還是舊有的
display_amount = default_total
if 'current_item' in st.session_state and st.session_state.current_item == item_name:
    display_amount = st.session_state.current_total

st.metric(label="目前待繳", value=f"$ {display_amount:,}")
