from sklearn import metrics
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import pandas as pd


def auc(y,pre):
    fpr, tpr, thresholds = metrics.roc_curve(y, pre)
    auc=metrics.auc(fpr, tpr)
    return auc

def getAmountLevel(t):
    if t<=10:
        return 1
    elif t<=100:
        return 2
    else:
        return 3
    
def time_cut(t):
    if t<=0:
        return ['0',1]
    elif t<=3:
        return ['(0,3])',2]
    elif t<=14:
        return ['(3,14])',3]
    elif t<=90:
        return ['(14,90])',4]
    elif t<=180:
        return ['(90,180])',5]
    else:
        return ['>180',6]

def fans_cut(t):
    if t<10:
        return 1
    elif t<67:
        return 2
    elif t<348:
        return 3
    else:
        return 4
    
import matplotlib.pyplot as plt
import matplotlib as mpl

def draw1(data,fea_values,fea,ylim_value=0):
    x = fea_values
    y = data[data.label==0][[fea,'label']].groupby([fea]).count().reset_index().label.values
    y1 = data[data.label==1][[fea,'label']].groupby([fea]).count().reset_index().label.values

    plt.xlabel(fea+" gift count")
    plt.legend()
    plt.bar(x, y, align="center", color="c", tick_label=fea_values, label="click=0")
    plt.bar(x, y1, align="center", bottom=y, color="g", label="click=1")
    value=780000
    if ylim_value!=0:
        value=ylim_value
    plt.ylim(0, value)
    
    plt.show()
    
def draw2(data,fea_values,fea,ascending_value):
    ##柱状图
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import pyplot as plt
    fig,ax=plt.subplots()
    # 生成数据
    #x = np.linspace(0, 20, 20)
    tmp=data[fea_values+['label','user_id']].groupby(fea_values+['label']).count().reset_index()\
                                                  .sort_values(by=[fea_values[1]],ascending=0)[[fea_values[0],'label','user_id']]
    
    tmp=pd.pivot_table(tmp,index=fea_values[0],columns=['label'])
    #newtmp=tmp.T[['>180','(90,180])','(14,90])', '(3,14])','(0,3])','0']]
    newtmp=tmp.T[['0','(0,3])', '(3,14])','(14,90])','(90,180])','>180']]
    if(ascending_value==True):
        newtmp=tmp.T[['>180','(90,180])','(14,90])', '(3,14])','(0,3])','0']]
    col=[i for i in newtmp]  #年份从header中提取
    value=newtmp.T.values   #将冠亚季军所吃热狗的数量转化成matrix，也就是[[25,24,22],[50.0,31.0,23.5],...]
    value=value[np.lexsort(value[:,::-1].T)]
    v1=[i[0]+i[1] for i in value]  #第一次画的柱形图y值为冠亚季军所吃热狗数量的总和
    v2=[i[0] for i in value]  #第二次画的柱形图y值为亚军所吃热狗的数量+季军所吃热狗的数量

    #v1.sort(reverse=ascending_value)
    #v2.sort(reverse=ascending_value)
    ax.barh(col,v1,color="g")
    ax.barh(col,v2,color="c")
    ax.set(xlabel=fea,title=fea+" gift count")
    #ax.text(1998,184,"(HDB)")  #设置文字
    ax.legend(["click=1","click=0"])  #设置图例

    plt.show()

