import json
from helper.proxy import Proxy

res = '{"code":"SUCCESS","data":[{"proxy_ip":"115.62.15.149","server":"27.152.28.227:30177","area":"河南省濮阳市","isp":"联通","deadline":"2024-10-18 17:10:00"}],"request_id":"09932b21-f9b4-4bf8-aaa0-95f8a7387d1d"}'
print(res)
data = json.loads(res)
print(data)
https = True
if data["code"] == "SUCCESS" and data["data"]:
    proxy_info = data["data"][0]
    proxy = Proxy(proxy=proxy_info["server"],source="VIP",https = https,region=proxy_info["area"],isp=proxy_info["isp"],deadline=proxy_info["deadline"])
    proxy.isp =proxy_info["isp"]
    proxy.out_ip =proxy_info["proxy_ip"]
    proxy.deadline = proxy_info["deadline"]
    # 打印 
    print(proxy.to_json)