from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.service import Service
import time

app = Flask(__name__)


@app.route("/",methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review",methods=['POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            s=Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=s)
            driver.maximize_window()
            channelname = request.form['content'].replace(" ","")
            driver.get(f"https://www.youtube.com/@{channelname}/videos")
            time.sleep(4)
            driver.execute_script("window.scrollTo(0, 400)")
            #driver.get("https://www.youtube.com/@PW-Foundation/videos")
            links = driver.find_elements(By.XPATH,'//*[@id="thumbnail"]')
            urls = []
            for link in links[::2]:
                 url = link.get_attribute("href")
                 urls.append(url)
                 #print(url)
            #thumnails
            links = driver.find_elements(By.TAG_NAME,"img")
            thumbnails = []
            for thumbnail in links:
                thumb = thumbnail.get_attribute("src")
                if str(thumb).find('i.ytimg.com')>0:
                    thumbnails.append(thumb)
                    #print(thumb)
            #title
            titles = driver.find_elements(By.XPATH,'//*[@id="video-title"]')
            titles_video = []
            for i in titles:
                titles_video.append(i.get_attribute('aria-label'))
                #print(i.get_attribute('aria-label'))
            #views
            views = driver.find_elements(By.XPATH,'//*[@id="metadata-line"]/span[1]')
            video_views = []
            for i in views:
                video_views.append(i.text)
                #print(i.text)
            #posting time
            times = driver.find_elements(By.XPATH,'//*[@id="metadata-line"]/span[2]')
            video_times = []
            for i in times:
                video_times.append(i.text)
                #print(i.text)
            absolute_time = []
            for i in video_times:
                if i.find('hours')>0:
                    hours = int(i.split(" ")[0])
                    tm_absolute = datetime.now() - pd.Timedelta(hours=hours)
                    dt_string = tm_absolute.strftime("%d %b %Y")
                    absolute_time.append(dt_string)
                elif i.find('day')>0:
                    days = int(i.split(" ")[0])
                    tm_absolute = datetime.now() - pd.Timedelta(days=days)
                    dt_string = tm_absolute.strftime("%d %b %Y")
                    absolute_time.append(dt_string)
                elif i.find('week')>0:
                    weeks = int(i.split(" ")[0])
                    tm_absolute = datetime.now() - pd.Timedelta(weeks=weeks)
                    dt_string = tm_absolute.strftime("%d %b %Y")
                    absolute_time.append(dt_string)
                elif i.find('month')>0:
                    months = int(i.split(" ")[0])
                    tm_absolute = datetime.now() - relativedelta(months=months)
                    dt_string = tm_absolute.strftime("%d %b %Y")
                    absolute_time.append(dt_string)
                elif i.find('year')>0:
                    years = int(i.split(" ")[0])
                    tm_absolute = datetime.now() - relativedelta(years=years)
                    dt_string = tm_absolute.strftime("%d %b %Y")
                    absolute_time.append(dt_string) 
            
            dict = {'Title':titles_video[:5],'UploadDate':absolute_time[:5],'Views':video_views[:5],'VideoURL':urls[1:6],'ThumbnailURL':thumbnails[:5]}
           
            new = pd.DataFrame.from_dict(dict)
            #print(new)
            new.to_csv('youtubereview.csv',index=False)

            client = pymongo.MongoClient("mongodb+srv://kishan42:kishan42@review.hzf2bua.mongodb.net/test")
            db = client['Review_scrap']
            review_col = db['review_scrap_data']
            data = [{"channel_name": channelname}]
            
            review_col.insert_many(data) 
            

            return render_template('result.html',df=new,channelName=channelname)

        except Exception as e:
            return "somthing wrong"      

    else:
        return render_template('index.html')
        
if __name__=="__main__":
    app.run(debug=True)