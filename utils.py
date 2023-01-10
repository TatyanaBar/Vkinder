import datetime

from dateutil.relativedelta import relativedelta


sex_table = {
    0: 'любой',
    1: 'женский',
    2: 'мужской',
}

reversed_sex_table = {
    1: 2,
    2: 1,
}


def date_to_age(date):
    date_object = datetime.datetime.strptime(date, '%d.%m.%Y')
    today = datetime.date.today()
    return relativedelta(today, date_object).years
