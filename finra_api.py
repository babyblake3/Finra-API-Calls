import requests
import base64
import numpy as np
import pandas as pd
import re
import pprint
def finra_auth(api_key='',secret='',grant_type='client_credentials',auth_type='Basic'):
    #Block to populate api_key and/or secret
    while api_key == '' or secret == '':
        if api_key == '':
            api_key = input("Enter your API Key/UserID: ")
        elif secret =='':
            secret = input("Enter your secret in plain text:" )
        else:
            pass
    url = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type="+grant_type
    auth_string = api_key+':'+secret
    auth_string = str(base64.b64encode(bytes(auth_string, 'utf-8')))
    auth_string = auth_string.split("'")
    headers = {
        'Authorization' : auth_type + ' '+ auth_string[1]
    }
    response = requests.post(url,headers=headers)
    data = {'http_code':response.status_code,'reply':response.text}
    data['reply'] = data['reply'].replace('"','')
    data['reply'] = data['reply'].replace('{','')
    data['reply'] = data['reply'].replace('}','')
    reply = data['reply'].split(',')
    count1 = 0
    for items in reply:
        reply[count1] = items.split(':')
        count1 += 1
    reply_dict = {}
    count2 = 0
    for x in reply:
        reply_dict.update({reply[count2][0]:reply[count2][1]})
        count2 +=1
    data['reply'] = reply_dict
    print('Successfully retrieved access_token!!!\n') 
    return data
response = finra_auth()
#http_code = response['http_code']

if response['http_code'] == 200:
    access_token = response['reply']['access_token']
    token_type = response['reply']['token_type']
else:
    print('There was an error resulting in a, ',response['http_code'],', from the host. \nPlease check your credentials and try again.\n')
    response = finra_auth()
endpoint = {'group':'','dataset':''}

#data_url = 'https://api.finra.org/data/group/{group}/name/{dataset}'

headers = {
    'Authorization' : token_type+' '+access_token,
    #'Accept' : '',
    #'Data-API-Version' : ''
    }
#params = {
#    'fields' : '',
#    'limit' : 1000,
#    'quotevalues' : '',
#    'async' : '',
#    'sortFields' : ''
#}
while endpoint['group'] != ('q' or 'Q') or endpoint['dataset'] != ('q' or 'Q'):

    for point in endpoint:
        endpoint[point] = input('Please enter the endpoint '+point+' that you would like to access(q or Q to quit): ')
        if endpoint[point] == 'q' or endpoint[point] == 'Q':
            exit()
        else:
            continue
    data_url = f"https://api.finra.org/data/group/{endpoint['group']}/name/{endpoint['dataset']}"
    query = requests.get(data_url.format_map(endpoint),headers=headers)
    #pp = pprint.PrettyPrinter()
    #pp.pprint(query.headers)
    file = f"./{endpoint['group']}_{endpoint['dataset']}.txt"
    if query.status_code == 200:
        with open(file,'wb') as mod_file:
            
            for line in query.iter_lines():
                mod_file.write(line.replace(b", ", b" ").replace(b",,S",b",S"))
                mod_file.write(b"\n")
    else:
        print('You\'ve input an invalid request results in a ',query.status_code, ' response from the server, please try again.')            

    #query_df = pd.read_table(file, sep=",")
    #print(query_df)


