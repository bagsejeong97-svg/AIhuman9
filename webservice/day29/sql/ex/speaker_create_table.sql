--테이블 생성 SQL
CREATE TABLE IF NOT EXISTS SPEAKERS(
    ID SERIAL PRIMARY KEY, -- 자동증가값, 주키
    NAME VARCHAR(50) NOT NULL, -- 널 불허
    LANGUAGE VARCHAR(20) NOT NULL, -- 널 불허
    SAMPLE_COUNT INTEGER NOT NULL DEFAULT 0 -- 널 불허, 기본값 0
)














































