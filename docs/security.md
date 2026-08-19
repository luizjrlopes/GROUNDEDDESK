# Security model

- JWT sessions carry user id, role and organization id.
- Every tenant-owned query applies organization scope server-side.
- RBAC is enforced in API dependencies; frontend visibility is only UX.
- Requesters can only see/comment their own tickets.
- AI drafts cannot send messages.
- Knowledge publication/reprocessing is restricted to Admin KB.
- Audit read access is limited to Gestor, Admin KB and Auditor.
- Demo credentials are intentionally passwordless user selectors and must not be interpreted as production authentication.
