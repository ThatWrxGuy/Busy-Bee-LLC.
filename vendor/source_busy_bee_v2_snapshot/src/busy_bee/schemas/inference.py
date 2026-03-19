from pydantic import BaseModel, Field


class CustomerFeatures(BaseModel):
    age: int = Field(ge=18, le=120)
    monthly_spend: float = Field(ge=0)
    tenure_months: int = Field(ge=0)
    contract_type: str
    support_calls: int = Field(ge=0)
