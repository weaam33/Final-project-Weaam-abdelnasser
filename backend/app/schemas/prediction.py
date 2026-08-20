from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    location: str = Field(..., examples=["Mumbai Sector 10"])
    bhk: int = Field(..., ge=1, le=10, examples=[2], description="Number of bedrooms (BHK)")
    carpet_area_sqft: float = Field(..., gt=0, examples=[1200.0])
    floor_num: int = Field(..., ge=-1, examples=[3])
    bathroom: int = Field(..., ge=0, examples=[2])
    balcony: int = Field(..., ge=0, examples=[1])
    car_parking: int = Field(0, ge=0, examples=[1])
    furnishing: str = Field(..., examples=["Semi-Furnished"])  # Furnished | Semi-Furnished | Unfurnished
    transaction: str = Field(..., examples=["Resale"])  # New Property | Resale
    ownership: str = Field(..., examples=["Freehold"])
    facing: str = Field(..., examples=["East"])


class PredictionResponse(BaseModel):
    predicted_price: float


class HealthResponse(BaseModel):
    status: str
