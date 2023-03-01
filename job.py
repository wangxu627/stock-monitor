import json
import requests
import schedule
import time
import datetime
from functools import partial
from collections import namedtuple, defaultdict
from chinese_calendar import is_workday
from utils import find_index
from mail_tools import send_mail


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


StockCompareItem = namedtuple("StockCompareItem", "code cost_price amount cur_amount")
StockTodayInfo = namedtuple(
    "StockTodayInfo",
    "code cur_price up_down_price up_down_price_percent highest_price lowest_price open_price",
)


condition_trigger_record = defaultdict(dict)

stock_compare_data = [
    StockCompareItem("600673", 9.0, 20000, 16116), # 东阳光
    StockCompareItem("002823", 9.6, 9050, 6288), # 凯中精密
    StockCompareItem("510300", 3.921, 11766, 12615) # 沪深ETF
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
    # "up_percent_1_from_cost": partial(up_down_percent_n_from_cost, diff_percent=1),
    # "up_percent_5_from_cost": partial(up_down_percent_n_from_cost, diff_percent=5),
    # "up_percent_10_from_cost": partial(up_down_percent_n_from_cost, diff_percent=10),
    # "down_percent_1_from_cost": partial(up_down_percent_n_from_cost, diff_percent=-1),
    # "down_percent_5_from_cost": partial(up_down_percent_n_from_cost, diff_percent=-5),
    # "down_percent_10_from_cost": partial(up_down_percent_n_from_cost, diff_percent=-10),
}


def get_stock_info(code):
    try:
        if code[0] in ["5", "6"]:
            code = "sh" + code
        elif code[0] in ["0"]:
            code = "sz" + code
        URL = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m1"
        st = json.loads(requests.get(URL).content)
        detail = st["data"][code]["qt"][code]
        info = StockTodayInfo(
            code,
            float(detail[3]),
            float(detail[31]),
            float(detail[32]),
            float(detail[33]),
            float(detail[34]),
            float(detail[4]),
        )
        return info
    except Exception as e:
        send_mail(["350821495@qq.com"], "Stock Error", str(e))
        


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
            data["code"], float(data["cost_price"]), float(data["amount"])
        )
    else:
        stock_compare_data.append(
            StockCompareItem(
                data["code"], float(data["cost_price"]), float(data["amount"])
            )
        )


def job():
    if not is_workday(datetime.date.today()):
        return
    for data in stock_compare_data:
        info = get_stock_info(data.code)
        for condition, func in condition_config.items():
            if not check_condition(data.code, condition) and func(info, data):
                trigger_condition(data.code, condition)
                print("Trigger : ", data.code, condition)
                mail_info = "Stock Notify:" + data.code + "   " + condition
                send_mail(["350821495@qq.com"], mail_info, mail_info)


def get_diff_info():
    collected_info = []
    for data in stock_compare_data:
        info = get_stock_info(data.code)
        diff_price = info.cur_price - data.cost_price 
        diff_percent = (diff_price / data.cost_price) * 100
        diff_percent_str = str(round(diff_percent, 2)) + "%"
        collected_info.append({
            "code": data.code,
            "percent": diff_percent_str,
            "amount": data.amount,
            "cur_amount": data.cur_amount,
            "cost_price": data.cost_price
        })
    return collected_info


def run():
    schedule.every(10).seconds.do(job)
    schedule.every().day.at("09:30").do(clear_trigger_condition)

    while True:
        schedule.run_pending()
        time.sleep(1)
