import requests
from bs4 import BeautifulSoup

# --- ধাপ ১: আপনার তথ্যগুলো পূরণ করুন ---
LOGIN_URL = 'http://180.92.235.190:8022/erp/login.php'
FORM_ACTION_URL = 'http://180.92.235.190:8022/erp/login.php'
DATA_URL = 'http://180.92.235.190:8022/erp/production/reports/requires/sewing_input_and_output_report_controller.php'

USERNAME = 'Clothing-cutting'
PASSWORD = '489356'

USERNAME_FIELD_NAME = 'txt_userid'
PASSWORD_FIELD_NAME = 'txt_password'

# --- লগইন করার জন্য ডেটা (Payload) ---
login_payload = {
    'hiddenUserIP': '',
    'hiddenUserMAC': '',
    USERNAME_FIELD_NAME: USERNAME,
    PASSWORD_FIELD_NAME: PASSWORD,
    'submit': 'Login',
    'txt_reset_user': '',
    'txt_reset_email': '',
}

# --- ডেটা খোঁজার জন্য হেডার ---
data_headers = {
    'Host': '180.92.235.190:8022',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://180.92.235.190:8022',
    'Referer': 'http://180.92.235.190:8022/erp/production/reports/sewing_input_and_output_report.php?permission=1_1_1_1',
}

# একটি সেশন অবজেক্ট তৈরি করা হচ্ছে যা কুকি মনে রাখবে
session = requests.Session()

try:
    # --- ধাপ ২: লগইন করা ---
    print("⏳ Logging in...")
    login_response = session.post(FORM_ACTION_URL, data=login_payload)
    login_response.raise_for_status()

    if "logout" not in login_response.text.lower():
        print("❌ Login failed. Please check credentials.")
    else:
        print("✅ Login successful!")
        
        # --- ধাপ ৩: তথ্য খোঁজা ---
        txt_int_ref = input("🔢 Enter Reference (txt_int_ref): ")
        found = False

        for year in ['2025', '2024']:
            for company_id in range(1, 11):
                data_payload = {
                    'action': 'generate_report',
                    'cbo_company_name': str(company_id),
                    'hidden_job_id': '',
                    'hidden_color_id': '',
                    'cbo_year': year,
                    'cbo_wo_company_name': '2',
                    'cbo_location_name': '2',
                    'hidden_floor_id': '',
                    'hidden_line_id': '',
                    'txt_int_ref': txt_int_ref,
                    'type': '1',
                    'report_title': '❏ Sewing Input and Output Report'
                }

                # লগইন করা সেশনটি ব্যবহার করে ডেটা রিকোয়েস্ট পাঠানো
                response = session.post(DATA_URL, headers=data_headers, data=data_payload)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_no = None
                    buyer = None

                    for td in soup.find_all('td'):
                        if 'Job No' in td.get_text(strip=True):
                            job_no = td.find_next_sibling('td').get_text(strip=True)
                        if 'Buyer' in td.get_text(strip=True):
                            buyer = td.find_next_sibling('td').get_text(strip=True)

                    if job_no or buyer:
                        print('\n✅ তথ্য পাওয়া গেছে:')
                        print(f'📅 Year: {year}')
                        print(f'🏢 Company ID: {company_id}')
                        if job_no:
                            print('📌 Job No:', job_no)
                        if buyer:
                            print('📌 Buyer:', buyer)
                        found = True
                        break
            if found:
                break
        
        if not found:
            print('\n❌ কোনো তথ্য পাওয়া যায়নি।')

except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred: {e}")
