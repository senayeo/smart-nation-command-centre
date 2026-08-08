import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime
import os
from assets import BASE64_IMAGE

st.set_page_config(page_title="Smart Waste & Rodent Prevention Console", layout="wide", page_icon="🇸🇬")

import psycopg2

def run_query(query, params=None):
    supabase_uri = st.secrets["SUPABASE_URI"]
    # Open connection
    conn = psycopg2.connect(supabase_uri)
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        # Fetch data immediately before closing connection lines
        results = cursor.fetchall()
        return results
    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return []
    finally:
        # Guarantee memory blocks close perfectly to prevent leaking database connections
        cursor.close()
        conn.close()

st.markdown("""
    <style>
        .block-container { padding-top: 2.0rem !important; padding-bottom: 1rem !important; }
        h2 { margin-bottom: 0.5rem !important; }
        .stSelectbox { margin-bottom: 0.4rem !important; }
        hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
        .alert-banner { padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; font-family: Arial; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: left; color: #102542; font-family: Arial;'>Smart Waste Management with AIoT Rodent Prevention</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #7F8C8D; font-size: 13px; margin-top: -15px; margin-bottom: 25px;'><b>Operational Prototype Simulation</b> • Joint Agency (NEA Environmental Public Health / Town Councils) Smart City Ingestion & Rodent Prevention Command Centre • Developed via GovTech/OGP Architectural Evaluation Framework</p>", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='color: #102542; font-family: Arial; margin-bottom: 5px;'>Surveillance Control</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size:11px; color:#7f8c8d; margin-top:5px; margin-bottom:2px; font-weight:bold;'>ENVIRONMENTAL PUBLIC HEALTH OPERATIONS DEPARTMENT</p>", unsafe_allow_html=True)

div_options = ["All NEA Regional Offices", "Central Regional Office (CRO)", "North West Regional Office (NWRO)", "North East Regional Office (NERO)", "South West Regional Office (SWRO)", "South East Regional Office (SERO)"]
selected_div = st.sidebar.selectbox("NEA Regional Office:", div_options)

# --- POSTGRES CONVERSION STEP 1: DROPDOWN ROUTING LOGIC ---
if selected_div == "All NEA Regional Offices":
    center_query = "SELECT hawker_centre FROM hawker_registry ORDER BY hawker_centre;"
    center_rows = run_query(center_query)
else:
    center_query = "SELECT hawker_centre FROM hawker_registry WHERE nea_division = %s ORDER BY hawker_centre;"
    center_rows = run_query(center_query, (selected_div,))

# Convert the resulting list of data tuples seamlessly into flat text layout strings
center_list = ["All Centres (Global View)"] + [row[0] for row in center_rows]
selected_center = st.sidebar.selectbox("Target Hawker Centre Location:", center_list)

# --- POSTGRES CONVERSION STEP 2: CACHED TELEMETRY INGESTION ---
def load_master_telemetry(selected_center, selected_div):
    # 1. Base query selecting ONLY from telemetry to completely eliminate database-level join strain
    sql_base = """
        SELECT timestamp, nea_division, hawker_centre, stall_id, zone_cluster, 
               fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered 
        FROM nea_telemetry
    """
    params = []
    limit_clause = ""

    # 2. Construct clean, index-optimized filtering constraints
    if selected_center == 'All Centres (Global View)':
        if selected_div != 'All NEA Regional Offices':
            sql_base += " WHERE nea_division = %s"
            params.append(selected_div)
        # Force a safety constraint to protect 1G container memory while preserving full 15-day timelines
        limit_clause = " ORDER BY timestamp DESC LIMIT 25000"
    else:
        sql_base += " WHERE hawker_centre = %s"
        params.append(selected_center)

    # Append the structural limit tracking modifier
    sql_query = sql_base + limit_clause
    
    # 3. Fetch raw rows using your background query runner
    row_rows = run_query(sql_query, tuple(params) if params else None)
    
    # 4. Map columns explicitly to match your exact metrics schema definitions
    cols = [
        'timestamp', 'nea_division', 'hawker_centre', 'stall_id', 'zone_cluster', 
        'fill_level', 'lid_breaches_count', 'rat_detections_count', 'pir_wakeups_count', 'deterrence_triggered'
    ]
    
    return pd.DataFrame(row_rows, columns=cols)

# --- POSTGRES CONVERSION STEP 3: CACHED MAP REGISTRY INGESTION ---
def load_map_registry(selected_div):
    if selected_div == 'All NEA Regional Offices':
        sql = "SELECT hawker_centre, nea_division, latitude, longitude, photo_url, postal_code, address, constituency FROM hawker_registry;"
        raw_rows = run_query(sql)
    else:
        sql = "SELECT hawker_centre, nea_division, latitude, longitude, photo_url, postal_code, address, constituency FROM hawker_registry WHERE nea_division = %s;"
        raw_rows = run_query(sql, (selected_div,))
        
    cols = ['hawker_centre', 'nea_division', 'latitude', 'longitude', 'photo_url', 'postal_code', 'address', 'constituency']
    
    # SYSTEM FIX: Fallback to a clean layout template if the database returns None to prevent fatal TypeErrors
    if not raw_rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(raw_rows, columns=cols)

@st.cache_resource
def generate_gis_map(map_data, color_target, hover_name_val, hover_data_list, zoom_level):
    custom_ylorrd = [
        [0.0, "#FDE68A"], [0.25, "#F59E0B"], [0.5, "#EF4444"], [1.0, "#7F1D1D"]   
    ]
    fig_map = px.scatter_map(
        map_data, lat="latitude", lon="longitude", size="Display Size",
        color=color_target, color_continuous_scale=custom_ylorrd,
        size_max=40, zoom=zoom_level,
        map_style="carto-positron", hover_name=hover_name_val, hover_data=hover_data_list,
        labels={"total_rats": "AI-Verified Rodents", "total_lids": "Lid Open Flags"}
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, height=410,
        coloraxis=dict(cmin=0, cmax=4, showscale=True)
    )
    return fig_map

# --- SYSTEM FIX: Combined Cloud Native Initialization Engine ---
def initialize_global_dashboard_state(selected_center, selected_div):
    # 1. Fetch telemetry and geospatial map records cleanly from cache loaders
    master_df = load_master_telemetry(selected_center, selected_div)
    n_view = load_map_registry(selected_div)
    
    # 2. Convert timestamp metrics safely inside the isolated scope layer
    if master_df is not None and not master_df.empty:
        master_df['timestamp'] = pd.to_datetime(master_df['timestamp'])
    else:
        master_df = pd.DataFrame()
        
    # 3. Pull operational thresholds and runtime snapshots from Supabase cloud tables
    config_rows = run_query("SELECT key, value FROM system_config;")
    sys_configs = dict(config_rows)
    
    snapshot_rows = run_query("""
        SELECT t.hawker_centre,
               MAX(CASE WHEN t.stall_id = 'MASTER_NODE' THEN t.rat_detections_count ELSE 0 END) AS total_rats,
               SUM(CASE WHEN t.stall_id != 'MASTER_NODE' THEN t.lid_breaches_count ELSE 0 END) AS total_lids
        FROM nea_telemetry t
        WHERE t.timestamp = (SELECT MAX(timestamp) FROM nea_telemetry WHERE stall_id = 'MASTER_NODE')
        GROUP BY t.hawker_centre;
    """)
    snapshots_df = pd.DataFrame(snapshot_rows, columns=['hawker_centre', 'total_rats', 'total_lids'])
    
    # 4. Build combined runtime dataframe via clean vector merge, fallback to placeholders if telemetry is empty
    if not master_df.empty and not n_view.empty:
        cols_to_use = n_view.columns.difference(master_df.columns).tolist() + ['hawker_centre']
        master_df = pd.merge(master_df, n_view[cols_to_use], on='hawker_centre', how='inner')
    elif not n_view.empty:
        # CRITICAL HARDENING LAYER: Force default data alignment to ensure 100% crash protection on any filter combination
        master_df = n_view.copy()
        master_df['timestamp'] = pd.Timestamp.now()
        master_df['fill_level'] = 0.0
        master_df['lid_breaches_count'] = 0.0
        master_df['rat_detections_count'] = 0
        master_df['pir_wakeups_count'] = 0
        master_df['deterrence_triggered'] = 0
        master_df['stall_id'] = 'MASTER_NODE'
        master_df['zone_cluster'] = 'CLUSTER-A'
    else:
        # Emergency dictionary keys fail-safe boundary
        standard_cols = ['constituency', 'address', 'postal_code', 'photo_url', 'hawker_centre', 'nea_division']
        for col in standard_cols:
            if col not in master_df.columns:
                master_df[col] = ["Central Regional Office (CRO)" if col == 'nea_division' else "Operational Simulation Profile"]
                
    return master_df, n_view, sys_configs, snapshots_df

# --- SYSTEM PLATFORM ACTIVATION HUB: UNIFIED ENTERPRISE COLD INGESTION ---
master_df, df_map_view, system_configs, latest_snapshots = initialize_global_dashboard_state(selected_center, selected_div)

# --- SIDEBAR OFFICE METADATA ARRAYS ---
if selected_div != 'All NEA Regional Offices':
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:12px; color:#102542; font-weight:bold; margin-bottom:4px;'>🏢 NEA REGIONAL OFFICE DETAILS</p>", unsafe_allow_html=True)
    office_details = {
        "CRO": "4545 Jalan Bukit Merah, Singapore 159466",
        "NWRO": "18 Attap Valley Road, Singapore 759910",
        "NERO": "174 Sin Ming Drive, Singapore 575715",
        "SWRO": "5 Albert Winsemius Lane, Singapore 126787",
        "SERO": "70 Tannery Lane, Singapore 347810"
    }
    token = "CRO"
    for k in office_details.keys():
        if k in selected_div: token = k; break
        
    st.sidebar.markdown(f"""
        <div style='font-size:13px; line-height:1.4;'>
            <b>Region Name:</b> {selected_div}<br>
            <b>Address:</b> {office_details[token]}
        </div>
    """, unsafe_allow_html=True)

if selected_center != 'All Centres (Global View)' and not master_df.empty:
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='font-size:12px; color:#102542; font-weight:bold; margin-bottom:4px;'>📍 PHOTO FEED: {selected_center}</p>", unsafe_allow_html=True)
    
    unique_stalls_count = len(master_df['stall_id'].unique())
    active_mesh_zones = sorted([str(x) for x in master_df['zone_cluster'].dropna().unique()])
    zones_list_str = "Zone " + ", ".join(active_mesh_zones)
    
    # SYSTEM FIX: Appended index brackets [0] onto .iloc to extract raw values and permanently stop the browser rendering freeze
    st.sidebar.markdown(f"""
        <div style='font-size:13px; line-height:1.4; margin-bottom:8px;'>
            <b>Constituency:</b> {master_df['constituency'].iloc[0]}<br>
            <b>Street Address:</b> {master_df['address'].iloc[0]}<br>
            <b>Number of Food Stalls:</b> {unique_stalls_count}<br>
            <b>Tray Return Stations:</b> {zones_list_str}
        </div>
    """, unsafe_allow_html=True)
    
    # SYSTEM FIX: Appended index bracket [0] to safely convert url records to flat strings
    raw_img_url = str(master_df['photo_url'].iloc[0]).strip()
    if not raw_img_url or raw_img_url == "None" or raw_img_url == "":
        st.sidebar.markdown(f'<img src="data:image/jpeg;base64,{BASE64_IMAGE}" style="width:100%; border-radius:4px;" />', unsafe_allow_html=True)
    else:
        st.sidebar.image(raw_img_url, width="stretch")

st.sidebar.markdown("<hr><p style='font-size:11px; color:#95a5a6; font-style:italic; margin-top:2px;'>Data Source: Open Data Portal (data.gov.sg) • 'Hawker Centres (GEOJSON)' 2026 Dataset Edition. Regional office organisational clusters simulated for GovTech/OGP architectural evaluation. Connected via Mock MQTT Ingestion Broker.</p>", unsafe_allow_html=True)

# --- HORIZONTAL STRIP OF STATUTORY KPI METRICS ---
m1, m2, m3, m4 = st.columns(4)
with m1: 
    true_total_centres = len(center_list) - 1
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #102542; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">HAWKER CENTRES TRACKED</p><h3 style="margin:0px; color:#102542; font-size: 22px;">{true_total_centres} Centres</h3></div>', unsafe_allow_html=True)
with m2: 
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #2980b9; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">LID BREACHES [F1]</p><h3 style="margin:0px; color:#2980b9; font-size: 22px;">{master_df["lid_breaches_count"].sum() if not master_df.empty and "lid_breaches_count" in master_df.columns else 0} Flags</h3></div>', unsafe_allow_html=True)
with m3: 
    st.markdown(f'<div style="background-color: #FFF0F0; padding: 12px; border-left: 4px solid #E74C3C; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">YOLOv8 DETECTIONS [F2]</p><h3 style="margin:0px; color:#E74C3C; font-size: 22px;">{master_df["rat_detections_count"].sum() if not master_df.empty and "rat_detections_count" in master_df.columns else 0} Verified</h3></div>', unsafe_allow_html=True)
with m4: 
    st.markdown(f'<div style="background-color: #F8F9FA; padding: 12px; border-left: 4px solid #2ECC71; border-radius: 4px;"><p style="margin:0px; font-size:11px; color:#7f8c8d; font-weight:bold;">MEAN FILL VOLUME [F1]</p><h3 style="margin:0px; color:#2ECC71; font-size: 22px;">{round(master_df["fill_level"].mean(), 1) if not master_df.empty and "fill_level" in master_df.columns else 0.0}%</h3></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #102542; font-family: Arial; margin-bottom: 10px;'>📍 Geospatial Information System (GIS) Hotspot Map</h4>", unsafe_allow_html=True)

# --- POSTGRES CONVERSION: MAP LAYER SNAPSHOTS ---
supabase_uri = st.secrets["SUPABASE_URI"]
conn_map = psycopg2.connect(supabase_uri)
sql_map = """
    SELECT t.hawker_centre, 
           MAX(CASE WHEN t.stall_id = 'MASTER_NODE' THEN t.rat_detections_count ELSE 0 END) as total_rats,
           SUM(CASE WHEN t.stall_id != 'MASTER_NODE' THEN t.lid_breaches_count ELSE 0 END) as total_lids
    FROM nea_telemetry t
    WHERE t.timestamp = (SELECT MAX(timestamp) FROM nea_telemetry WHERE stall_id = 'MASTER_NODE')
    GROUP BY t.hawker_centre;
"""
latest_snapshots = pd.read_sql_query(sql_map, conn_map)
conn_map.close()

# --- EXECUTE OPTIMIZED GIS MAP RENDERER FROM MEMORY CACHE ---
if selected_center == 'All Centres (Global View)':
    map_data = df_map_view.merge(latest_snapshots, on='hawker_centre', how='left').fillna(0)
    map_data['Display Size'] = 16.0 + (map_data['total_rats'] * 6.0)
    fig_map = generate_gis_map(map_data, "total_rats", "hawker_centre", ["total_rats", "total_lids", "constituency"], 10.6)
else:
    map_data = df_map_view[df_map_view['hawker_centre'] == selected_center].merge(latest_snapshots, on='hawker_centre', how='left').fillna(0)
    map_data['Display Size'] = 35.0 
    fig_map = generate_gis_map(map_data, "total_rats", "hawker_centre", ["total_rats", "total_lids"], 14.5)

st.plotly_chart(fig_map, width="stretch")

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- UNIFIED CONFIGURATION INTERFACE FOR SUB-GRIDS ---
if selected_center == 'All Centres (Global View)':
    target_centers = list(master_df[master_df['stall_id'] == 'MASTER_NODE'].groupby('hawker_centre')['rat_detections_count'].sum().nlargest(10).index)
    center_filter_clause = "t1.hawker_centre IN (" + ",".join(["%s"] * len(target_centers)) + ")"
    chart_params = tuple(target_centers)
    center_trends = master_df[master_df['hawker_centre'].isin(target_centers)].copy()
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 1: Smart Waste Fill Status & Bin Lid Status Analytics</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    target_centers = [selected_center]
    center_filter_clause = "(%s LIKE '%' || t1.hawker_centre || '%' OR t1.hawker_centre = %s)"
    chart_params = (selected_center, selected_center)
    center_trends = master_df[master_df['hawker_centre'] == selected_center].copy()
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 1: Smart Waste Fill Status & Bin Lid Status Analytics</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

center_trends['date_str'] = center_trends['timestamp'].dt.strftime('%Y-%m-%d')
unique_db_dates = sorted(center_trends['date_str'].unique())[-30:]

# --- ROW 1: SNAPSHOT VS TIME-SERIES LINE (ARRANGED SIDE-BY-SIDE IN PAIRS) ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # --- ORIGINAL UNALTERED CHART 1 DATA INGESTION SUITE ---
    # SYSTEM FIX: Separates the metrics so fill level takes a rolling average while lid count snaps instantly to the latest pushed record
    # SYSTEM FIX: Forces unmapped null values to process as a clean 0 to prevent backward historical rollbacks
    zone_waste = center_trends.sort_values('timestamp').groupby('zone_cluster').tail(4).groupby('zone_cluster').agg({'fill_level': 'mean', 'lid_breaches_count': 'last'}).fillna(0).reset_index()
    
    # SYSTEM FIX: Pulled instantly from the global master dictionary configuration to eliminate lagging disk connections
    current_fill_limit = float(system_configs.get('fill_threshold', 75.0))
    current_lid_limit = float(system_configs.get('lid_threshold', 4.0))
    
    # DYNAMIC COLOR ALIGNMENT LAYER: Generates distinct color arrays matching threshold states
    fill_colors = ['#D35400' if val > current_fill_limit else '#2ECC71' for val in zone_waste['fill_level']]
    lid_colors = ['#C0392B' if val > current_lid_limit else '#5DADE2' for val in zone_waste['lid_breaches_count']]
    
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    fig_bar = make_subplots(specs=[[{"secondary_y": True}]])
    
    # TRACE 1: Add primary Mean Fill percentage bars (Left Axis)
    fig_bar.add_trace(
        go.Bar(
            x=zone_waste['zone_cluster'],
            y=zone_waste['fill_level'],
            name='Mean Zone Fill Level (%)',
            marker_color=fill_colors,
            offsetgroup=1
        ),
        secondary_y=False
    )
    
    # TRACE 2: Add secondary Lid count bars (Right Axis) - High-contrast sky blue
    fig_bar.add_trace(
        go.Bar(
            x=zone_waste['zone_cluster'],
            y=zone_waste['lid_breaches_count'],
            name='Open Bins (<100% Fill, >5 Mins) Count',
            marker_color=lid_colors,
            offsetgroup=2
        ),
        secondary_y=True
    )
   
    # SHAPE 1: Lightened Green Volume SLA Target Limit Line bound to left axis
    fig_bar.add_shape(
        type="line", x0=-0.5, x1=len(zone_waste['zone_cluster'])-0.5,
        y0=current_fill_limit, y1=current_fill_limit,
        line=dict(color="#27AE60", width=2.5, dash="dash"),
        name=f"Volume SLA Limit ({int(current_fill_limit)}%)"
    )
    
    # SHAPE 2: Blue Lid SLA Target Limit Line - Sharp dark navy line over sky blue bars
    fig_bar.add_shape(
        type="line", x0=-0.5, x1=len(zone_waste['zone_cluster'])-0.5,
        y0=current_lid_limit, y1=current_lid_limit,
        yref="y2",
        line=dict(color="#2980B9", width=2.5, dash="dot"),
        name=f"Lid SLA Limit ({int(current_lid_limit)} Units)"
    )
    
    # Format advanced layout styling, applying matching colors to axis titles, ticks, and legends correctly
    fig_bar.update_layout(
        title="Feature 1: Mean Zone Fill Level & Open Lid Profile by Mesh Zone",
        barmode='group',
        font_family="Arial",
        margin=dict(t=75, b=60, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Mean Zone Fill Level (%)",
                font=dict(color="#2ECC71")
            ),
            tickfont=dict(color="#2ECC71"),
            range=[0, 100],
            dtick=10
        ),
        yaxis2=dict(
            title=dict(
                text="Open Bins (<100% Fill, >5 Mins) Count",
                font=dict(color="#2980B9")
            ),
            tickfont=dict(color="#2980B9"),
            range=[0, 15],
            dtick=2,
            overlaying="y",
            side="right"
        )
    )
    st.plotly_chart(fig_bar, width="stretch")

with col_chart2:
    # --- NEW CHART 2: CONTINUOUS 15-Day HISTORICAL MONTHLY OBSERVATION TIMELINE ---

    # SYSTEM FIX: True database alignment, extracting both metrics from the stall rows and scaling to match your operational bounds
    f1_history = center_trends[center_trends['stall_id'] != 'MASTER_NODE'].groupby('date_str').agg({
        'fill_level': 'mean', # Extracts and tracks the true average stall fill capacity baseline
        'lid_breaches_count': lambda x: round(x.mean() * 15.0, 0) # Normalises the raw stall baseline to a realistic 15-25 whole unit count
    }).reset_index()
    
    # SYSTEM FIX: Dynamically calculates vertical padding headroom to mirror Chart 4's timeline axis scaling rules
    max_history_lids = int(f1_history['lid_breaches_count'].max()) if not f1_history.empty else 10
    ceil_history_lids = max(25, math.ceil(max_history_lids * 1.25))

    # SYSTEM FIX: Converted horizontal coordinates to datetime objects and removed category locks to eliminate timeline text collision
    fig_timeline1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_timeline1.add_trace(
        go.Scatter(
            x=pd.to_datetime(f1_history['date_str']), # Converted to datetime object arrays
            y=f1_history['fill_level'],
            name='Mean Zone Fill Level (%)', # Locked-in Step 2 Terminology
            mode="lines+markers",
            line=dict(color="#2ECC71", width=2.5)
        ),
        secondary_y=False
    )
    
    fig_timeline1.add_trace(
        go.Scatter(
            x=pd.to_datetime(f1_history['date_str']), # Converted to datetime object arrays
            y=f1_history['lid_breaches_count'],
            name='Open Bins (<100% Fill, >5 Mins) Count', # Locked-in Step 2 Terminology
            mode="lines+markers",
            line=dict(color="#5DADE2", width=2.5, dash="dash")
        ),
        secondary_y=True
    )
    
    fig_timeline1.update_layout(
        title="Smart Waste Management (Feature 1): Time-Series Observation Timeline", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=60), 
        xaxis=dict(
            title="15-Day Monthly Observation Timeline", 
            tickangle=0 # Perfectly horizontal flat text strings with automated temporal filtering
        ),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.25, 
            xanchor="center", 
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Mean Zone Fill Level (%)", font=dict(color="#2ECC71")), 
            tickfont=dict(color="#2ECC71"),
            range=[0, 100],
            dtick=10
        ),
        yaxis2=dict(
            title=dict(text="Open Bins (<100% Fill, >5 Mins) Count", font=dict(color="#5DADE2")),
            tickfont=dict(color="#5DADE2"),
            showgrid=False,
            tickformat="d", # Enforces integer formatting with zero decimal positions
            range=[0, ceil_history_lids], # Binds the ceiling dynamically to your updated headroom ceiling variable
            overlaying="y", 
            side="right"
        )
    )
    st.plotly_chart(fig_timeline1, width="stretch")

# --- ROW 2: RODENT SURVEILLANCE & PREDICTIVE OUTBREAK INTELLIGENCE (FEATURE 2 & 3) ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 2: Rodent Surveillance & Predictive Outbreak Intelligence</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 2: Rodent Surveillance & Predictive Outbreak Intelligence</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    # SYSTEM FIX: Corrects the inner subquery WHERE clause by removing the invalid outer t1 alias to clear the DatabaseError
    # --- POSTGRES CONVERSION: CHART 3 SURVEILLANCE ---
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn_c3 = psycopg2.connect(supabase_uri)
    
    if selected_center == 'All Centres (Global View)':
        placeholders_c3 = ",".join(["%s"] * len(target_centers))
        sql_c3 = f"""
            SELECT t1.zone_cluster, t1.rat_detections_count, t1.pir_wakeups_count
            FROM nea_telemetry t1
            INNER JOIN (
                SELECT zone_cluster, MAX(id) as max_id
                FROM nea_telemetry
                WHERE hawker_centre IN ({placeholders_c3}) AND stall_id = 'MASTER_NODE'
                GROUP BY zone_cluster
            ) t2 ON t1.id = t2.max_id
            WHERE t1.hawker_centre IN ({placeholders_c3}) AND t1.stall_id = 'MASTER_NODE'
            ORDER BY t1.zone_cluster;
        """
        zone_surv = pd.read_sql_query(sql_c3, conn_c3, params=tuple(target_centers) + tuple(target_centers))
    else:
        sql_c3 = """
            SELECT t1.zone_cluster, t1.rat_detections_count, t1.pir_wakeups_count
            FROM nea_telemetry t1
            INNER JOIN (
                SELECT zone_cluster, MAX(id) as max_id
                FROM nea_telemetry
                WHERE hawker_centre = %s AND stall_id = 'MASTER_NODE'
                GROUP BY zone_cluster
            ) t2 ON t1.id = t2.max_id
            WHERE t1.hawker_centre = %s AND t1.stall_id = 'MASTER_NODE'
            ORDER BY t1.zone_cluster;
        """
        zone_surv = pd.read_sql_query(sql_c3, conn_c3, params=(selected_center, selected_center))
    conn_c3.close()

    if zone_surv.empty:
        zone_surv = pd.DataFrame([{'zone_cluster': z, 'rat_detections_count': 0, 'pir_wakeups_count': 0} for z in ['A','B','C','D','E','F']])

    # SYSTEM FIX: Extract the dynamic Feature 3 PIR Activity Limit directly from the global system dictionary configuration
    current_rat_limit = float(system_configs.get('rat_threshold', 2.0))

    # SYSTEM FIX: Shifted target metrics matrix to rat_detections_count to resolve pristine profile display bug
    c3_max_rats = int(zone_surv['rat_detections_count'].max()) if not zone_surv.empty else 0
    c3_ceil_rats = max(5, math.ceil(c3_max_rats * 1.15))

    # SYSTEM FIX: Reverted to a single, clean bar trace with a static zero baseline floor to align symmetrically with Chart 5's logic
    # Set dynamic alert color variables: turns Red if hardware wakeups breach the trigger limit, green if within safe tracking bounds
    bar_colors_c3 = ['#E74C3C' if val > current_rat_limit else '#95A5A6' for val in zone_surv['rat_detections_count']] 
    
    fig_c3 = go.Figure()
    
    # TRACE 1: Pure single-axis sensor activity tracking profile matching Chart 5 layout properties
    fig_c3.add_trace(
        go.Bar(
            x=zone_surv['zone_cluster'], 
            y=zone_surv['rat_detections_count'],
            name='Verified YOLOv8 Rodent Sighting Count',
            marker_color=bar_colors_c3
        )
    )
    
    # SHAPE 1: Injects your authentic horizontal trigger boundary limit line across the active cluster tracking blocks
    fig_c3.add_shape(
        type="line", x0=-0.5, x1=len(zone_surv['zone_cluster'])-0.5,
        y0=current_rat_limit, y1=current_rat_limit,
        line=dict(color="#C0392B", width=3, dash="dash"),
        name=f"Pest SLA Limit ({int(current_rat_limit)} Rodents)"
    )
    
    # SYSTEM FIX: Synchronized Chart 3 labels and axis definitions with the backend Tab 2 data structures
    fig_c3.update_layout(
        title="Night-time Rodent Surveillance (Feature 2 & 3): Profile by Mesh Cluster Zone", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(
            title="Feature 3: Verified YOLOv8 Rodent Sighting Count",
            range=[0, c3_ceil_rats],
            tickformat="d"
        )
    )

    st.plotly_chart(fig_c3, width="stretch")

with col_chart4:
    # --- RESTORED ORIGINAL UNTRUNCATED SURVEILLANCE VALIDATION TIMELINE ---
    if selected_center == 'All Centres (Global View)':
        # SYSTEM FIX: Correctly aggregates cumulative data across all top 10 locations to drive global view dynamic ranges
        daily_summary = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
            'pir_wakeups_count': 'sum', 
            'rat_detections_count': 'sum'
        }).reset_index()
    else:
        # Localized target center tracks single facility node thresholds cleanly
        daily_summary = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
            'pir_wakeups_count': 'max', 
            'rat_detections_count': 'max'
        }).reset_index()
        
    daily_summary = daily_summary[daily_summary['date_str'].isin(unique_db_dates)]
    
    # SYSTEM FIX: Fully dynamic maximum boundaries calculated directly from active metrics array
    max_val_pir = int(daily_summary['pir_wakeups_count'].max()) if not daily_summary.empty else 10
    max_val_rats = int(daily_summary['rat_detections_count'].max()) if not daily_summary.empty else 5
    
    # SYSTEM FIX: Preserves your working dynamic database math for large datasets while enforcing safe whole-number floors for small metrics
    dynamic_ceil_pir = max(15, math.ceil(max_val_pir * 1.15))
    dynamic_ceil_rats = max(5, math.ceil(max_val_rats * 1.15))
    
    fig_c4 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primary line trace (Left Axis)
    fig_c4.add_trace(
        go.Scatter(
            x=daily_summary['date_str'], 
            y=daily_summary['pir_wakeups_count'], 
            name='Feature 2: PIR Sensor Activity Count',
            mode="lines+markers", 
            line=dict(color="#95A5A6", width=2.5)
        ), 
        secondary_y=False
    )
    
    # Secondary line trace (Right Axis)
    fig_c4.add_trace(
        go.Scatter(
            x=daily_summary['date_str'], 
            y=daily_summary['rat_detections_count'], 
            name='Feature 3: Verified YOLOv8 Rodent Sighting Count',
            mode="lines+markers", 
            line=dict(color="#E74C3C", width=2.5, dash="dash")
        ), 
        secondary_y=True
    )
    
    # SYSTEM FIX: Hard-locked explicit zero-floor baselines, dynamic ceil parameters, and expanded bottom margin to b=150
    fig_c4.update_layout(
        title="Night-time Rodent Surveillance (Feature 2 & 3): Time-Series Validation Timeline", 
        font_family="Arial", 
        margin=dict(t=75, b=60, l=10, r=60), 
        xaxis=dict(title="15-Day Monthly Observation Timeline"),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.25,
            xanchor="center", 
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Feature 2: PIR Sensor Activity Count", font=dict(color="#95A5A6")), 
            tickfont=dict(color="#95A5A6"),
            range=[0, dynamic_ceil_pir],  # SYSTEM FIX: Hardened exact zero floor baseline parameter tracking
            tickformat="d"
        ),
        yaxis2=dict(
            title=dict(text="Feature 3: Rodent Sighting Count", font=dict(color="#E74C3C")), 
            tickfont=dict(color="#E74C3C"), 
            range=[0, dynamic_ceil_rats], # SYSTEM FIX: Hardened exact zero floor baseline parameter tracking
            showgrid=False,
            tickmode="array",
            tickvals=list(range(0, dynamic_ceil_rats + 1)) if dynamic_ceil_rats <= 15 else None, # Clean array values lock out duplicate strings
            tickformat="d",
            overlaying="y", 
            side="right"
        )
    )
    st.plotly_chart(fig_c4, width="stretch")

# --- ROW 3: AUTOMATED COUNTERMEASURE PERFORMANCE TRACKING & HARDWARE FAILURE ANALYTICS ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 3: Automated Countermeasure Performance Tracking & Hardware Failure Analytics</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 3: Automated Countermeasure Performance Tracking & Hardware Failure Analytics</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

col_chart5, col_chart6 = st.columns(2)

# SYSTEM FIX: Pulled instantly from the global master dictionary configuration to eliminate the final lagging disk connection
current_relay_limit = float(system_configs.get('relay_threshold', 8.0))

with col_chart5:
    # --- POSTGRES CONVERSION: CHART 5 DETERRENCE ---
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn_c5 = psycopg2.connect(supabase_uri)
    
    if selected_center == 'All Centres (Global View)':
        target_centers = list(master_df[master_df['stall_id'] == 'MASTER_NODE'].groupby('hawker_centre')['rat_detections_count'].sum().nlargest(10).index)
        placeholders = ",".join(["%s"] * len(target_centers))
        sql_c5 = f"""
            SELECT t.zone_cluster, t.rat_detections_count, t.deterrence_triggered
            FROM nea_telemetry t
            WHERE t.hawker_centre IN ({placeholders}) AND t.stall_id = 'MASTER_NODE';
        """
        zone_deter = pd.read_sql_query(sql_c5, conn_c5, params=tuple(target_centers))
    else:
        sql_c5 = """
            SELECT t.zone_cluster, t.rat_detections_count, t.deterrence_triggered
            FROM nea_telemetry t
            WHERE t.hawker_centre = %s AND t.stall_id = 'MASTER_NODE';
        """
        zone_deter = pd.read_sql_query(sql_c5, conn_c5, params=(selected_center,))
        
    conn_c5.close()

    if zone_deter.empty:
        zone_deter = pd.DataFrame([{'zone_cluster': z, 'rat_detections_count': 0, 'deterrence_triggered': 0} for z in ['A','B','C','D','E','F']])

    zone_deter['ineffective_cycles'] = zone_deter.apply(lambda r: max(0, int(r['rat_detections_count']) - int(r['deterrence_triggered'])), axis=1)
    bar_colors = ['#E74C3C' if val > current_relay_limit else '#2ECC71' for val in zone_deter['ineffective_cycles']]

    fig_c5 = go.Figure()
    fig_c5.add_trace(go.Bar(x=zone_deter['zone_cluster'], y=zone_deter['ineffective_cycles'], name='Ineffective Cycles', marker_color=bar_colors))

    # SHAPE 1: SLA Target Limit Line mapping threshold rules clearly over your cluster tracks
    fig_c5.add_shape(
        type="line", x0=-0.5, x1=len(zone_deter['zone_cluster'])-0.5, 
        y0=current_relay_limit, y1=current_relay_limit, 
        line=dict(color="#C0392B", width=3, dash="dash"), 
        name="SLA Target Limit"
    )

    fig_c5.update_layout(
        title="Ineffective Deterrence Countermeasure Cycles by Mesh Cluster Zone",
        font_family="Arial", 
        margin=dict(t=75, b=20, l=10, r=10),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(title="Ineffective Countermeasure Cycles", range=[0, max(15, zone_deter['ineffective_cycles'].max() + 2)], dtick=2)
    )
    st.plotly_chart(fig_c5, width="stretch")

with col_chart6:
    # --- NEW CHART 6: TIME-SERIES TIMELINE FOR FEATURE 2 & 4 AUTOMATED COUNTERMEASURES ---
    f4_history = center_trends[center_trends['stall_id'] == 'MASTER_NODE'].groupby('date_str').agg({
        'pir_wakeups_count': 'max',
        'rat_detections_count': 'max',
        'deterrence_triggered': 'max'
    }).reset_index()
    
    # Vectorized calculation matching your exact Feature 4 hardware failure tracking logic
    f4_history['ineffective_cycles'] = (f4_history['rat_detections_count'] - f4_history['deterrence_triggered']).clip(lower=0)
    
    # Calculate vertical scale padding headroom matching Chart 4 rules
    max_c6_pir = int(f4_history['pir_wakeups_count'].max()) if not f4_history.empty else 10
    ceil_c6_pir = max(15, math.ceil(max_c6_pir * 1.25))
    
    max_c6_fail = int(f4_history['ineffective_cycles'].max()) if not f4_history.empty else 10
    ceil_c6_fail = max(15, math.ceil(max_c6_fail * 1.25))
    
    fig_c6 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. Primary Line Trace (Left Axis - Feature 2 Activity perfectly aligned with Chart 4 naming)
    fig_c6.add_trace(
        go.Scatter(
            x=pd.to_datetime(f4_history['date_str']),
            y=f4_history['pir_wakeups_count'],
            name="Feature 2: PIR Sensor Activity Count",
            mode="lines+markers",
            line=dict(color="#2ECC71", width=2.5)
        ),
        secondary_y=False
    )
    
    # 2. Secondary Line Trace (Right Axis - Feature 4 Failure Cycles)
    fig_c6.add_trace(
        go.Scatter(
            x=pd.to_datetime(f4_history['date_str']),
            y=f4_history['ineffective_cycles'],
            name="Feature 4: Ineffective Deterrence Cycles",
            mode="lines+markers",
            line=dict(color="#E74C3C", width=2.5, dash="dash")
        ),
        secondary_y=True
    )
    
    # 3. Synchronize Layout and Horizontal Centered Legend with Chart 4 Standards
    fig_c6.update_layout(
        title="Countermeasure Performance (Feature 2 & 4): Time-Series Observation Timeline",
        font_family="Arial",
        margin=dict(t=75, b=60, l=40, r=60), # Expanded left margin padding to 40px to completely prevent text clipping
        xaxis=dict(
            title="15-Day Monthly Observation Timeline",
            tickangle=0
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        yaxis=dict(
            title=dict(text="Feature 2: PIR Sensor Activity Count", font=dict(color="#2ECC71")), # Restored mirror consistency with Chart 4
            tickfont=dict(color="#2ECC71"),
            range=[0, ceil_c6_pir],
            tickformat="d"
        ),
        yaxis2=dict(
            title=dict(text="Feature 4: Ineffective Deterrence Cycles", font=dict(color="#E74C3C")),
            tickfont=dict(color="#E74C3C"),
            showgrid=False,
            range=[0, ceil_c6_fail],
            tickformat="d",
            overlaying="y",
            side="right"
        )
    )
    
    st.plotly_chart(fig_c6, width="stretch")

# --- ROW 4: ANALYTICAL PHASE 4 MAIN HEADER CONTAINER ---
st.markdown("<br><hr>", unsafe_allow_html=True)

if selected_center == 'All Centres (Global View)':
    st.markdown("""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 4: Predictive Analytical Intelligence (Unified Risk Vector)</h4>
            <h5 style='color: #E74C3C; margin-top: -12px; margin-bottom: 15px;'>📍 Global Overview • Top 10 High-Risk Hawker Centres Nationwide</h5>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='font-family: Arial;'>
            <h4 style='color: #102542; margin-bottom: 0px; font-weight: bold;'>Analytical Phase 4: Predictive Analytical Intelligence (Unified Risk Vector)</h4>
            <h5 style='color: #2C3E50; margin-top: -12px; margin-bottom: 15px;'>📍 Target Location: {selected_center}</h5>
        </div>
    """, unsafe_allow_html=True)

# --- ROW 4: DYNAMIC COMPOSITE RISK INTELLIGENCE MATRIX (CHART 7) ---
# --- POSTGRES CONVERSION STEP 3A: CHART 7 GLOBAL THREAT INGESTION ---

if selected_center == 'All Centres (Global View)':
    # GLOBAL SQL QUERY: Aggregates features at the hawker centre level nationwide
    sql_threat = """
        SELECT 
            hawker_centre AS location_key,
            AVG(fill_level) AS fill_level,
            AVG(lid_breaches_count) AS lid_breaches_count,
            SUM(rat_detections_count) AS rat_detections_count
        FROM nea_telemetry
        WHERE stall_id = 'MASTER_NODE'
        GROUP BY hawker_centre;
    """
    threat_rows = run_query(sql_threat)
    threat_data = pd.DataFrame(threat_rows, columns=['location_key', 'fill_level', 'lid_breaches_count', 'rat_detections_count'])

    # --- SYSTEM FIX: Cast database metrics to primitive floats to prevent multiplication errors ---
    if not threat_data.empty:
        threat_data['fill_level'] = threat_data['fill_level'].astype(float)
        threat_data['lid_breaches_count'] = threat_data['lid_breaches_count'].astype(float)
        threat_data['rat_detections_count'] = threat_data['rat_detections_count'].astype(float)
    
    # Compute composite vector outbreak public health risk score mapping
    threat_data['threat_index'] = (threat_data['fill_level'] * 0.2) + (threat_data['lid_breaches_count'] * 1.5) + (threat_data['rat_detections_count'] * 20.0)
    
    # Sort ascending so the absolute highest-risk facility sits elegantly at the very top of the horizontal graph axis
    chart_data = threat_data.sort_values('threat_index', ascending=True).tail(10)
    
    fig_c7 = go.Figure()
    fig_c7.add_trace(go.Bar(
        x=chart_data['threat_index'], # Numerical scores move to the horizontal x-axis
        y=chart_data['location_key'], # Long facility text names move to the roomy left y-axis
        orientation='h', # SYSTEM FIX: Flips chart horizontally to permanently resolve vertical squashing
        name="Centre Threat Risk Index",
        marker=dict(
            color=chart_data['threat_index'], 
            colorscale='Reds', 
            showscale=True, # Auto-scales color mapping based on actual data limits
            colorbar=dict(
                thickness=15, len=0.75, yanchor="middle", y=0.5, xpad=15,
                title=dict(text="Risk Score", font=dict(size=10), side="bottom"),
                tickfont=dict(size=10)
            )
        )
    ))
    fig_c7.update_layout(
        title="Unified System Analytics: Calculated Public Health Threat Matrix by Center",
        font_family="Arial",
        margin=dict(t=75, b=60, l=350, r=40), # Expanded left margin to 350px to fit long names perfectly without clipping
        xaxis=dict(title="Vector Threat Index Score"),
        yaxis=dict(title="Top 10 High-Risk Hawker Centres Nationwide", automargin=True)
    )
else:
    # SYSTEM FIX: Resolves binding crash by querying the database using a direct string match instead of parameterized inputs
    # --- POSTGRES CONVERSION STEP 3B: CHART 7 LOCALIZED THREAT INGESTION ---
    supabase_uri = st.secrets["SUPABASE_URI"]
    conn_threat = psycopg2.connect(supabase_uri)
    sql_threat = """
        SELECT 
            t1.zone_cluster AS location_key,
            t1.fill_level,
            t1.lid_breaches_count,
            t1.rat_detections_count
        FROM nea_telemetry t1
        INNER JOIN (
            SELECT zone_cluster, MAX(id) AS max_id
            FROM nea_telemetry
            WHERE hawker_centre = %s AND stall_id = 'MASTER_NODE'
            GROUP BY zone_cluster
        ) t2 ON t1.id = t2.max_id;
    """

    threat_data = pd.read_sql_query(sql_threat, conn_threat, params=(selected_center,))
    conn_threat.close()
    
    if threat_data.empty:
        threat_data = pd.DataFrame([{'location_key': z, 'fill_level': 0, 'lid_breaches_count': 0, 'rat_detections_count': 0} for z in ['A','B','C','D','E','F']])
        
    threat_data['threat_index'] = (threat_data['fill_level'] * 0.2) + (threat_data['lid_breaches_count'] * 1.5) + (threat_data['rat_detections_count'] * 20.0)
    chart_data = threat_data
    
    fig_c7 = go.Figure()
    fig_c7.add_trace(go.Bar(
        x=chart_data['location_key'],
        y=chart_data['threat_index'],
        name="Vector Threat Risk Index",
        marker=dict(
            color=chart_data['threat_index'], colorscale='Reds', cmin=0, cmax=60, showscale=True,
            colorbar=dict(
                thickness=15, len=0.75, yanchor="middle", y=0.5, xpad=15,
                title=dict(text="Risk Score", font=dict(size=10), side="bottom"),
                tickfont=dict(size=10)
            )
        )
    ))
    fig_c7.update_layout(
        title="Unified System Analytics: Calculated Public Health Threat Matrix by Zone",
        font_family="Arial",
        margin=dict(t=75, b=60, l=40, r=40),
        xaxis=dict(title="Mesh Cluster Zone"),
        yaxis=dict(title="Vector Threat Index Score", range=[0, max(70, chart_data['threat_index'].max() * 1.25)])
    )

st.plotly_chart(fig_c7, width="stretch")

# --- RE-APPEND THE TIME-SERIES STREAM LOG DATA DATA GRIDS ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.subheader("📋 Granular Time-Series Network Data Stream Log")

# --- POSTGRES CONVERSION STEP 4: BOTTOM STREAM DATA LOGS ---
supabase_uri = st.secrets["SUPABASE_URI"]
conn_log = psycopg2.connect(supabase_uri)

if selected_center == 'All Centres (Global View)':
    # SYSTEM FIX: Enforces a strict SQL syntax format compatible with your migrated Supabase columns
    sql_log = """
        SELECT id, timestamp, nea_division, hawker_centre, stall_id, zone_cluster, 
               fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered 
        FROM nea_telemetry 
        ORDER BY timestamp DESC 
        LIMIT 100;
    """
    df_log = pd.read_sql_query(sql_log, conn_log)
else:
    sql_log = """
        SELECT id, timestamp, nea_division, hawker_centre, stall_id, zone_cluster, 
               fill_level, lid_breaches_count, rat_detections_count, pir_wakeups_count, deterrence_triggered 
        FROM nea_telemetry 
        WHERE hawker_centre = %s 
        ORDER BY timestamp DESC 
        LIMIT 100;
    """
    df_log = pd.read_sql_query(sql_log, conn_log, params=(selected_center,))

conn_log.close()

if not df_log.empty:
    df_log['timestamp'] = pd.to_datetime(df_log['timestamp'])
    st.dataframe(
        df_log, 
        width="stretch", 
        hide_index=True
    )
else:
    st.warning("⚠️ No central operational telemetry data log streams currently active in memory.")

# --- OFFICIAL DISCLAIMER & PROJECT OPERATIONAL FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='border-top: 1px solid #E2E8F0; padding-top: 15px; padding-bottom: 5px; text-align: center; font-family: Arial;'>
        <p style='margin: 0; font-size: 11px; color: #94A3B8; letter-spacing: 0.5px;'>
            © 2026 Smart Nation Command Centre • Designed & Developed by Sena Yeo / 9024083G
        </p>
        <p style='margin: 4px 0 0 0; font-size: 11px; color: #94A3B8; font-weight: bold;'>
            ⚠️ PROJECT DISCLAIMER & NOTICE:
        </p>
        <p style='margin: 2px auto 0 auto; font-size: 10px; color: #CBD5E1; max-width: 800px; line-height: 1.4; font-style: italic;'>
            This application is an independent academic/simulation project built utilising open public data metrics from data.gov.sg. It is purely a functional mock-up designed to evaluate smart city AIoT dashboard architectures (GovTech / Open Government Products frameworks) and holds no official affiliation, endorsement, or sanction from the National Environment Agency (NEA) or any Singapore Government entity.
        </p>
    </div>
""", unsafe_allow_html=True)

