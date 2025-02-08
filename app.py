import streamlit as st
import pandas as pd
import time
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder


@st.cache_data
def load_data():
    return pd.read_excel("test.xlsx")   

st.set_page_config(layout="wide", page_title="📊 داشبورد فروش و پورسانت")


st.markdown("""
    <style>
        .big-font { font-size:80px !important; text-align: center; color: #222; font-weight: bold; }
        .stApp { background-color: #f8f9fa; }
        .ag-theme-streamlit {
            --ag-header-background-color: #007bff !important;
            --ag-header-text-color: white !important;
            --ag-odd-row-background-color: #f0f8ff !important;
            --ag-even-row-background-color: #e6f7ff !important;
            --ag-font-size: 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)


data = load_data()

branches = data["Branch"].unique()
selected_branch = st.selectbox("🏢 لطفاً شعبه مورد نظر را انتخاب کنید:", branches)

filtered_data = data[data["Branch"] == selected_branch]


sellers = filtered_data["Name"].unique()

if len(sellers) == 0:
    st.warning("⚠ هیچ فروشنده‌ای در این شعبه یافت نشد!")
    st.stop()

if "seller_index" not in st.session_state:
    st.session_state.seller_index = 0


current_seller = sellers[st.session_state.seller_index]

seller_data = filtered_data[filtered_data["Name"] == current_seller].copy()

if seller_data.empty:
    st.warning("⚠ هیچ داده‌ای برای این فروشنده موجود نیست!")
    st.stop()


required_columns = {"Ctg", "Sale", "Tgt", "%Achivement", "commesion"}
if not required_columns.issubset(seller_data.columns):
    st.error("🚨 برخی از ستون‌های موردنیاز در داده‌ها وجود ندارند!")
    st.stop()

seller_data["%Achivement"] = pd.to_numeric(
    seller_data["%Achivement"], errors="coerce"
) * 100
seller_data["%Achivement"] = seller_data["%Achivement"].round(2).astype(str) + " %"

for col in ["Sale", "Tgt", "commesion"]:
    seller_data[col] = seller_data[col].apply(lambda x: f"{x:,.0f}")


st.markdown(f"<p class='big-font'>📌 فروشنده: {current_seller}</p>", unsafe_allow_html=True)


gb = GridOptionsBuilder.from_dataframe(seller_data[["Ctg", "Sale", "Tgt", "%Achivement", "commesion"]])
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
gb.configure_grid_options(domLayout='autoHeight') 
grid_options = gb.build()

st.write("📋 **جدول اطلاعات فروشنده:**")
AgGrid(
    seller_data[["Ctg", "Sale", "Tgt", "%Achivement", "commesion"]],
    gridOptions=grid_options,
    fit_columns_on_grid_load=True,  # تنظیم خودکار عرض ستون‌ها
    height=min(800, len(seller_data) * 40),  # افزایش ارتفاع جدول
    theme="streamlit",  # 🎨 تم رنگی جذاب
)

y_values = pd.to_numeric(seller_data["%Achivement"].str.replace(" %", ""), errors="coerce")

fig = px.bar(
    seller_data,
    x="Ctg",
    y=y_values,
    title="📈 درصد تحقق هدف برای هر کتگوری",
    labels={"y": "درصد تحقق هدف", "Ctg": "دسته‌بندی"},
    color=y_values,
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("⏭ فروشنده بعدی"):
        st.session_state.seller_index = (st.session_state.seller_index + 1) % len(sellers)
        st.rerun()

time.sleep(10)
st.session_state.seller_index = (st.session_state.seller_index + 1) % len(sellers)
st.rerun()
