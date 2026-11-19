-- PostgreSQL 15+ 호환, Neon에서도 사용 가능합니다.
CREATE TABLE IF NOT EXISTS media_assets (
    id BIGSERIAL PRIMARY KEY,
    space_seq BIGINT NOT NULL,
    media_seq BIGINT NOT NULL,
    kind VARCHAR(10) NOT NULL CHECK (kind IN ('audio','video')),
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (space_seq, media_seq)
);

CREATE TABLE IF NOT EXISTS perso_jobs (
    id BIGSERIAL PRIMARY KEY,
    space_seq BIGINT NOT NULL,
    project_seq BIGINT NOT NULL,
    media_seq BIGINT,
    parent_project_seq BIGINT,
    job_type VARCHAR(24) NOT NULL CHECK (job_type IN ('stt','audio-separation','dubbing','lip-sync')),
    title TEXT NOT NULL DEFAULT '',
    status VARCHAR(40) NOT NULL DEFAULT 'Submitted',
    progress NUMERIC(6,2),
    result_json JSONB,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(space_seq, project_seq)
);
CREATE INDEX IF NOT EXISTS ix_jobs_created ON perso_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_jobs_space_status ON perso_jobs(space_seq, status);

CREATE TABLE IF NOT EXISTS operation_events (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    space_seq BIGINT,
    project_seq BIGINT,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
