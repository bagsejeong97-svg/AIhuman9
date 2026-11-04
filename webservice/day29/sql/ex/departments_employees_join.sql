--join(inner join:PK와 FK가 같다는 조건의 조인)
SELECT
    E.ID,
    E.NAME AS EMPLOYEE_NAME,
    D.NAME AS DEPARTMENT_NAME,
    E.SALARY
FROM
    EMPLOYEES AS E -- EMPLOYEES테이블 별칭을 E
    INNER JOIN DEPARTMENTS AS D -- DEPARTMENTS 테이블 별칭을 D로 해서 E와 조인
        --조인 조건 : D.ID(DEPARTMENTS 테이블의 PK)와
        --          E.DEPARTMENT_ID(EMPLOYEES 테이블의 FK)가 같다는 조건
        ON E.DEPARTMENT_ID = D.ID
ORDER BY E.ID





