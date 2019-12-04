#구글 트렌드 그래프 메뉴

from pytrends.request import TrendReq
import numpy as np


def google_trend(key_word):
    keyword = [key_word]
    pytrend = TrendReq(hl='ko', tz=540)
    pytrend.build_payload(keyword, timeframe='today 5-y')
    # Interest Over Time
    cointrenddf = pytrend.interest_over_time()
    cointrenddf = cointrenddf.iloc[:, :1]

    date_list = []
    value_list = []

    # index 기준으로 리스트화
    date = cointrenddf.index.tolist()
    # 값을 2차원배열로 출력.
    value = cointrenddf.values.tolist()
    # 2차원의 배열을 1차원 배열로 변환
    value = np.ravel(value, order='C')

    for _date, _value in zip(date, value):
        value_list.append(_value)
        date_list.append(str(str(_date)[:10]))

    return date_list[214:], value_list[214:]



