from fastapi import FastAPI, Depends, Query, HTTPException
import sqlalchemy as db

from secrets import token_hex

from sqlalchemy.orm import declarative_base, sessionmaker

from playcount_model import PlayCountResponseModel
from score_model import SingleScoreResponseModel, ScoreListResponseModel

auth_key = token_hex(20)
with open("auth.txt", "w", encoding="utf-8") as f:
    f.write(f"----------AUTH KEY----------\n{auth_key}\n----------AUTH KEY END----------")
print("PRIVATE AUTH KEY:", auth_key)

app = FastAPI(title="부평고 2022 코딩 동아리", description="2022년도 부평고등학교 코딩 동아리에서 만든 게임에 쓰이는 백엔드 API입니다.", docs_url=None,
              redoc_url="/docs")

engine = db.create_engine("sqlite:///db.sqlite3")
connection = engine.connect()

base = declarative_base()
Session = sessionmaker(bind=engine)

season = 1


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
    print(str(auth_key)+",", "Type: "+str(type(auth_key)))
    print(key+",", "Type: "+str(type(key)))
    if key == str(auth_key):
        return {"error": False, "key": key}
    else:
        return {"error": True, "obj": HTTPException(status_code=403, detail="보안 키가 올바르지 않습니다.")}


@app.get('/get-score',
         summary="점수 가져오기",
         response_model=ScoreListResponseModel or SingleScoreResponseModel,
         description="학번을 기반으로 점수를 가져옵니다. 학번을 입력하지 않을 경우 모든 점수 데이터를 가져옵니다.",
         status_code=200)
async def get_score(player_id: str = Query(None, title="학번", description="스코어를 가져올 학생의 학번"),
                    season: int = Query(None, title="시즌", description="회차을 선택합니다.")):
    with Session() as session:
        if player_id:
            if session.query(Score).filter(Score.id == player_id).count() == 0:
                return {"key": player_id, "time_score": -1, "action_score": -1, "overall_score": -1}
            data = session.query(Score).filter(Score.id == player_id).first()
            return SingleScoreResponseModel(id=player_id, season=data.season, score=data.score, action=data.action, time=data.time)
        else:
            if season:
                data = session.query(Score).filter(Score.season == season).order_by(Score.score.desc()).all()
                return ScoreListResponseModel(scores=[SingleScoreResponseModel(id=i.id, season=i.season, score=i.score, action=i.action, time=i.time) for i in data])
            else:
                data = session.query(Score).order_by(Score.score.desc()).all()
                return ScoreListResponseModel(scores=[SingleScoreResponseModel(id=i.id, season=i.season, score=i.score, action=i.action, time=i.time) for i in data])


@app.put("/put-score",
         summary="점수 저장",
         status_code=201,
         response_model=SingleScoreResponseModel,
         description="학번을 기반으로 점수를 저장합니다. 학번이 이미 존재할 경우 기존 점수를 덮어씁니다.")
async def put_score(auth: dict = Depends(auth),
                    season: int = Query(..., title="회차"),
                    player_id: int = Query(..., title="학번"),
                    time: int = Query(..., title="시간 점수"),
                    action: int = Query(..., title="액션 점수"),
                    score: int = Query(..., title="점수 합계")):
    if auth["error"]:
        raise auth["obj"]
    with Session() as session:
        data = session.query(Score).filter(Score.id == player_id).first()
        if data:
            data.time = time
            data.action = action
            data.score = score
        else:
            data = Score(id=player_id, season=season, time=time, action=action, score=score)
            session.add(data)
        session.commit()
        return SingleScoreResponseModel(id=player_id, season=season, time=time, action=action, score=score)


@app.get("/get-playcount",
         summary="플레이 횟수 가져오기",
         status_code=200,
         response_model=PlayCountResponseModel,
         description="플레이 횟수를 가져옵니다.")
async def get_playcount(player_id: int = Query(..., title="학번")):
    with Session() as session:
        data = session.query(Playcount).filter(Playcount.id == player_id).first()
        if not data:
            data = Playcount(id=player_id, count=0)
            session.add(data)
            session.commit()
        return PlayCountResponseModel(id=player_id, count=data.count)


@app.put("/put-playcount",
         summary="플레이 횟수 저장",
         status_code=201,
         response_model=PlayCountResponseModel,
         description="플레이 횟수를 저장합니다.")
async def put_playcount(auth: dict = Depends(auth),
                        player_id: int = Query(..., title="학번")):
    if auth["error"]:
        raise auth["obj"]
    with Session() as session:
        data = session.query(Playcount).filter(Playcount.id == player_id).first()
        if data:
            data.count = data.count + 1
        else:
            print("Here!")
            data = Playcount(id=player_id, count=1)
            session.add(data)
        session.commit()
        return PlayCountResponseModel(id=player_id, count=data.count)


@app.put("/put-playcount-any",
         summary="플레이 횟수 저장",
         status_code=201,
         response_model=PlayCountResponseModel,
         description="플레이 횟수를 저장합니다.")
async def put_playcount_any(auth: dict = Depends(auth),
                            player_id: int = Query(..., title="학번"),
                            count: int = Query(..., title="플레이 횟수")):
    if auth["error"]:
        raise auth["obj"]
    with Session() as session:
        data = session.query(Playcount).filter(Playcount.id == player_id).first()
        if data:
            data.count = count
        else:
            data = Playcount(id=player_id, count=count)
            session.add(data)
        session.commit()
        return PlayCountResponseModel(id=player_id, count=data.count)


@app.get("/get-season",
         summary="회차 가져오기",
         status_code=200,
         description="회차를 가져옵니다.")
async def get_season():
    global season
    return {"season": season}


@app.put("/set-season",
         summary="회차 저장",
         status_code=201,
         description="회차를 저장합니다.")
async def set_season(auth: dict = Depends(auth),
                     updated_season: int = Query(...), title="회차"):
    global season
    season = updated_season
    return {"season": season}


@app.get("/check", status_code=200)
async def checkalive():
    return {"alive": True}
