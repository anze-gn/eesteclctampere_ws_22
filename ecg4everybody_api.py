import requests

URL = 'https://ecg4everybody.com/service/getdata.php'

def get(id):
    response = requests.post(URL, data = {'i': id})
    data = response.json()

    # useful fields:
    # print(data['recorded_utc'])
    # print(data['hr'])
    # print(data['rmssd'])

    return data
