# 🏥 Clinic Management System (Odoo 17)

## 📌 Project Overview
The **Clinic Management System** is a custom healthcare management module developed using the Odoo 17 ERP framework.  
This system helps clinics efficiently manage patient records, appointments, prescriptions, and follow-ups through a centralized platform.

The module automates daily clinic operations and improves workflow by organizing medical data in a structured and accessible way.

---

## 🚀 Features

- Patient Registration & Management  
- Doctor Management  
- Appointment Scheduling  
- OPD Management  
- Follow-up Tracking  
- Prescription Management (Wizard)  
- Appointment Stage Tracking  
- Kanban View for Appointments  
- Centralized Patient Medical Records  

---

## 🛠 Technologies Used

- Python  
- PostgreSQL  
- Odoo 17 Framework  
- XML (Odoo Views)  
- HTML / CSS  

---

## 📂 Module Structure
lax_hms
│
├── models
│ ├── __init__.py
│ ├── appointment.py
│ ├── patient.py
│ ├── doctor.py
│ ├── opd.py
│ ├── stage.py
│ └── diseases.py
│
├── views
│ ├── appointment_view.xml
│ ├── patient_view.xml
│ ├── doctor_view.xml
│ ├── opd_view.xml
│ ├── followup_view.xml
│ └── menu.xml
│
├── wizard
│ ├── prescription_wizard.py
│ └── prescription_wizard_view.xml
│
├── security
│ └── ir.model.access.csv
│
├── data
│ ├── sequence.xml
│ └── stage_data.xml
│
├── __init__.py
└── __manifest__.py

---

## ⚙️ Installation

1. Clone the repository

git clone https://github.com/yukta890/clinic_management_system.git

2. Move the module to the **Odoo custom_addons** folder.

3. Restart the Odoo server.

4. Go to **Apps → Update Apps List**.

5. Install **Clinic Management System** module.

---

## 🎯 Purpose of the Project

The main objective of this project is to gain practical experience in **ERP development using Odoo** and build a real-world healthcare management solution.

This project demonstrates:

- Odoo module development  
- Backend logic using Python  
- Database integration with PostgreSQL  
- ERP workflow and data management  

---

## 👩‍💻 Author

**Yukta Lakhani**

LinkedIn  
https://www.linkedin.com/in/yukta-lakhani-992a1b277

GitHub  
https://github.com/yukta890

---

⭐ If you find this project useful, feel free to star the repository.
