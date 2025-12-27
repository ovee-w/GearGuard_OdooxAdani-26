import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime

# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("gearguard.db", check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        serial TEXT,
        category TEXT,
        department TEXT,
        owner TEXT,
        team TEXT,
        technician TEXT,
        location TEXT,
        purchase_date TEXT,
        warranty TEXT,
        scrapped INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        team TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        equipment_id INTEGER,
        team TEXT,
        technician TEXT,
        request_type TEXT,
        status TEXT,
        scheduled_date TEXT,
        duration REAL,
        created_at TEXT
    )
    """)


    conn.commit()

init_db()

# ---------------- HELPERS ---------------- #

def get_equipment():
    return pd.read_sql("SELECT * FROM equipment WHERE scrapped=0", conn)

def get_requests():
    return pd.read_sql("SELECT * FROM requests", conn)

def get_technicians(team):
    return pd.read_sql(
        "SELECT name FROM technicians WHERE team = ?", conn, params=(team,)
    )

# ---------------- UI ---------------- #

st.set_page_config("GearGuard", layout="wide")
st.title("🔧 GearGuard – The Ultimate Maintenance Tracker")

if "redirect_to" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("redirect_to")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Equipment", "Teams", "Create Request", "Kanban Board", "Calendar View"], key="nav"
)

# =========================================================
# EQUIPMENT MODULE
# =========================================================
EMPTY_STATE_MESSAGES = {
    "New": "🎉 No new issues right now! Everything is running smoothly.",
    "In Progress": "💪 No ongoing work at the moment. The team is all caught up!",
    "Repaired": "✨ No repaired items here — looks like nothing needed fixing today.",
    "Scrap": "🧹 No scrapped equipment found. That’s a good sign!"
}

if menu == "Dashboard":
    st.header("Dashboard")
    df = pd.read_sql("""
    SELECT
        r.id,
        r.subject,
        COALESCE(e.name, 'Unknown') AS equipment,
        r.team,
        r.technician,
        COALESCE(r.status, 'New') AS status,
        r.request_type,
        r.scheduled_date
    FROM requests r
    LEFT JOIN equipment e ON r.equipment_id = e.id
    WHERE COALESCE(r.status, 'New') != 'Repaired'
    ORDER BY r.created_at DESC
    """, conn)
    colA, colB = st.columns([5, 1])
    with colB:
        if st.button("➕ Create Request"):
            st.session_state["redirect_to"] = "Create Request"
            st.rerun()
         
    st.subheader("🔎 Filter Requests")
    f1, f2, f3, f4, f5, f6 = st.columns(6)

    with f1:
        team_f = st.multiselect(
            "Team",
            sorted(df["team"].dropna().unique()),
            key="filter_team"
        )

    with f2:
        tech_f = st.multiselect(
            "Technician",
            sorted(df["technician"].dropna().unique()),
            key="filter_technician"
        )

    with f3:
        STATUS_OPTIONS = ["New", "In Progress", "Repaired", "Scrap"]
        status_f = st.multiselect(
            "Status",
            options=STATUS_OPTIONS,
            key="filter_status"
        )

    with f4:
        type_f = st.multiselect(
            "Type",
            sorted(df["request_type"].dropna().unique()),
            key="filter_type"
        )

    with f5:
        equip_f = st.multiselect(
            "Equipment",
            sorted(df["equipment"].dropna().unique()),
            key="filter_equipment"
        )

    with f6:
        overdue_only = st.checkbox(
            "Overdue Only",
            key="filter_overdue"
        )

    filtered_df = df.copy()
    if team_f:
        filtered_df = filtered_df[filtered_df["team"].isin(team_f)]

    if tech_f:
        filtered_df = filtered_df[filtered_df["technician"].isin(tech_f)]

    if status_f:
        filtered_df = filtered_df[filtered_df["status"].isin(status_f)]

    if type_f:
        filtered_df = filtered_df[filtered_df["request_type"].isin(type_f)]

    if equip_f:
        filtered_df = filtered_df[filtered_df["equipment"].isin(equip_f)]

    if overdue_only:
        filtered_df = filtered_df[
            filtered_df["scheduled_date"].notna() &
            (filtered_df["scheduled_date"] < str(date.today()))
        ]
    
    if filtered_df.empty:

        # Case 1: Exactly ONE status filter selected
        if status_f and len(status_f) == 1:
            msg = EMPTY_STATE_MESSAGES.get(
                status_f[0],
                "🎉 All clear! No requests match your filters."
            )
            st.success(msg)

        # Case 2: Multiple status filters selected
        elif status_f and len(status_f) > 1:
            st.success(
                "🎯 You’re all caught up across these stages! Nothing pending here."
            )

        # Case 3: Overdue filter active
        elif overdue_only:
            st.success(
                "⏰ No overdue tasks — amazing job staying ahead!"
            )

        # Case 4: Other filters applied (team, tech, equipment, etc.)
        elif team_f or tech_f or type_f or equip_f:
            st.info(
                "🔍 No requests match these filters. Try adjusting them to explore more."
            )

        # Case 5: No filters at all (true empty dashboard)
        else:
            st.success(
                "🌈 Your maintenance board is clear! Enjoy the calm while it lasts 😄"
            )
        st.caption("Pro tip: Preventive maintenance today avoids breakdowns tomorrow.")
        st.stop()

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

elif menu == "Equipment":
    st.header("🏭 Equipment Management")

    with st.form("add_equipment"):
        name = st.text_input("Equipment Name")
        serial = st.text_input("Serial Number")
        category = st.selectbox("Category", ["CNC", "Printer", "Laptop", "Vehicle", "Other"])
        dept = st.text_input("Department")
        owner = st.text_input("Assigned Employee")
        team = st.text_input("Maintenance Team")
        tech = st.text_input("Default Technician")
        location = st.text_input("Location")
        purchase = st.date_input("Purchase Date")
        warranty = st.date_input("Warranty Expiry")

        if st.form_submit_button("Add Equipment"):
            cur.execute("""
            INSERT INTO equipment
            (name, serial, category, department, owner, team, technician,
             location, purchase_date, warranty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, serial, category, dept, owner, team, tech,
                  location, str(purchase), str(warranty)))
            conn.commit()
            st.success("Equipment Added")

    st.subheader("📋 Equipment List")

    eq = get_equipment()
    for _, row in eq.iterrows():
        with st.expander(f"{row['name']} (Team: {row['team']})"):
            st.write(f"Category: {row['category']}")
            st.write(f"Serial: {row['serial']}")
            st.write(f"Location: {row['location']}")

            count = cur.execute(
                "SELECT COUNT(*) FROM requests WHERE equipment_id=? AND status!='Repaired'",
                (row["id"],)
            ).fetchone()[0]

            if st.button(f"🛠 Maintenance ({count})", key=row["id"]):
                st.dataframe(
                    pd.read_sql(
                        "SELECT subject, status, technician FROM requests WHERE equipment_id=?",
                        conn, params=(row["id"],)
                    )
                )

# =========================================================
# TEAM & TECHNICIANS
# =========================================================

elif menu == "Teams":
    st.header("👷 Maintenance Teams")

    team = st.text_input("Team Name")
    print (team)
    if st.button("Add Team"):
        try:
            cur.execute("INSERT INTO teams (name) VALUES (?)", (team,))
            conn.commit()
            st.success("Team Added")
        except:
            st.error("Team already exists")

    st.divider()

    name = st.text_input("Technician Name")
    tech_team = st.text_input("Technician Team")

    if st.button("Add Technician"):
        cur.execute(
            "INSERT INTO technicians (name, team) VALUES (?, ?)",
            (name, tech_team)
        )
        conn.commit()
        st.success("Technician Added")

    st.subheader("👥 Technicians")
    st.dataframe(pd.read_sql("SELECT * FROM technicians", conn))

# =========================================================
# CREATE REQUEST
# =========================================================

elif menu == "Create Request":
    st.header("🧾 Create Maintenance Request")

    eq = get_equipment()
    eq_map = dict(zip(eq["name"], eq["id"]))

    subject = st.text_input("Issue / Subject")
    eq_name = st.selectbox("Equipment", eq_map.keys())

    eq_row = eq[eq["id"] == eq_map[eq_name]].iloc[0]

    st.info(f"Auto-filled Category: {eq_row['category']}")
    st.info(f"Auto-filled Team: {eq_row['team']}")
    st.info(f"Auto-filled Technician: {eq_row['technician']}")

    req_type = st.selectbox("Request Type", ["Corrective", "Preventive"])
    sched_date = st.date_input("Scheduled Date") if req_type == "Preventive" else None

    if st.button("Create Request"):
        cur.execute("""
        INSERT INTO requests
        (subject, equipment_id, team, technician,
         request_type, status, scheduled_date, created_at)
        VALUES (?, ?, ?, ?, ?, 'New', ?, ?)
        """, (
            subject,
            eq_row["id"],
            eq_row["team"],
            eq_row["technician"],
            req_type,
            str(sched_date) if sched_date else None,
            str(datetime.now())
        ))
        conn.commit()
        st.success("Request Created")

# =========================================================
# KANBAN BOARD
# =========================================================

elif menu == "Kanban Board":
    st.header("🗂 Maintenance Kanban Board")

    req = get_requests()
    today = date.today()

    stages = ["New", "In Progress", "Repaired", "Scrap"]
    cols = st.columns(4)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.subheader(stage)
            subset = req[req["status"] == stage]

            for _, r in subset.iterrows():
                overdue = (
                    r["scheduled_date"] and
                    date.fromisoformat(r["scheduled_date"]) < today and
                    stage != "Repaired"
                )

                st.markdown(
                    f"**{r['subject']}**  \n"
                    f"👨‍🔧 {r['technician']}  \n"
                    + ("🔴 OVERDUE" if overdue else "")
                )

                if stage in ["New", "In Progress"]:
                    if st.button("➡ Move", key=f"{r['id']}_{stage}"):
                        next_stage = stages[i + 1]
                        cur.execute(
                            "UPDATE requests SET status=? WHERE id=?",
                            (next_stage, r["id"])
                        )

                        if next_stage == "Scrap":
                            cur.execute(
                                "UPDATE equipment SET scrapped=1 WHERE id=?",
                                (r["equipment_id"],)
                            )

                        conn.commit()
                        st.rerun()

                if stage == "In Progress":
                    hrs = st.number_input("Hours Spent", min_value=0.0, key=f"h{r['id']}")
                    if st.button("Complete", key=f"c{r['id']}"):
                        cur.execute("""
                        UPDATE requests
                        SET status='Repaired', duration=?
                        WHERE id=?
                        """, (hrs, r["id"]))
                        conn.commit()
                        st.rerun()

# =========================================================
# CALENDAR VIEW
# =========================================================

elif menu == "Calendar View":
    st.header("📅 Preventive Maintenance Calendar")

    selected = st.date_input("Select Date")

    # df = pd.read_sql("""
    # SELECT r.subject, e.name AS equipment, r.technician
    # FROM requests r
    # JOIN equipment e ON r.equipment_id = e.id
    # WHERE r.request_type='Preventive' AND r.scheduled_date=?
    # """, conn, params=(str(selected),))


    df = pd.read_sql("""
    SELECT r.subject, e.name AS equipment, r.technician, r.scheduled_date
    FROM requests r
    JOIN equipment e ON r.equipment_id = e.id
    WHERE r.request_type='Preventive'
    ORDER BY r.scheduled_date
    """, conn)


    # st.dataframe(pd.read_sql("SELECT * FROM requests", conn))


    if df.empty:
        st.info("No preventive maintenance scheduled.")
    else:
        st.dataframe(df)
