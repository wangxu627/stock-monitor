import requests


def send_notification(sub, content):
    requests.get(f"http://router.wxioi.fun:8990/msg/?title={sub}&content={content}", timeout=10, verify=False)
