from config import *
from utils import divide_chunks

def load_data(offset,limit):
    global api_key
    global api
    try:
        f_data = {
            "data":[]
        }

        with open(leads_file,"r",encoding="utf-8") as file:
            data = json.load(file)["data"]
            for d in data:

                user = {
                    "phones":[],
                    "display_name":"",
                    "title":"",
                    "id":"",
                    "lead_id":""
                }

                user["display_name"] = d["display_name"]
                user["title"] = d["title"]
                user["id"] = d["id"]
                user["lead_id"] = d["lead_id"]

                phones = d["phones"] if len(d["phones"]) > 0 else []
                user["phones"] += [phone for phone in phones if len(phones) > 0]
                f_data["data"].append(user)

        total = len(f_data["data"])
        f_data["data"] = list(divide_chunks(f_data["data"],limit))
        len_list = len(f_data["data"])
        f_data["data"] = f_data["data"][offset]
        return True,f_data,total,len_list
    except Exception as error:
        return False,error
    
def send_sms(local_number='',remote_number='',proxies={},lead_id='',contact_id='',message='',wait=0,api_key=''):
    global state
    try:
        time.sleep(random.randint(0,wait))
        if not state['ON']:return False,'Obeyed stop command'
        headers = {'Content-Type': 'application/json','User-Agent': 'Close/{} python ({})'.format('2.0',requests.utils.default_user_agent())}
        local_number = str(local_number).strip().replace('-','').replace(' ','').replace('+','')
        data = {
            "status": "outbox",
            "text": f"{message}",
            "remote_phone": f"{remote_number}",
            "local_phone": f"+{local_number}",
            "source": "Close.io",
            "lead_id": f"{lead_id}",
            "contact_id": f"{contact_id}",
        }

        response = requests.post('https://api.close.com/api/v1/activity/sms', json=data,headers=headers,proxies=proxies,auth=(api_key, ''),timeout=20)
        
        if response.status_code == 429:
            wait = response.json()['error']['rate_reset']
            time.sleep(wait)
            repeat = send_sms(local_number=local_number,remote_number=remote_number,proxies=proxies,lead_id=lead_id,contact_id=contact_id,message=message)
            if repeat[0]: return True,remote_number
            else: return False,remote_number
        
        elif response.status_code != 200 and response.status_code != 429:
            return False,f'Error sending message to {remote_number}: {response.text},{api_key}'
        
        return True,remote_number
    
    except Exception as error:
        return False,f'Error sending message to {remote_number}: {error},{api_key}'
