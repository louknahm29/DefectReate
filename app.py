import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเพจ Web App
st.set_page_config(page_title="Quality Control Dashboard", layout="wide")
st.title("📊 Production Quality Control Dashboard")

# 2. ฟังก์ชันโหลดข้อมูล (ปรับให้ชี้ไปยังไฟล์ Excel หรือ CSV ของคุณ)
@st.cache_data
def load_data():
    # โค้ดส่วนนี้เป็นการสร้างข้อมูลจำลองตามโครงสร้างข้อมูลจากไฟล์แนบของคุณ
    # ในการใช้งานจริง ให้เปลี่ยนเป็น pd.read_excel('your_file.xlsx', sheet_name='...')
    
    # ตัวอย่างข้อมูล Defect Rate (แปลงจากโครงสร้างคอลัมน์โรงงานให้เป็นแถวเพื่อให้ Filter ง่ายขึ้น)
    data = {
        'Date': pd.date_range(start='2026-01-09', periods=10, freq='D'),
        'Month': ['Jan']*10,
        'Year': ['2026']*10,
        'Section': ['Inline', 'Endline', 'Final', 'Cutting', 'Embalishment']*2,
        'Factory': ['HITCP4', 'HITSR', 'HIC', 'HIT91', 'HIT70']*2,
        'Defect_Rate': [80.40, 16.49, 40.92, 1.74, 8.48, 0, 0, 1.13, 1.31, 0.47]
    }
    df = pd.DataFrame(data)
    
    # ตัวอย่างข้อมูล Top 3 Defect
    top3_data = {
        'Date': pd.date_range(start='2026-01-09', periods=5, freq='D'),
        'Section': ['Inline', 'Endline', 'Final', 'Cutting', 'Embalishment'],
        'Top1': ['ผ้าเป็นตำหนิ', 'ตัวรีดเป็นตำหนิ', 'รอยเกี่ยวเกิดจากผ้า', 'รีดผิดหน้าผ้า', 'ไม่ได้สเปค'],
        'Top2': ['ตัวรีดหลุดลอก', 'ตัวรีดมีคราบกาว', 'ตัดเศษด้ายไม่เกลี้ยง', 'ผ้าเปื้อน', 'รีดเอียง'],
        'Top3': ['สีตัวรีดแตก', 'ผ้าติดริม', 'เย็บตกร่อง', 'ตัวรีดเปิด', 'ด้ายโดด']
    }
    df_top3 = pd.DataFrame(top3_data)
    
    return df, df_top3

df, df_top3 = load_data()

# 3. สร้าง Filter ด้านข้าง (Sidebar)
st.sidebar.header("🔍 Filters")

# ดึงค่าที่ไม่ซ้ำกันเพื่อสร้างตัวเลือก (Dropdown)
years = df['Year'].drop_duplicates()
months = df['Month'].drop_duplicates()
sections = ['Inline', 'Endline', 'Final', 'Cutting', 'Embalishment']
factories = df['Factory'].drop_duplicates()

year_choice = st.sidebar.selectbox('ปี (Year)', years)
month_choice = st.sidebar.selectbox('เดือน (Month)', months)
section_choice = st.sidebar.selectbox('แผนก (Section)', sections)
factory_choice = st.sidebar.selectbox('โรงงาน (Factory)', factories)

# การกรองข้อมูลด้วย Pandas 
filtered_df = df[(df['Year'] == year_choice) & 
                 (df['Month'] == month_choice) & 
                 (df['Section'] == section_choice) & 
                 (df['Factory'] == factory_choice)]

filtered_top3 = df_top3[(df_top3['Section'] == section_choice)]

# 4. ออกแบบสีสันให้สวยงามตามหลักการสร้าง Dashboard
# ใช้ชุดสี Classic Blue สำหรับความน่าเชื่อถือ และ Bold Contrast (Red) สำหรับจุดแจ้งเตือน
primary_color = "#288cfa" 
alert_color = "#FF0000"
bg_color = "#F5F5F5"

# 5. แสดงผล KPI Card และข้อมูล
st.markdown("### 📈 Key Performance Indicators (KPI)")
col1, col2, col3 = st.columns(3)

# คำนวณค่าเฉลี่ย Defect 
avg_defect = filtered_df['Defect_Rate'].mean() if not filtered_df.empty else 0

col1.metric(label="Selected Section", value=section_choice)
col2.metric(label="Selected Factory", value=factory_choice)
col3.metric(label="Average Defect Rate (%)", value=f"{avg_defect:.2f}%", delta="- Target 0%", delta_color="inverse")

st.divider()

# 6. สร้างกราฟ
col_chart, col_table = st.columns([6, 7])

with col_chart:
    st.markdown("#### 📊 Defect Rate Trend (%)")
    if not filtered_df.empty:
        # สร้าง Line Chart แสดงเทรนด์รายวัน
        fig = px.line(filtered_df, x='Date', y='Defect_Rate', markers=True, 
                      title=f"Defect Rate of {factory_choice} in {section_choice}",
                      color_discrete_sequence=[primary_color])
        # ปรับความสวยงาม
        fig.update_layout(plot_bgcolor=bg_color, xaxis_title="วันที่", yaxis_title="% Defect Rate")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับตัวกรองที่เลือก")

with col_table:
    st.markdown("#### 🏆 Top 3 Defects in Section")
    if not filtered_top3.empty:
        st.dataframe(filtered_top3[['Date', 'Top1', 'Top2', 'Top3']], use_container_width=True)
    else:
        st.info("ไม่มีข้อมูล Top 3 สำหรับแผนกที่เลือก")