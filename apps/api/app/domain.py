from __future__ import annotations

ROLE_PERMISSIONS = {
    "requester": {"dashboard:read", "tickets:own", "tickets:create", "tickets:comment"},
    "agent": {"dashboard:read", "tickets:read", "tickets:create", "tickets:reply", "tickets:transition", "knowledge:read", "search:read", "ai:use"},
    "manager": {"dashboard:read", "tickets:read", "tickets:create", "tickets:reply", "tickets:transition", "knowledge:read", "search:read", "audit:read", "ai:use"},
    "kbadmin": {"dashboard:read", "knowledge:read", "knowledge:write", "knowledge:reprocess", "search:read", "audit:read"},
    "auditor": {"dashboard:read", "audit:read"},
}

TICKET_TRANSITIONS = {
    "Aberto": {"Em atendimento", "Aguardando cliente"},
    "Em atendimento": {"Aguardando cliente", "Resolvido"},
    "Aguardando cliente": {"Em atendimento", "Resolvido"},
    "Resolvido": {"Fechado", "Em atendimento"},
    "Fechado": set(),
}

def can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())

def can_transition(current: str, target: str) -> bool:
    return target in TICKET_TRANSITIONS.get(current, set())

def reciprocal_rank_fusion(lexical_rank: int | None, vector_rank: int | None, k: int = 60) -> float:
    score = 0.0
    if lexical_rank is not None:
        score += 1.0 / (k + lexical_rank)
    if vector_rank is not None:
        score += 1.0 / (k + vector_rank)
    return score
