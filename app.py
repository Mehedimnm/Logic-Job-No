import requests
from bs4 import BeautifulSoup

# ====== তুমি এখানে রেফারেন্স বসাও ======
txt_int_ref = input("🔢 Enter Reference (txt_int_ref): ")

url = 'http://180.92.235.190:8022/erp/production/reports/requires/sewing_input_and_output_report_controller.php'

headers = {
    'Host': '180.92.235.190:8022',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://180.92.235.190:8022',
    'Referer': 'http://180.92.235.190:8022/erp/production/reports/sewing_input_and_output_report.php?permission=1_1_1_1',
    'Accept-Language': 'en-US,en;q=0.9,de;q=0.8,bn;q=0.7',
    'Cookie': 'PHPSESSID=e5f800f578df0085043b3663626659ac'
}

found = False

# ====== 2025 ও 2024 - দুইটা সালেই চেষ্টা করবে ======
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

        response = requests.post(url, headers=headers, data=data)

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
                print('✅ তথ্য পাওয়া গেছে:')
                print(f'📅 Year: {year}')
                print(f'🏢 Company ID: {company_id}')
                if job_no:
                    print('📌 Job No:', job_no)
                if buyer:
                    print('📌 Buyer:', buyer)
                found = True
                break  # তথ্য পেলে আর চালাতে হবে না
    if found:
        break

if not found:
    print('❌ কোনো তথ্য পাওয়া যায়নি। Year ও Company ID সব চেষ্টা করা হয়েছে।')