from fastapi import FastAPI, Depends, Query, HTTPException
import sqlalchemy as db

from pydantic import BaseModel, Field
from secrets import token_hex

from sqlalchemy.orm import declarative_base, sessionmaker

auth_key = token_hex(20)
with open("auth.txt", "w", encoding="utf-8") as f:
    f.write(f"----------AUTH KEY----------\n{auth_key}\n----------AUTH KEY END----------")

app = FastAPI(title="부평고 2022 코딩 동아리", description="2022년도 부평고등학교 코딩 동아리에서 만든 게임에 쓰이는 백엔드 API입니다.", docs_url=None,
              redoc_url="/docs")

engine = db.create_engine("sqlite:///db.sqlite3")
connection = engine.connect()

base = declarative_base()
Session = sessionmaker(bind=engine)


class Score(base):
    __tablename__ = "score"
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer)
    score = db.Column(db.Integer)
    action = db.Column(db.Integer)
    time = db.Column(db.Integer)


class Playcount(base):
    __tablename__ = "playcount"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)


base.metadata.create_all(engine)


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
async def get_score(player_id: str = Query(None, title="학번", description="스코어를 가져올 학생의 학번")):
    if player_id:
        session = Session()
        data = session.query(Score).filter(Score.id == player_id).all()
        session.close()
        return data
    else:
        session = Session()
        data = session.query(Score).all()
        session.close()
        return data


@app.put("/put-score",
         summary="점수 저장",
         status_code=201,
         response_model=SingleScoreResponseModel,
         description="학번을 기반으로 점수를 저장합니다. 학번이 이미 존재할 경우 기존 점수를 덮어씁니다.")
async def put_score(auth: dict = Depends(auth),
                    player_id: int = Query(..., title="학번"),
                    time: int = Query(..., title="시간 점수"),
                    action: int = Query(..., title="액션 점수"),
                    score: int = Query(..., title="점수 합계")):
    if auth["error"]:
        raise auth["obj"]
    session = Session()
    data = session.query(Score).filter(Score.id == player_id).first()
    if data:
        data.time = time
        data.action = action
        data.score = score
    else:
        data = Score(id=player_id, time=time, action=action, score=score)
        session.add(data)
    session.commit()
    session.close()
    return data


@app.get("/get-playcount",
         summary="플레이 횟수 가져오기",
         status_code=200,
         description="플레이 횟수를 가져옵니다.")
async def get_playcount():
    session = Session()
    data = session.query(Playcount).first()
    session.close()
    return data


@app.put("/put-playcount",
         summary="플레이 횟수 저장",
         status_code=201,
         description="플레이 횟수를 저장합니다.")
async def put_playcount(auth: dict = Depends(auth)):
    if auth["error"]:
        raise auth["obj"]
    session = Session()
    data = session.query(Playcount).first()
    if data:
        data.count = data.count + 1
    else:
        data = Playcount(count=1)
        session.add(data)
    session.commit()
    session.close()
    return data


@app.get("/check", status_code=200)
async def checkalive():
    return {"alive": True}
