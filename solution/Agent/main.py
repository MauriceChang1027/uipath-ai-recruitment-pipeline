from datetime import datetime, timezone
from typing import Annotated, Any, TypedDict, Literal
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from eval import evaluate_candidate
from schemas import Candidate, CandidateAssessment, EvaluationResult
from schemas import DimensionScores
from schemas import InputModel
from schemas import StateModel
from schemas import AgentResponse

from uipath_langchain.chat import UiPathChat


llm = UiPathChat(
    model="anthropic.claude-haiku-4-5-20251001-v1:0",
    temperature=0,
)

async def evaluate_node(state: StateModel) -> StateModel:
    evaluation = await evaluate_candidate(
        candidate=state.candidate,
        llm=llm,
    )

    return StateModel(
        candidate=state.candidate,
        evaluation=evaluation,
    )

def build_response(
        candidate: Candidate,
        evaluation: EvaluationResult,
) -> AgentResponse:
    assessment = evaluation.Assessment
    final_score = evaluation.FinalScore

    # 技术能力和相关工程经验属于核心硬门槛。
    technical_requirements_met = (
            assessment.TechnicalSkills.Score >= 60
            and assessment.RelevantEngineeringExperience.Score >= 70
    )

    # 教育和领导力容易受到简历信息完整度影响。未达到门槛时转人工复核，
    # 避免把“缺少明确证据”直接解释为“不满足岗位要求”。
    supporting_requirements_met = (
            assessment.Education.Score >= 60
            and assessment.LeadershipOwnership.Score >= 60
    )

    if assessment.ExperienceInformationInsufficient:
        fit_status = "needs_review"
        fit_status_label = "需要人工复核"
        meets_minimum_requirements = None

        summary = (
            f"候选人综合匹配分为 {final_score} 分。"
            "由于工作经历或职责信息不足，"
            "暂时无法确认是否满足岗位最低要求，建议人工复核。"
        )

    elif not technical_requirements_met:
        fit_status = "does_not_meet_requirements"
        fit_status_label = "现有资料未满足岗位要求"
        meets_minimum_requirements = False

        summary = (
            f"候选人综合匹配分为 {final_score} 分。"
            "根据当前提供的资料，技术能力或相关工程经验未达到岗位核心门槛。"
        )

    elif not supporting_requirements_met:
        fit_status = "needs_review"
        fit_status_label = "需要人工复核"
        meets_minimum_requirements = None

        summary = (
            f"候选人综合匹配分为 {final_score} 分。"
            "技术核心门槛已经达到，但教育背景或领导力证据未达到自动通过标准，"
            "建议人工复核相关经历和等效实践能力。"
        )

    elif final_score >= 75:
        fit_status = "meets_requirements"
        fit_status_label = "符合岗位要求"
        meets_minimum_requirements = True

        summary = (
            f"候选人综合匹配分为 {final_score} 分，"
            "满足主要岗位要求，建议进入下一轮人工评估。"
        )

    else:
        fit_status = "needs_review"
        fit_status_label = "基本符合，需要人工复核"
        meets_minimum_requirements = True

        summary = (
            f"候选人综合匹配分为 {final_score} 分，"
            "基本满足最低要求，但部分能力证据不足，建议人工复核。"
        )

    return AgentResponse(
        CandidateName=candidate.CandidateName,
        Position="Software Engineer, Product (Singapore)",
        FitStatus=fit_status,
        FitStatusLabel=fit_status_label,
        MeetsMinimumRequirements=meets_minimum_requirements,
        FinalScore=final_score,
        Summary=summary,
        DimensionScores=DimensionScores(
            Education=assessment.Education.Score,
            TechnicalSkills=assessment.TechnicalSkills.Score,
            RelevantEngineeringExperience=(
                assessment.RelevantEngineeringExperience.Score
            ),
            LeadershipOwnership=assessment.LeadershipOwnership.Score,
            EngineeringDepth=assessment.EngineeringDepth.Score,
            AIReadiness=assessment.AIReadiness.Score,
        ),
        MatchedSkills=assessment.MatchedSkills,
        MissingSkills=assessment.MissingSkills,
        ExperienceInformationInsufficient=(
            assessment.ExperienceInformationInsufficient
        ),
        DetailedAssessment=assessment,
    )

async def output_node(state: StateModel) -> AgentResponse:
    if state.evaluation is None:
        raise ValueError("Candidate evaluation was not generated")

    return build_response(
        candidate=state.candidate,
        evaluation=state.evaluation,
    )

builder = StateGraph(
    StateModel,
    input=InputModel,
    output=AgentResponse,
)

builder.add_node("evaluate_candidate", evaluate_node)
builder.add_node("build_response", output_node)

builder.add_edge(START, "evaluate_candidate")
builder.add_edge("evaluate_candidate", "build_response")
builder.add_edge("build_response", END)

graph = builder.compile()
