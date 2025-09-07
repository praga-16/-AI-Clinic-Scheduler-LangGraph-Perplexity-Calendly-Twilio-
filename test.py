
import os
import re
import requests
import pandas as pd
import streamlit as st
from typing import TypedDict, Dict, Any
from datetime import datetime, date, time as dtime, timedelta
from email.message import EmailMessage
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# -------------------------

load_dotenv()

# -------------------------

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "").strip()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "").strip()
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "").strip()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "").strip()

_RAW_CAL_NEW = os.getenv("EVENT_TYPE_NEW", "").strip()
_RAW_CAL_RET = os.getenv("EVENT_TYPE_RETURNING", "").strip()
CALENDLY_TOKEN = os.getenv("CALENDLY_TOKEN", "").strip()  # optional, for converting API URIs to public URLs

APPOINTMENTS_FILE = os.getenv("APPOINTMENTS_FILE", "appointments.xlsx")
PATIENTS_FILE = os.getenv("PATIENTS_FILE", "patients_50_sample.csv")
SCHEDULE_FILE = os.getenv("SCHEDULE_FILE", "doctor_schedules_14days.xlsx")
PDF_FORM = os.getenv("INTAKE_FORM", "New Patient Intake Form.pdf")
REMINDER_MODE = os.getenv("REMINDER_MODE", "demo").lower()  # demo or prod

# -------------------------

def fetch_calendly_public_url(event_type_value: str, token: str) -> str:
    """If event_type_value is an API event_type URI, fetch scheduling_url via Calendly API v2 using token."""
    if not event_type_value:
        return ""
    m = re.search(r"api\.calendly\.com/event_types/([0-9a-fA-F-]+)", event_type_value)
    if not m:
    
        return event_type_value
    event_uuid = m.group(1)
    if not token:
        print("⚠️ CALENDLY_TOKEN not set — can't fetch scheduling_url; using provided value:", event_type_value)
        return event_type_value
    url = f"https://api.calendly.com/event_types/{event_uuid}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            scheduling_url = None
            if isinstance(data, dict):
                if data.get("resource") and isinstance(data["resource"], dict):
                    scheduling_url = data["resource"].get("scheduling_url")
                scheduling_url = scheduling_url or data.get("scheduling_url")
            if scheduling_url:
                print("✅ Fetched Calendly scheduling_url:", scheduling_url)
                return scheduling_url
            else:
                print("⚠️ 'scheduling_url' not found in Calendly response; using original value.")
                return event_type_value
        else:
            print(f"⚠️ Calendly API returned {r.status_code}: {r.text}; using original value.")
            return event_type_value
    except Exception as e:
        print("⚠️ Error calling Calendly API:", e, " — using original value")
        return event_type_value

CALENDLY_NEW = fetch_calendly_public_url(_RAW_CAL_NEW, CALENDLY_TOKEN) if _RAW_CAL_NEW else os.getenv("CALENDLY_NEW", "https://calendly.com/pragatheesvaranab/new-meeting")
CALENDLY_RETURNING = fetch_calendly_public_url(_RAW_CAL_RET, CALENDLY_TOKEN) if _RAW_CAL_RET else os.getenv("CALENDLY_RETURNING", "https://calendly.com/pragatheesvaranab/30min")


if "api.calendly.com" in (CALENDLY_NEW or ""):
    CALENDLY_NEW = "https://calendly.com/pragatheesvaranab/new-meeting"
if "api.calendly.com" in (CALENDLY_RETURNING or ""):
    CALENDLY_RETURNING = "https://calendly.com/pragatheesvaranab/30min"

# -------------------------
# Load data files (safe)
if os.path.exists(PATIENTS_FILE):
    patients = pd.read_csv(PATIENTS_FILE, dtype=str)
else:
    patients = pd.DataFrame(columns=["first_name", "last_name", "dob"])

if os.path.exists(SCHEDULE_FILE):
    try:
        schedules = pd.read_excel(SCHEDULE_FILE, sheet_name="schedules", dtype=str)
    except Exception:
        schedules = pd.read_excel(SCHEDULE_FILE, dtype=str)
else:
    schedules = pd.DataFrame(columns=["doctor_id", "date", "start_time", "is_available"])

# -------------------------

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        print("⚠️ Twilio init error:", e)
        twilio_client = None

# -------------------------

scheduler = BackgroundScheduler()
scheduler.start()

# -------------------------

class PerplexityClient:
    def __init__(self, api_key: str, model: str = "sonar-pro"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.perplexity.ai/chat/completions"

    def ask(self, prompt: str, timeout: int = 30) -> str:
        if not self.api_key:
            return "[Perplexity API key not set]"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        try:
            r = requests.post(self.url, headers=headers, json=payload, timeout=timeout)
        except Exception as e:
            return f"❌ Request failed: {e}"
        if r.status_code == 200:
            data = r.json()
            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                return str(data)
        else:
            return f"❌ Error {r.status_code}: {r.text}"

perplexity = PerplexityClient(PERPLEXITY_API_KEY)

# -------------------------

def send_email(to_email: str, subject: str, body: str, attach_pdf: str = PDF_FORM) -> str:
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        return "Email credentials not configured."
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    if attach_pdf and os.path.exists(attach_pdf):
        with open(attach_pdf, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(attach_pdf))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return "Email sent"
    except Exception as e:
        return f"Email error: {e}"

def send_sms(to_number: str, body: str) -> str:
    if not twilio_client:
        return "Twilio not configured"
    try:
        msg = twilio_client.messages.create(body=body, from_=TWILIO_PHONE_NUMBER, to=to_number)
        return f"SMS sent ({msg.sid})"
    except Exception as e:
        return f"SMS error: {e}"

def lookup_patient(name: str, dob_str: str):
    if patients.empty or not name:
        return None
    first = name.split()[0].strip().lower()
    found = patients[
        (patients["first_name"].astype(str).str.lower() == first) &
        (patients["dob"].astype(str) == dob_str)
    ]
    return found.iloc[0].to_dict() if not found.empty else None

def find_slot(doctor_id: str, date_str: str, is_new: bool):
    if schedules.empty:
        return {"start_time": "10:00"}
    slot = schedules[
        (schedules["doctor_id"].astype(str) == str(doctor_id)) &
        (schedules["date"].astype(str) == str(date_str)) &
        (schedules["is_available"].astype(str).str.lower() == "true")
    ]
    if not slot.empty:
        return slot.iloc[0].to_dict()
    return None

def save_appointment(appt: dict):
    if os.path.exists(APPOINTMENTS_FILE):
        df_existing = pd.read_excel(APPOINTMENTS_FILE)
        df_new = pd.concat([df_existing, pd.DataFrame([appt])], ignore_index=True)
    else:
        df_new = pd.DataFrame([appt])
    df_new.to_excel(APPOINTMENTS_FILE, index=False)

def compute_reminder_times(appt_date_str: str, slot_time_str: str):
    now = datetime.now()
    if REMINDER_MODE == "prod":
        try:
            appt_date = datetime.strptime(appt_date_str, "%Y-%m-%d").date()
        except Exception:
            appt_date = datetime.today().date()
        try:
            hhmm = slot_time_str.split()[0]
            hh, mm = hhmm.split(":")
            appt_time = dtime(int(hh), int(mm))
        except Exception:
            appt_time = dtime(10, 0)
        appt_dt = datetime.combine(appt_date, appt_time)
        run1 = appt_dt - timedelta(hours=24)
        run2 = appt_dt - timedelta(hours=6)
        run3 = appt_dt - timedelta(hours=1)
        run1 = run1 if run1 > now else now + timedelta(seconds=10)
        run2 = run2 if run2 > now else now + timedelta(seconds=20)
        run3 = run3 if run3 > now else now + timedelta(seconds=30)
        return run1, run2, run3
    else:
        return now + timedelta(seconds=15), now + timedelta(seconds=30), now + timedelta(seconds=45)

def schedule_reminders(patient_email, patient_name, doctor_id, date_str, slot_time_str, patient_phone=None):
    run1, run2, run3 = compute_reminder_times(date_str, slot_time_str)
    scheduler.add_job(send_email, 'date', run_date=run1,
                      args=[patient_email, f"Reminder: {patient_name}", f"Hello {patient_name}, this is your reminder for {date_str} at {slot_time_str}"])
    scheduler.add_job(send_email, 'date', run_date=run2,
                      args=[patient_email, f"Reminder: Intake form - {patient_name}", f"Hello {patient_name}, please complete the attached intake form."])
    scheduler.add_job(send_email, 'date', run_date=run3,
                      args=[patient_email, f"Reminder: Confirm/cancel - {patient_name}", f"Hello {patient_name}, please confirm or cancel your visit."])
    if patient_phone and twilio_client:
        scheduler.add_job(send_sms, 'date', run_date=run1, args=[patient_phone, f"Reminder: Appointment on {date_str} at {slot_time_str}"])
        scheduler.add_job(send_sms, 'date', run_date=run2, args=[patient_phone, "Have you filled the intake form?"])
        scheduler.add_job(send_sms, 'date', run_date=run3, args=[patient_phone, "Please confirm/cancel your appointment."])

# -------------------------

class State(TypedDict):
    patient_name: str
    dob: str
    doctor_id: str
    date: str
    patient_email: str
    patient_phone: str
    answer: str
    recommended_slot: Dict[str, Any]
    booking_result: str

def node_validate(state: State) -> Dict[str, Any]:
    prompt = (
        "Validate this appointment form: "
        f"Name: {state.get('patient_name')}, DOB: {state.get('dob')}, Doctor: {state.get('doctor_id')}, Date: {state.get('date')}.\n"
        "If OK, start with VALID. Otherwise mention issues briefly."
    )
    resp = perplexity.ask(prompt) if PERPLEXITY_API_KEY else "[Perplexity not configured — skipping LLM validation]"
    return {"answer": resp}

def node_recommend(state: State) -> Dict[str, Any]:
    is_new = lookup_patient(state.get("patient_name", ""), state.get("dob", "")) is None
    slot = find_slot(state.get("doctor_id", ""), state.get("date", ""), is_new)
    slot_text = slot.get("start_time") if slot else "No slot available"
    prompt = f"Friendly one-line message for patient about slot: {slot_text} for {state.get('date')} with {state.get('doctor_id')}."
    friendly = perplexity.ask(prompt) if PERPLEXITY_API_KEY else "[No LLM]"
    return {"recommended_slot": slot or {}, "answer": state.get("answer", "") + "\n\n" + friendly}

def node_confirm(state: State) -> Dict[str, Any]:
    slot = state.get("recommended_slot") or find_slot(state.get("doctor_id",""), state.get("date",""), lookup_patient(state.get("patient_name",""), state.get("dob","")) is None)
    if not slot:
        return {"booking_result": "No slot available; booking not created.", "answer": state.get("answer", "") + "\n\nBooking not created."}

    appt = {
        "patient_name": state.get("patient_name"),
        "dob": state.get("dob"),
        "doctor_id": state.get("doctor_id"),
        "date": state.get("date"),
        "start_time": slot.get("start_time"),
        "is_new_patient": lookup_patient(state.get("patient_name",""), state.get("dob","")) is None,
        "insurance_carrier": None,
        "member_id": None,
        "group_number": None,
        "patient_phone": state.get("patient_phone")
    }
    save_appointment(appt)
    booking_link = CALENDLY_NEW if appt["is_new_patient"] else CALENDLY_RETURNING

    email_status = send_email(state.get("patient_email"), "Appointment Confirmation", f"Hello {appt['patient_name']},\nYour appointment is confirmed.\nDoctor: {appt['doctor_id']}\nDate: {appt['date']}\nTime: {appt['start_time']}\nBooking link: {booking_link}\nPlease find attached the intake form.", attach_pdf=PDF_FORM) if state.get("patient_email") else "No email provided"
    sms_status = send_sms(state.get("patient_phone"), f"Appointment confirmed: {appt['date']} {appt['start_time']}. Link: {booking_link}") if state.get("patient_phone") else "No phone provided"

    schedule_reminders(state.get("patient_email"), appt["patient_name"], appt["doctor_id"], appt["date"], appt["start_time"], appt["patient_phone"])

    result = f"Booking created. Email: {email_status}. SMS: {sms_status}. Link: {booking_link}"
    return {"booking_result": result, "answer": state.get("answer", "") + "\n\n" + result}


graph = StateGraph(State)
graph.add_node("validate", node_validate)
graph.add_node("recommend", node_recommend)
graph.add_node("confirm", node_confirm)
graph.set_entry_point("validate")
graph.add_edge("validate", "recommend")
graph.add_edge("recommend", "confirm")
graph.add_edge("confirm", END)
workflow = graph.compile()

# -------------------------

st.set_page_config(page_title="AI Clinic Scheduler", layout="centered")
st.title("🏥 AI Clinic Scheduler (LangGraph)")

st.markdown("Fill the form. Booking will be created automatically and you will receive confirmation + reminders.")

with st.form("booking_form", clear_on_submit=True):
    patient_name = st.text_input("Patient Name")
    dob_date = st.date_input("Date of Birth", min_value=date(1900,1,1), max_value=date.today())
    doctor_id = st.text_input("Doctor ID", value="D001")
    appointment_date = st.date_input("Appointment Date", min_value=date.today())
    patient_email = st.text_input("Email")
    patient_phone = st.text_input("Phone (E.164, e.g. +918220420788)")
    insurance_carrier = st.text_input("Insurance (optional)")
    member_id = st.text_input("Member ID (optional)")
    group_number = st.text_input("Group Number (optional)")
    submitted = st.form_submit_button("📅 Book Appointment")

if submitted:
    state_in = {
        "patient_name": patient_name.strip(),
        "dob": dob_date.strftime("%Y-%m-%d"),
        "doctor_id": doctor_id.strip(),
        "date": appointment_date.strftime("%Y-%m-%d"),
        "patient_email": patient_email.strip(),
        "patient_phone": patient_phone.strip(),
        "answer": "",
        "recommended_slot": {},
        "booking_result": ""
    }

    result_state = workflow.invoke(state_in)

    if result_state.get("booking_result", "").lower().startswith("booking created"):
        st.success(result_state["booking_result"])
        is_new = lookup_patient(state_in["patient_name"], state_in["dob"]) is None
        booking_link = CALENDLY_NEW if is_new else CALENDLY_RETURNING
        st.markdown(f"📅 **Booking link:** [{booking_link}]({booking_link})")
    else:
        st.error(result_state.get("booking_result") or "Booking could not be created. Check logs.")



