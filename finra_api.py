import requests
import base64
import numpy as np
import pandas as pd
import os
import datetime
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

def print_endpoints(dict, key='' , dict2={}):
    if len(dict2) == 0:
        for k in dict:
            print(k)
    else:
        keys = list(dict2.keys())
        counter = 0
        for v in dict[key]:
            print(keys[counter],':',dict2[v],'\n')
            counter+=1



response = finra_auth()

#if response['http_code'] == 200:
    #access_token = response['reply']['access_token']
    #token_type = response['reply']['token_type']
while response['http_code'] != 200:
    print('There was an error resulting in a, ',response['http_code'],' HTTP status code from the host. \nPlease check your credentials and try again.\n')
    response = finra_auth()
access_token = response['reply']['access_token']
token_type = response['reply']['token_type']
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
groups = {
    'otcMarket':['equityShortInterestStandardized','monthlySummary','otcBlocksSummary','regShoDaily','thresholdList','weeklySummary','weeklySummaryHistoric'],
    'finra':['industrySnapshotFirmsByRegistrationType'],
    'fixedIncomeMarket':['agencyMarketBreadth','agencyMarketSentiment','corporate144AMarketBreadth','corporate144AMarketSentiment','corporatesAndAgenciesCappedVolume','corporateMarketBreadth','corporateMarketSentiment','securitizedProductsCappedVolume','treasuryWeeklyAggregates']}


datasets = {
    'equityShortInterestStandardized':'OTC equity short positions reported by FINRA member firm in the new industry standardized format.',
    'monthlySummary':'Monthly aggregate trade data for OTC (non-ATS) trading data for each firm with trade reporting obligations under FINRA rules.',
    'otcBlocksSummary':'Aggregated OTC (Non-ATS) trade data in NMS stocks that meets certain share based and dollar based thresholds.',
    'regShoDaily':'Daily short sale aggregated volume by security for all short sale trades executed and reported to a FINRA trade reporting facility.',
    'thresholdList':'OTC Regulation SHO and Rule 4320 Threshold Securities.',
    'weeklySummary':'Weekly aggregate trade data for OTC (ATS and non-ATS) trading data for each ATS/firm with trade reporting obligations under FINRA rules.',
    'weeklySummaryHistoric':'',
    'industrySnapshotFirmsByRegistrationType':'Breakdown of securities industry registered firms by type of registration.',
    'agencyMarketBreadth':'Market breadth calculations for Agency debt securities.',
    'agencyMarketSentiment':'Market sentiment calculations for Agency debt securities.',
    'corporate144AMarketBreadth':'Market breadth calculations for Rule 144A corporate debt securities.',
    'corporate144AMarketSentiment':'Market sentiment calculations for Rule 144A corporate debt securities.',
    'corporatesAndAgenciesCappedVolume':'Capped volume calculations for corporate and agency debt.',
    'corporateMarketBreadth':'Market breadth calculations for corporate debt securities.',
    'corporateMarketSentiment':'Market sentiment calculations for corporate debt securities.',
    'securitizedProductsCappedVolume':'Capped volume calculations for securitized products.',
    'treasuryWeeklyAggregates':'Trading volume in US Treasury Securities reported to TRACE.'}


while endpoint['group'] != ('q' or 'Q') or endpoint['dataset'] != ('q' or 'Q'):

    for point in endpoint:
        istr = '\nPlease enter the endpoint '+point+' that you would like to access(q or Q to quit): '
        if point == 'group':
            print('Possible Endpoints:\n_________________')
            print_endpoints(groups)
            ##Use regex to map user input to groups keys as long as input matches first 3 letters of key.
            endpoint[point] = input(istr)
        elif point == 'dataset':
            print('Possible Datasets:\n________________')
            print_endpoints(groups,endpoint['group'],datasets)
            ##Use regex to map user input to datasets keys as long as input matches a TBD regex expression.
            endpoint[point] = input(istr)
        if endpoint[point] == 'q' or endpoint[point] == 'Q':
            exit()
    data_url = f"https://api.finra.org/data/group/{endpoint['group']}/name/{endpoint['dataset']}"
    query = requests.get(data_url.format_map(endpoint),headers=headers)
    file = f"./{endpoint['group']}/{endpoint['dataset']}_{datetime.datetime.now().strftime('%m-%d-%Y_%I%M%S')}.txt"
    
    if query.status_code == 200:
        os.makedirs(os.path.dirname(file),exist_ok=True)
        with open(file,'wb') as mod_file:
            
            for line in query.iter_lines():
                mod_file.write(line.replace(b", ", b" ").replace(b",,S",b",S"))
                mod_file.write(b"\n")
                print('File successfully written to: ', file,'\n')
    else:
        print('You\'ve input an invalid request results in a ',query.status_code, ' response from the server, please try again.')            

    #query_df = pd.read_table(file, sep=",")
    #print(query_df)


