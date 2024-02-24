import datetime
import os
import sys
import re
import requests
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from hashlib import sha256
 pip install pdfminer

def generate_otp(mobile:str, request_header:dict):
    '''
    generates otp and returns txnId
    '''
    url = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"

    response = requests.post(url, headers=request_header, json={'mobile':mobile})
    status_code = response.status_code
    if status_code == 400:
        print("[!] OTP has been already generated")
    elif status_code == 200:
        print("[*] OTP generated successfully")
        return response.json()["txnId"]
    else:
        # error codes : 401, 500
        print("[x] Error! try again after few moments")    
    sys.exit()

def confirm_otp(txn_id:str, request_header:dict):
    '''
    confirms otp and returns token
    '''
    url = "https://cdn-api.co-vin.in/api/v2/auth/public/confirmOTP"
    otp = input('[+] Enter OTP : ').strip().encode('utf-8')
    data = {
        'otp':sha256(otp).hexdigest(),
        'txnId':txn_id,
    }

    response = requests.post(url, headers=request_header, json=data)
    status_code = response.status_code

    if status_code == 200:
        print("[*] OTP Verification Successful")
        return response.json()["token"]
    elif status_code == 400 or status_code == 401:
        print("[x] Verification Failed, Verify details before entering.")
    else:
        # for 500
        print('[x] Cannot Verify at the moment. please try again later')
    sys.exit()
    
    

def save_pdf(ben_id, token, request_header):
    '''
    saves certificate as pdf and return path to the file
    '''
    url = f"https://cdn-api.co-vin.in/api/v2/registration/certificate/public/download?beneficiary_reference_id={ben_id}"
    request_header["accept"] = "application/pdf"
    request_header["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=request_header)
    status_code = response.status_code

    if status_code == 200:
        print("[*] PDF file received.")

        file_name = f'CowinCertificate-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.pdf' 
        file_path = os.path.join(os.getcwd(), file_name)
        print(f"[*] Saving File at {file_path}")

        with open(file_path,'wb+') as file:
            file.write(response.content)
            print("[*] File Saved successfully.")
        return file_path
    else:
        print("[x] Unable to save pdf, try again after few moments...")
    sys.exit()
    

def get_doses(path):
    '''
    get user vaccination details from the downloaded pdf file
    returns: number of doses the person is vaccinated with
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    
    # extract doses
    pattern = r"\((\d) Dose.\)"
    # doses = re.search(pattern, text, flags=0).group(0)
    doses = re.findall(pattern, text)[0]

    fp.close()
    device.close()
    retstr.close()
    return doses


if __name__ == "__main__":
    content_type = "application/json"
    base_request_header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
                "origin": "https://selfregistration.cowin.gov.in",
                "referer": "https://selfregistration.cowin.gov.in/",
                "accept" : content_type,
                "Content-Type" : content_type,
            }

    mobile = "9876543210"
    ben_id = "get_id_from_cowin_app_or_website"
    txn_id = generate_otp(mobile, base_request_header)
    token = confirm_otp(txn_id, base_request_header)
    # print("[*] TOKEN : ",token) # might come handy if something goes wrong
    file_path = save_pdf(ben_id, token, base_request_header)

    doses = get_doses(file_path)
    print(f'[*] The Beneficiary user has been vaccinated with {doses} dose of vaccine.')

    # delete vaccine file after getting vaccine detais
    print(f"[*] Deleting file {file_path}")
    os.remove(file_path)
