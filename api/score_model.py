from pydantic import BaseModel
from fastapi import Field

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