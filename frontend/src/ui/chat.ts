import { App } from "../app";

export function setupChat(app: App) {
  app.el.sendButton.onclick = () => {
    if (!app.state.hasName()) return app.needsName();
    if (!app.state.me?.space) return app.addChat("enter a space first");
    if (!app.el.messageInput.value.trim()) return;

    app.send({ type: "message.send", message: app.el.messageInput.value });
    app.el.messageInput.value = "";
  };

  app.el.messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter") app.el.sendButton.click();
  });
}
