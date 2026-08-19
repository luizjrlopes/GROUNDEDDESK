export type Role="requester"|"agent"|"manager"|"kbadmin"|"auditor";
export type User={id:string;name:string;role:Role;org_id:string};
export type TicketMessage={id:string;author:string;kind:"customer"|"agent";body:string;created_at:string};
export type Ticket={id:string;subject:string;requester:string;queue:string;priority:string;status:string;sla:number;assignee:string;category:string;sentiment:string;created_at:string;messages:TicketMessage[]};
export type KnowledgeDoc={id:string;title:string;type:string;version:string;status:string;scope:string;quality:number;chunks:number;updated_at:string};
