from fastapi import FastAPI, Depends, Path, Query
from deta import Deta
from typing import Optional

from pydantic import BaseModel

deta = Deta(project_key="c0ck7b4e_HQ7hAy9hspk5gJPKQvkS9csYyBu1oLeo")

app = FastAPI(title="부평고 2022 코딩 동아리", description="2022년도 부평고등학교 코딩 동아리에서 만든 게임에 쓰이는 백엔드 API입니다.", docs_url=None, redoc_url="/docs")

async def deta_connection():
    return deta.Base("game_score")

class ScoreResponseModel(BaseModel):
    player_id: str
    score: int

@app.get('/get-score')
async def get_score(player_id: str = Query(None, title="학번", description="스코어를 가져올 학생의 학번을 입력합니다. 입력하지 않을 경우 모든 점수를 가져옵니다."), db: deta.Base = Depends(deta_connection)):
    res = db.fetch()
    all_items = res.items
    
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items
    return all_items

@app.put("/put-score",
         summary="점수 저장")
async def put_score(player_id: str = Query(..., title="학번", description="학생의 학번을 입력합니다."), score: int = Query(..., title="점수", description="학생의 점수를 입력합니다."), db: deta.Base = Depends(deta_connection)):
    if db.get(player_id):
        db.update(player_id, {"score": score})
    else:
        db.put({"score": score}, player_id)