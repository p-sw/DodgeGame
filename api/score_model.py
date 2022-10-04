from pydantic import BaseModel, Field
from typing import List

class SingleScoreResponseModel(BaseModel):
    student_id: str = Field(None, description="학번")
    time_score: int = Field(None, description="시간 점수")
    action_score: int = Field(None, description="액션 점수")
    overall_score: int = Field(None, description="전체 점수")
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": "10101",
                "time_score": 20000,
                "action_score": 2000,
                "overall_score": 22000
            }
        }

class ScoreListResponseModel(BaseModel):
    scores: List[SingleScoreResponseModel] = Field(None, description="점수 목록")
    
    class Config:
        schema_extra = {
            "example": {
                "scores": [
                    {
                        "student_id": "10101",
                        "time_score": 20000,
                        "action_score": 2000,
                        "overall_score": 22000
                    },
                    {
                        "student_id": "10102",
                        "time_score": 15000,
                        "action_score": 1000,
                        "overall_score": 16000
                    },
                    {
                        "student_id": "10103",
                        "time_score": 10000,
                        "action_score": 0,
                        "overall_score": 10000
                    }
                ]
            }
        }
    
    class Config:
        schema_extra = {
            "example": [
                {
                    "student_id": "10101",
                    "time_score": 20000,
                    "action_score": 2000,
                    "overall_score": 22000
                },
                {
                    "student_id": "10102",
                    "time_score": 21000,
                    "action_score": 0,
                    "overall_score": 21000
                }
            ]
        }