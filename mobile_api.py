from time import time
from httpx import Client
from random import choice
from module import Utils
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, wait
from json import loads

proxies_list = open("./input/proxies.txt").read().splitlines()
devices_list = open("./input/devices.txt").read().splitlines()
mobile_account_list = open("./input/accounts.txt").read().splitlines()

script_setting  = {
    "retry_count": 6,
    "thread_count": 100
}

class TikTok:
    def __init__(
            self, 
            types:          str = "shares", 
            amount:         int = 10, 
            video_id:       str = "7425269420152605953", 
            user_id:        str = "7105895631647310875", 
            sec_user_id:    str = "MS4wLjABAAAA-mRuMoFgk4-5FK-goKUCc8k4EkmGFUR9nUf5sUyJIqzraHIq1EO6dOg3A95budw0"
        ):
        if types not in ["views", "shares", "favourites", "comments", "comment_likes", "live_comments"]: # "likes", "follows", "live_views", "live_likes", "live_follows", "orders" is not for free plan
            raise Exception("[Cybrix] 'types' not avaliable!")

        self.videoid, self.user_id, self.sec_user_id = video_id, user_id, sec_user_id
        self.sent, self.fail, self.error, self.thread, self.endpoints = 0, 0, 0, [], Utils.fetch_endpoints(video_id, user_id, sec_user_id)
        start_time = time()
        with ThreadPoolExecutor(max_workers = script_setting["thread_count"]) as executor:
            for _ in range(amount):
                self.thread.append(executor.submit(self.send_services, types))
            wait(self.thread)
        end_time = round(time() - start_time)
        print(f"{self.sent, self.fail, self.error, end_time}")
    
    def send_services(self, types: str):
        lanusk, client = None, Client(http2 = True, verify = False) 
        for _ in range(script_setting['retry_count']):
            try:
                device_data = loads(choice(devices_list))
                if self.endpoints[types]["accounts"]:
                    account_data = loads(choice(mobile_account_list))
                    extra_header = account_data["headers"]
                    lanusk = extra_header["x-bd-client-key"]
                else:
                    account_data = {}   
                
                # MAIN
                preperation_data = Utils.format_device(device_data) 
                payload = Utils.services_payload(types, self.videoid, "fuck", self.user_id, self.sec_user_id)
                algorithm = Utils.sign_tiktok(
                    self.endpoints[types]["endpoints"].split("?")[1] + preperation_data["encoded_params"],  # query params  [required]
                    payload,                                                                                # x_ss_stub
                    preperation_data["device_token"],                                                       # sdi/get_token
                    int(time()),                                                                            # timestamp
                    None, None,                                                                             # ms/get_seed   [not recommendeded]
                    lanusk,                                                                                 # x_bd_lanusk   [required for login actions]
                    device_data["mssdk_version_str"]                                                        # mssdk_version [required]
                )  
                headers = Utils.generate_header(types, preperation_data, algorithm, payload) 
                if lanusk != None:
                    headers.update({
                        "x-bd-kmsv": extra_header["x-bd-kmsv"],
                        "x-tt-token": extra_header["x-tt-token"],
                        "x-bd-client-key": extra_header["x-bd-client-key"]
                    })
                    headers["Cookie"] += extra_header["cookie"]

                resp = client.request(
                    self.endpoints[types]["method"],
                    f"https://{self.endpoints[types]['domain']}" + self.endpoints[types]["endpoints"] + preperation_data["encoded_params"], 
                    data = payload,
                    headers = headers
                )
                print(resp.text.strip())
                if Utils.check_status(types, resp):
                    self.sent += 1
                    break
                else:
                    self.fail += 1
            except Exception as e:
                print(e)
                self.error += 1
                continue

if __name__ == "__main__":
    TikTok(
        # types = "views",
        # amount = 10, 
        # video_id = "7468641591968779038",
        # user_id = "7105895631647310875",
        # sec_user_id = "MS4wLjABAAAA-mRuMoFgk4-5FK-goKUCc8k4EkmGFUR9nUf5sUyJIqzraHIq1EO6dOg3A95budw0"
    )
