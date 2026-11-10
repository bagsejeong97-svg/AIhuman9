# make_daily_folder&file.py
# 학습 일차를 입력하면 일차에 필요한 폴더와 파일 생성

from pathlib import Path

SUBJECT_NAME = 'llm' # 과정명

# 폴더 생성 함수
def make_directory(path: Path) -> bool:
    if not path.exists():
        path.mkdir(parents=True)
        return True
    return False

# 파일 생성 함수
def make_file(path: Path) -> bool:
    if not path.exists():
        with path.open(mode='w', encoding='utf-8') as file:
            file.write(f'# {path.name}\n')
            file.write('# 주제:\n')
        return True
    return False

# 메인 실행 함수
def main():
    try:
        subject_path = Path(SUBJECT_NAME) # 과정명 폴더 경로
        if make_directory(subject_path):
            print(f'{subject_path} 과정명 폴더가 생성되었습니다.')
        else:
            print(f'{subject_path} 과정명 폴더가 이미 존재합니다.')

        day_str = input('학습 일차를 입력하세요: ').strip() # 학습 일차 입력

        # 입력값 검증
        if not day_str.isdigit():
            raise ValueError('학습 일차는 숫자로 입력해야 합니다.')

        if int(day_str) <= 0:
            raise ValueError('학습 일차는 1 이상의 숫자여야 합니다.')

        day_path = subject_path / f'day{day_str}' # 학습 일차 폴더 경로

        if make_directory(day_path):
            print(f'day{day_str} 학습 일차 폴더가 생성되었습니다.')
        else:
            print(f'day{day_str} 학습 일차 폴더가 이미 존재합니다.')

        # 파일명에 들어갈 접미사
        suffix_list = ['ex', 'basic', 'application', 'challenge']

        # 파일 생성
        for num, suffix in enumerate(suffix_list, start=1):
            file_name = f'day{day_str}_{suffix}.py' # 파일명
            file_path = day_path / file_name # 파일 경로
            if make_file(file_path):
                print(f'[{num}] {file_path} 파일이 생성되었습니다.')
            else:
                print(f'[{num}] {file_path} 파일이 이미 존재합니다.')

    except ValueError as error:
        print(f'[입력 오류] {error}')
    except OSError as error:
        print(f'[파일 시스템 오류] {error}')
    except Exception as error:
        print(f'[예상하지 못한 오류] {error}')

if __name__ == '__main__':
    main()