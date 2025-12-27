#  GearGuard – The Ultimate Maintenance Tracker

GearGuard is a **Streamlit-based Maintenance Management System (CMMS)** designed to efficiently track equipment, manage maintenance requests, assign technicians, and plan preventive maintenance using calendar-based scheduling.

It mirrors **real-world industrial maintenance workflows** while remaining lightweight and easy to deploy using **SQLite**.

---

##  Problem Statement

Organizations struggle with:
- Untracked equipment maintenance
- Reactive repairs instead of preventive planning
- Poor visibility of technician workload
- No clear lifecycle management for equipment

**GearGuard solves this by providing a centralized, intelligent maintenance tracking platform.**

---

##  Solution Overview

GearGuard allows organizations to:
- Maintain a complete inventory of equipment
- Track corrective & preventive maintenance requests
- Assign maintenance teams and technicians
- Visualize maintenance status using a Kanban board
- Plan preventive maintenance via calendar views
- Scrap equipment safely while preserving history
- Analyze workload and performance using reports

---

##  Key Features

###  Equipment Management
- Add & manage equipment details
- Assign maintenance team & default technician
- Track warranty, location, and ownership
- Scrap equipment (soft delete – history preserved)

###  Maintenance Requests
- Corrective & Preventive requests
- Auto-fill team & technician from equipment
- Status tracking: New → In Progress → Repaired → Scrap
- Track hours spent on repairs

###  Kanban Board
- Visual workflow for maintenance stages
- Overdue task detection
- Auto-scrap equipment from Kanban

###  Preventive Maintenance Calendar
- Daily / Weekly / Monthly views
- Filter preventive schedules by date range

###  Teams & Technicians
- Create maintenance teams
- Assign technicians using dropdowns
- Team-wise technician listing
- Workload & active request count per team
- Safe deletion (blocked if dependencies exist)

###  Reports & Analytics
- Team workload overview
- Equipment failure frequency
- Preventive vs corrective ratio
- Maintenance time analysis

---

##  System Architecture

User → Streamlit UI → SQLite Database

---

##  Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** SQLite  
- **Data Handling:** Pandas  

---

##  Installation & Setup

```bash
git clone https://github.com/your-username/gearguard.git
cd gearguard
pip install streamlit pandas
streamlit run app1.py
```

---

##  Why Equipment Scrapping Exists

Scrapping:
- Removes equipment from active operations
- Prevents new maintenance requests
- Preserves historical data for audits & reports

> Scrapping is a soft delete, not a permanent removal.

---

##  Future Enhancements

- Role-based authentication
- Technician auto-assignment
- SLA & cost tracking
- Predictive maintenance using ML

---




