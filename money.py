import streamlit as st
import time
import json
from streamlit_local_storage import LocalStorage

# 1. 網頁基本設定
st.set_page_config(page_title="每月記帳", page_icon="💰", layout="centered")

# 2. 初始化 Local Storage 控制器 (改用更深層的手機記憶體)
localS = LocalStorage()
time.sleep(0.2) # 給手機一點點時間讀取記憶

# 3. 讀取之前的紀錄
saved_data = localS.getItem('saved_items')

# 確保讀取出來的資料正確轉換為 Python 字典
if saved_data and saved_data != "null":
    try:
        # 有時候套件會自動轉好，有時候是字串，這裡做雙重保險
        saved_items = json.loads(saved_data) if isinstance(saved_data, str) else saved_data
    except:
        saved_items = {}
else:
    saved_items = {}

# 定義按鈕行為
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
    
    for item, amount in saved_items.items():
        st.sidebar.button(
            f"📂 {item} : $ {int(amount):,}", 
            key=f"btn_{item}", 
            on_click=select_item,  
            args=(item,),          
            use_container_width=True
        )
    
    st.sidebar.markdown("---")
    
    # 刪除功能
    st.sidebar.subheader("🗑️ 刪除項目")
    item_to_delete = st.sidebar.selectbox("選擇要刪除的項目", ["無"] + list(saved_items.keys()))
    if st.sidebar.button("刪除此項目", type="secondary"):
        if item_to_delete != "無":
            del saved_items[item_to_delete]
            # 🌟 刪除後更新 Local Storage
            localS.setItem('saved_items', json.dumps(saved_items))
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
    st.button("➕ 建立新項目", on_click=clear_selection, use_container_width=True)

item_name = st.text_input("繳費項目名稱 (例如：車貸、學貸)", key="item_input")

default_total = int(saved_items.get(item_name, 0)) if item_name else 0

total_amount = st.number_input("總金額", value=default_total, step=100, format="%d")
add_amount = st.number_input("本月增加金額", value=0, step=100, format="%d")
pay_amount = st.number_input("本月已繳金額", value=0, step=100, format="%d")

# 5. 計算與按鈕
if st.button("開始計算並存檔", type="primary", use_container_width=True):
    if not item_name.strip():
        st.error("⚠️ 請先輸入「繳費項目」名稱！")
    else:
        new_total = int(total_amount + add_amount - pay_amount)
        saved_items[item_name] = new_total
        
        # 🌟 重點：存進 Local Storage 裡！(預設就是永久保存)
        localS.setItem('saved_items', json.dumps(saved_items))
        
        st.session_state.current_item = item_name
        st.session_state.current_total = new_total
        
        st.success(f"✅ 已更新【{item_name}】！目前剩下待繳：$ {new_total:,}")
        
        # 多等 1.5 秒，確保手機有足夠時間把資料寫入硬碟再重新整理
        time.sleep(1.5) 
        st.rerun()    

# 6. 顯示當次計算結果
st.markdown("---")
display_name = item_name if item_name else "該項目"
st.subheader(f"🏷️ {display_name} 的剩下待繳金額：")

display_amount = default_total
if 'current_item' in st.session_state and st.session_state.current_item == item_name:
    display_amount = st.session_state.current_total

st.metric(label="目前待繳", value=f"$ {display_amount:,}")
