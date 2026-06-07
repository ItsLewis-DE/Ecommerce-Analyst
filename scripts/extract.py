from curl_cffi import requests
import json

# LƯU Ý: Bạn cần copy lại cURL từ trình duyệt một lần nữa vì token và cookies (đặc biệt là cf_clearance và XSRF-TOKEN) sẽ hết hạn rất nhanh.


cookies = {
    '_gcl_au': '1.1.1579798339.1779551379',
    '_taid': 'N62uohGAOa.1779551379695',
    '_fbp': 'fb.1.1779551380150.70732008587825946',
    '_tt_enable_cookie': '1',
    '_ttp': '01KSARE8Z39ATN2AE6ERD2HBFF_.tt.1',
    '_gid': 'GA1.2.697677342.1780795725',
    'popup-ebook-cv': '1',
    '_tasid': 'ywO8TVfHDq.1780795725180',
    '_tafp': 'dfe0b8b7a6013116eafbb57f444e65de',
    '_clck': '9fvn99%5E2%5Eg6p%5E0%5E2334',
    'popup-anti-scam': 'false',
    'cf_clearance': '29v0d8mSw2C888xif7irjE6nWFbBsqY_yBHIAwAmc7E-1780798194-1.2.1.1-myvPWaLf04I_WEOn.DGaMnDJ7a1OCXN3W3cAK3OpGj2ghnPb6a7reQHxUo68xe7CD0FVAN3gK6jDwrEYDF8w.dFzOWXK4YeUouJE3j65dkCP0rIHOqDJm_tpJ_YvNNXbkvvDHu5iEGM.IRTskLLR.69vjelaeHMEVE.iDU0NQHO.tlQwSUmsHZFt1ZKw3Q.84bok9tvK9wtmo2zszUArIgYcGZ0HNDMh0uSoENIB9C8g07cj0RPEi1ZfeJpDOt9NMDqEmcWxlBppClzUsKFZEqmb59piOt6Y4v1ezgP.gvMM.b5zVEtIs1Rv5q7YR5jNM2.u2Vqq4BpqHUp7E8z_FA',
    'g_state': '{"i_l":0,"i_ll":1780798335719,"i_b":"OsxFo3P5CmOU7UU7MfN3swAtEKWuRSmGH+O1DH6GMG8","i_e":{"enable_itp_optimization":0},"i_et":1779551380083}',
    '_ga_F385SHE0Y3': 'GS2.1.s1780795726$o3$g1$t1780798745$j60$l0$h0',
    '_tasla': '1780798745678',
    '_ga': 'GA1.2.2022484824.1779551378',
    '_gat_UA-55579411-1': '1',
    '_clsk': 'e6pqer%5E1780798746389%5E10%5E0%5Ei.clarity.ms%2Fcollect',
    'ttcsid': '1780795727913::StU85i9HyHiM_wNul862.3.1780798746414.0::1.3017077.3018286::963068.9.925.798::2878710.148.400',
    'ttcsid_D0FPAFRC77UA600KP0E0': '1780795727912::AwxwVrl8O2BrlIuSGHSH.3.1780798746414.1',
    'ref_source_tracking_id': 'eyJpdiI6IlpNQWlxSVlSZFU5Ny9XdlJ4bzhVc2c9PSIsInZhbHVlIjoiVHNDenQ2bGdEWVhPeW1QcTFxRGRBcDdhRjBtbEdNQVBLdXRuZ0ZrYUZNcExoNUJ0ZEhncGhQeUZUNzh6ZHU3cFVhcTk2emhlM2JTaHNwdUtDZlFkNWJtOHRzMnI3Yi9pS1RBRU5RbjgveTg9IiwibWFjIjoiNGZkOWJhOGIzZWQ4YmMxMjc0OGM5NDVmMTg4ZmU5MjkwZjNkODEyYzAxZWU3N2UwNDI2OWVlNTI5OGMxMGYyOSIsInRhZyI6IiJ9',
    'XSRF-TOKEN': 'eyJpdiI6IkVpVEpnOHJaT25PNWhXWEZ1UEtzVnc9PSIsInZhbHVlIjoiZXBJT2pwVGxuWEJ2TVRwNEYzZDIrYUhsaUFNTitzS3RIYVRId3h5am5wZXROY3dYajZuN2xuWlY5YXRwaFdWMnEwalBmd29wY0V4M3VEc1lxMEU2aWEyUmpIK1NINGZ4S1c1eGlld3IxWDloMXBTcjYzcXJrbnphY3V6b3MwSVAiLCJtYWMiOiJkZjZhNmNjYTE5MGFlMDU2OTljMGVkYWZmNmIzYjA5NmI5NGY1ZWI3YzJmMWZiYTQwNThhYzVlYjE3ODIwNWViIiwidGFnIjoiIn0%3D',
    'topcv_session': 'eyJpdiI6IlFsSWR5WW5SZUE4ejM0NVY1Tk8rSlE9PSIsInZhbHVlIjoibFpkRmxJUmZoMFI2anIxTjBxY01wSk9EVE9uemlKUEhuS2U5WS8zbk85NlVoUXBQMkxRelJlR09Vayt0ZFNYQ08xUFUzQVQxR0VjVGs0WG12MnlCYzhWZm9OU1VqMHVReWhoQ0NFVVVtM0pnblpYY1RRNUhvZXd3Ym9ZK3dqZ2UiLCJtYWMiOiIxYjExMzc3OWM5MjAwNzg5ODllZDhhNGZlOGFhMGU0NmJmMjc0MWZkNDE4ZTUzZjg4ZWU3MWVlZWEwNTYxZmQ5IiwidGFnIjoiIn0%3D',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.topcv.vn',
    'priority': 'u=1, i',
    'referer': 'https://www.topcv.vn/',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-xsrf-token': 'eyJpdiI6IkVpVEpnOHJaT25PNWhXWEZ1UEtzVnc9PSIsInZhbHVlIjoiZXBJT2pwVGxuWEJ2TVRwNEYzZDIrYUhsaUFNTitzS3RIYVRId3h5am5wZXROY3dYajZuN2xuWlY5YXRwaFdWMnEwalBmd29wY0V4M3VEc1lxMEU2aWEyUmpIK1NINGZ4S1c1eGlld3IxWDloMXBTcjYzcXJrbnphY3V6b3MwSVAiLCJtYWMiOiJkZjZhNmNjYTE5MGFlMDU2OTljMGVkYWZmNmIzYjA5NmI5NGY1ZWI3YzJmMWZiYTQwNThhYzVlYjE3ODIwNWViIiwidGFnIjoiIn0=',
    # 'cookie': '_gcl_au=1.1.1579798339.1779551379; _taid=N62uohGAOa.1779551379695; _fbp=fb.1.1779551380150.70732008587825946; _tt_enable_cookie=1; _ttp=01KSARE8Z39ATN2AE6ERD2HBFF_.tt.1; _gid=GA1.2.697677342.1780795725; popup-ebook-cv=1; _tasid=ywO8TVfHDq.1780795725180; _tafp=dfe0b8b7a6013116eafbb57f444e65de; _clck=9fvn99%5E2%5Eg6p%5E0%5E2334; popup-anti-scam=false; cf_clearance=29v0d8mSw2C888xif7irjE6nWFbBsqY_yBHIAwAmc7E-1780798194-1.2.1.1-myvPWaLf04I_WEOn.DGaMnDJ7a1OCXN3W3cAK3OpGj2ghnPb6a7reQHxUo68xe7CD0FVAN3gK6jDwrEYDF8w.dFzOWXK4YeUouJE3j65dkCP0rIHOqDJm_tpJ_YvNNXbkvvDHu5iEGM.IRTskLLR.69vjelaeHMEVE.iDU0NQHO.tlQwSUmsHZFt1ZKw3Q.84bok9tvK9wtmo2zszUArIgYcGZ0HNDMh0uSoENIB9C8g07cj0RPEi1ZfeJpDOt9NMDqEmcWxlBppClzUsKFZEqmb59piOt6Y4v1ezgP.gvMM.b5zVEtIs1Rv5q7YR5jNM2.u2Vqq4BpqHUp7E8z_FA; g_state={"i_l":0,"i_ll":1780798335719,"i_b":"OsxFo3P5CmOU7UU7MfN3swAtEKWuRSmGH+O1DH6GMG8","i_e":{"enable_itp_optimization":0},"i_et":1779551380083}; _ga_F385SHE0Y3=GS2.1.s1780795726$o3$g1$t1780798745$j60$l0$h0; _tasla=1780798745678; _ga=GA1.2.2022484824.1779551378; _gat_UA-55579411-1=1; _clsk=e6pqer%5E1780798746389%5E10%5E0%5Ei.clarity.ms%2Fcollect; ttcsid=1780795727913::StU85i9HyHiM_wNul862.3.1780798746414.0::1.3017077.3018286::963068.9.925.798::2878710.148.400; ttcsid_D0FPAFRC77UA600KP0E0=1780795727912::AwxwVrl8O2BrlIuSGHSH.3.1780798746414.1; ref_source_tracking_id=eyJpdiI6IlpNQWlxSVlSZFU5Ny9XdlJ4bzhVc2c9PSIsInZhbHVlIjoiVHNDenQ2bGdEWVhPeW1QcTFxRGRBcDdhRjBtbEdNQVBLdXRuZ0ZrYUZNcExoNUJ0ZEhncGhQeUZUNzh6ZHU3cFVhcTk2emhlM2JTaHNwdUtDZlFkNWJtOHRzMnI3Yi9pS1RBRU5RbjgveTg9IiwibWFjIjoiNGZkOWJhOGIzZWQ4YmMxMjc0OGM5NDVmMTg4ZmU5MjkwZjNkODEyYzAxZWU3N2UwNDI2OWVlNTI5OGMxMGYyOSIsInRhZyI6IiJ9; XSRF-TOKEN=eyJpdiI6IkVpVEpnOHJaT25PNWhXWEZ1UEtzVnc9PSIsInZhbHVlIjoiZXBJT2pwVGxuWEJ2TVRwNEYzZDIrYUhsaUFNTitzS3RIYVRId3h5am5wZXROY3dYajZuN2xuWlY5YXRwaFdWMnEwalBmd29wY0V4M3VEc1lxMEU2aWEyUmpIK1NINGZ4S1c1eGlld3IxWDloMXBTcjYzcXJrbnphY3V6b3MwSVAiLCJtYWMiOiJkZjZhNmNjYTE5MGFlMDU2OTljMGVkYWZmNmIzYjA5NmI5NGY1ZWI3YzJmMWZiYTQwNThhYzVlYjE3ODIwNWViIiwidGFnIjoiIn0%3D; topcv_session=eyJpdiI6IlFsSWR5WW5SZUE4ejM0NVY1Tk8rSlE9PSIsInZhbHVlIjoibFpkRmxJUmZoMFI2anIxTjBxY01wSk9EVE9uemlKUEhuS2U5WS8zbk85NlVoUXBQMkxRelJlR09Vayt0ZFNYQ08xUFUzQVQxR0VjVGs0WG12MnlCYzhWZm9OU1VqMHVReWhoQ0NFVVVtM0pnblpYY1RRNUhvZXd3Ym9ZK3dqZ2UiLCJtYWMiOiIxYjExMzc3OWM5MjAwNzg5ODllZDhhNGZlOGFhMGU0NmJmMjc0MWZkNDE4ZTUzZjg4ZWU3MWVlZWEwNTYxZmQ5IiwidGFnIjoiIn0%3D',
}

data = {
    'page': 1,
    'limit': 20,
    'city': 0,
    'salary': None,
    'exp': None,
    'category': ['Data Engineer,Data Analyst, Data Science'],
    'reRanking': '[]',
}
try:
    print("Đang gửi request...")
    # Sử dụng curl_cffi.requests.post thay cho requests.post
    # impersonate="chrome" giúp qua mặt Cloudflare TLS fingerprint
    response = requests.post('https://www.topcv.vn/api-featured-jobs', cookies=cookies, headers=headers, json=data, impersonate="chrome")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Lấy dữ liệu thành công!")
        res_json = response.json()
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(res_json, f, indent=2, ensure_ascii=False)
    elif response.status_code == 419:
        print("Lỗi 419 (Page Expired) - CSRF Token hoặc Session đã hết hạn. Bạn cần F5 lại trình duyệt, copy cURL mới và thử lại!")
    else:
        print(f"Lỗi {response.status_code}:", response.text[:200])

except Exception as e:
    print("Lỗi hệ thống:", e)
