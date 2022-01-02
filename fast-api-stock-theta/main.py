from fastapi import FastAPI, templating, Request, Form
from fastapi.params import Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pandas.core.frame import DataFrame
from pydantic import BaseModel
import yfinance as yf
import datetime
import pandas as pd
from fastapi.openapi.utils import get_openapi

app = FastAPI()
templates = Jinja2Templates(directory="htmldirectory")
#working combo 

def my_schema():
   openapi_schema = get_openapi(
       title="Selling theta - handbook",
       version=".1",
       routes=app.routes,
   )
   openapi_schema["info"] = {
       "title" : "Selling theta - handbook",
       "version" : "0.1",
       "description" : "Learn about programming language history!",
       "termsOfService": "https://www.azuremonk.com",
       "contact": {
           "name": "Get Help with this API",
           "url": "http://www.programming-languages.com/help",
           "email": "support@programming-languages.com"
       },
       "license": {
           "name": "Apache 2.0",
           "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
       },
   }
   app.openapi_schema = openapi_schema
   return app.openapi_schema

app.openapi = my_schema
    
    

    

class stockcompute:
    
    def __init__(self, ticker, start_date, end_date, day_change_variable,std_dev_input) -> None:
        self.yfobj = yf.Ticker(ticker)
        self.logo = self.yfobj.info['logo_url']
        #self.businessummary = self.yfobj.info['longBusinessSummary']
        self.ticker = ticker
        self.stddevinput = std_dev_input
        self.startdate = start_date
        self.enddate = end_date
        self.daychangevariable = day_change_variable
        self.data = yf.download(self.ticker,self.startdate,self.enddate)
        
        if self.daychangevariable==30:
            self.periods = 23
            self.data["MonthPriceChange"]= self.data['Close'].pct_change(periods=self.periods)*100
            self.mean = self.data['MonthPriceChange'].mean()
            self.std = self.data['MonthPriceChange'].std()
            self.outliersdf = self.data[(self.data.MonthPriceChange >= self.mean + self.std*self.stddevinput) | (self.data.MonthPriceChange <= self.mean - self.std*self.stddevinput)][:]
            self.outlierssorted = self.outliersdf.sort_values(by='MonthPriceChange', ascending=False)
            try:
                self.dropped = self.outlierssorted.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume', 'WeekPriceChange'], axis=1)
            except:
                self.dropped = self.outlierssorted.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume'], axis=1)
        else:
            self.periods = 5
            self.data["WeekPriceChange"]= self.data['Close'].pct_change(periods=self.periods)*100
            self.mean = self.data['WeekPriceChange'].mean()
            self.std = self.data['WeekPriceChange'].std()  
            self.outliersdf = self.data[(self.data.WeekPriceChange >= self.mean + self.std*self.stddevinput) | (self.data.WeekPriceChange <= self.mean - self.std*self.stddevinput)][:]
            self.outlierssorted = self.outliersdf.sort_values(by='WeekPriceChange', ascending=False)
            try:
                self.dropped = self.outlierssorted.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume', 'MonthPriceChange'], axis=1)
            except:
                self.dropped = self.outlierssorted.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume'], axis=1)
    def return_raw_df(self):
        return self.data
    def return_mean(self):
        return str(round(self.mean,2))
    def return_std(self):
        return str(round(self.std,2))
    def week_mean(self):
        return str(round(self.weekmean,2))
    def week_std(self):
        return str(round(self.weekstd,2))
    def outliers(self):
        return self.outliers
    def return_html(self):
        self.temphtml = self.dropped.to_html()
        self.return_html = self.temphtml.replace('dataframe','ui celled table',1)  
        return self.return_html 
    def return_logo(self):
        if self.logo:
            return self.logo
        else:
            return "https://i.pinimg.com/favicons/177e61c3f861d88bd2153738cce101e1d192ae3c6352ffd50f5ea022.png?2f4866302e741dcf0ba9a28a6d7718ab"
    def return_business_summary(self):
        return self.businessummary
    def return_prob_percentage(self):
        if self.stddevinput ==1:
            return "68%"
        elif self.stddevinput ==2:
            return "95%"
        else:
            return "99%"
    def return_lower_bounds(self):
        self.lowerbounds = str(round(self.mean - self.std*self.stddevinput,2))
        return self.lowerbounds
    def return_periods(self):
        if self.periods == 5:
            return "one week"
        else:
            return "one month"
    def return_upper_bounds(self):
        self.upperbounds = str(round(self.mean + self.std*self.stddevinput,2))
        return self.upperbounds
        

def initialize_stock(ticker_input, start_date, end_date, day_change_variable,std_dev_input):
    stock_initialize = stockcompute(ticker_input,start_date, end_date, day_change_variable, std_dev_input)
    return stock_initialize







@app.get("/", response_class=HTMLResponse)
def write_data(myrequest:Request, tickeruiinput: str = None, stddevinput: int = None, samplingrate: int =None, daychangevariable: int = None):
    if not samplingrate: 
        samplingrate= 1
    if not daychangevariable:
        daychangevariable =30
    if not tickeruiinput:
        tickeruiinput = "MSFT"
    if not stddevinput:
        stddevinput = 1  
    enddate = datetime.date.today()
    startdate = enddate - datetime.timedelta(weeks=52*samplingrate)
    intitialized_stock_object = initialize_stock(tickeruiinput, startdate, enddate, daychangevariable,stddevinput)
    print(intitialized_stock_object.logo)
    return templates.TemplateResponse("home.html", {"request": myrequest, "stockobject": intitialized_stock_object, "ticker":tickeruiinput, "samplingrate":samplingrate})
    
   


# This is a valid response to return JSON without Jinja2
    # return {
        
    #     openprice_on_particulardate.to_json(),
    #     data['delta'].mean(),
    #     max_close,
    #     anand
    # } 
