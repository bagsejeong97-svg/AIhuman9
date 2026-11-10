# day16_application.py
# 주제:
from sklearn.metrics import classification_report

from mldl.day16.day16_ex import FEATURES, TARGET
from util.print_util import pp, pt, up
import pandas as pd
import sklearn
from sklearn.datasets import load_iris
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.utils.multiclass import type_of_target
from sklearn.utils.validation import check_X_y

df = pd.DataFrame({
'login_days_30'   : [27, 5, 18, 2, 25, 8, 21, 4, 29, 11],
'support_tickets' : [0, 4, 1, 5, 0, 3, 1, 4, 0, 2],
'contract_months' : [18, 2, 10, 1, 24, 5, 15, 3, 30, 7],
'autopay'         : ["Y", "N", "Y", "N", "Y", "N", "Y", "N", "Y", "N"],
'churned'         : [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
})

# 오토페이 0,1로 변경
df['autopay'] = (df['autopay']=='Y').astype(int)

pp(df['autopay'])

FEATURES = ['login_days_30', 'support_tickets', 'contract_months', 'autopay']

TARGET = 'churned'

X = df[FEATURES]
y = df[TARGET]

pp(type_of_target(y))  # 분류 binary


# 검증된 X,y 의 shape 출력
X_checked, y_checked = check_X_y(X, y, dtype="numeric")
print(X_checked.shape, y_checked.shape)


#신규 이용자
new_X = pd.DataFrame([{
    'login_days_30': 9,
    'support_tickets':2,
    'contract_months':6,
    'autopay':"N"
}])


new_X['autopay'] = (new_X['autopay'] == 'Y').astype(int)

pp(new_X['autopay'])

a = list(X.columns)
b = list(new_X.columns)
c = type_of_target(y)

d = a == b

pp('분류:',c,'같은가:',d)






















