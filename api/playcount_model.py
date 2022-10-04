from pydantic import BaseModel, Field

class PlayCountResponseModel(BaseModel):
    student_id: str = Field(..., description="학번")
    playcount: int = Field(..., description="플레이 횟수")
    
    class Config:
        schema_extra = {
            "student_id": "10101",
            "playcount": 1
        }