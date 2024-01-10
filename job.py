import json
import requests
import schedule
import time
import datetime
from functools import partial
from collections import namedtuple, defaultdict, OrderedDict
from chinese_calendar import is_workday
from utils import find_index
from notification_tools import send_notification


def notify(title, content):
    print("Send notification : ", title, content)
    try:
        send_notification(title, content)
    except Exception as e:
        print(str(e))

def up_down_percent_n(current_info, compare_data, diff_percent):
    if diff_percent > 0:
        return current_info.up_down_price_percent > diff_percent
    else:
        return current_info.up_down_price_percent < diff_percent


def up_down_percent_n_from_cost(current_info, compare_data, diff_percent):
    if diff_percent > 0:
        return current_info.cur_price > compare_data.cost_price * (
            1 + diff_percent / 100
        )
    else:
        return current_info.cur_price < compare_data.cost_price * (
            1 + diff_percent / 100
        )


StockCompareItem = namedtuple("StockCompareItem", "code cost_price current_price amount")
StockTodayInfo = namedtuple(
    "StockTodayInfo",
    "code name cur_price up_down_price up_down_price_percent highest_price lowest_price today_avg_price open_price",
)


condition_trigger_record = defaultdict(dict)

# stock_compare_data = [
#     StockCompareItem("600673", 9.0, None, 3100), # 东阳光
#     StockCompareItem("512170", 0.456, None, 9120), # 医疗ETF
#     StockCompareItem("512880", 0.899, None, 0), # 证券ETF
#     StockCompareItem("002823", 9.6, None, 0), # 凯中精密
#     StockCompareItem("510300", 3.921, None,0) # 沪深ETF
# ]

stock_compare_data = [
    StockCompareItem("600673", 13.130, None, 10000), # 东阳光
    StockCompareItem("002823", 12.770, None, 0), # 凯中精密
    StockCompareItem("601838", 13.250, None, 0), # 成都银行
    StockCompareItem("600036", 28.566, None, 10000), # 招商银行
    StockCompareItem("601233", 15.160, None, 0), # 桐昆股份
    StockCompareItem("512170", 0.456, None, 0), # 医疗ETF
    StockCompareItem("512880", 0.899, None, 0), # 证券ETF
    StockCompareItem("510300", 3.921, None,10000) # 沪深ETF
]


condition_config = {
    "up_percent_1": partial(up_down_percent_n, diff_percent=1),
    "up_percent_2": partial(up_down_percent_n, diff_percent=2),
    "up_percent_3": partial(up_down_percent_n, diff_percent=3),
    "up_percent_5": partial(up_down_percent_n, diff_percent=5),
    "up_percent_6": partial(up_down_percent_n, diff_percent=6),
    "up_percent_4": partial(up_down_percent_n, diff_percent=4),
    "up_percent_7": partial(up_down_percent_n, diff_percent=7),
    "up_percent_8": partial(up_down_percent_n, diff_percent=8),
    "up_percent_9": partial(up_down_percent_n, diff_percent=9),
    "down_percent_1": partial(up_down_percent_n, diff_percent=-1),
    "down_percent_2": partial(up_down_percent_n, diff_percent=-2),
    "down_percent_3": partial(up_down_percent_n, diff_percent=-3),
    "down_percent_4": partial(up_down_percent_n, diff_percent=-4),
    "down_percent_5": partial(up_down_percent_n, diff_percent=-5),
    "down_percent_6": partial(up_down_percent_n, diff_percent=-6),
    "down_percent_7": partial(up_down_percent_n, diff_percent=-7),
    "down_percent_8": partial(up_down_percent_n, diff_percent=-8),
    "down_percent_9": partial(up_down_percent_n, diff_percent=-9),
}


def get_stock_info(code):
    try:
        if code[0] in ["5", "6"]:
            code = "sh" + code
        elif code[0] in ["0"]:
            code = "sz" + code
        url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m1"
        st = json.loads(requests.get(url).content)
        detail = st["data"][code]["qt"][code]
        info = StockTodayInfo(
            code,
            detail[1],
            float(detail[3]),
            float(detail[31]),
            float(detail[32]),
            float(detail[33]),
            float(detail[34]),
            float(detail[4]),
            float(detail[5]),
        )
        return info
    except Exception as e:
        notify("Stock Error", str(e))
        


def trigger_condition(code, condition):
    condition_trigger_record[code][condition] = True


def check_condition(code, condition):
    global condition_trigger_record
    return condition_trigger_record[code].get(condition, False)


def clear_trigger_condition():
    condition_trigger_record.clear()


def add_compare_data(data):
    index = find_index(stock_compare_data, lambda x: x.code == data["code"])
    if index != -1:
        stock_compare_data[index] = StockCompareItem(
            data["code"], float(data["cost_price"]), None, float(data["amount"])
        )
    else:
        stock_compare_data.append(
            StockCompareItem(
                data["code"], float(data["cost_price"]), None, float(data["amount"])
            )
        )


def job():
    if not is_workday(datetime.date.today()):
        return
    do_job_impl()


def do_job_impl():
    print("do job")
    for data in stock_compare_data:
        info = get_stock_info(data.code)
        if info is None:
            continue
        for condition, func in condition_config.items():
            if not check_condition(data.code, condition) and func(info, data):
                trigger_condition(data.code, condition)
                print("Trigger : ", data.code, data.name, condition)
                mail_info = f"Stock Notify:{data.code}({data.name})   {condition}"
                notify(mail_info, mail_info)
                


def get_diff_info(include_all=False):
    collected_info = []
    if(include_all == False):
        filtered_stock_compare_data = (data for data in stock_compare_data if data.amount > 0)
    else:
        filtered_stock_compare_data = stock_compare_data
    for data in filtered_stock_compare_data:
        info = get_stock_info(data.code)
        diff_price = info.cur_price - data.cost_price 
        diff_percent = (diff_price / data.cost_price) * 100
        diff_percent_str = str(round(diff_percent, 2)) + "%"
        diff_price_today = info.cur_price - info.today_avg_price
        diff_percent_today = (diff_price_today / info.today_avg_price) * 100
        diff_percent_str_today = str(round(diff_percent_today, 2)) + "%"

        collected_info.append(OrderedDict({
            "code": data.code,
            "name": info.name,
            "percent": diff_percent_str,
            "up_down": ('🔺' if diff_price_today > 0 else '🔻'),
            "today_percent": diff_percent_str_today,
            "cost_price": data.cost_price,
            "current_price": info.cur_price,
            "amount": data.amount,
            "original_money": float(data.amount) * float(data.cost_price),
            "current_money": float(data.amount) * float(info.cur_price)
        }))
    return collected_info

def send_running_mail():
    if not is_workday(datetime.date.today()):
        return
    notify("Monitor is running", "Monitor is running")

def report_stat():
    if not is_workday(datetime.date.today()):
        return
    info = get_diff_info()
    content = ""
    for i in info:
        content += f'{i["name"]}:{i["today_percent"]};' 
    notify("Report", content)

def conclude_stat():
    if not is_workday(datetime.date.today()):
        return
    info = get_diff_info()
    notify("Conclude", json.dumps(info,ensure_ascii=False))


def run():
    try:
        schedule.every(10).seconds.do(job)
        for hour in range(9, 15):  # 从9点到15点
            schedule.every().day.at(f"{hour:02d}:00").do(report_stat)
            schedule.every().day.at(f"{hour:02d}:30").do(report_stat)
        schedule.every().day.at("09:25").do(send_running_mail)
        schedule.every().day.at("09:30").do(clear_trigger_condition)
        schedule.every().day.at("15:00").do(conclude_stat)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print("ERROR : ", str(e))
        pass
