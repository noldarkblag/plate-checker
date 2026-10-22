import streamlit as st
import pandas as pd
import re
import urllib.parse

SHEET_ID = "1Rs4Emg2TPd373AnMfTtVVdoIE8n3YHRPB_6_ksXei8M"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Ang Folder ID kung saan nakatago ang lahat ng PDF Files
CVA_FOLDER_ID = "1ur4-5ItneFGrbaGYR90aLq-tkVYhlDYQ"

def convert_drive_url(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.search(r'(?:/d/|id=)([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return url

st.set_page_config(page_title="Plate Number Search", layout="wide")
st.title("🚗 Live Plate Number Search System")

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    search_plate = st.text_input("I-type ang Plate Number (hal. DBO4993):").strip().upper()

    if search_plate:
        result = df[df['Plate Number'].astype(str).str.strip().str.upper() == search_plate]
        
        if not result.empty:
            row = result.iloc[0]
            st.success(f"Nahanap ang record para sa Plate Number: **{search_plate}**")
            
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
                        st.link_button("👉 Buksan sa Drive", raw_link)
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
                        st.link_button("👉 Buksan sa Drive", raw_link_or)
                else:
                    st.write("Walang available na litrato.")
                    
            # Column E: Checklist / CVA (Direct PDF Search sa Folder)
            with col3:
                st.subheader("Checklist / CVA")
                # Direct na hahanapin ang PDF file na may pangalang [Plate Number] sa Drive Folder
                encoded_query = urllib.parse.quote(f"{search_plate}")
                pdf_search_url = f"https://drive.google.com/drive/folders/{CVA_FOLDER_ID}?q={encoded_query}"
                
                st.link_button(f"📄 Buksan ang {search_plate}.pdf", pdf_search_url)

        else:
            st.error("Walang nahanap na Plate Number.")

    if st.button("🔄 Refresh Data mula sa Google Sheet"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"Nagka-error sa pagkuha ng data mula sa Google Sheet: {e}")
