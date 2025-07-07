import autogen
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

llm_config = {
    "model": AZURE_OPENAI_DEPLOYMENT,  # Azure에서 배포한 모델명
    "api_type": "azure",
    "api_key": AZURE_OPENAI_API_KEY,
    "base_url": AZURE_OPENAI_ENDPOINT,
    "api_version": AZURE_OPENAI_API_VERSION,
    "temperature": 0.3,
    "max_tokens": 1024,
}

def generate_study_plan(topic: str):
    prompt = f"""
    '{topic}' 전문가가 되기 위해 필요한 학습 카테고리를 3~5개로 나누고,
    각 카테고리별로 세부 학습 내용(2~4개)과 공식 문서/추천 링크를 순서대로 정리해줘.
    마지막엔 각 카테고리별로 1~2문제의 퀴즈(문제와 정답)를 만들어줘.
    아래와 같은 JSON 포맷으로 답변해줘.
    {{
      "categories": [
        {{
          "name": "카테고리명",
          "details": ["세부내용1", ...],
          "links": ["링크1", ...],
          "quizzes": [{{"question": "문제", "answer": "정답"}}, ...]
        }}, ...
      ]
    }}
    """
    response = autogen.Completion.create(
        prompt=prompt,
        **llm_config
    )
    return response["choices"][0]["text"]
