from __future__ import annotations
from sqlalchemy import delete
from sqlalchemy.orm import Session
from .ai import provider
from .models import AuditEvent, IngestionJob, KnowledgeChunk, KnowledgeDocument, Organization, SystemFlag, Ticket, TicketMessage, User

def reset_demo(db:Session):
    for model in [TicketMessage,KnowledgeChunk,IngestionJob,AuditEvent,SystemFlag,Ticket,KnowledgeDocument,User,Organization]: db.execute(delete(model))
    seed(db)

def seed(db:Session):
    if db.get(Organization,"orbital"): return
    db.add_all([Organization(id="orbital",name="Orbital Systems"),Organization(id="northstar",name="Northstar Labs")])
    users=[("u1","Marina Costa","requester"),("u2","Carlos Mendes","requester"),("u3","Rafael Lima","agent"),("u4","Bianca Reis","agent"),("u5","Juliana Alves","manager"),("u6","Ana Martins","kbadmin"),("u7","Otávio Faria","auditor")]
    db.add_all([User(id=i,org_id="orbital",name=n,role=r) for i,n,r in users])
    t1=Ticket(id="GD-1842",org_id="orbital",subject="VPN desconecta após atualização do cliente",requester_name="Marina Costa",queue="Workplace",priority="Alta",status="Em atendimento",sla_remaining=34,assignee_name="Rafael Lima",category="Acesso remoto",sentiment="Frustrado")
    t1.messages=[TicketMessage(author_name="Marina Costa",kind="customer",body="Depois da atualização 5.8.1, a VPN conecta por cerca de dois minutos e cai. Já reiniciei o notebook e continuo com o mesmo problema."),TicketMessage(author_name="Rafael Lima",kind="agent",body="Recebi o caso. Vou validar a versão do cliente e comparar com os procedimentos aprovados para esse tipo de falha.")]
    db.add_all([t1,Ticket(id="GD-1841",org_id="orbital",subject="Erro 403 no portal financeiro",requester_name="Carlos Mendes",queue="Aplicações",priority="Média",status="Aguardando cliente",sla_remaining=72,assignee_name="Bianca Reis",category="Autorização"),Ticket(id="GD-1839",org_id="orbital",subject="Notebook não recebe políticas de segurança",requester_name="Fernanda Rocha",queue="Workplace",priority="Crítica",status="Em atendimento",sla_remaining=18,assignee_name="Rafael Lima",category="Endpoint"),Ticket(id="GD-1835",org_id="orbital",subject="Solicitação de acesso ao ambiente QA",requester_name="Paulo Souza",queue="IAM",priority="Baixa",status="Resolvido",sla_remaining=100,assignee_name="Bianca Reis",category="Acesso")])
    docs=[("KB-017","VPN: falha após atualização","MD","v3.2","Workplace",98,"A versão 5.8.1 pode manter um perfil legado incompatível. Remova o perfil legado, sincronize a configuração corporativa e reinicie o serviço de VPN."),("RUNBOOK-09","Escalonamento de acesso remoto","PDF","v2.1","Workplace",96,"Após duas tentativas de recuperação sem sucesso, encaminhe para Network Operations com logs e horário das falhas."),("KB-031","Matriz de erros do portal financeiro","DOCX","v1.7","Aplicações",91,"Erros 403 devem validar papel, grupo de autorização e expiração da sessão antes de escalonar."),("POL-004","Política de concessão de acessos","PDF","v4.0","IAM",99,"Acessos a ambientes devem possuir solicitante, justificativa, aprovador e prazo de validade.")]
    for i,title,ft,ver,scope,quality,text in docs:
        d=KnowledgeDocument(id=i,org_id="orbital",title=title,file_type=ft,version=ver,status="Indexado",scope=scope,quality=quality,source_text=text); db.add(d); db.flush()
        db.add(KnowledgeChunk(org_id="orbital",document_id=i,section="§ 1",content=text,embedding=provider().embed(text)))
    db.add(KnowledgeDocument(id="KB-044",org_id="orbital",title="Troubleshooting de políticas endpoint",file_type="MD",version="v1.1",status="Processando",scope="Workplace",quality=0,source_text="Valide sincronização de MDM, identidade do dispositivo e conectividade com o serviço de políticas."))
    db.add(KnowledgeDocument(id="ARCH-12",org_id="orbital",title="Mapa de serviços internos",file_type="PDF",version="v2.4",status="Falha",scope="Infra",quality=0,source_text="Mapa demonstrativo de serviços internos."))
    for action,res,detail in [("AI_DRAFT_REVIEWED","Ticket GD-1842","Resposta gerada com 2 citações · groundedness 94%"),("RETRIEVAL_COMPLETED","Ticket GD-1842","Hybrid search · candidatos fundidos por RRF"),("TICKET_CLASSIFIED","Ticket GD-1842","Acesso remoto · confiança 0.92")]: db.add(AuditEvent(org_id="orbital",actor_name="GroundedDesk",actor_role="system",action=action,resource=res,detail=detail))
    db.commit()
