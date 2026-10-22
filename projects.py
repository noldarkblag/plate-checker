import streamlit as st
import pandas as pd
import re

# Direct link sa CSV export ng iyong Google Sheet
SHEET_ID = "1Rs4Emg2TPd373AnMfTtVVdoIE8n3YHRPB_6_ksXei8M"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Function para gawing Direct Display Image Link ang Google Drive URL
def convert_drive_url(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    # Kukunin ang File ID mula sa Google Drive URL
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    return url

st.set_page_config(page_title="Plate Number Search", layout="wide")
st.title("🚗 Live Plate Number Search System")

@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # Search Bar Input
    search_plate = st.text_input("I-type ang Plate Number (hal. DBO4993):").strip().upper()

    if search_plate:
        # Hahanapin ang Plate Number sa Column 'Plate Number'
        result = df[df['Plate Number'].astype(str).str.strip().str.upper() == search_plate]
        
        if not result.empty:
            row = result.iloc[0]
            st.success(f"Nahanap ang record para sa Plate Number: **{search_plate}**")
            
            # Accounted to Details
            if 'Accounted to' in row and pd.notna(row['Accounted to']):
                st.info(f"👤 **Accounted to:** {row['Accounted to']}")

            col1, col2, col3 = st.columns(3)
            
            # Column C: Certificate of Registration
            with col1:
                st.subheader("Certificate of Registration")
                raw_link = row.get('Certificate of Registration')
                img_url = convert_drive_url(raw_link)
                if img_url:
                    try:
                        st.image(img_url, use_container_width=True)
                    except Exception:
                        st.warning("Hindi ma-preview ang larawan.")
                        st.markdown(f"👉 [I-click para buksan sa Drive]({raw_link})")
                else:
                    st.write("Walang available na litrato.")
                    
            # Column D: OR 2026
            with col2:
                st.subheader("OR 2026")
                raw_link_or = row.get('OR 2026')
                or_url = convert_drive_url(raw_link_or)
                if or_url:
                    try:
                        st.image(or_url, use_container_width=True)
                    except Exception:
                        st.warning("Hindi ma-preview ang larawan.")
                        st.markdown(f"👉 [I-click para buksan sa Drive]({raw_link_or})")
                else:
                    st.write("Walang available na litrato.")
                    
            # Column E: Accountability and Checklist File's or CVA
            with col3:
                st.subheader("Checklist / CVA")
                cva_raw_link = row.get("Accountability and Checklist File's or CVA")
                if pd.notna(cva_raw_link):
                    st.markdown(f"📄 **[I-click para buksan ang CVA File]({cva_raw_link})**")
                else:
                    st.write("Walang file.")
        else:
            st.error("Walang nahanap na Plate Number.")

    if st.button("🔄 Refresh Data mula sa Google Sheet"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"Nagka-error sa pagkuha ng data mula sa Google Sheet: {e}")