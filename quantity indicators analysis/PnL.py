
import random
import csv
import numpy as np
import pandas as pd
import datetime
#from datetime import datetime
import time
from pandas import Series,DataFrame
from locale import *
import calendar


def Getdatelist(BeginDate, EndDate):#获取时间段内的交易日，并返回交易日列表
    trading_date_df = pd.read_csv('TradingDates.csv')
    #print(trading_date_df)
    tdlist = trading_date_df['TRADE_DT'].tolist()
    datelist = []
    for date in tdlist:
        if date < int(BeginDate):
            yesterdaydate = date
        if date < int(BeginDate) or date > int(EndDate):
            continue
        datelist.append(date)
    return datelist


def Daily_return_random(BeginDate, EndDate):#随机生成每日盈利
    datelist = Getdatelist(BeginDate, EndDate)
    df_random = pd.DataFrame()
    df_random['Date'] = datelist
    lenth = len(datelist)
    Retlist = [ random.uniform(-0.1, 0.1) for i in range(lenth) ]
    df_random['Ret'] = Retlist
    #df.to_csv('DailyReturn.csv', encoding='gbk', index = None)
    return df_random

def OutputReport(file, Start, End):#计算时间段内的收益等指标
    df_daily_return = pd.read_csv(file)
    daily_return_all = []
    for i in range(len(df_daily_return)):  
        daily_return_all.append(1 + df_daily_return.loc[0:i, 'Ret'].sum())
    df_daily_return['NAV'] = daily_return_all#计算daily净值
    #print(df_daily_return)
    #df_daily_return.to_csv('df_daily_return.csv', encoding='gbk', index = None)
    Start = int(Start)
    End = int(End)
    
    datelist = Getdatelist(Start, End) #获取时间段内的交易日列表
    df_report = pd.DataFrame(columns=[
        'Date','Ret', 'Vol', 'Sharp', 'NAV', 'MDD', 'MDD_N', 'MDD_T0',
        'MDD_T1', 'LDD', 'LDD_N', 'LDD_T0', 'LDD_T1'])
    start_date = datelist[0]
    end_date = datelist[-1]
    df_start_end = df_daily_return[(df_daily_return['Date']>=start_date) & (df_daily_return['Date']<=end_date)]
    df_start_end.index = range(len(df_start_end))#重置索引
    daily_return_list = df_start_end['Ret'].tolist() #时间段内的日盈利率
    daily_Nav_list = df_start_end['NAV'].tolist() #时间段内的日净值
    #daily_Nav_list=[ 1,1,1,1,1.01,1.01,1.01,1.03,1.05,0.8,0.9,1.01,1.01,1.01,1.06,1.05,1.04,1.05,1.02,1.02,1.02,1.03,1.04,1.05,1.06,1.07,1.07,1.07,1.08,1.09,1.09]
    drawdown_rate, drawdown_tian, j, i = MaxDrawdown(daily_Nav_list) #计算最大回撤
    LongdayDraw, Longdaylast, n, m = LongDrawdown(daily_Nav_list)#计算最长回撤
    #print(daily_Nav_list)
    #print(daily_return_list)
    print(End)
    df_report.loc[0, 'Date'] = End
    df_report.loc[0, 'Ret'] = sum(daily_return_list)#总收益
    df_report.loc[0, 'Vol'] = np.std(daily_return_list) * np.sqrt(len(daily_return_list))#年化波动率

    df_report['Sharp'] = df_report['Ret']/df_report['Vol']#夏普比率
    #df_report.loc[0, 'NAV'] = df_start_end.loc[len(datelist)-1, 'NAV']
    df_report.loc[0, 'MDD'] = drawdown_rate#最大回撤
    df_report.loc[0, 'MDD_N'] = drawdown_tian#最大回撤天数
    #print(df_start_end)
    df_report.loc[0, 'MDD_T0'] = df_start_end.loc[j, 'Date']#最大回撤起始日期
    df_report.loc[0, 'MDD_T1'] = df_start_end.loc[i, 'Date']#最大回撤结束日期
    df_report.loc[0, 'NAV'] = df_start_end.loc[len(datelist)-1, 'NAV']
    df_report.loc[0, 'LDD'] = LongdayDraw#最长回撤
    df_report.loc[0, 'LDD_N'] = Longdaylast#最长回撤持续天数
    df_report.loc[0, 'LDD_T0'] = df_start_end.loc[n, 'Date']#最长回撤起始日期
    df_report.loc[0, 'LDD_T1'] = df_start_end.loc[m, 'Date']#最长回撤结束日期
    #df_report.to_csv('df_report.csv', encoding='gbk', index = None)
    
    
    return df_report
    
    
def MaxDrawdown(daily_Nav_list):#计算最大回撤
    df = pd.DataFrame()
    df['回撤'] = np.maximum.accumulate(daily_Nav_list) - daily_Nav_list
    #print(df)
    if df['回撤'].sum() == 0 or len(daily_Nav_list) == 1:#特殊情况处理
        drawdown_max, drawdown_tian, j, i = 0, 0, len(daily_Nav_list)-1, len(daily_Nav_list)-1
    else:
        #print(daily_Nav_list)
        i = np.argmax((np.maximum.accumulate(daily_Nav_list) - daily_Nav_list)) #结束位置
        if i == 0:
            return 0
        j = np.argmax(daily_Nav_list[:i])  # 开始位置
        drawdown_max = daily_Nav_list[i] - daily_Nav_list[j]
    drawdown_tian = i - j
    return drawdown_max, drawdown_tian, j, i

    

def LongDrawdown(daily_Nav_list):#最长回撤计算
    df = pd.DataFrame()
    #print(daily_Nav_list)
    df['回撤'] = np.maximum.accumulate(daily_Nav_list) - daily_Nav_list
    l = len(daily_Nav_list)
    #print(l)
    if df['回撤'].sum() == 0 or l == 1:
        #print(l)
        LongdayDraw, Longdaylast, n, m = 0, 0, l-1, l-1
    if l>1 and df['回撤'].sum() != 0:
        day_last_list = [0]*l
        max_list = [0]*l
        long_day_start = [0]*l
        long_day_end = [0]*l
        for i in range(1, l):#这里下标从1开始
            wealth_max = max(daily_Nav_list[0:i+1])
            max_index = daily_Nav_list.index(wealth_max)
            if max_index == i:
                wealth_min = wealth_max
                min_index = i
            if max_index < i:
                wealth_min = min(daily_Nav_list[max_index:i])
            min_index = daily_Nav_list.index(wealth_min, max_index)
            longdd = min_index - max_index
            max_list[i] = longdd
            long_day_start[i] = max_index
            long_day_end[i] = min_index
            day_last_list[i] = longdd
        Longdaylast = max(max_list[1:])
        m = max_list[1:].index(Longdaylast) # 结束下标
        n = m - Longdaylast # 开始下标
        LongdayDraw = daily_Nav_list[m] - daily_Nav_list[n]
    return LongdayDraw, Longdaylast, n, m

    
def WeekMonthYear(BeginDate, EndDate):
    datelist = Getdatelist(BeginDate, EndDate)
    week_list = []
    month_list = []
    year_list = []
    #print(datelist)
    for date in datelist:
        date = str(date)
        #print(date)
        month_date = []
        m = int(int(date)/100)%100
        month_date.append(date)
        month_date.append(m)
        month_list.append(month_date)
        
        year_date = []
        y = int(int(date)/10000)
        year_date.append(date)
        year_date.append(y)
        year_list.append(year_date)
        
        week_date = []
        
        weekday = datetime.datetime.strptime(date,'%Y%m%d').strftime('%W')#找出第几周,存储到二维列表中
        week_date.append(date)
        week_date.append(weekday)
        week_list.append(week_date)

        year_BeginDate_list = []
        year_EndDate_list = [] 
        year_BeginDate_list.append(str(BeginDate))
        year_BeginDate_list, year_EndDate_list = WeekMY(year_EndDate_list, year_BeginDate_list, year_list)
        year_EndDate_list.append(str(EndDate))
        
        
        month_BeginDate_list = []
        month_EndDate_list = [] 
        month_BeginDate_list.append(str(BeginDate))
        month_BeginDate_list, month_EndDate_list = WeekMY(month_EndDate_list, month_BeginDate_list, month_list)
        month_EndDate_list.append(str(EndDate))
        
        week_BeginDate_list = []
        week_EndDate_list = [] 
        week_BeginDate_list.append(str(BeginDate))
        week_BeginDate_list, week_EndDate_list = WeekMY(week_EndDate_list, week_BeginDate_list, week_list)
        week_EndDate_list.append(str(EndDate))
    
    #print(week_BeginDate_list)
    #print(week_EndDate_list)
    #print(year_BeginDate_list)
    #print(year_EndDate_list)
    #print(month_BeginDate_list)
    #print(month_EndDate_list)
    return  week_BeginDate_list, week_EndDate_list, month_BeginDate_list, month_EndDate_list, year_BeginDate_list, year_EndDate_list
        
    
def WeekMY(EndDate_list, BeginDate_list, W_M_Y_list):#分别计算出相同周、月、年对应的起始时间
    for i in range(1, len(W_M_Y_list)):
        if W_M_Y_list[i][1] != BeginDate_list[-1][1] and W_M_Y_list[i][1] != W_M_Y_list[i-1][1]:
            EndDate_list.append(W_M_Y_list[i-1][0])
            BeginDate_list.append(W_M_Y_list[i][0])
    return BeginDate_list, EndDate_list
    #week_EndDate_list.append(str(EndDate))
    
def Main_Function(BeginDate, EndDate):
    week_BeginDate_list, week_EndDate_list, month_BeginDate_list, month_EndDate_list, year_BeginDate_list, year_EndDate_list = WeekMonthYear(BeginDate, EndDate)
    #print(week_BeginDate_list)
    #print(week_EndDate_list)
    Total_return(week_BeginDate_list, week_EndDate_list)
    df_TotalReport_week = Total_return(week_BeginDate_list, week_EndDate_list)
    df_TotalReport_week.to_csv('Weekly.csv', encoding = 'gbk', index = None)
    
    df_TotalReport_month = Total_return(month_BeginDate_list, month_EndDate_list)
    df_TotalReport_month.to_csv('monthly.csv', encoding = 'gbk', index = None)
    
    df_TotalReport_year = Total_return(year_BeginDate_list, year_EndDate_list)
    df_TotalReport_year.to_csv('yearly.csv', encoding = 'gbk', index = None)
    
    #print(df_TotalReport_week)
    
    
def Total_return(BeginDate_list, EndDate_list):
    n = len(BeginDate_list)
    df_TotalReport = pd.DataFrame()
    for i in range(n):
        Start = BeginDate_list[i]
        End = EndDate_list[i]
        df_report = OutputReport(file, Start, End)
        df_TotalReport = pd.concat([df_TotalReport, df_report], axis=0) 
    return df_TotalReport


if __name__ == '__main__':
    file = 'DailyReturn.csv'
    BeginDate = 20180101
    EndDate = 20201231
    Main_Function(BeginDate, EndDate)

    
    