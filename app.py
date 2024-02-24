from sys import api_version
from flask import Flask, json, request, jsonify
from hashlib import sha256
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


import copy
import datetime
import re
import requests
import os


app = Flask(__name__)
content_type = "application/json"
base_request_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "origin": "https://selfregistration.cowin.gov.in",
    "referer": "https://selfregistration.cowin.gov.in/",
    "accept" : content_type,
    "Content-Type" : content_type,
}


@app.route('/', methods=['POST', 'GET'])
def root():
    if request.method == 'GET':
        return "Get request"
    elif request.method == 'POST':
        return 'POST request'
    return 'Invalid Request'

@app.route('/generate_otp/<int:phone_num>', methods=['GET'])
def generate_otp(phone_num):
    if request.method == 'GET':
        # return str(phone_num)
        mobile = str(phone_num)
        print(mobile)
        if len(mobile) != 10:
            return jsonify({"Error":"Invalid Mobile Number"})

        
        url = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
        response = requests.post(url, headers=base_request_header, json={'mobile':mobile})
        txn_generated = False
        status_code = response.status_code
        if status_code == 400:
            message = "OTP has been already generated"
        elif status_code == 200:
            message = "OTP generated successfully"
            txn_id = response.json()["txnId"]
            txn_generated = True
        else:
            # error codes : 401, 500
            message = "[x] Error! try again after few moments"

        api_response = {"message" : message}
        if txn_generated:
            api_response["txn_id"] = txn_id

        return jsonify(api_response)
    return 'Invalid Request'


@app.route('/confirm_otp', methods=['GET'])
# http://127.0.0.1:8000/confirm_otp?txn_id=something&otp=123456
def confirm_otp():
    if request.method == "GET":
        request_header = copy.deepcopy(base_request_header)
        txn_id = request.args.get('txn_id')
        otp = request.args.get('otp')
        print(txn_id, otp)

        # return f"{txn_id} {otp}"

        url = "https://cdn-api.co-vin.in/api/v2/auth/public/confirmOTP"
        # otp = input('[+] Enter OTP : ').strip().encode('utf-8')
        data = {
            'otp':sha256(otp.encode()).hexdigest(),
            'txnId':txn_id,
        }

        response = requests.post(url, headers=request_header, json=data)
        status_code = response.status_code

        token_is_generated = False
        if status_code == 200:
            message = "[*] OTP Verification Successful"
            token = response.json()["token"]
            token_is_generated = True
        elif status_code == 400 or status_code == 401:
            print(response.content.decode())
            message = "[x] Verification Failed, Verify details before entering."
        else:
            # for 500
            message = '[x] Cannot Verify at the moment. please try again later'

        api_response = { 'message' : message }
        if token_is_generated:
            api_response["token"] = token

        # print(api_response)
        return jsonify(api_response)

@app.route('/get_details', methods=['GET'])
# http://127.0.0.1:8000/confirm_otp?txn_id=something&otp=123456
def get_details():
    if request.method == "GET":
        token = request.args.get('token')
        ben_id = request.args.get('ben_id')
        request_header = copy.deepcopy(base_request_header)

        url = f"https://cdn-api.co-vin.in/api/v2/registration/certificate/public/download?beneficiary_reference_id={ben_id}"
        request_header["accept"] = "application/pdf"
        request_header["Authorization"] = f"Bearer {token}"

        response = requests.get(url, headers=request_header)
        status_code = response.status_code

        details_received = False
        if status_code == 200:
            message = "binary data fetched successfully"


            file_name = f'CowinCertificate-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.pdf' 
            file_path = os.path.join(os.getcwd(), file_name)

            with open(file_path,'wb+') as file:
                file.write(response.content)
                name, doses, dates, vaccine = get_doses_from_file(file_path)
                message = "Details fetched successfully"
                details_received = True
        else:
            message = "[x] Unable to fetch pdf, try again after few moments..."

        os.remove(file_path)
        # api_response = { 'message' : message + str(response.content) + str(response.status_code)}
        api_response = { 'message' : message }
        if details_received:
            api_response["name"] = name
            api_response["doses"] = doses
            api_response["dates"] = dates
            api_response["vaccine"] = vaccine

        return api_response


def get_doses_from_file(path):
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
    vaccine = "NOT FOUND"

    dose_no_pattern = r"(\d\/\d)"
    dates_pattern = r'(\d\d\d\d-\d\d-\d\d)'
    name_pattern = r'(\b[a-zA-Z]+\s\b[a-zA-Z]+\s\b[a-zA-Z]+|\b[a-zA-Z]+\s\b[a-zA-Z]+)'
    vaccine_pattern = r'(COVISHIELD|COVAXIN)'
    doses = re.findall(dose_no_pattern, text)[-1]
    dates = re.findall(dates_pattern, text)
    name = re.findall(name_pattern, text)[0]
    vaccine = re.findall(vaccine_pattern, text)
    print(doses, dates, name, vaccine)

    fp.close()
    device.close()
    retstr.close()
    return (name, doses, dates, vaccine)


if __name__ == "__main__":
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8000)

    app.run(host='0.0.0.0', port=8000, debug=True)
    # python app.py