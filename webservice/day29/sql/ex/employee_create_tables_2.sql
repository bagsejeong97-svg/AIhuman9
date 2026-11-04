-- 직원 테이블
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY, -- 직원 아이디
    name VARCHAR(50) NOT NULL, -- 직원명
    department_id INTEGER NOT NULL, -- 부서 아이디(FK)
    salary INTEGER NOT NULL, -- 월급
    -- EMPLOYEES 테이블의 DEPARTMENT_ID 컬럼의 값은 DEPARTMENTS 테이블의 ID 컬럼의 값을 참조
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
