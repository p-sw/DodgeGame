from fastapi import FastAPI, Depends, Path, Query, HTTPException, Body
from deta import Deta
from typing import Optional

from pydantic import BaseModel, Field

from os import environ
from secrets import token_hex

deta = Deta(project_key=environ.get("DATABASE_KEY"))

auth_key = token_hex(20)
with open("auth.txt", "w", encoding="utf-8") as f:
    f.write(f"----------AUTH KEY----------\n{auth_key}\n----------AUTH KEY END----------")

app = FastAPI(title="부평고 2022 코딩 동아리", description="2022년도 부평고등학교 코딩 동아리에서 만든 게임에 쓰이는 백엔드 API입니다.", docs_url=None, redoc_url="/docs")

async def deta_connection():
    return deta.Base("game_score")

async def auth(key: str = Query(..., title="보안 키")):
    if key == auth_key:
        return {"error": False, "key": key}
    else:
        return {"error": True, "obj": HTTPException(status_code=403, detail="보안 키가 올바르지 않습니다.")}

class SingleScoreResponseModel(BaseModel):
    key: str = Field(..., description="학번")
    time_score: int = Field(..., description="시간 점수")
    action_score: int = Field(..., description="액션 점수")
    overall_score: int = Field(..., description="전체 점수")
    
    class Config:
        schema_extra = {
            "example": {
                "key": "10101",
                "time_score": 20000,
                "action_score": 2000,
                "overall_score": 22000
            }
        }

class ScoreResponseModel(BaseModel):
    key: str = Field(..., description="학번")
    time_score: int = Field(..., description="시간 점수")
    action_score: int = Field(..., description="액션 점수")
    overall_score: int = Field(..., description="전체 점수")
    
    class Config:
        schema_extra = {
            "example": [
                {
                    "key": "10101",
                    "time_score": 20000,
                    "action_score": 2000,
                    "overall_score": 22000
                },
                {
                    "key": "10102",
                    "time_score": 21000,
                    "action_score": 0,
                    "overall_score": 21000
                }
            ]
        }

@app.get('/get-score', 
         summary="점수 가져오기", 
         response_model=ScoreResponseModel,
         description="학번을 기반으로 점수를 가져옵니다. 학번을 입력하지 않을 경우 모든 점수 데이터를 가져옵니다.",
         status_code=200)
async def get_score(player_id: str = Query(None, title="학번", description="스코어를 가져올 학생의 학번"), 
                    db: deta.Base = Depends(deta_connection)):
    if player_id:
        return db.get(player_id)
    res = db.fetch()
    all_items = res.items
    
    while res.last:
        res = db.fetch(last=res.last)
        all_items += res.items
    return all_items

@app.put("/put-score",
         summary="점수 저장",
         status_code=201,
         response_model=SingleScoreResponseModel,
         description="학번을 기반으로 점수를 저장합니다. 학번이 이미 존재할 경우 기존 점수를 덮어씁니다.")
async def put_score(auth: dict = Depends(auth),
                    player_id: str = Query(..., title="학번"),
                    time: int = Query(..., title="시간 점수"),
                    action: int = Query(..., title="액션 점수"), 
                    score: int = Query(..., title="점수 합계"), 
                    db: deta.Base = Depends(deta_connection)):
    if auth["error"]:
        raise auth["obj"]
    obj = {
        "time_score": time,
        "action_score": action,
        "overall_score": score
    }
    if db.get(player_id):
        db.update(player_id, obj)
    else:
        db.put(player_id, obj)
    return obj

@app.get("/check", status_code=200)
async def checkalive():
    return {"alive": True}