# 🏥 AI Clinic Scheduler (LangGraph + Perplexity + Calendly + Twilio)

An intelligent **clinic appointment booking and reminder system** built with:

- **LangGraph** → multi-agent orchestration (validate → recommend → confirm).  
- **Perplexity LLM** → validates input & generates patient-friendly messages.  
- **Calendly** → provides booking/rescheduling links.  
- **Email (SMTP)** → sends confirmations & intake forms.  
- **Twilio SMS** → sends SMS confirmations and reminders.  
- **Streamlit** → interactive web app for patients to book appointments.  
- **APScheduler** → schedules reminders (demo mode + production mode).  
- **Excel/CSV** → stores patients, doctor schedules, and appointments.  

---

## ✨ Features

- 📋 Patient form (Streamlit) → Name, DOB, Doctor, Date, Email, Phone, Insurance.  
- 🤖 **LangGraph workflow**:
  1. **Validate** → Perplexity checks appointment details.  
  2. **Recommend** → Suggests available slot in friendly language.  
  3. **Confirm** → Books appointment, sends email/SMS, attaches intake form, schedules reminders.  
- 📅 **Calendly links**:
  - New patients → `/new-meeting`  
  - Returning patients → `/30min`  
- 📧 Email notifications with PDF intake form.  
- 📱 SMS confirmations + reminders (via Twilio).  
- ⏰ Automated reminders (demo mode: 15s/30s/45s, prod mode: 24h/6h/1h before).  
- 📊 Appointments stored in `appointments.xlsx`.  

---

## 🛠️ Setup

<img width="1912" height="1021" alt="image" src="https://github.com/user-attachments/assets/8cd0ee4c-a73e-4994-82a9-bc107be93ee9" />

<img width="1919" height="1028" alt="image" src="https://github.com/user-attachments/assets/9e6f9d35-c71a-4fdc-95fe-094b57869317" />
<img width="1914" height="1034" alt="image" src="https://github.com/user-attachments/assets/0b256a8a-e88b-4b8c-8cad-0649b87ee8a8" />
## Email + SMS confirmation sent.
<img width="1919" height="1024" alt="image" src="https://github.com/user-attachments/assets/afd4337b-0174-43b4-824c-7048f9a1df4a" />
<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/c02f3f97-2892-43cd-9be2-ebb947d24ae8" />
### 📱 SMS reminders

https://github.com/user-attachments/assets/ea03dd8f-a8aa-4295-97a6-aee859ae3819





## BOOKING DETAILS ON EXCEL FOR ADMIN USES(Appointment saved to Excel)
<img width="1918" height="1079" alt="image" src="https://github.com/user-attachments/assets/9ba7e8f3-d3af-4952-bfe8-3e9ad9893a64" />
## FULL VIDEO EXPLAINATION
https://github.com/user-attachments/assets/11eaa2ed-bf09-46e5-b46f-110dc79f996c
### 1. Clone Repo
```bash
git clone https://github.com/yourusername/ai-clinic-scheduler.git
cd ai-clinic-scheduler
