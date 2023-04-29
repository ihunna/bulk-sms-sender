from config import *

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def load_proxies():
    with open(proxy_file,"r") as pro_file:
        proxies = []
        for proxy in pro_file:
            proxy = proxy.replace(",",":").replace(";",":")
            proxy = proxy.replace("\n","").split(":")
            proxy = f"{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
            proxies.append({
                "http":f"http://{proxy}",
                "https":f"http://{proxy}"
            })
    return proxies
