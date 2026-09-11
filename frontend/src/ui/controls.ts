import { App } from "../app";

export function updateControls(app: App) {
  const named = app.state.hasName();
  const inSpace = Boolean(app.state.me?.space);

  app.el.spaceInput.disabled = !named;
  app.el.spaceDescriptionInput.disabled = !named;
  app.el.spaceLayout.disabled = !named || app.state.availableLayouts.length === 0;
  app.el.createSpaceButton.disabled = !named;
  app.el.messageInput.disabled = !named || !inSpace;
  app.el.sendButton.disabled = !named || !inSpace;

  app.el.messageInput.placeholder = !named ? "login first" : !inSpace ? "enter a space" : "message";
}
