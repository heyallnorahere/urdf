import urllib
import urllib.parse
import base64
import hmac
import string
import random
import datetime
import hashlib
import json
import requests

def make_nonce():
    chars = string.digits + string.ascii_letters
    return "".join(random.choice(chars) for i in range(25))

class OnshapeAuth:
    def __init__(self, access: str, secret: str):
        self.access = access
        self.secret = secret
    
    def serialize(self, hmac_str: str):
        sig = base64.b64encode(hmac.new(self.secret.encode(), hmac_str, digestmod=hashlib.sha256).digest())
        return f"On {self.access}:HmacSHA256:{sig.decode()}"

class Onshape:
    def __init__(self, auth: OnshapeAuth):
        self.auth = auth
    
    def make_headers(self, method: str, path: str, query={}, headers={}):
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        nonce = make_nonce()
        content_type: str = headers.get("Content-Type") if headers.get("Content-Type") else "application/json"

        request_headers: dict[str, str | list[str]] = {
            "Content-Type": content_type,
            "Date": date,
            "On-Nonce": nonce,
            "User-Agent": "Onshape Python Sample App",
            "Accept": "application/json"
        }

        for name in headers:
            request_headers[name] = headers[name]
        
        if self.auth is not None:
            hmac_str = (method + "\n" + nonce + "\n" + date + "\n" + content_type + "\n" + path + "\n" + urllib.parse.urlencode(query) + "\n").lower().encode()
            request_headers["Authorization"] = self.auth.serialize(hmac_str)
        
        return request_headers
    
    def send_request(self, method: str, path: str, query={}, headers={}, body={}, base_url="https://cad.onshape.com") -> tuple[requests.Response, bool]:
        req_headers = self.make_headers(method, path, query, headers)
        url = base_url + path + "?" + urllib.parse.urlencode(query)
        json_body = json.dumps(body) if type(body) == dict else body

        res = requests.request(method, url, headers=req_headers, data=json_body, allow_redirects=False, stream=True)
        success = True

        if res.status_code == 307:
            location = urllib.parse.urlparse(res.headers["Location"])
            querystring = urllib.parse.parse_qs(location.query)

            new_query = {}
            new_base_url = location.scheme + "://" + location.netloc

            for key in querystring:
                new_query[key] = querystring[key][0]
            
            return self.send_request(method, location.path, query=new_query, headers=headers, body=body, base_url=new_base_url)
        elif not 200 <= res.status_code <= 206:
            print(f"{method} request to {url} returned status code {res.status_code}")
            success = False
        
        return res, success