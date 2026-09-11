import { App } from "../app";

export function renderMembers(app: App) {
  app.el.members.innerHTML = "";

  for (const member of [...app.state.members.values()].sort((a, b) => a.name.localeCompare(b.name))) {
    const li = document.createElement("li");
    li.textContent = member.name;
    app.el.members.appendChild(li);
  }
}
