import requests

def summarize(querydata,lines, key = 'ad26a38d88e40eff5160affcd452b5ca'):
    url = 'https://api.meaningcloud.com/summarization-1.0'
    params = {'key':key, 'txt':querydata,'sentences':str(lines)}
    results = requests.get(url,params=params)
    if results.status_code==200:
        return results.text
    return "please check the error"
