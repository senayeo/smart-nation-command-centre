import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2

# --- THIRD-PARTY EMBEDDED INTEGRATION: TWILIO MESSAGING OPERATIONS API ---
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

st.set_page_config(page_title="Command Console: Operations Backend", layout="centered", page_icon="🌐")

st.markdown("""
    <style>
        /* SYSTEM FIX: Tightly condenses the centered app container column to 850px for a clean card layout */
        .block-container {
            max-width: 768px !important;
        }
        /* Sets a balanced width constraint for the data field container boxes */
        div[data-baseweb="input"] {
            max-width: 200px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Systemic database settings table initialization
def init_system_config_tables():
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value REAL
        );
    """)
    cursor.execute("INSERT INTO system_config (key, value) VALUES ('fill_threshold', 75.0) ON CONFLICT (key) DO NOTHING;")
    cursor.execute("INSERT INTO system_config (key, value) VALUES ('lid_threshold', 5.0) ON CONFLICT (key) DO NOTHING;")
    cursor.execute("INSERT INTO system_config (key, value) VALUES ('pir_threshold', 10.0) ON CONFLICT (key) DO NOTHING;")
    cursor.execute("INSERT INTO system_config (key, value) VALUES ('ai_threshold', 3.0) ON CONFLICT (key) DO NOTHING;")
    cursor.execute("INSERT INTO system_config (key, value) VALUES ('relay_threshold', 8.0) ON CONFLICT (key) DO NOTHING;")
    conn.commit()
    cursor.close()
    conn.close()

init_system_config_tables()

st.title("📡 Smart Nation Public Hygiene SensorGrid Hub")
st.markdown("""
    <div style='font-family: Arial, sans-serif; font-size: 11px; color: #7F8C8D; line-height: 1.5; margin-top: -15px; margin-bottom: 25px;'>
        <div style='display: inline-block; background-color: #FFF0F0; color: #C0392B; border: 1px solid #E74C3C; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; margin-bottom: 8px; letter-spacing: 0.5px;'>
            🔒 RESTRICTED ACCESS • AUTHORISED GOVTECH / OGP DEVELOPER UAT SANDBOX
        </div>
        <div style='color: #64748B; font-weight: 500;'>🏢 SYSTEMS ENGINEERING & EVALUATION INGESTION HUB</div>
        <div style='color: #94A3B8; font-style: italic; font-size: 10.5px; margin-top: 2px;'>📦 Framework Module: Independent Simulation Pipeline Engine for Mock Telemetry Data Ingestion Architecture</div>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# --- APPARATUS MANAGEMENT SEGMENT: LIVE INTERFACE SECURITY CREDENTIALS ---
# =========================================================================
st.markdown("### 🔑 Staff API Access Credentials")
with st.expander("Configure Twilio Master Gateway & Staff API Routing Keys", expanded=False):
    st.markdown("""
    This framework utilises the **Twilio API Gateway** to broadcast real-time, automated public safety notifications to WhatsApp channels. To execute live demonstration testing:
    1. **Provision a Free Gateway:** Initialise a developer trial account via the main Twilio Console dashboard.
    2. **Authenticate Recipient Device:** Pair your mobile device by texting your assigned sandbox verification string to the Twilio system number.
    3. **Link API Endpoint Keys:** Paste your secure credentials below to bridge the live telemetry event triggers.
    """)
    
    # SYSTEM UPGRADE FIXED: Restricts text box widths cleanly using your proportional layout formula
    col_sid, _ = st.columns([4.5, 3.5])
    with col_sid:
        account_sid = st.text_input("Account SID:", value="", type="password", help="Paste your master Twilio Account SID string line.")
        
    col_tok, _ = st.columns([4.5, 3.5])
    with col_tok:
        auth_token = st.text_input("Auth Token:", value="", type="password", help="Reveal and copy your secure token signature.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Device Channel Routing Parameters")
    
    col_pho, _ = st.columns([2.3, 3.5])
    with col_pho:
        target_phone = st.text_input("Recipient Mobile Phone Number:", value="", help="Include country prefix, e.g., +6591234567")
        
    col_snd, _ = st.columns([2.3, 3.5])
    with col_snd:
        sandbox_sender = st.text_input("Twilio Sandbox Sender Origin Number:", value="+14155238886", help="The pre-allocated sandbox broadcast line.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🏢 Facility Selection Target Routing")

supabase_uri = st.secrets["SUPABASE_URI"]
conn = psycopg2.connect(supabase_uri)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT nea_division FROM hawker_registry WHERE nea_division IS NOT NULL;")
raw_divs = cursor.fetchall()
cursor.close()
conn.close()

div_options = []
for row in raw_divs:
    (db_div_name,) = row
    if db_div_name.strip(): div_options.append(db_div_name.strip())

st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 4px;">Select Target NEA Regional Office Jurisdiction:</p>', unsafe_allow_html=True)
col_div_drop, _ = st.columns([2, 2.5])
with col_div_drop:
    selected_div = st.selectbox("Select Target NEA Regional Office Jurisdiction:", div_options, label_visibility="collapsed")

supabase_uri = st.secrets["SUPABASE_URI"]
conn = psycopg2.connect(supabase_uri)
cursor = conn.cursor()
cursor.execute("SELECT hawker_centre FROM hawker_registry WHERE nea_division = %s ORDER BY hawker_centre;", (selected_div,))
center_rows = cursor.fetchall()
cursor.close()
conn.close()

center_list = [r for (r,) in center_rows]
st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 4px;">Select Target Hawker Centre Location:</p>', unsafe_allow_html=True)
col_center_drop, _ = st.columns([6.8, 2.5])
with col_center_drop:
    selected_center = st.selectbox("Select Target Hawker Centre Location:", center_list, label_visibility="collapsed")

supabase_uri = st.secrets["SUPABASE_URI"]
conn = psycopg2.connect(supabase_uri)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT zone_cluster FROM nea_telemetry WHERE hawker_centre = %s ORDER BY zone_cluster;", (selected_center,))
zone_rows = cursor.fetchall()
cursor.close()
conn.close()

zone_list = [z for (z,) in zone_rows]

st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 4px;">Select Target Master Node Mesh Cluster Zone:</p>', unsafe_allow_html=True)
col_dropdown, _ = st.columns([0.8, 5])
with col_dropdown:
    selected_zone = st.selectbox("Select Target Master Node Mesh Cluster Zone:", zone_list, label_visibility="collapsed")

st.markdown("<hr>", unsafe_allow_html=True)

# Helper function to extract latest historical baseline database records for pre-fill synchronization
def fetch_latest_telemetry_defaults():
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fill_level, lid_breaches_count, pir_wakeups_count, rat_detections_count, deterrence_triggered 
        FROM nea_telemetry 
        WHERE hawker_centre = %s AND zone_cluster = %s 
        ORDER BY timestamp DESC LIMIT 1;
    """, (selected_center, selected_zone))
    res = cursor.fetchone()
    cursor.close()
    conn.close()

    if res:
        return {"fill": int(res[0]), "lids": int(res[1]), "pir": int(res[2]), "rats": int(res[3]), "relays": int(res[4])}
    return {"fill": 35, "lids": 2, "pir": 4, "rats": 0, "relays": 0}

db_defaults = fetch_latest_telemetry_defaults()

# Helper function to modularize Twilio dispatches cleanly
def dispatch_twilio_whatsapp(msg_payload):
    # SYSTEM FIX: This helper now successfully transmits your unrestricted full alert paragraph during the open 24-hour sandbox testing window
    if not account_sid or not auth_token or not target_phone:
        st.info("💡 Presentation Simulation Mode: Alert compiled successfully!")
        st.code(msg_payload, language="markdown")
    elif not TWILIO_AVAILABLE:
        st.error("System Environment Failure: Twilio module missing.")
    else:
        try:
            client = Client(account_sid, auth_token)
            
            # SYSTEM FIX: Transmits your dense, custom project warning message directly with full type-safety
            message = client.messages.create(
                from_=f"whatsapp:{sandbox_sender}",
                body=f"🚨 {msg_payload}",
                to=f"whatsapp:{target_phone}"
            )
            st.success(f"📱 API Live Push Success! WhatsApp notification dispatched. SID: {message.sid}")
        except Exception as e:
            st.error(f"Twilio Core Gateway Communication Failure: {str(e)}")

# Initialize the tab layouts
tab1, tab2, tab3 = st.tabs(["🚛 Waste Operations", "🌙 Night Surveillance", "⚙️ Countermeasure Diagnostics"])

with tab1:
    st.markdown("### 🚛 Day-time Smart Waste Management & Central SLA Ingestion Node") 
    st.caption("GovTech Central Sandbox: **Pre-Deployment UAT & Town Council / Social Enterprise SLA Audit Node**")
    
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'fill_threshold';")
    t1_fill_thresh = cursor.fetchone()
    cursor.execute("SELECT value FROM system_config WHERE key = 'lid_threshold';")
    t1_lid_thresh = cursor.fetchone()
    cursor.execute("SELECT COUNT(DISTINCT stall_id) FROM nea_telemetry WHERE hawker_centre = %s;", (selected_center,))
    stalls_query = cursor.fetchone()
    cursor.close()
    conn.close()
    
    t1_f_val = t1_fill_thresh[0] if t1_fill_thresh else 75.0
    t1_l_val = t1_lid_thresh[0] if t1_lid_thresh else 5.0
    total_stalls_count = int(stalls_query[0]) if stalls_query and stalls_query[0] is not None else 84
    
    # Restores your dynamic partitioning algorithms completely to calculate accurate cluster bounds early
    if total_stalls_count >= 170:   num_zones = 20
    elif total_stalls_count >= 120: num_zones = 17
    elif total_stalls_count >= 70:  num_zones = 12
    elif total_stalls_count >= 40:  num_zones = 6
    else:                           num_zones = 3
        
    import math
    stalls_per_zone = int(math.ceil(total_stalls_count / num_zones))
    
    # SYSTEM FIX: Row 1 holds the description text labels on a uniform horizontal row
    col_txt1, col_txt2 = st.columns(2)
    with col_txt1:
        st.markdown('<p style="color: #31333F; font-size: 13.5px; white-space: nowrap; margin-bottom: 12px;">Set Feature 1 Mean Zone Fill Level Alert Threshold (%):</p>', unsafe_allow_html=True)
    with col_txt2:
        st.markdown('<p style="color: #31333F; font-size: 13.5px; white-space: nowrap; margin-bottom: 12px;">Set Feature 1 Maximum Allowed Open Lids Threshold (Units):</p>', unsafe_allow_html=True)
        
    # Row 2 holds the actual interactive tracking lines to force absolute horizontal alignment
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        new_t1_f_thresh = st.slider("Define F1: Mean Zone Fill Level Alert Threshold (%):", min_value=65.0, max_value=85.0, value=float(t1_f_val), step=5.0, key="slider_t1_fill", label_visibility="collapsed")

    with col_s2:
        # SYSTEM UPGRADE FIXED: Employs a dynamic key rotation index to force the physical UI handle to re-render back to compliance
        risk_limit_cap = float(max(1, stalls_per_zone // 2))
        slider_ceiling = float(stalls_per_zone)
        
        # Initialize state memory and layout version indicators
        if "t1_lid_slider_state" not in st.session_state:
            st.session_state.t1_lid_slider_state = min(float(t1_l_val), risk_limit_cap)
        if "slider_version" not in st.session_state:
            st.session_state.slider_version = 0

        # Define the instant callback logic to manipulate states and force widget key rotation
        def enforce_lid_threshold_ceiling():
            # Fix: Dynamically checks for your exact active key to prevent initialization errors
            key_name = f"current_lid_slider_val_v{st.session_state.slider_version}"
            if key_name not in st.session_state:
                return
                
            raw_input_val = st.session_state[key_name]
            if raw_input_val > risk_limit_cap:
                st.session_state.t1_lid_slider_state = risk_limit_cap
                st.session_state.slider_version += 1  # Forces Streamlit to instantly redraw the widget handle position
                st.toast(f"⚠️ **SLA Constraint Enforced:** GovTech regulations cap maximum allowed open lids at 50% of zone capacity ({int(risk_limit_cap)} bins). Defaulting target configuration to limit threshold.", icon="🛡️")
            else:
                st.session_state.t1_lid_slider_state = raw_input_val

        # Render the physical widget tracking against a dynamically rotating key identity
        st.slider(
            "Define F1: Cumulative Zone Lid Breaches Alert Threshold (Incidents):",
            min_value=1.0,
            max_value=slider_ceiling,
            step=1.0,
            key=f"current_lid_slider_val_v{st.session_state.slider_version}",
            value=st.session_state.t1_lid_slider_state,
            on_change=enforce_lid_threshold_ceiling,
            label_visibility="collapsed"
        )
        
        new_t1_l_thresh = st.session_state.t1_lid_slider_state
    
    if new_t1_f_thresh != t1_f_val or new_t1_l_thresh != t1_l_val:
        supabase_uri = st.secrets["SUPABASE_URI"]
        conn = psycopg2.connect(supabase_uri)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_config SET value = %s WHERE key = 'fill_threshold';", (new_t1_f_thresh,))
        cursor.execute("UPDATE system_config SET value = %s WHERE key = 'lid_threshold';", (new_t1_l_thresh,))
        conn.commit()
        cursor.close()
        conn.close()
        st.toast("✅ Day-time operational threshold rules updated!", icon="⚙️")
        
    st.markdown("---")
    st.markdown("**Manually Enter Live Day-time Sensor Values:**")
    
    # Double column packing for narrow input boxes
    col_inp1, col_inp2 = st.columns(2)
    with col_inp1:
        st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 8px;">Simulated Telemetry Input: Mean Zone Fill Level (%)</p>', unsafe_allow_html=True)
        col_w1, _ = st.columns([1.5, 2.5])
        with col_w1:
            # SYSTEM FIX: Expands max_value to 200 so the box lets you type in extreme test parameters without forcing it to 0%
            inp_fill = st.number_input(label="Simulated Telemetry Input: Mean Zone Fill Level (%)", min_value=0, max_value=100, value=db_defaults.get("fill", 0), step=1, key="inp_fill", label_visibility="collapsed")
    with col_inp2:
        st.markdown("<p style='color: #31333F; font-size: 14px; margin-bottom: 8px;'>Simulated Telemetry Input: Open Bins (<100% Fill, >5 Mins)</p>", unsafe_allow_html=True)
        col_w2, _ = st.columns([1.4, 2.5])
        with col_w2:
            # SYSTEM FIX: Expands max_value to 100 so you can type large entries to explicitly trigger the orange error block
            inp_lids = st.number_input(label="Simulated Telemetry Input: Open Bins (<100% Fill, >5 Mins)", min_value=0, max_value=50, value=db_defaults.get("lids", 0), step=1, key="inp_lids", label_visibility="collapsed")
 
    if st.button("🚀 Push Day-time Telemetry & Test GovTech SensorGrid Alert Routing API", use_container_width=True, key="btn_t1"):
        # UI SAFETY GATE: Instantly catches manual parameter inflation, fires an orange warning banner, and intercepts code execution path cleanly
        # SYSTEM FIX: Separates validation paths so error text only fires for the exact parameter breaking reality
        if inp_fill > 100 and int(inp_lids) > stalls_per_zone:
            warning_msg = (
                "⚠️ **[GovTech SensorGrid Telemetry Validation Error]** The submitted data packet contains mathematically impossible parameters for the selected zone cluster.\n\n"
                f"• Simulated Mean Zone Fill Level entered is **{int(inp_fill)}%**, which exceeds absolute maximum volume capacity (100%).\n\n"
                f"• Simulated Current Count of Left-Open Lids entered is **{int(inp_lids)}**, which exceeds the calculated physical stall capacity of this zone cluster ({stalls_per_zone} stalls).\n\n"
                "**Execution Halted:** Central registry data insertion blocked due to telemetry parameter inflation."
            )
            st.warning(warning_msg)
            st.stop()
        elif inp_fill > 100:
            warning_msg = (
                "⚠️ **[GovTech SensorGrid Telemetry Validation Error]** The submitted data packet contains mathematically impossible parameters for the selected zone cluster.\n\n"
                f"• Simulated Mean Zone Fill Level entered is **{int(inp_fill)}%**, which exceeds absolute maximum volume capacity (100%).\n\n"
                "**Execution Halted:** Central registry data insertion blocked due to telemetry parameter inflation."
            )
            st.warning(warning_msg)
            st.stop()
        elif int(inp_lids) > stalls_per_zone:
            warning_msg = (
                "⚠️ **[GovTech SensorGrid Telemetry Validation Error]** The submitted data packet contains mathematically impossible parameters for the selected zone cluster.\n\n"
                f"• Simulated Current Count of Left-Open Lids entered is **{int(inp_lids)}**, which exceeds the calculated physical stall capacity of this zone cluster ({stalls_per_zone} stalls).\n\n"
                "**Execution Halted:** Central registry data insertion blocked due to telemetry parameter inflation."
            )
            st.warning(warning_msg)
            st.stop()

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        supabase_uri = st.secrets["SUPABASE_URI"]
        conn = psycopg2.connect(supabase_uri)
        historical_logs = pd.read_sql_query('SELECT fill_level, lid_breaches_count FROM nea_telemetry WHERE hawker_centre = %s AND zone_cluster = %s ORDER BY timestamp DESC LIMIT 3;', conn, params=(selected_center, selected_zone))
        rolling_fill_mean = (historical_logs['fill_level'].sum() + inp_fill) / (len(historical_logs) + 1) if not historical_logs.empty else inp_fill
        rolling_lid_sum = historical_logs['lid_breaches_count'].sum() + inp_lids if not historical_logs.empty else inp_lids
        
        cursor = conn.cursor()
        cursor.execute("SELECT nea_division FROM hawker_registry WHERE hawker_centre = %s;", (selected_center,))
        reg_data = cursor.fetchone()
        db_division = reg_data[0] if reg_data and reg_data[0] else selected_div
        
        cursor.execute("SELECT stall_id FROM nea_telemetry WHERE hawker_centre = %s AND zone_cluster = %s LIMIT 1;", (selected_center, selected_zone))
        stall_row = cursor.fetchone()
        db_stall_id = stall_row[0] if stall_row and stall_row[0] else "STALL-001"
        
        cursor.execute("""
            INSERT INTO nea_telemetry (timestamp, nea_division, hawker_centre, stall_id, zone_cluster, fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0, 0);
        """, (now_str, db_division, selected_center, db_stall_id, selected_zone, float(inp_fill), float(inp_lids)))
        conn.commit()
        cursor.close()
        conn.close()
        
        st.success("🎉 Day-time telemetry packet logged into the central database registry successfully!")
        
        # SYSTEM UPGRADE FIXED: Computes dynamic, consecutive stall block bounds to match the updated seed_db array rules
        if inp_fill > new_t1_f_thresh or inp_lids > new_t1_l_thresh:
            
            # Step 1: Initialize our clean operational alphabet skipping the letter 'O'
            clean_alphabet = [chr(i) for i in range(65, 91) if i != 79]
            current_zone_char = str(selected_zone).upper().strip()
            
            try:
                target_zone_idx = clean_alphabet.index(current_zone_char)
            except ValueError:
                target_zone_idx = 0
                
            base_offset = target_zone_idx * stalls_per_zone
            
            # Formulate consecutive stall strings while strictly capping them at the building's physical capacity limit
            stalls_in_chosen_zone = []
            for i in range(1, stalls_per_zone + 1):
                allocated_num = base_offset + i
                if allocated_num <= total_stalls_count:
                    stalls_in_chosen_zone.append(f"STALL-{allocated_num:03d}")
            
            # Step 5: FIXED - Unifies dynamic mathematical distribution to isolate open lids that do NOT overlap with overflowing bins
            import random
            import math
            
            seed_hash = hash(str(selected_center) + str(selected_zone)) & 0xFFFFFFFF
            random.seed(seed_hash)
            
            shuffled_zone_pool = list(stalls_in_chosen_zone)
            random.shuffle(shuffled_zone_pool)
            
            # 1. Isolate the overflowing bins using continuous proportional scaling
            if inp_fill > new_t1_f_thresh:
                total_zone_capacity = len(shuffled_zone_pool)
                range_span = max(1.0, 100.0 - new_t1_f_thresh)
                penetration_ratio = (inp_fill - new_t1_f_thresh) / range_span
                fill_trigger_count = max(1, int(math.ceil(penetration_ratio * total_zone_capacity)))
            else:
                fill_trigger_count = 0
                
            overflow_stalls = shuffled_zone_pool[:fill_trigger_count] if shuffled_zone_pool else []
            remaining_pool = [s for s in shuffled_zone_pool if s not in overflow_stalls]
            
            # 2. Extract separate, non-overlapping stalls for your input of lids left open with nominal volumes
            input_lids_count = int(inp_lids)
            lids_only_stalls = remaining_pool[:min(len(remaining_pool), input_lids_count)]
            
            # 3. Dynamically compile the evidence rows, completely hiding any row that evaluates to empty
            matrix_rows = []
            
            if overflow_stalls:
                overflow_str = ", ".join(sorted(overflow_stalls))
                matrix_rows.append(f"• Bins Overflowing & Lids Open (Critical Vector Risk): {overflow_str}")
                
            if lids_only_stalls:
                lids_str = ", ".join(sorted(lids_only_stalls))
                matrix_rows.append(f"• Bins Left Open But Not Overflowing (Housekeeping Risk): {lids_str}")
                
            if not matrix_rows:
                matrix_rows.append("• Operational Baseline: All monitored zone nodes reporting within standard parameters.")
                
            evidence_matrix_payload = "\n".join(matrix_rows)

            conn_sync = psycopg2.connect(supabase_uri)
            cursor_sync = conn_sync.cursor()
            cursor_sync.execute("UPDATE system_config SET value = %s WHERE key = 'fill_threshold';", (float(new_t1_f_thresh),))
            cursor_sync.execute("UPDATE system_config SET value = %s WHERE key = 'lid_threshold';", (float(new_t1_l_thresh),))
            conn_sync.commit()
            cursor_sync.close()
            conn_sync.close()
            
            # Step 6: Combined evidence matrices and refined enforcement phrasing to accurately reflect GovTech's institutional data logging boundaries
            if inp_fill > new_t1_f_thresh and inp_lids > new_t1_l_thresh:
                banner_title = "CRITICAL METRIC ANOMALY: DUAL INFRASTRUCTURE SLA BREACH"
                payload = "*[GovTech Smart Nation Alert]*\n*[Pre-emptive Waste Management SLA Violation]*\n\n📥 *Target Action Unit:* Town Council / Operator Management\n🏛️ *Facility:* " + str(selected_center) + " [Zone " + str(selected_zone) + "] Jurisdiction: NEA " + str(selected_div) + "\n🚨 *Status:* Central data logging verifies concurrent threshold breaches. Zone overall Mean Fill Level has reached " + str(int(inp_fill)) + "% (SLA Target: < " + str(int(new_t1_f_thresh)) + "%), alongside a Current Count of " + str(int(inp_lids)) + " bins left open but not overflowing (SLA Target: < " + str(int(new_t1_l_thresh)) + " units).\n\n🗂️ *Evidence Matrix - High-Volume Outlier Violations:*\n" + str(evidence_matrix_payload) + "\n\n⚡ *System Dispatch Notice:* Telemetry logs confirm active public hygiene threshold violations. Review analysed trend charts on your local terminal dashboard to cross-examine these live anomalies against historical 4-block rolling average trends."
            elif inp_fill > new_t1_f_thresh:
                banner_title = "CRITICAL METRIC ANOMALY: WASTE VOLUME SLA BREACH"
                payload = "*[GovTech Smart Nation Alert]*\n*[Pre-emptive Waste Management SLA Violation]*\n\n📥 *Target Action Unit:* Town Council / Operator Management\n🏛️ *Facility:* " + str(selected_center) + " [Zone " + str(selected_zone) + "] Jurisdiction: NEA " + str(selected_div) + "\n📈 *Status:* Central data logging verifies a waste volume SLA breach. Zone overall Mean Fill Level has reached " + str(int(inp_fill)) + "% (SLA Target: < " + str(int(new_t1_f_thresh)) + "%). Current Count of Bins Left Open But Not Overflowing is " + str(int(inp_lids)) + " units, which remains within nominal operating tolerances (SLA Target: < " + str(int(new_t1_l_thresh)) + " units).\n\n⚠️ *Identified Anomalies & Baseline Tracking:*\n" + str(evidence_matrix_payload) + "\n\n⚡ *System Dispatch Notice:* Telemetry logs confirm active public hygiene threshold violations. Review analysed trend charts on your local terminal dashboard to cross-examine these live anomalies against historical 4-block rolling average trends."
            else:
                banner_title = "CRITICAL METRIC ANOMALY: PHYSICAL LID EXPOSURE SLA BREACH"
                payload = "*[GovTech Smart Nation Alert]*\n*[Pre-emptive Waste Management SLA Violation]*\n\n📥 *Target Action Unit:* Town Council / Operator Management\n🏛️ *Facility:* " + str(selected_center) + " [Zone " + str(selected_zone) + "] Jurisdiction: NEA " + str(selected_div) + "\n🪟 *Status:* Central data logging verifies a lid exposure SLA breach. Current Count of bins left open but not overflowing has reached " + str(int(inp_lids)) + " units sitting continuously open for over 5 minutes (SLA Target: < " + str(int(new_t1_l_thresh)) + " units). Zone overall Mean Fill Level is " + str(int(inp_fill)) + "%, which remains within nominal operating tolerances (SLA Target: < " + str(int(new_t1_f_thresh)) + "%).\n\n⚠️ *Identified Anomalies & Baseline Tracking:*\n" + str(evidence_matrix_payload) + "\n\n⚡ *System Dispatch Notice:* Telemetry logs confirm active public hygiene threshold violations. Review analysed trend charts on your local terminal dashboard to cross-examine these live anomalies against historical 4-block rolling average trends."

            # Renders your dynamic flashing red box header on your application page canvas view
            st.markdown(f"""
                <div class="flashing-alarm-box" style="background-color: #FFD2D2; border-left: 6px solid #D8000C; color: #D8000C; padding: 15px; font-weight: bold; border-radius: 4px; margin-bottom: 15px;">
                    🚨 {banner_title} DETECTED
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <style>
                    .flashing-alarm-box { animation: flash 1.5s infinite alternate; }
                    @keyframes flash { 0% { opacity: 0.6; } 100% { opacity: 1; } }
                </style>
            """, unsafe_allow_html=True)
            
            # Transmits the shared string text paragraph to run your live notification push
            dispatch_twilio_whatsapp(payload)
        else:
            st.info(f"ℹ️ Day-time public hygiene telemetry analysed successfully. SensorGrid registry logs active manual entry ({int(inp_fill)}%) while computing a smoothed rolling average of {int(rolling_fill_mean)}% for frontend chart trend plotting. Cumulative lid breaches ({int(inp_lids)}) remain safely within nominal parameters. No SLA escalation required.")

with tab2:
    st.markdown("### 🌙 Night-time Rodent Surveillance & Predictive Outbreak Analytics")
    st.caption("GovTech Central Sandbox: **Pre-Deployment UAT & NEA Rodent Control Alert Routing Node**")
    
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'pir_threshold';")
    t2_pir_row = cursor.fetchone()
    cursor.execute("SELECT value FROM system_config WHERE key = 'ai_threshold';")
    t2_ai_row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    t2_p_val = t2_pir_row[0] if t2_pir_row else 10.0
    t2_a_val = t2_ai_row[0] if t2_ai_row else 3.0
       
    # SYSTEM UPGRADE FIXED: Replaces loose markdown dividers with compressed HTML rules to eliminate excessive line gaps completely
    st.markdown('<p style="color: #31333F; font-size: 14px; font-weight: bold; margin-top: 5px; margin-bottom: 2px;">Feature 2: Night-time Passive Infrared (PIR) Sensor Activity Tracker</p>', unsafe_allow_html=True)
    # SYSTEM FIX: Corrected to line 335 to insert the callback sync loop into Tab 2 flawlessly
    def sync_t2_to_t3():
        st.session_state["f2_gate_toggle_t3"] = st.session_state["f2_gate_toggle"]

    f2_sighting_confirmed = st.toggle("Toggle to simulate a hardware motion tracking trigger event", value=False, key="f2_gate_toggle", on_change=sync_t2_to_t3)
    
    if f2_sighting_confirmed:
        # SYSTEM FIX: Compressed thin divider line directly below the toggle to remove the loose vertical gap
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 4px; margin-bottom: 6px;">', unsafe_allow_html=True)
        
        # SYSTEM FIX: Excised old 2-column slider container layout to implement full-width pill switches with strict 8-space nesting indentation
        st.markdown('<p style="color: #31333F; font-size: 14px; font-weight: bold; margin-top: 5px; margin-bottom: 5px;">Set Feature 3 Edge AI Outbreak SLA Target Trigger Limit (Sighting Count):</p>', unsafe_allow_html=True)
        
        new_ai_thresh = st.segmented_control(
            label="Outbreak SLA Trigger Limit",
            options=[2, 1],
            format_func=lambda x: "2 (Standard Surveillance Baseline Mode)" if x == 2 else "1 (Post-Outbreak Eradication Monitoring Mode)",
            default=2,
            label_visibility="collapsed",
            key="segmented_ai_thresh"
        )

        # SYSTEM FIX: Commits your dynamic threshold toggle switch straight to the central cloud configuration table in real-time
        conn_sync = psycopg2.connect(supabase_uri)
        cursor_sync = conn_sync.cursor()
        cursor_sync.execute("UPDATE system_config SET value = %s WHERE key = 'ai_threshold';", (float(new_ai_thresh),))
        conn_sync.commit()
        cursor_sync.close()
        conn_sync.close()
        
        # SYSTEM FIX: Second compressed divider line directly below the slider to pull the inputs up tightly
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 2px; margin-bottom: 6px;">', unsafe_allow_html=True)
        st.markdown('<p style="color: #31333F; font-size: 16px; font-weight: bold; margin-top: 0px; margin-bottom: 5px;">Manually Enter After-Hours Surveillance Intersecting Values:</p>', unsafe_allow_html=True)
        # SYSTEM FIX: Separated the field-of-view alert string onto a distinct sub-line row using strict 8-space nesting indentation
        st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 2px;">Simulated Telemetry Input: Verified YOLOv8 Rodent Identification Sighting Count</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: #C0392B; font-weight: bold; font-size: 12px; margin-top: 0px; margin-bottom: 6px;">⚠️ Note: Hardware Constraint — Maximum 15 Rodents Detectable Per Single Camera Frame Field-of-View</p>', unsafe_allow_html=True)
       
        col_l2_w1, _ = st.columns([0.6, 2.5])
        with col_l2_w1:
            inp_rats = st.number_input("", min_value=0, max_value=15, value=12, step=1, key="inp_rats_t2", label_visibility="collapsed")
            inp_pir = int(db_defaults.get("pir", 4))
    else:
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 4px; margin-bottom: 6px;">', unsafe_allow_html=True)
        # SYSTEM FIX: Sanitises layout jargon and unifies feature names word-for-word with your active GovTech sandbox views
        st.markdown("""
            <div style="background-color: #E8F4FD; border-left: 4px solid #1D72B8; color: #1D72B8; padding: 12px; border-radius: 4px; font-size: 14px; margin-top: 5px; font-weight: normal;">
                🔒 <b>Surveillance Pipeline Locked:</b> Passive Infrared (PIR) traffic tracking and threshold rule configurations are offline. SensorGrid telemetry pipelines will remain inactive until Feature 2 Edge AI Sighting Sensor logs a positive rodent classification event.
            </div>
            <br>
        """, unsafe_allow_html=True)
        inp_pir = 0
        inp_rats = 0
        new_ai_thresh = 2 # SYSTEM FIX: Default fallback mode set to 2 (Standard Surveillance) when hardware is offline
    
    # SYSTEM UPGRADE FIXED: Cleans out the flawed rolling population math and updates the database row values dynamically
    if st.button("🚀 Push Night-time Telemetry & Test GovTech SensorGrid Alert Routing API", use_container_width=True, key="btn_t2"):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Step 1: Connect to your database and pull the correct agency region registry parameters
        supabase_uri = st.secrets["SUPABASE_URI"]
        conn = psycopg2.connect(supabase_uri)
        cursor = conn.cursor()
        
        cursor.execute("SELECT nea_division FROM hawker_registry WHERE hawker_centre = %s;", (selected_center,))
        reg_data = cursor.fetchone()
        selected_div_data = reg_data[0] if reg_data else selected_div
        
        db_stall_id = "MASTER_NODE"
        
        cursor.execute("SELECT fill_level, lid_breaches_count FROM nea_telemetry WHERE hawker_centre = %s AND zone_cluster = %s ORDER BY timestamp DESC LIMIT 1;", (selected_center, selected_zone))
        fl_row = cursor.fetchone()
        db_fill = float(fl_row[0]) if fl_row else 20.0
        db_lids = float(fl_row[1]) if fl_row else 2.0
        
        cursor.execute("""
            INSERT INTO nea_telemetry (timestamp, nea_division, hawker_centre, stall_id, zone_cluster, fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0);
        """, (now_str, selected_div_data, selected_center, db_stall_id, selected_zone, db_fill, db_lids, int(inp_rats), int(inp_pir)))

        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Step 3: Standardised operational alert trigger check using your exact slider configuration parameters
        if f2_sighting_confirmed and int(inp_rats) > int(new_ai_thresh): 

            # SYSTEM FIX: Corrected the interpretation to explicitly map both Feature 2 (YOLOv8) and Feature 3 (PIR) intersections
            banner_title = "CRITICAL METRIC ANOMALY: PREDICTIVE RODENT OUTBREAK VECTOR BREACH"
            payload = "*[GovTech Smart Nation Alert]*\n*[Predictive Rodent Outbreak Violation]*\n\n📥 *Target Action Unit:* NEA " + str(selected_div) + "\n🏛️ *Facility:* " + str(selected_center) + " [Zone " + str(selected_zone) + "]\n📈 *Status:* On-device Edge AI analytics verify a biological vector threshold breach. Night-time surveillance cameras confirm a Sighting Count of " + str(int(inp_rats)) + " verified rodent identifications, exceeding statutory limits (SLA Target: < " + str(int(new_ai_thresh)) + " rodents).\n\n⚡ *System Dispatch Notice:* Triggered by Edge AI computer vision logic. Review automated tracking logs and time-series validation charts on your local terminal dashboard to cross-examine these live anomalies against historical nightly baseline profiles prior to regulatory auditing."
  
            # Displays the flashing red container block directly inside the active agency supervisor view tab
            st.markdown(f"""
                <div class="flashing-alarm-box" style="background-color: #FFD2D2; border-left: 6px solid #D8000C; color: #D8000C; padding: 15px; font-weight: bold; border-radius: 4px; margin-bottom: 15px; font-size: 14px;">
                    🚨 {banner_title}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <style>
                    .flashing-alarm-box { animation: flash 1.5s infinite alternate; }
                    @keyframes flash { 0% { opacity: 0.6; } 100% { opacity: 1; } }
                </style>
            """, unsafe_allow_html=True)
            
            # Dispatches the single, high-density telemetry data text alert straight to your phone window
            dispatch_twilio_whatsapp(payload)
        else:
            # Silently archives minor baseline activity strings without sending any text message notification spam
            st.info(f"ℹ️ Automated surveillance health signature verified for {selected_center} [Zone {selected_zone}]. SensorGrid telemetry confirms Edge AI rodent sighting counts remain safely within nominal parameters. No cross-agency escalation required.")

with tab3:
    # SYSTEM FIX: Restores the missing polished section title and agency caption at the absolute top of Tab 3
    st.markdown("### ⚙️ Automated Countermeasure Performance Tracking & Hardware Failure Analytics")
    st.caption("GovTech Central Sandbox: **Pre-Deployment UAT & External Pest Control SLA Compliance Node**")

    # SYSTEM FIX: Safely unpacks the SQLite row tuple container to extract the raw numeric value and prevent TypeErrors
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_config WHERE key = 'relay_threshold';")
    t3_relay_row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Unpacks the row tuple data safely if records exist
    t3_r_val = t3_relay_row[0] if t3_relay_row else 8.0
    
    def sync_t3_to_t2():
        st.session_state["f2_gate_toggle"] = st.session_state["f2_gate_toggle_t3"]
        
    st.markdown('<p style="color: #31333F; font-size: 14px; font-weight: bold; margin-top: 5px; margin-bottom: 2px;">Feature 2: Night-time Passive Infrared (PIR) Sensor Activity Tracker</p>', unsafe_allow_html=True)
    f2_sighting_confirmed = st.toggle("Toggle to simulate a hardware motion tracking trigger event", key="f2_gate_toggle_t3", on_change=sync_t3_to_t2)
    
    if f2_sighting_confirmed:
        # Compressed thin divider line directly below the toggle to remove loose vertical gaps
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 4px; margin-bottom: 6px;">', unsafe_allow_html=True)
        
        # SYSTEM FIX: Extracts text label to full row width to prevent awkward column wrapping completely
        st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 2px;">Set Feature 4 Automated Countermeasure Failure Threshold (Relay Activations):</p>', unsafe_allow_html=True)
        
        col_t3_slider, _ = st.columns(2)

        with col_t3_slider:
            new_relay_thresh = st.slider("", min_value=5.0, max_value=10.0, value=float(min(10.0, float(t3_r_val))), step=1.0, key="slider_relay_thresh", label_visibility="collapsed")
            
            # SYSTEM FIX: Commits your slider movement directly to the central configuration table in real time
            conn_sync = psycopg2.connect(supabase_uri)
            cursor_sync = conn_sync.cursor()
            cursor_sync.execute("UPDATE system_config SET value = %s WHERE key = 'relay_threshold';", (float(new_relay_thresh),))
            conn_sync.commit()
            cursor_sync.close()
            conn_sync.close()

        
        # SYSTEM FIX: Second compressed divider pulls up the input section headers tightly
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 2px; margin-bottom: 6px;">', unsafe_allow_html=True)
        st.markdown('<p style="color: #31333F; font-size: 16px; font-weight: bold; margin-top: 0px; margin-bottom: 5px;">Manually Enter Automated Hardware Countermeasure Activity Logs:</p>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: #31333F; font-size: 14px; margin-bottom: 4px;">Simulated Telemetry Input: 5V Automated Deterrence Hardware Relay Activations</p>', unsafe_allow_html=True)
        col_l3_w1, _ = st.columns([0.6, 2.5])
        with col_l3_w1:
            inp_relay = st.number_input("", min_value=1, max_value=50, value=12, step=1, key="inp_relays", label_visibility="collapsed")
        # Automatically maps indicators to your push variables since presence is confirmed
        inp_rats = 1
    else:
        st.markdown('<hr style="border: 0; border-top: 1px solid #E6E8EB; margin-top: 4px; margin-bottom: 6px;">', unsafe_allow_html=True)
        # SYSTEM FIX: Unifies the gated lock banner text word-for-word with Tab 2 and links directly to your new Feature 2 terminology
        st.markdown("""
            <div style="background-color: #E8F4FD; border-left: 4px solid #1D72B8; color: #1D72B8; padding: 12px; border-radius: 4px; font-size: 14px; margin-top: 5px; font-weight: normal;">
                🔒 <b>Surveillance Mitigation Locked:</b> Automated mitigation relay monitoring and hardware failure thresholds are offline. Hardware log tracking will not activate until Feature 2 Edge AI Sighting Sensor logs a positive rodent classification event.
            </div>
            <br>
        """, unsafe_allow_html=True)
        inp_relay = 0
        inp_rats = 0
        new_relay_thresh = 8
    
    # SYSTEM UPGRADE FIXED: Processes a contractor field dispatch notice ONLY if the deterrence relay count breaches your slider limit
    if st.button("🚀 Push Hardware Telemetry & Test GovTech SensorGrid Alert Routing API", use_container_width=True, key="btn_t3_run"):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # SYSTEM UPGRADE FIXED: Pulls the true database postal code column natively and scrubs out the obsolete db_stall_id query loop
        supabase_uri = st.secrets["SUPABASE_URI"]
        conn = psycopg2.connect(supabase_uri)
        cursor = conn.cursor()
        
        # SYSTEM FIX: Separates execution from row fetching to ensure native PostgreSQL compatibility
        cursor.execute("SELECT nea_division, postal_code FROM hawker_registry WHERE hawker_centre = %s;", (selected_center,))
        reg_data = cursor.fetchone()
        selected_div = reg_data[0] if reg_data else "Unknown Office"
        live_postcode = reg_data[1] if reg_data else "050335"
        
        # SYSTEM FIX: Correctly maps Tab 3 inputs straight to deterrence_triggered while forcing rodent counts to stay at 0
        cursor.execute("""
            INSERT INTO nea_telemetry (timestamp, nea_division, hawker_centre, stall_id, zone_cluster, fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered)
            VALUES (%s, %s, %s, %s, %s, 0, 0, 0, 0, %s);
        """, (now_str, selected_div, selected_center, "MASTER_NODE", selected_zone, int(inp_relay)))

        conn.commit()
        cursor.close()
        conn.close()
        
        # Step 3: Operational hardware failure threshold evaluation check
        if inp_rats == 1 and int(inp_relay) > int(new_relay_thresh):
            banner_title = "CRITICAL METRIC ANOMALY: INFRASTRUCTURE SLA BREACH DETECTED"
        
            # SYSTEM FIX: Synchronises the unique master node Asset ID and short text payload
            simulated_serial = f"GovTech-AOP-S{live_postcode}-MN-{selected_zone.upper()}"

            payload = f"*[GovTech Smart Nation Alert]*\n*[Hardware Anomaly Flagged]*\n\n📥 *Target Action Unit:* Appointed Hardware Maintenance Engineering Vendor (SNSG Contracted Fleet Team)\n🆔 *Asset ID:* {simulated_serial}\n📈 *Status:* Automated system diagnostic loops confirm a 99% probability of physical hardware failure. Local edge-sensor cross-correlations verify {int(inp_relay)} ineffective countermeasure cycles during active pest detections, breaching the operating tolerance limit (SLA Target: < {int(new_relay_thresh)} cycles).\n\n⚡ *Action Required:* Deploy on-site technician immediately within the contracted 2-hour SLA window for physical hardware rectification. Central database registry logs have initiated the automated ticket timestamp audit clock to track compliance."
          
            st.markdown(f"""
                <div class="flashing-alarm-box" style="background-color: #FFD2D2; border-left: 6px solid #D8000C; color: #D8000C; padding: 15px; font-weight: bold; border-radius: 4px; margin-bottom: 15px; font-size: 14px;">
                    🚨 {banner_title}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <style>
                    .flashing-alarm-box { animation: flash 1.5s infinite alternate; }
                    @keyframes flash { 0% { opacity: 0.6; } 100% { opacity: 1; } }
                </style>
            """, unsafe_allow_html=True)
            
            # Dispatches the SLA notice straight to your phone window
            dispatch_twilio_whatsapp(payload)
        else:
            # Archives baseline operational metrics quietly without pushing text notification spam to the agency
            st.info(f"ℹ️ Automated hardware health signature verified for {selected_center} [Zone {selected_zone}]. SensorGrid telemetry confirms mitigation relay activity is within nominal parameters. External vendor operational logs comply with active SLA performance baselines.")

# --- OFFICIAL DISCLAIMER & BACKEND OPERATIONAL FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='border-top: 1px solid #E2E8F0; padding-top: 15px; padding-bottom: 5px; text-align: center; font-family: Arial;'>
        <p style='margin: 0; font-size: 11px; color: #94A3B8; letter-spacing: 0.5px;'>
            © 2026 Smart Nation Command Centre • Backend Ingestion Pipeline Tool • Designed & Developed by Sena Yeo / 9024083G
        </p>
        <p style='margin: 4px 0 0 0; font-size: 11px; color: #94A3B8; font-weight: bold;'>
            ⚠️ PROJECT DISCLAIMER & NOTICE:
        </p>
        <p style='margin: 2px auto 0 auto; font-size: 10px; color: #CBD5E1; max-width: 800px; line-height: 1.4; font-style: italic;'>
            This application is an independent academic/simulation project built utilizing open public data metrics from data.gov.sg. It is purely a functional backend prototype designed to simulate real-time smart city data ingestion architectures (GovTech / Open Government Products frameworks) and holds no official affiliation, endorsement, or sanction from the National Environment Agency (NEA) or any Singapore Government entity.
        </p>
    </div>
""", unsafe_allow_html=True)

