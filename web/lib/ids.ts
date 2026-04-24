import crypto from "node:crypto";

export function randomCode(bytes = 6): string {
  return crypto.randomBytes(bytes).toString("base64url").toUpperCase();
}

export function randomToken(bytes = 24): string {
  return crypto.randomBytes(bytes).toString("base64url");
}
