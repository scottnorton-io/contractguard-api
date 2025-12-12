-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tenants
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'suspended')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Contracts
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contract_name TEXT NOT NULL,
    party_name TEXT NOT NULL,
    counterparty_name TEXT NOT NULL,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    status TEXT NOT NULL CHECK (status IN ('active', 'expired', 'terminated')),
    classification TEXT NOT NULL DEFAULT 'sensitive',
    document_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL,
    last_modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contracts_tenant ON contracts(tenant_id);
CREATE INDEX idx_contracts_status ON contracts(status) WHERE status = 'active';

-- Contract Clauses
CREATE TABLE contract_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    clause_type TEXT NOT NULL,
    clause_text TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('material_breach', 'minor_breach', 'notice_required')),
    requires_approval BOOLEAN NOT NULL DEFAULT false,
    approval_authority TEXT,
    minimum_notice_days INTEGER,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clauses_contract ON contract_clauses(contract_id);
CREATE INDEX idx_clauses_type ON contract_clauses(clause_type);
CREATE INDEX idx_clauses_embedding ON contract_clauses USING ivfflat (embedding vector_cosine_ops);

-- Compliance Queries (Audit Trail)
CREATE TABLE compliance_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    contract_id UUID NOT NULL REFERENCES contracts(id),
    actor_id UUID NOT NULL,
    query_payload JSONB NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('COMPLIANT', 'BREACH_RISK', 'REQUIRES_APPROVAL')),
    risk_level TEXT CHECK (risk_level IN ('P0', 'P1', 'P2')),
    triggered_clauses JSONB NOT NULL DEFAULT '[]',
    response_payload JSONB NOT NULL,
    query_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_ip INET,
    user_agent TEXT,
    trace_id TEXT NOT NULL
);

CREATE INDEX idx_queries_tenant ON compliance_queries(tenant_id);
CREATE INDEX idx_queries_contract ON compliance_queries(contract_id);
CREATE INDEX idx_queries_timestamp ON compliance_queries(query_timestamp DESC);

-- Precedent Cases
CREATE TABLE precedent_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID REFERENCES contracts(id),
    case_name TEXT NOT NULL,
    outcome TEXT NOT NULL,
    facts_summary TEXT NOT NULL,
    clauses_involved TEXT[] NOT NULL,
    date_occurred DATE NOT NULL,
    public_reference_url TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_precedent_contract ON precedent_cases(contract_id);
CREATE INDEX idx_precedent_embedding ON precedent_cases USING ivfflat (embedding vector_cosine_ops);

-- Audit Events (Immutable)
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    actor_id UUID NOT NULL,
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    result TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_ip INET,
    trace_id TEXT NOT NULL
);

CREATE INDEX idx_audit_tenant ON audit_events(tenant_id);
CREATE INDEX idx_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX idx_audit_actor ON audit_events(actor_id);
