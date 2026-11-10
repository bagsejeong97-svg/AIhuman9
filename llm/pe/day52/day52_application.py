# day52_application.py
# 주제:  채용공고 기술 스택 태킹 프롬프트 설계

from util.print_util import pp

POSTINGS = [
    "Python과 Pandas로 데이터 분석 서비스를 개발합니다.",
    "PostgreSQL 쿼리 작성과 Docker 배포 경험이 필요합니다.",
    "AWS 인프라 및 Kubernetes 운영을 담당합니다.",
]

EXAMPLES = [
    ("Python 자동화 개발", "Python"),
    ("SQL 기반 데이터 조회", "SQL"),
    ("Docker 이미지 배포", "Docker"),
    ("AWS 클라우드 서비스", "AWS"),
]

# 프롬프트 생성 함수
# text: 채용공고
# strategy : zero 또는 few 선택
def make_prompt(text,strategy):
    if strategy not in ('zero','few'):
        raise ValueError('strategy는 zero 또는 few이어야 합니다.')

    lines = [
        '채용공고의 요구 기술을  추출하세요.',
        '허용 태그 : Python, SQL, Docker, AWS, 기타',
        '복수 태그는 쉼표로 구분하고 중복은 제거하세요.',
        '예시에 없는 기술만 나타나면 기타를 사용하세요.'
    ]
    if strategy == 'few': # few - shot
        for source, tag in EXAMPLES:
            lines.append(f'예시: {source} => {tag}')
    lines.append(f'<공고>{text}</공고>\n결과:')
    return '\n'.join(lines) # 줄바꿈이 포함된 전체 한 문장으로 리턴

def main():
    for strategy in ('zero','few'):
        for text in POSTINGS:
            pp(f'[{strategy}] \n{make_prompt(text,strategy)}\n')

if __name__ == '__main__':
    main()
























































