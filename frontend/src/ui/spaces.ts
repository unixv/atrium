import { App } from "../app";

function renderLayouts(app: App) {
  const current = app.el.spaceLayout.value;
  app.el.spaceLayout.innerHTML = "";

  for (const layout of app.state.availableLayouts) {
    const option = document.createElement("option");
    option.value = layout.id;
    const size = layout.width && layout.height ? ` ${layout.width}x${layout.height}` : "";
    option.textContent = `${layout.name}${size}`;
    app.el.spaceLayout.appendChild(option);
  }

  if (current && [...app.el.spaceLayout.options].some(option => option.value === current)) app.el.spaceLayout.value = current;
}

function renderCurrentSpace(app: App) {
  const space = app.state.currentSpaceInfo;
  app.el.currentSpaceName.textContent = space?.name ?? "Main";
  app.el.currentSpaceOwner.textContent = space?.owner ? `owned by ${space.owner}` : "";
  app.el.currentSpaceDescription.textContent = space?.description ?? "";
}

export function renderSpaces(app: App) {
  renderLayouts(app);
  renderCurrentSpace(app);
  app.el.spaces.innerHTML = "";

  for (const space of app.state.spaces) {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.className = space.id === app.state.currentSpace ? "active" : "";
    button.disabled = !app.state.hasName();
    button.onclick = () => app.state.hasName() ? app.send({ type: "space.join", space: space.id }) : app.needsName();

    const title = document.createElement("strong");
    title.textContent = space.name;
    const meta = document.createElement("span");
    meta.textContent = `${space.members} online`;
    button.append(title, meta);

    li.appendChild(button);
    app.el.spaces.appendChild(li);
  }
}

export function setupSpaces(app: App) {
  app.el.roomDrawerToggle.onclick = () => {
    const open = app.el.gameShell.classList.toggle("rooms-open");
    app.el.roomDrawerToggle.textContent = open ? "close" : "spaces";
  };

  app.el.createSpaceButton.onclick = () => {
    if (!app.state.hasName()) return app.needsName();
    if (!app.el.spaceInput.value.trim()) return;
    const layoutId = app.el.spaceLayout.value || app.state.availableLayouts[0]?.id;
    app.send({
      type: "space.create",
      space: app.el.spaceInput.value,
      description: app.el.spaceDescriptionInput.value,
      layout_id: layoutId,
    });
    app.el.spaceInput.value = "";
    app.el.spaceDescriptionInput.value = "";
  };

  app.el.spaceInput.addEventListener("keydown", event => { if (event.key === "Enter") app.el.createSpaceButton.click(); });
  app.el.spaceDescriptionInput.addEventListener("keydown", event => { if (event.key === "Enter") app.el.createSpaceButton.click(); });
}
