from typing import Literal, Annotated, Any

from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    Company: str
    Title: str
    Duration: str

class Candidate(BaseModel):
    CandidateName: str
    Education: str
    TechSkills: str
    WorkExperience: list[WorkExperience]

class DimensionScores(BaseModel):
    Education: int = Field(ge=0, le=100)
    TechnicalSkills: int = Field(ge=0, le=100)
    RelevantEngineeringExperience: int = Field(ge=0, le=100)
    LeadershipOwnership: int = Field(ge=0, le=100)
    EngineeringDepth: int = Field(ge=0, le=100)
    AIReadiness: int = Field(ge=0, le=100)


class DimensionScore(BaseModel):
    Score: int = Field(ge=0, le=100)
    Evidence: list[str]
    MissingEvidence: list[str]
    Confidence: Literal["high", "medium", "low"]


class CandidateAssessment(BaseModel):
    Education: DimensionScore
    TechnicalSkills: DimensionScore
    RelevantEngineeringExperience: DimensionScore
    LeadershipOwnership: DimensionScore
    EngineeringDepth: DimensionScore
    AIReadiness: DimensionScore

    MatchedSkills: list[str]
    MissingSkills: list[str]

    ExperienceInformationInsufficient: bool

class InputModel(BaseModel):
    candidate: Candidate


class AgentResponse(BaseModel):
    CandidateName: str
    Position: str

    FitStatus: Literal[
        "meets_requirements",
        "needs_review",
        "does_not_meet_requirements",
    ]

    FitStatusLabel: str

    # 信息不足时返回 None
    MeetsMinimumRequirements: bool | None

    FinalScore: int = Field(ge=0, le=100)

    Summary: str

    DimensionScores: DimensionScores

    MatchedSkills: list[str]
    MissingSkills: list[str]

    ExperienceInformationInsufficient: bool

    DetailedAssessment: CandidateAssessment


class EvaluationResult(BaseModel):
    Assessment: CandidateAssessment
    FinalScore: int = Field(ge=0, le=100)


class StateModel(BaseModel):
    candidate: Candidate
    evaluation: EvaluationResult | None = None
