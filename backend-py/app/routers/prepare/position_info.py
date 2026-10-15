from fastapi import APIRouter, HTTPException, Form
from app.database.mysql import execute_query

router = APIRouter()

@router.post("/position_info")
def get_position_info(
    domain_name: str = Form(...),
    position_name: str = Form(...)
):
    # 1. 查找领域ID
    domain_result = execute_query(
        "SELECT domain_id FROM domains WHERE domain_name=%s", (domain_name,)
    )
    if not domain_result:
        raise HTTPException(status_code=404, detail="未找到该领域")
    domain_id = domain_result[0]["domain_id"]

    # 2. 查找岗位ID
    position_result = execute_query(
        "SELECT position_id FROM positions WHERE position_name=%s AND domain_id=%s", (position_name, domain_id)
    )
    if not position_result:
        raise HTTPException(status_code=404, detail="未找到该岗位")
    position_id = position_result[0]["position_id"]

    # 3. 查 core_competences
    core_competences = execute_query(
        "SELECT competence_id, competence_name, competence_description FROM core_competences WHERE position_id=%s", (position_id,)
    )

    # 4. 查 terms
    terms = execute_query(
        "SELECT term_id, term_name, term_explanation, frequency FROM terms WHERE position_id=%s", (position_id,)
    )

    # 5. 查 high_freq_questions
    high_freq_questions = execute_query(
        "SELECT question_type_id, question_type_name, question_example, scoring_focus, answer_template FROM high_freq_questions WHERE position_id=%s", (position_id,)
    )

    return {
        "core_competences": core_competences,
        "terms": terms,
        "high_freq_questions": high_freq_questions
    } 