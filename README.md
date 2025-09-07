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

### Set Up Environment Variables
Install Dependencies
Create a .env file in the project root with the following:
```
# === LLM (Perplexity) ===
PERPLEXITY_API_KEY=your_perplexity_api_key

# === Email Settings (Gmail example) ===
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password  # Use App Password, not personal password

# === Twilio SMS Settings ===
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio number

# === Calendly Event Types ===
EVENT_TYPE_NEW=https://calendly.com/yourname/new-meeting
EVENT_TYPE_RETURNING=https://calendly.com/yourname/30min
CALENDLY_TOKEN=your_calendly_api_token   # Optional (needed only if using API event_type URIs)

# === File Paths ===
APPOINTMENTS_FILE=appointments.xlsx
PATIENTS_FILE=patients_50_sample.csv
SCHEDULE_FILE=doctor_schedules_14days.xlsx
INTAKE_FORM=New Patient Intake Form.pdf

# === Reminder Mode ===
REMINDER_MODE=demo   # use "prod" for real reminder scheduling (24h, 6h, 1h before)

```
⚠️ Important:

For Gmail, generate an App Password
 and use it instead of your regular password.

Twilio requires you to verify your phone number
 in trial mode.

### 📂 Project Structure
```
├── test.py                        # Main Streamlit app (LangGraph workflow)
├── patients_50_sample.csv        # Sample patient data
├── doctor_schedules_14days.xlsx  # Doctor availability schedule
├── appointments.xlsx             # Saved bookings (auto-generated)
├── New Patient Intake Form.pdf    # Example intake form (sent via email)
├── requirements.txt              # Python dependencies
└── README.md                     # Project docs
```
### Prepare Mock Data

Ensure these files are present in your project folder:
patients_50_sample.csv → Synthetic patient data (50 records).
doctor_schedules_14days.xlsx → Doctor availability schedule (2 weeks).
New Patient Intake Form.pdf → Intake form sent to patients.
(Samples are provided — replace with your own if needed)

### Run the App

Start the Streamlit app:
```
streamlit run test.py
```
This will open the UI in your default browser → fill patient details → book appointment.

### Verify Outputs
```
✅ Appointment saved in appointments.xlsx
✅ Email sent to patient with intake form
✅ SMS confirmation sent (if Twilio configured)
✅ Reminders scheduled automatically
✅ Calendly reschedule link included
```
### STREAMLIT INTERFACE
<img width="1912" height="1021" alt="Streamlit interface" src="https://github.com/user-attachments/assets/8cd0ee4c-a73e-4994-82a9-bc107be93ee9" />

### FILL THE FORM
<img width="1919" height="1028" alt="Fill the form" src="https://github.com/user-attachments/assets/9e6f9d35-c71a-4fdc-95fe-094b57869317" />

### HIT SUBMIT
<img width="1914" height="1034" alt="Submit form" src="https://github.com/user-attachments/assets/0b256a8a-e88b-4b8c-8cad-0649b87ee8a8" />

### Email + SMS Confirmation
<img width="1919" height="1024" alt="Email confirmation" src="https://github.com/user-attachments/assets/afd4337b-0174-43b4-824c-7048f9a1df4a" />
<img width="1919" height="1030" alt="SMS confirmation" src="https://github.com/user-attachments/assets/c02f3f97-2892-43cd-9be2-ebb947d24ae8" />

### 📱 SMS Reminders
https://github.com/user-attachments/assets/ea03dd8f-a8aa-4295-97a6-aee859ae3819

![SMS Screenshot](https://github.com/user-attachments/assets/ccfec2f5-8ebe-4c0c-8af4-ef61754638ad)

---

## BOOKING DETAILS ON EXCEL (Admin View)
<img width="1918" height="1079" alt="Excel booking details" src="https://github.com/user-attachments/assets/9ba7e8f3-d3af-4952-bfe8-3e9ad9893a64" />

---

## 🎥 Full Video Walkthrough




https://github.com/user-attachments/assets/888bd0a5-88ff-4bb6-a90f-f2903a932351


---

## 🚀 Setup Instructions

### 1. Clone Repo
```bash
[git clone https://github.com/yourusername/ai-clinic-scheduler.git
cd ai-clinic-scheduler
](https://github.com/praga-16/-AI-Clinic-Scheduler-LangGraph-Perplexity-Calendly-Twilio-.git)
