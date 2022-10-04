from fastapi import FastAPI, Depends, Path, Query, HTTPException, Body

from os import environ
from secrets import token_hex

import databases
import sqlalchemy

from score_model import *
from playcount_model import *

auth_key = token_hex(20)
with open("auth.txt", "w", encoding="utf-8") as f:
    f.write(f"----------AUTH KEY----------\n{auth_key}\n----------AUTH KEY END----------")

app = FastAPI(title="부평고 2022 코딩 동아리", description="2022년도 부평고등학교 코딩 동아리에서 만든 게임에 쓰이는 백엔드 API입니다.", docs_url="/docs", redoc_url="/redoc")

database = databases.Database("sqlite:///./db.sqlite3")

metadata = sqlalchemy.MetaData()

scores = sqlalchemy.Table(
    "scores",
    metadata,
    sqlalchemy.Column("student_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("time_score", sqlalchemy.Integer),
    sqlalchemy.Column("action_score", sqlalchemy.Integer),
    sqlalchemy.Column("overall_score", sqlalchemy.Integer)
)

playcount_records = sqlalchemy.Table(
    "playcount",
    metadata,
    sqlalchemy.Column("student_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("playcount", sqlalchemy.Integer)
)

engine = sqlalchemy.create_engine(
    "sqlite:///./db.sqlite3", connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

async def auth(key: str = Query(..., title="보안 키")):
    if key == auth_key:
        return {"error": False, "key": key}
    else:
        return {"error": True, "obj": HTTPException(status_code=403, detail="보안 키가 올바르지 않습니다.")}

@app.get('/get-score', 
         summary="점수 가져오기", 
         response_model=ScoreListResponseModel,
         description="학번을 기반으로 점수를 가져옵니다. 학번을 입력하지 않을 경우 모든 점수 데이터를 가져옵니다.",
         status_code=200,
         tags=["Score", "Load"])
async def get_score(player_id: str = Query(None, title="학번", description="스코어를 가져올 학생의 학번")):
    if player_id:
        return await database.fetch_one(scores.select().where(scores.c.student_id == player_id))
    return await database.fetch_all(scores.select())

@app.put("/put-score",
         summary="점수 저장",
         status_code=201,
         response_model=SingleScoreResponseModel,
         description="학번을 기반으로 점수를 저장합니다. 학번이 이미 존재할 경우 기존 점수를 덮어씁니다.",
         tags=["Score", "Save"])
async def put_score(auth: dict = Depends(auth),
                    player_id: str = Query(..., title="학번"),
                    time: int = Query(..., title="시간 점수"),
                    action: int = Query(..., title="액션 점수"), 
                    score: int = Query(..., title="점수 합계")):
    if auth["error"]:
        raise auth["obj"]
    obj = {
        "student_id": player_id,
        "time_score": time,
        "action_score": action,
        "overall_score": score
    }
    if await database.fetch_one(scores.select().where(scores.c.student_id == player_id)):
        await database.execute(scores.update().where(scores.c.student_id == player_id).values(obj))
    else:
        obj["student_id"] = player_id
        await database.execute(scores.insert().values(obj))
    return obj

@app.get("/get-playcount",
         summary="플레이 횟수 가져오기",
         status_code=200,
         response_model=PlayCountResponseModel,
         description="학번을 기반으로 플레이한 횟수를 가져옵니다.",
         tags=["PlayCount", "Load"])
async def get_playcount(player_id: str = Query(..., title="학번", description="플레이 횟수를 가져올 학생의 학번")):
    return await database.fetch_one(playcount_records.select().where(playcount_records.c.student_id == player_id))

@app.put('/put-playcount',
         summary="플레이 횟수 저장",
         status_code=201,
         description="학번을 기반으로 플레이 횟수를 저장합니다. 학번이 이미 존재할 경우 기존 플레이 횟수에 1을 더한 값을 저장합니다. 생성값은 1입니다.",
         tags=["PlayCount", "Save"])
async def put_playcount(auth: dict = Depends(auth),
                        player_id: str = Query(..., title="학번")):
    if auth["error"]:
        raise auth["obj"]
    if await database.fetch_one(playcount_records.select().where(playcount_records.c.student_id == player_id)):
        await database.execute(playcount_records.update().where(playcount_records.c.student_id == player_id).values(playcount=playcount_records.c.playcount + 1))
    else:
        await database.execute(playcount_records.insert().values(student_id=player_id, playcount=1))
    return {"student_id": player_id}

@app.get("/check", status_code=200, tags=["Etc"])
async def checkalive():
    return {"alive": True}