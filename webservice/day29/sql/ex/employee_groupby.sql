-- 부서별 평균 연봉이 4800이상인 부서를 조회
SELECT
    DEPARTMENT_ID, --부서아이디
    -- 그룹핑된 각 부서의 직원 수를 EMPLOYEE_COUNT 별칭으로
    COUNT(*) AS EMPLOYEE_COUNT,
    --전체 행의 수를 EMPLOYEE_COUNT 별칭으로
    ROUND(AVG(SALARY),0) AVG_SALARY
    -- 부서별 평균 연봉을 정수만 표시해서 AVG_SALARY 별칭으로
FROM
    EMPLOYEES
GROUP BY
    DEPARTMENT_ID -- 부서 아이디가 같은 행들을 그룹핑
HAVING
    AVG(SALARY) >= %s -- 각 그룹에 조건을 부여, 평균 연봉이 보내준 평균 연봉 이상인 그룹
ORDER BY
    AVG(SALARY) DESC -- 평균 연봉 내림차순 정렬







