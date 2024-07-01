import fastapi
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,FileResponse
import pandas as pd
import lightgbm as lgb
# from sklearn.metrics import mean_squared_error, r2_score
from sklearn.svm import SVR
import numpy as np
from fastapi import File
from typing import Annotated

app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

loaded_model = lgb.Booster(model_file='lightgbm_model.txt')

@app.get("/", response_class=HTMLResponse)
async def root(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit", response_class=FileResponse)
async def submit(request: fastapi.Request, file: Annotated[bytes, File()]):
    # save the file to csv first
    with open('test.csv', 'wb') as f:
        f.write(file)
    testdf = pd.read_csv('test.csv')
    
    testdf.replace('\\N', None, inplace=True)

    # dropping values that are not neeeded
    df=testdf.drop(['time_x', 'timetaken_in_millisec', 'fastestLap', 'rank', 'fastestLapTime', 'max_speed', 'time_y', 'url_x', 'fp1_date', 'fp1_time', 'fp2_date'
                , 'fp2_time', 'fp3_date', 'fp3_time', 'quali_date', 'quali_time', 'sprint_date', 'sprint_time', 'driver_num', 'driver_code', 'url_y'
                ,"number", "position_x", 'nationality_y', 'url', 'status', 'constructorRef', 'forename', 'surname', 'driverRef', 'positionText_x', 'nationality'], axis=1)


    #converting the dob and date column into years to determine the age of the driver
    df['dob'] = pd.to_datetime(df['dob'])
    df['date'] = pd.to_datetime(df['date'])
    df['time_difference'] = df['date'] - df['dob']
    df['years'] = (df['time_difference'].dt.days / 365.25).astype(int)

    df = df.drop(['dob', 'date', 'time_difference'], axis=1)

    frequency_company = df['company'].value_counts(normalize=True)
    df['company_encoded'] = df['company'].map(frequency_company)
    df = df.drop(['grand_prix', 'company'], axis=1)

    df["position"] = loaded_model.predict(df, num_iteration=loaded_model.best_iteration)
    newdf = df[["position", "result_driver_standing"]]
    newdf.to_csv('prediction.csv', index=False)
    
    return FileResponse('prediction.csv', media_type='text/csv', filename='prediction.csv')