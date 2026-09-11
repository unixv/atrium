import type { Message } from "./types";

export class Encoder {
  encode(message: Message): string {
    const bytes = new TextEncoder().encode(JSON.stringify(message));
    let binary = "";
    for (const byte of bytes) binary += String.fromCharCode(byte);
    return btoa(binary);
  }

  decode(data: string): Message {
    const binary = atob(data);
    const bytes = Uint8Array.from(binary, char => char.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes)) as Message;
  }
}
