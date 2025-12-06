from sqlmodel import SQLModel, Field


class Medication(SQLModel, table=True):
    __tablename__ = "medications"

    medicationId: str = Field(primary_key=True, index=True)

    name: str
    formula: str
    producer: str
    dosage: str
    baseUnit: str
    restrictionLevel: int
    chemicalStabilityHours: int


class MedicationCreate(SQLModel):
    medicationId: str
    name: str
    formula: str
    producer: str
    dosage: str
    baseUnit: str
    restrictionLevel: int
    chemicalStabilityHours: int


MEDICATION_EXAMPLE = {
    "medicationId": "relaxant-001",
    "name": "Midazolam",
    "formula": "Solution",
    "producer": "Fresenius",
    "dosage": "5 mg/ml",
    "baseUnit": "mL",
    "restrictionLevel": 2,
    "chemicalStabilityHours": 48
}