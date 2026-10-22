import streamlit as st
import pandas as pd
import re
import urllib.parse

SHEET_ID = "1Rs4Emg2TPd373AnMfTtVVdoIE8n3YHRPB_6_ksXei8M"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Google Drive Folder ID para sa CVA PDF files
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
st.title("🚗 Live Vehicle Record Search System")

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # Gagamit ng columns para paliitin ang lapad ng search input box
    search_col1, search_col2 = st.columns([1, 2])
    
    with search_col1:
        search_query = st.text_input("Enter Plate Number or Conduction Number:").strip().upper()

    if search_query:
        # Match Plate Number
        plate_match = df['Plate Number'].astype(str).str.strip().str.upper() == search_query
        
        # Match Conduction Number Column
        cond_col = [col for col in df.columns if 'CONDUCTION' in col.upper()]
        if cond_col:
            cond_match = df[cond_col[0]].astype(str).str.strip().str.upper() == search_query
            result = df[plate_match | cond_match]
        else:
            result = df[plate_match]
        
        if not result.empty:
            row = result.iloc[0]
            
            plate_num = row.get('Plate Number', 'N/A')
            conduction_num = row.get(cond_col[0], 'N/A') if cond_col else 'N/A'
            
            st.success("Record Found!")
            
            # Header Details
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.write(f"🚘 **Plate Number:** {plate_num}")
            with info_col2:
                st.write(f"🏷️ **Conduction No.:** {conduction_num}")
            with info_col3:
                if 'Accounted to' in row and pd.notna(row['Accounted to']):
                    st.write(f"👤 **Accounted to:** {row['Accounted to']}")

            st.divider()

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
                        st.warning("Image preview not available.")
                        st.link_button("👉 Open in Drive", raw_link)
                else:
                    st.write("No image available.")
                    
            # Column D: OR 2026
            with col2:
                st.subheader("OR 2026")
                raw_link_or = row.get('OR 2026')
                or_url = convert_drive_url(raw_link_or)
                if or_url:
                    try:
                        st.image(or_url, use_container_width=True)
                    except Exception:
                        st.warning("Image preview not available.")
                        st.link_button("👉 Open in Drive", raw_link_or)
                else:
                    st.write("No image available.")
                    
            # Column E: Checklist / CVA
            with col3:
                st.subheader("Checklist / CVA")
                search_term = plate_num if pd.notna(plate_num) and str(plate_num).strip() != '' else search_query
                encoded_query = urllib.parse.quote(f"{search_term}")
                pdf_search_url = f"https://drive.google.com/drive/folders/{CVA_FOLDER_ID}?q={encoded_query}"
                
                st.link_button(f"📄 Open {search_term}.pdf", pdf_search_url)

        else:
            st.error("No record found for the given Plate Number or Conduction Number.")

    if st.button("🔄 Refresh Data from Google Sheet"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"Error loading data from Google Sheet: {e}")
