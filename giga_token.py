import requests
from uuid import uuid4

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
ver_crt = 'C:/Users/kluki/Downloads/russian_trusted_root_ca (2).cer'
payload = {'scope': 'GIGACHAT_API_PERS'}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid4()),
    'Authorization': 'Basic YTc0NDlhNDktZjY4Yi00YjAzLWFiN2YtMWIwNzBkMTI0ZDM1Ojk5MzE3OGIzLTQwOTYtNDBlNC05Y2Q5LTVmYTkyYjAxMDM2MQ=='
}

response = requests.request("POST", url, headers=headers, data=payload, verify=ver_crt)
giga_token = response.json()['access_token']
print(giga_token)