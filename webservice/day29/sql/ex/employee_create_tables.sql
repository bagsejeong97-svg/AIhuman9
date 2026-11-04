CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY, --부서앙디, 자동증가번호, 주키
    name VARCHAR(50) NOT NULL UNIQUE--부서명,널 불허, 유일값
);
