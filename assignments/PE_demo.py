# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np

# 初始化数据，目的是预留空间
sheet_data = ["","",""]   # sheet_data 是一个数组，数组中有三组数据，分别存放sheet1,sheet2，sheet3数据
# 数组的索引都是从0开始
# 从 副本PE分国别-2105.xlsx 中读取 sheet_name 是 "LLD-1" 的Excel数据
sheet_data[0] = pd.read_excel("副本PE分国别-2105.xlsx",sheet_name = "LLD-1")
sheet_data[1] = pd.read_excel("副本PE分国别-2105.xlsx",sheet_name = "LD-1")
sheet_data[2] = pd.read_excel("副本PE分国别-2105.xlsx",sheet_name = "HD-1")


#---------------------------------- 获取重复列名 -------------------------------------
# 初始化
column_name = sheet_data[0].columns.tolist() # 将sheet1的列名储存到列（list）中
column_check = []                            # 将sheet1和sheet2共同拥有的列名(国家名)储存
column_check_2 = []                          # 将sheet1和sheet3共同拥有的列名(国家名)储存
column_list = []                             # 获取sheet1、sheet2、sheet3 共同的列名(国家名)


# 将sheet1和sheet2共同拥有的列名储存到 column_check 中
for name in sheet_data[1].columns.tolist():  # 遍历国家名，将sheet2中的国家名依次取出，赋值到依次赋值name中
    if name in column_name:                  # 如果该国家名出现在 column_name 的列表里
        if name not in column_check:         # 并且不在 column_check 的列表里
            column_check.append(name)        # 将该国家名存进 column_check 的列表 
        continue                             # 如果该国家名已经存在在，进行下一个循环（确保不会重复添加国家名）
    elif name.find("Unnamed") != -1:         # 如果不是共同拥有的国家名，并且，列表名不含“Unname”（这个是Excel的问题，如果有列表名未赋值，则默认为Unname..）
        continue                             # 继续下一个循环
    

# 将sheet1和sheet3共同拥有的列名储存到 column_check_2 中
for name in sheet_data[2].columns.tolist():  # 同上一个过程
    if name in column_name:
        if name not in column_check_2:
            column_check_2.append(name)
        continue
    elif name.find("Unnamed") != -1:
        continue

# 将 column_check 与 column_check_2 对比，存储共同拥有的国家到新的 column_list
index = [{},{},{}]                            # 将3个sheet中对应的国家的列的索引号，分别记录下来，以字典的形式，方便之后检索对应

'''
    补充知识：
        1.index是一个大的数组，里面有三个字典形式的数据结构
    例子：
        index = [{"中国":1,"加拿大":6,"美国":3},{"中国":3,"加拿大":2,"美国":4},{"中国":2,"加拿大":5,"美国":1}]
    我们可以知道  index[1] = {"中国":3,"加拿大":2,"美国":4}
                index[0]["中国"] = 1
                index[2]["加拿大"] = 5
    以本程序为例，我们可以从中得知，在sheet1中国在第一列，sheet2中国在第三列，sheet3中国在第二列，这样就可以方便索引
    另外，我们要注意：python中所有的索引都是默认从0开始，也就是说 0 = 实际表格的第一列

'''
for name in column_check:                               # 遍历 column_check 的国家名 
    if name in column_check_2:                          # 如果该国家名在 column_check_2 中
        if name not in column_list:                     # 并且不在 column_list 中
            index[0][name]= sheet_data[0].columns.get_loc(name)   # 获取该国家列在sheet1的索引
            index[1][name]= sheet_data[1].columns.get_loc(name)   # 获取该国家列在sheet2的索引
            index[2][name]= sheet_data[2].columns.get_loc(name)   # 获取该国家列在sheet3的索引
            column_list.append(name)                    # 将该国家名加入到 column_list
        continue
    elif name.find("Unnamed") != -1:                    # 如果国家名是“Unname” 就跳过，进入下一个循环
        continue
        
column_list.remove("总数")                               # 我们不需要“总数”和“类别”着两个列名，删去即可
column_list.remove("类别")

#---------------------------------- 将对应的三个表中对应的数值相加 -------------------------------------

array = [[],[],[]]                                       # 初始化一个而 数组 套 三个数组
# 初始化一个二维数组
final_array =[[0 for col in range(len(column_list))] for row in range(sheet_data[2].shape[0]+1)]
'''
    补充知识：
        1.二维数组就和Excel表格差不多，我们可以通过行列获取值
    例子：
        11 12 5 2
        15 6 10
        10 8 12 5
        12 15 8 6
        可以表示为：
        array = [[11, 12, 5, 2], [15, 6, 10], [10, 8, 12, 5], [12,15,8,6]]
        array[0] = [11, 12, 5, 2]
        array[1][2] = 10
    在上一条代码中 我们是通过两层循环，初始化了一个二维数组
        2.len(column_list)是指 column_list 的长度，假设一共有15个国家，则 len(column_list) = 15
        3.range(len(column_list)) = range(15) 意思是默认0到15的范围 ='[0,15)' 其中 col 从 0 开始，一遍一遍取到 14，一共取15次
            注：range 是取左不取右。也就是说 col 可以取 0 但是不可以取 15
            当然我们也可以 range(10,30) 意思就是 [10,30) 
        4.sheet_data[2].shape[0]+1 意思就是 sheet2 中的行数+1
            shape[0] 是列表的行数，shape[1] 是列表的列数

'''


for j in range(3):                                         # 遍历三个sheet的数据，将sheet中的NAN值全部替换为0，因为有些函数无法处理NAN，所以要替换
    array[j] = sheet_data[j].fillna("0").values            # 并且存入新的array中
    

for row in range(sheet_data[2].shape[0]):                  # 遍历 sheet3 中的行
    for j in column_list:                                  # 遍历 column_list 中的列名
        final_index = column_list.index(j)                 # j(中国) 是当前的国家名，在 column_list 中找到 j(中国) 在该列表中的索引号
                                                           # 比如 a = ["意大利","中国","美国"]   a.index("中国") = 1
        for k in range(3):
            col = index[k][j]                              # k 代表是第一个sheet, j 索引该 sheet 中 国家名对应的 列序号(索引) 如有不明白可查看补充知识 

            if j == "年" or j == "月":                      # 排除列名中的 年、 月， 因为我们不需要相加这个数据
                final_array[row][final_index] = int(array[k][row][col]) # 将 年、月 的数据 存在新的数组里,详细可以看下方补充知识
                break
            else:
                
                final_array[row][final_index]  += float(array[k][row][col])

'''
    补充知识：
        1.int(a) 是强制类型转换，将 a 强行转换为整数
        2.float(b) 将 b 强行转为浮点型（就是小数），只有转为小数，才可以相加
        3.a += 1 是 a = a + 1 的简写
        4.array[k][row][col] 中 k 是指第k个sheet, row 是指第row行，col 是指第col列
    在上面的循环例子中：
        假设 j 为"年"，将年的数据(ie."2020")存到 final_array 中

        假设 j 为"中国"时 , 我们通过 final_index = column_list.index(j) 得到 
            final_index = column_list.index("中国") = 1 
        当 k = 0 时
            col = index[0]["中国"] 是指 sheet1 中 中国 是第 col 列， 假设为 col = 3
        判断 j 不是 "年" 和 "月"：
            将三个表中的数据相加 赋值到 新的表中
        
'''

#---------------------------------- 排序 -------------------------------------

index = 0     # 记录第一个2020出现的行数
flag = 0      # 可被视为信号标

for col in range(0,np.array(final_array).shape[1]):                           # 遍历 列
    for row in range(index,sheet_data[2].shape[0]):                           # 遍历 行

        if final_array[row][col] == 2020 and flag == 0:                       # 如果是 2020年 开始的数据 并且 信号标为0
            index = row                                                       # 就记录 2020年 起始的行数
            flag = 1                                                          # 信号标 设为 1， 目的是不会重复的设置 index, 保证下一个循环中，不会进入该判断语块
            break                                                             # break 是指 跳出该循环块 
        elif flag == 1:
            final_array[sheet_data[2].shape[0]][col] += final_array[row][col]  # 计算每个国家的2020年的总额

'''
    补充知识：
        1.continue和break的区别
        for a in range(100):
            for b in range(30):
                print("内循环")
                if c:
                    continue
                if d:
                    break
                print("还是内循环")
            print("外循环")

        当 a = 5, b = 10 时, continue 被触发，则
            下一个打印的是 "内循环"
            "还是内循环"将不会打印,相当于略过内循环的剩下部分
        同时 a = 5, b = 11

        当 a = 76, b = 13 时, break 被触发，则
            下一个打印的是 "外循环"，相当于直接进入到下一个外循环
        同时 a = 77, b = 0

'''
# 将 final_array 转为 dataframe 格式，不额外设置行名，设置列名为column_list，
# .T 的意思是将行转列，列转行                
df = pd.DataFrame(final_array,index=None,columns =column_list).T  

# sheet_data[2].shape[0] 得到的是刚刚我们求出2020总额的索引
# df.columns[sheet_data[2].shape[0]] 的意思是根据2020总额这一列来进行排序
# ascending = False 的意思是降序排列
# 如果不写 ascending=False， 则默认升序
df = df.sort_values(df.columns[sheet_data[2].shape[0]],ascending=False)  

# 因为我们排序的时候会默认把 年月 也排进去，所以要新建一个列表，将“年”，“月” 以及 总额对应的国家名 记录下来
# 因为我们最后生成的 文件中， sheet2, sheet3, sheet4 的国家排列顺序，应该与第一个表中一样，未出现在第一个表中的国家，将放在表的最后，没有序列要求
sorted_list = ["年","月"]       
for index in df.index:                                      # 因为已经将列转行， 所以读取国家名应该用 df.index
    if index in sorted_list:                                # 如果该国家已经在 sorted_list 中，继续下一个循环
        continue
    else:                                                   # 如果没有，则加入到 sorted_list
        sorted_list.append(index)

df = df.reindex(index=sorted_list)                          # 通过 reindex, 将行的顺序根据sorted_list的顺序重新排列

new_list = [[],[],[]]
for i in range(3):
    new_list[i] = df.index.tolist()                          # 将df（最终输出表）中的行名信息（国家名）保存到列表中
    for index in sheet_data[i].columns:                      # 遍历原sheet中的国家名
        if index in df.index:                                # 如果该国家名在df中存在，则继续下一个循环
            continue
        elif "Unname" not in index:                          # 如果不是“Unname” 且未出现在df中
            new_list[i].append(index)                        # 则在将该国家名放在列表的后面，其中“类别” 将作为分割线，更方便查看

#---------------------------------- 将数据写入新的Excel文件 -------------------------------------

writer = pd.ExcelWriter('result.xlsx')                       # 创建一个新的Excel文件，自定义名称
df.to_excel(writer,sheet_name = "月度汇总")                   #  将df写入名字为“阅读汇总”的sheet里

# 根据刚刚重新排序的 国家名
# 重新排 列的顺序 （国家的顺序）
sheet_data[0]=sheet_data[0].reindex(columns=new_list[0])
sheet_data[1]=sheet_data[0].reindex(columns=new_list[1])
sheet_data[2]=sheet_data[0].reindex(columns=new_list[2])

# 将sheet_data 的数据，行转列，列转行，写入Excel
sheet_data[0].T.to_excel(writer,sheet_name = "LLD")
sheet_data[1].T.to_excel(writer,sheet_name = "LD")
sheet_data[2].T.to_excel(writer,sheet_name = "HD")
# 保存 Excel
writer.save()
# writer.close()