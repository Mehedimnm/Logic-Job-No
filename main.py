from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/get_info', methods=['GET'])
def get_sewing_info():
    # URL থেকে রেফারেন্স নাম্বার নেওয়া হচ্ছে (যেমন: /get_info?ref=12345)
    txt_int_ref = request.args.get('ref')

    if not txt_int_ref:
        return jsonify({'error': 'Please provide a reference number using ?ref='}), 400

    url = 'http://180.92.235.190:8022/erp/production/reports/requires/sewing_input_and_output_report_controller.php'

    headers = {
        'Host': '180.92.235.190:8022',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://180.92.235.190:8022',
        'Referer': 'http://180.92.235.190:8022/erp/production/reports/sewing_input_and_output_report.php?permission=1_1_1_1',
        'Cookie': 'PHPSESSID=e5f800f578df0085043b3663626659ac'
    }

    # 2025 ও 2024 - দুইটা সালেই চেষ্টা করবে
    for year in ['2025', '2024']:
        for company_id in range(1, 11):
            data = {
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

            try:
                response = requests.post(url, headers=headers, data=data, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                # যদি সার্ভার কানেক্ট না হয়, পরেরটিতে চেষ্টা করবে
                continue

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
                        'status': 'success',
                        'year': year,
                        'company_id': company_id,
                        'job_no': job_no if job_no else 'N/A',
                        'buyer': buyer if buyer else 'N/A'
                    }
                    return jsonify(result)

    # সব চেষ্টা করার পরেও তথ্য না পাওয়া গেলে
    return jsonify({'status': 'error', 'message': 'No information found for the given reference.'}), 404

if __name__ == "__main__":
    app.run(debug=True)

