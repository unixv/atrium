import type { Elements } from "./dom";
import type { Message } from "./types";
import { State } from "./state";
import { Connection } from "./connection";

export class App {
  constructor(
    public state: State,
    public el: Elements,
    public connection: Connection,
  ) {}

  send(message: Message) {
    this.connection.send(message);
  }

  needsName() {
    this.addChat("login or register first");
    this.el.authScreen.hidden = false;
    this.el.authLoginName.focus();
  }

  addChat(text: string) {
    this.state.chatLines.push({ text });
    while (this.state.chatLines.length > 7) this.state.chatLines.shift();
    this.el.chatLog.innerHTML = "";

    for (const line of this.state.chatLines) {
      const li = document.createElement("li");
      li.textContent = line.text;
      this.el.chatLog.appendChild(li);
    }
  }
}
