import { Encoder } from "./encoder";
import type { Message } from "./types";

export class Connection {
  private socket?: WebSocket;
  private encoder = new Encoder();

  constructor(
    private onMessage: (message: Message) => void,
    private onStatus: (status: string) => void,
  ) {}

  connect() {
    const url = `ws://${window.location.hostname}:8787`;
    this.socket = new WebSocket(url);
    this.onStatus("connecting");

    this.socket.addEventListener("open", () => {
      this.onStatus("online");
      this.send({ type: "spaces.list" });
    });

    this.socket.addEventListener("message", event => {
      try {
        this.onMessage(this.encoder.decode(event.data));
      } catch {
        this.onStatus("bad message");
      }
    });

    this.socket.addEventListener("close", () => {
      this.onStatus("offline");
      window.setTimeout(() => this.connect(), 1000);
    });

    this.socket.addEventListener("error", () => this.onStatus("error"));
  }

  send(message: Message) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(this.encoder.encode(message));
    }
  }
}
