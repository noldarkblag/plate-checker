import streamlit as st
import pandas as pd
import re
from datetime import datetime
import urllib.parse

# --- GOOGLE SHEET CONFIGURATION ---
SHEET_ID = "1Rs4Emg2TPd373AnMfTtVVdoIE8n3YHRPB_6_ksXei8M"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Ang Iisang Password para sa Lahat
FIXED_PASSWORD = "Mmampongan"

# Folder ID para sa CVA PDF Files
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

# Session States
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""
if "activity_logs" not in st.session_state:
    st.session_state["activity_logs"] = []

# Log Activity Function
def log_activity(username, action, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "Timestamp": timestamp,
        "Username": username,
        "Action": action,
        "Details": details
    }
    st.session_state["activity_logs"].append(log_entry)

# Load Data and Allowed Usernames (Plate Numbers)
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # Kukunin ang lahat ng Plate Numbers at Conduction Numbers sa Google Sheet bilang Valid Usernames
    valid_plates = set(df['Plate Number'].dropna().astype(str).str.strip().str.upper())
    
    cond_col = [col for col in df.columns if 'CONDUCTION' in col.upper()]
    if cond_col:
        valid_conductions = set(df[cond_col[0]].dropna().astype(str).str.strip().str.upper())
        valid_usernames = valid_plates.union(valid_conductions)
    else:
        valid_usernames = valid_plates

    # --- LOGIN SCREEN ---
    if not st.session_state["logged_in"]:
        st.title("🔒 System Login")
        
        login_col1, login_col2 = st.columns([1, 2])
        
        with login_col1:
            username_input = st.text_input("Username (Enter your Plate Number):").strip().upper()
            password_input = st.text_input("Password:", type="password").strip()
            login_btn = st.button("Login")

            if login_btn:
                # I-veverify kung ang Username ay nasa Google Sheet at tama ang Password
                if username_input in valid_usernames and password_input == FIXED_PASSWORD:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = username_input
                    log_activity(username_input, "LOGIN", "User logged into the system")
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Plate Number Username or Password.")

    # --- MAIN SYSTEM SCREEN ---
    else:
        # Sidebar with Logout & History Logs
        with st.sidebar:
            st.write(f"👤 Logged in Plate: **{st.session_state['current_user']}**")
            
            if st.button("🚪 Logout"):
                log_activity(st.session_state['current_user'], "LOGOUT", "User logged out")
                st.session_state["logged_in"] = False
                st.session_state["current_user"] = ""
                st.rerun()

            st.divider()
            st.subheader("📋 Session Search History")
            if st.session_state["activity_logs"]:
                logs_df = pd.DataFrame(st.session_state["activity_logs"])
                st.dataframe(logs_df[['Timestamp', 'Action', 'Details']], hide_index=True)
            else:
                st.caption("No activities recorded yet.")

        st.title("🚗 Live Vehicle Record Search System")

        search_col1, search_col2 = st.columns([1, 2])
        
        with search_col1:
            search_query = st.text_input("Enter Plate Number or Conduction Number:").strip().upper()

        if search_query:
            plate_match = df['Plate Number'].astype(str).str.strip().str.upper() == search_query
            
            if cond_col:
                cond_match = df[cond_col[0]].astype(str).str.strip().str.upper() == search_query
                result = df[plate_match | cond_match]
            else:
                result = df[plate_match]
            
            if not result.empty:
                row = result.iloc[0]
                plate_num = row.get('Plate Number', 'N/A')
                conduction_num = row.get(cond_col[0], 'N/A') if cond_col else 'N/A'
                
                log_activity(st.session_state['current_user'], "SEARCH", f"Searched for: {search_query} (Match: {plate_num})")

                st.success("Record Found!")
                
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
                    cva_link = str(row.get("Accountability and Checklist File's or CVA", "")).strip()
                    
                    if cva_link and cva_link.startswith("http"):
                        st.link_button(f"📄 Open {plate_num}.pdf", cva_link)
                    else:
                        search_term = plate_num if pd.notna(plate_num) and str(plate_num).strip() != '' else search_query
                        encoded_query = urllib.parse.quote(f"{search_term}")
                        pdf_search_url = f"https://drive.google.com/drive/folders/{CVA_FOLDER_ID}?q={encoded_query}"
                        st.link_button(f"📄 Open {search_term}.pdf", pdf_search_url)

            else:
                log_activity(st.session_state['current_user'], "SEARCH_FAILED", f"No record found for: {search_query}")
                st.error("No record found for the given Plate Number or Conduction Number.")

        if st.button("🔄 Refresh Data from Google Sheet"):
            st.cache_data.clear()
            st.rerun()

except Exception as e:
    st.error(f"Error loading data from Google Sheet: {e}")
