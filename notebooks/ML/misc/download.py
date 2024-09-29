from http.client import HTTPException
from pathlib import Path

import pandas as pd
import requests

train_full = pd.read_csv('../data/train_full.csv')
train_part = train_full[
    train_full['is_duplicate']
    &
    ~train_full['exist_video']
    &
    ~train_full['exist_duplicate_for']
    ]

for i, row in train_part.iterrows():
    print(row)
    #response = requests.get(row['link'])
#
    #if not response.ok or response.status_code != 200:
    #    raise HTTPException(status_code=400, detail="Unable to download file by link")
#
    #try:
    #    with open(Path(f"../data/uploaded_videos/{row['uuid']}.mp4"), "wb") as file:
    #        file.write(response.content)
    #except Exception as e:
    #    raise HTTPException(status_code=400, detail=f"Unable to save file, traceback: {e}")

    response_orig = requests.get(f"https://s3.ritm.media/yappy-db-duplicates/{row['duplicate_for']}.mp4")
    if not response_orig.ok or response_orig.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to download file by link")

    try:
        with open(Path(f"../data/uploaded_videos/{row['duplicate_for']}.mp4"), "wb") as file:
            file.write(response_orig.content)
        duplicate_for = row['duplicate_for']
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unable to save file, traceback: {e}")

    print('----------------Файлы скачены------------------')
    print('-----------------------------------------')