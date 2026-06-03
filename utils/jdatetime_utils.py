import jdatetime


def get_current_shamsi_date():
    """تاریخ شمسی امروز"""
    return jdatetime.datetime.now().strftime('%Y/%m/%d')


def get_current_shamsi_datetime():
    """تاریخ و ساعت شمسی"""
    return jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


def gregorian_to_shamsi(date_str):
    """تبدیل تاریخ میلادی به شمسی"""
    try:
        from datetime import datetime
        g_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        j_date = jdatetime.datetime.fromgregorian(datetime=g_date)
        return j_date.strftime('%Y/%m/%d')
    except Exception:
        return date_str


def shamsi_to_gregorian(date_str):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        year, month, day = map(int, date_str.split('/'))
        j_date = jdatetime.date(year, month, day)
        g_date = j_date.togregorian()
        return g_date.strftime('%Y-%m-%d')
    except Exception:
        return date_str


def get_shamsi_months():
    """اسامی ماه‌های شمسی"""
    return [
        'فروردین', 'اردیبهشت', 'خرداد',
        'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر',
        'دی', 'بهمن', 'اسفند'
    ]


def get_current_season():
    """فصل جاری"""
    month = jdatetime.datetime.now().month
    if month <= 3:
        return 'بهار'
    elif month <= 6:
        return 'تابستان'
    elif month <= 9:
        return 'پاییز'
    else:
        return 'زمستان'
