from urllib.parse import urlencode, quote
from datetime import datetime
from hashlib import md5
from random import choice, choices, randint
from typing import Optional
from string import *
from httpx import head, get, post
from time import time
from re import findall
import random 

api_key = "" # RAPIDAPI KEY
os_version_list = ['9'] # DO NOT MODIFY

class Utils:
    def fetch_endpoints(video_id: object, user_id: str, sec_user_id: str) -> dict:
        return {
            # SHOP
            "orders":           {}, # PRIVATE
            # NORMAL
            "views":            {"domain": "api-va.tiktokv.com",     "endpoints": "/aweme/v1/aweme/stats/?", "method": "POST", "accounts": False},
            "likes":            {}, # PRIVATE
            "shares":           {"domain": "api-va.tiktokv.com",     "endpoints": "/aweme/v1/aweme/stats/?", "method": "POST", "accounts": True},
            "follows":          {}, # PRIVATE
            "favourites":       {"domain": "api-va.tiktokv.com",     "endpoints": f"/aweme/v1/aweme/collect/?aweme_id={video_id}&action=1&collect_privacy_setting={randint(1, 6)}&", "method": "GET", "accounts": True},
            # COMMENT
            "comments":         {"domain": "api-va.tiktokv.com",     "endpoints": "/aweme/v1/comment/publish/?", "method": "POST", "accounts": True},
            "comment_likes":    {"domain": "api-va.tiktokv.com",     "endpoints": "/aweme/v1/comment/digg/?", "method": "GET", "accounts": True},
            # LIVE
            "live_views":       {}, # PRIVATE
            "live_likes":       {}, # PRIVATE
            "live_follows":     {}, # PRIVATE
            "live_comments":    {"domain": "webcast-va.tiktokv.com", "endpoints": "/webcast/room/chat/?webcast_sdk_version=3740&webcast_language=en&webcast_locale=en_US&effect_sdk_version=18.2.0&current_network_quality_info=%7B%7D&", "method": "POST", "accounts": True},
        }

    def fetch_video_id(link_url: str):
        try:
            return str(
                findall(r"(\d{18,19})", link_url)[0]
                if len(findall(r"(\d{18,19})", link_url)) == 1
                else findall(r"(\d{18,19})", head(link_url, follow_redirects = True, timeout = 3).url
                )[0]
            )
        except:
            return None

    def fetch_comments(video_id: str) -> list: # PRIVATE
        pass
        # count, comment_list = 0, []
        # while True:
        #     0x10bd5 = None
        #     comments = 0x10bd5.json()["comments"]
        #     if len(comments) != 0:
        #         for comment in comments:
        #             comment_list.append(comment)
        #         count += 1
        #     else:
        #         break
        # return comment_list

    def fetch_account_info(session_id: str) -> object: 
        r = get("https://api-va.tiktokv.com/2/user/info/", headers = {"Cookie": f"sessionid={session_id};"})
        if "session expired" not in r.text:
            return r.json()
        else:
            return {}
    
    def encrypt_xor(string: str) -> str:
        return "".join([hex(ord(_) ^ 5)[2:] for _ in string])
        
    def os_versions(list_format: Optional[bool] = None) -> list: # Removed from preview line 73
        if list_format:
            return os_version_list
        else:
            return choice(os_version_list)
    
    def sign_tiktok(params: str, x_ss_stub: str, device_token: str, app_launch_time: int, seed_data: Optional[str] = None, seed_version: Optional[str] = None, lanusk: Optional[str] = None, mssdk_version: Optional[str] = None) -> dict:   
        r = post(
            "https://cybrix-bytedance1.p.rapidapi.com/service/signRequest",
            json = {
                "x_bd_lanusk": lanusk,
                "params": params,
                "x_ss_stub": x_ss_stub,
                "device_token": device_token,
                "mssdk_version_str": mssdk_version
            },
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "cybrix-bytedance1.p.rapidapi.com",
                "Content-Type": "application/json"
            }        
        )
        if "exceeded" in r.text:
            raise Exception("[-] API ratelimit, please purchase a bigger plan on rapidapi")
        else:
            return r.json()["data"]
    
    def format_device(device_data: dict) -> dict: # Line 92, 95, 96 removed from preview [os_version, os_api, ts]
        os_version = Utils.os_versions()
        dict_params = device_data["device_info"]
        dict_params["os_version"] = os_version
        
        data = {
            "cookie": device_data["cookie"], 
            "user_agent": device_data["user_agent"], 
            "dict_params": dict_params, 
            "encoded_params": urlencode(dict_params)
        }
        for item in ["seed_data", "seed_version", "device_token"]:
            if item in device_data:
                data[item] = device_data[item]
            else:
                data[item] = None
        return data

    def generate_header(service_type: str, preperation_data: dict, extra_data: dict = None, payload: str = None) -> dict:
        # md5 removed from preview line 108
        user_agent = ""
        content_type = "application/x-www-form-urlencoded; charset=UTF-8"
        match service_type:
            # Removed line 119 from preview [follow requirement]
            case "orders":
                content_type = "application/json"
                user_agent = preperation_data["user_agent"]
            case "follows":
                user_agent = "" # removed from preview
            case "views": 
                user_agent = f"{''.join(choices(ascii_lowercase + ascii_uppercase + digits, k=randint(10, 20)))}" # Temporary Solution - views doesnt accept normal useragents
            case _:
                user_agent = preperation_data["user_agent"]

        return {
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Content-Type': content_type,
            'Cookie': preperation_data["cookie"], # Line 124 - additional cookie - Removed logic for lowering ratelimit
            'passport-sdk-version': '6010290', # Need to update
            'pns_event_id': str(randint(10,50)),
            'sdk-version': '2',
            'User-Agent': user_agent, # Removed logic for lowering ratelimit
            'x-tt-web-proxy': 'TTNet', 
            'x-tt-store-region': preperation_data["dict_params"]["carrier_region"],
            'x-tt-store-region-src': 'did', 
            'x-metasec-event-source': 'native',
            'x-vc-bdturing-sdk-version': '2.3.8.i18n', 
        } | extra_data

    def services_payload(types: str, videoid: str = None, content: str = "", user_id: str = "", sec_user_id: str = "") -> Optional[str]:
        def request_id() -> str:
            random_a = ''.join(choice(ascii_uppercase + digits) for _ in range(19))
            random_b = ''.join(choice(digits) for _ in range(7))
            random_c = datetime.now().strftime("%Y%m%d")
            return random_c + random_b + random_a

        match types:
            case "orders":
                return None # PRIVATE
            case "views":
                # Line 146-152 Removed for lowering ratelimit payload
                return f"pre_item_playtime=&user_algo_refresh_status=false&first_install_time={int(time())}&enter_from=homepage_hot&item_id={videoid}&is_ad=0&follow_status=0&session_id={round(time() * 1000)}&sync_origin=false&follower_status=0&impr_order=1&last_impr_order=0&action_time={int(time())}&tab_type=0&item_distribute_source=for_you_page_1&pre_hot_sentence=&play_delta=1&request_id={request_id()}&aweme_type=0&order=0&pre_item_id=" 
            case "shares":
                return f"pre_item_playtime=&user_algo_refresh_status=false&first_install_time={int(time())}&enter_from=homepage_hot&item_id={videoid}&is_ad=0&follow_status=0&session_id={round(time() * 1000)}&sync_origin=false&follower_status=0&impr_order=1&last_impr_order=0&action_time={int(time())}&tab_type=0&item_distribute_source=for_you_page_1&pre_hot_sentence=&share_delta=1&request_id={request_id()}&aweme_type=0&order=0&pre_item_id=" 
            case "comments":
                return  f"aweme_id={videoid}&text={quote(content)}&text_extra=%5B%5D&image_extra=%5B%5D&is_self_see=0&channel_id=0&action_type=0&publish_scenario=0&skip_rethink=0"
            case "live_likes": # Depreciated - requires to connect to websocket, then like
                return None # PRIVATE
            case "live_views": # Depriciated - requires to connect to websocket
                return None # PRIVATE
            case "live_follows":
                return None # PRIVATE
            case "live_comments": 
                return f"room_id={videoid}&emotes_with_index=&common_label_list=&anchor_id={videoid}&is_ad=0&input_type=0&enter_source=&post_anyway=0&client_start_timestamp_millisecond={round(time() * 1000)}&content={quote(content)}&screen_time={round(time() * 1000)}&enter_method=live_cover&enter_from_merge=live_merge&tag=live_ad&request_id={request_id()}"
            case _:
                return None
    
    def check_status(types: str, response: object) -> bool:
        content, headers = response.text, ''.join(chr(ord(c) - 3) for c in "fkduvhw@xwi0;") in str(response.headers)
        if "Login expired" in content:
            return False  
        if types in ["views", "shares"]:
            return headers
        elif types == "likes":
            return None # PRIVATE
        elif types == "comments":
            return '"status":7' in content
        elif types == "favourites":
            return "saved" in content
        elif types == "follows":
            return None # PRIVATE

