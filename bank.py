import pandas as pd
from nltk.stem import SnowballStemmer
from collections import Counter
from pymystem3 import Mystem
from IPython.display import display

russian_stemmer = SnowballStemmer('russian')
m = Mystem()
df = pd.read_csv(r'\Users\User\Downloads\data.csv')
display(df.head(20))
display(df.info())




# Видим, что пропущенные значения присутствуют в графах с трудовым стажем и ежемесечным доходом.
# В графе с тружовым стажем появляются отрицательные значения и слишком большие значения, чего быть не может.
# Бросаются в глаза разные регистры в столбцах с образованием и полом.


for type in df['income_type'].unique():
    position = df[df['income_type'] == type]
    print('--------Информация о людях со статусом {}--------'.format(type))
    display(position.info())


# По выведенным данным заметим, что из 11119 сотрудников 1105 не имеют стажа и дохода,
# среди пенсионеров 413 из 3856, среди компаньонов 508 из 5085, среди госслужащих 147 из 1459, из предпринимателей 1 из 2-х.

# Количество пропусков варьируется от 1 до ~500.
# Пусть эти пропуски появились из-за того, что люди только устроились на работу, ещё не принесли справку о своих доходах, либо брали кредит под залог.

# Заполним эти пропуски нулями.



#информации о доходе и стаже ещё нет, заполним эти поля 0
df['days_employed'] = df['days_employed'].fillna(0)
df['total_income'] = df['total_income'].fillna(0)
print(df.info())


# обратим внимание, что столбец с данными о стаже имеет тип данных float, более того присутсвуют
# даже отрицательные значения и значения, которых совсем не может быть, например 340266.072047.
# для начала приведём всё в целочисленному типу.



df['days_employed'] = df['days_employed'].astype('int')
df['total_income'] = df['total_income'].astype('int')


# теперь разберёмся с "нереальными" числами.Будем считать, что каждый человек из таблицы начал работать не раньше чем в 16 лет, тогда если из его возраста вычесть его стаж в годах, то число не должно превышать 16на основе этого предположения напишем функцию, которая будет заменять 'нереальные' значенияна медиану столбца days_employed




def days_employed_median(row):
    days_employed = row['days_employed']
    dob_years = row['dob_years']
    years_employed = days_employed // 364
    if  dob_years - years_employed  < 16:
        return df['days_employed'].median() * -1
    else:
        return days_employed * -1
#применим её ко всему столбцу
df['days_employed'] = df.apply(days_employed_median, axis=1)
#выведем первые 20 строк для проверки
display(df['days_employed'].head(20))


# Проверим столбец с ежемесечным доходом на выбивающиеся значения


income_non_null = df[df['total_income'] != 0]
#просмотрим минимальные и максимальные значения
print(income_non_null['total_income'].min(), income_non_null['total_income'].max())


# Значения находятся в пределах нормы.



print(df['children'].min(), df['children'].max())


# Проверим количество таких значений, сильно ли они влияют на общий результат?


negative_number = 0
large_number = 0

for count in df['children']:
    if count < 0:
        negative_number += 1
    if count > 5:
        large_number += 1
print(negative_number,large_number)


# Получили десятки, в масшатабах дестков тысяч ими можно принебречь

# -1 это вообще невозможно, предположу, что минус в начале появился случайно, поэтому все отрицательные значения заменим на их модуль.
# А все значения больше 5, заменим на среднее число детей в семье по России.


def children_problem_solution(row):
    children_count = row['children']
    if children_count < 0:
        return children_count * -1
    elif children_count > 5:
        return 2
    else:
        return children_count
df['children'] = df.apply(children_problem_solution, axis=1)


# приведем все столбцы типа object к нижнему регистру
# создадим список со всеми столбацами и напишем цикл, который будет перебирать все столбцы
# поставим условие, если тип данных столбца object, то приводим к нижнему регистру.

columns = list(df)
for column in columns:
    if df[column].dtype == object:
        df[column] = df[column].str.lower()
#print(df.head())

for column in columns:
    if df[column].dtype == object:
        print('------Количество уникальных значений в столбце {}------'.format(column))
        #print(df[column].value_counts())


# в столбце purpose находится много по сути одинаковых целей, с ними и надо разобраться.
# создадим функцию, которая будет лемматизировать переданную ей строку


#данная часть кода закомментирована потому что на ПК очень долго выполняется.
'''def do_lemma(row):
    return m.lemmatize(row)

#применим ее ко всему столбцу purpose и создадим новый столбец с лемматизированными целями

df['lemmatize_purpose'] = df['purpose'].apply(do_lemma)


# Для начала создадим список с категориями для займа.
# Затем напишем функцию, которая будет категоризировать данные в столбце purpose
# Применим ее ко всему столбцу.


category = ['жилье','автомобиль','свадьба','образование','недвижимость']

def categorize_purpose(row):
    lemmatize_purpose = row['lemmatize_purpose']
    category = ['жилье','автомобиль','свадьба','образование','недвижимость']
    for aim in lemmatize_purpose:
        for credit_aim in category:
            if credit_aim in aim:
                return credit_aim


df['purpose'] = df.apply(categorize_purpose, axis=1)


df['lemmatize_purpose'] = df.apply(categorize_purpose, axis=1)
display(df.head())'''
#конец долгого выполнения

# Заранее создам функцию, которая будет разбивать уровни дохода на категории, для дальнейшего использования.

def income(total_income):
    if total_income == 0:
        return '0'
    elif total_income <= 50000:
        return '0-50'
    elif total_income <= 100000:
        return '50-100'
    elif total_income <= 250000:
        return '100-250'
    elif total_income <= 500000:
        return '250-500'
    else:
        return '500+'


# - Есть ли зависимость между наличием детей и возвратом кредита в срок?

#разделим вкладчиков на две категории с детьми и без

kids = df[df['children'] != 0]
no_kids = df[df['children'] == 0]

#найдем процент людей, которые имеют задолжности в каждой категории


kids_and_debit = kids['debt'].sum() / len(kids)
no_kids_and_have_dabit = no_kids['debt'].sum() / len(no_kids)
print('Процент среди людей с детьми, которые имели задолжности: {:.1%}'.format(kids_and_debit))
print('Процент среди бездетных, которые имели задолжности: {:.1%}'.format(no_kids_and_have_dabit))


# можно сделать вывод, что наличие детей усложняет вовзврат по задолжностям


# - Есть ли зависимость между семейным положением и возвратом кредита в срок?

#для ответа на этот вопрос составим сводную таблицу по статусу семейного положения
data_pivot_family_status_and_debt = df.pivot_table(index='family_status', columns='debt', values='family_status_id', aggfunc='count')
#найдем процент должников
data_pivot_family_status_and_debt['sum'] = data_pivot_family_status_and_debt[1] + data_pivot_family_status_and_debt[0]
data_pivot_family_status_and_debt['ratio %'] = (data_pivot_family_status_and_debt[1] / data_pivot_family_status_and_debt['sum']) * 100

#найдем общую сумму людей для каждой категории


#проверим результат
display(data_pivot_family_status_and_debt.head())


# Видно, что люди, которые не состояли в браке реже выплачивают свои задолжности


#- Есть ли зависимость между уровнем дохода и возвратом кредита в срок?

# Использую ранее созданную функцию income, пременяю ее ко всему столбцу с ежемесячным доходом и заношу данные в новый столбец.


df['category_income'] = df['total_income'].apply(income)

#создаем таблицу
data_pivot_category_income = df.pivot_table(index='category_income', columns='debt', values='total_income', aggfunc='count')
#найдем процент должников
data_pivot_category_income['sum'] = data_pivot_category_income[1] + data_pivot_category_income[0]
data_pivot_category_income['ratio %'] = (data_pivot_category_income[1] / data_pivot_category_income['sum']) * 100

#найдем общую сумму людей для каждой категории
data_pivot_category_income['sum'] = data_pivot_category_income[1] + data_pivot_category_income[0]

display(data_pivot_category_income)
#print(df.head())


# из таблицы видно, что наибольшая часть задолжностей находится у людей со средним уровнем зароботка
# наименьшая у людей с высоким уровнем зароботка и, как ни странно, с низким.

#

# - Как разные цели кредита влияют на его возврат в срок?


#создадим ещё один столбец с целями, чтобы по одному группировать, по другому выводить значения
df['purpose_for_groupby'] = df['purpose']
#и ещё одна сводная таблица
data_pivot_purpose = df.pivot_table(index='purpose_for_groupby', columns='debt', values='purpose', aggfunc='count')
#найдем процент должников
data_pivot_purpose['sum'] = data_pivot_purpose[1] + data_pivot_purpose[0]
data_pivot_purpose['ratio %'] = (data_pivot_purpose[1] / data_pivot_purpose['sum']) * 100
#найдем общую сумму людей для каждой категории
data_pivot_purpose['sum'] = data_pivot_purpose[1] + data_pivot_purpose[0]

display(data_pivot_purpose)
