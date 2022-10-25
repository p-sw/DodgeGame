from pydantic import BaseModel, Field
from typing import List, Optional


class SingleScoreResponseModel(BaseModel):
    id: int = Field(None, description="학번")
    season: int = Field(None, description="회차")
    time: int = Field(None, description="시간 점수")
    action: int = Field(None, description="액션 점수")
    score: int = Field(None, description="전체 점수")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "10101",
                "season": 1,
                "time": 20000,
                "action": 2000,
                "score": 22000
            }
        }


class ScoreListResponseModel(BaseModel):
    scores: List[Optional[SingleScoreResponseModel]] = Field(None, description="점수 목록")
    
    class Config:
        schema_extra = {
            "example": {
                "scores": [
                    {
                        "id": "10101",
                        "season": 1,
                        "time": 20000,
                        "action": 2000,
                        "score": 22000
                    },
                    {
                        "id": "10102",
                        "season": 1,
                        "time": 20000,
                        "action": 2000,
                        "score": 22000
                    },
                    {
                        "id": "10103",
                        "season": 1,
                        "time": 20000,
                        "action": 2000,
                        "score": 22000
                    }
                ]
            }
        }