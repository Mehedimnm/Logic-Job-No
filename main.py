from flask import Flask, request, jsonify
from flask_cors import CORS # নতুন লাইন
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app) # নতুন লাইন

# --- আপনার লগইন এবং অন্যান্য তথ্য ---
LOGIN_URL = 'http://180.92.235.190:8022/erp/login.php'
DATA_URL = 'http://180.92.235.190:8022/erp/production/reports/requires/sewing_input_and_output_report_controller.php'
USERNAME = 'Clothing-cutting'
PASSWORD = 'আপনার_সঠিক_পাসওয়ার্ড_দিন'

# --- লগইন ফর্মের সঠিক ফিল্ডের নাম ---
login_payload = {
    'hiddenUserIP': '', 'hiddenUserMAC': '', 'txt_userid': USERNAME,
    'txt_password': PASSWORD, 'submit': 'Login',
    'txt_reset_user': '', 'txt_reset_email': '',
}

# --- ডেটা খোঁজার জন্য হেডার ---
data_headers = {
    'Host': '180.92.235.190:8022',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://180.92.235.190:8022',
    'Referer': 'http://180.92.235.190:8022/erp/production/reports/sewing_input_and_output_report.php?permission=1_1_1_1',
}

session = requests.Session()

@app.route('/get_info', methods=['GET'])
def get_sewing_info():
    txt_int_ref = request.args.get('ref')
    if not txt_int_ref:
        return jsonify({'status': 'error', 'message': 'Please provide a reference number using ?ref='}), 400
    try:
        login_response = session.post(LOGIN_URL, data=login_payload, timeout=15)
        login_response.raise_for_status()
        if "logout" not in login_response.text.lower():
            return jsonify({'status': 'error', 'message': 'Login failed. Check credentials.'}), 401
        for year in ['2025', '2024']:
            for company_id in range(1, 11):
                data_payload = {
                    'action': 'generate_report', 'cbo_company_name': str(company_id),
                    'hidden_job_id': '', 'hidden_color_id': '', 'cbo_year': year,
                    'cbo_wo_company_name': '2', 'cbo_location_name': '2',
                    'hidden_floor_id': '', 'hidden_line_id': '',
                    'txt_int_ref': txt_int_ref, 'type': '1',
                    'report_title': '❏ Sewing Input and Output Report'
                }
                response = session.post(DATA_URL, headers=data_headers, data=data_payload, timeout=10)
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
                        result = {
                            'status': 'success', 'year': year, 'company_id': company_id,
                            'job_no': job_no if job_no else 'N/A',
                            'buyer': buyer if buyer else 'N/A'
                        }
                        return jsonify(result)
        return jsonify({'status': 'error', 'message': 'No information found for the given reference.'}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': f'An error occurred: {e}'}), 500
