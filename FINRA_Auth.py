import requests
url = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials"
headers = {'Authorization':'Basic ZDA2NmU0MzlmYzYwNDI1ZDk4NTY6RmFydG1vbnN0ZXI0IQ=='}
response = requests.request('POST', url, headers=headers)
print(response.text)
