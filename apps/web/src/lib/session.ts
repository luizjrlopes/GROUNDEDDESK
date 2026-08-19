import type { User } from "./types";
const KEY="groundeddesk_session";
export type Session={token:string;user:User};
export function getSession():Session|null{if(typeof window==="undefined")return null;try{return JSON.parse(localStorage.getItem(KEY)||"null")}catch{return null}}
export function setSession(s:Session){localStorage.setItem(KEY,JSON.stringify(s))}
export function clearSession(){localStorage.removeItem(KEY)}
