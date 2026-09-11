import { App } from "../app";
import { isCatalogItem, isRoomItem } from "../guards";
import type { CatalogItem, Message } from "../types";

function ensureSelection(app: App) {
  if (!app.state.selectedItemId || !app.state.catalog.some(item => item.id === app.state.selectedItemId)) {
    app.state.selectedItemId = app.state.catalog[0]?.id ?? null;
  }
}

export function renderInventory(app: App) {
  ensureSelection(app);

  app.el.buildModeOpen.disabled = !app.state.canBuild;
  app.el.buildModeOpen.textContent = app.state.buildMode ? "design on" : "design";
  app.el.buildModeOpen.className = app.state.buildMode ? "top-button active" : "top-button";

  app.el.buildTray.hidden = !app.state.buildMode;
  app.el.buildRemoveToggle.disabled = !app.state.canBuild || !app.state.buildMode;
  app.el.buildClear.disabled = !app.state.canBuild || !app.state.buildMode || app.state.items.length === 0;
  app.el.buildRemoveToggle.className = app.state.buildRemoveMode ? "active" : "";
  app.el.buildRemoveToggle.textContent = app.state.buildRemoveMode ? "removing" : "remove";
  app.el.buildToggle.textContent = "done";
  app.el.buildHint.textContent = app.state.buildRemoveMode
    ? "click an item to remove it"
    : "pick a prop, then click an open tile";

  const groups = new Map<string, CatalogItem[]>();
  for (const item of app.state.catalog) {
    const category = item.category || "Props";
    const current = groups.get(category) ?? [];
    current.push(item);
    groups.set(category, current);
  }

  app.el.itemCatalog.innerHTML = "";
  for (const [category, items] of groups) {
    const section = document.createElement("li");
    section.className = "catalog-section";

    const title = document.createElement("div");
    title.className = "catalog-section-title";
    title.textContent = category;

    const grid = document.createElement("div");
    grid.className = "catalog-section-items";

    for (const item of items) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = app.state.selectedItemId === item.id && !app.state.buildRemoveMode ? "active item-choice" : "item-choice";
      button.disabled = !app.state.canBuild;
      button.title = `${item.name} (${item.width}×${item.height})`;

      const imgWrap = document.createElement("span");
      imgWrap.className = "item-thumb";
      const img = document.createElement("img");
      img.src = item.sprite;
      img.alt = "";
      imgWrap.appendChild(img);

      const label = document.createElement("span");
      label.className = "item-label";
      label.textContent = item.name;

      const size = document.createElement("small");
      size.textContent = `${item.width}×${item.height}`;

      button.append(imgWrap, label, size);
      button.onclick = () => {
        app.state.selectedItemId = item.id;
        app.state.buildRemoveMode = false;
        app.state.buildMode = true;
        renderInventory(app);
      };

      grid.appendChild(button);
    }

    section.append(title, grid);
    app.el.itemCatalog.appendChild(section);
  }
}

export function setupInventory(app: App) {
  app.el.buildModeOpen.onclick = () => {
    if (!app.state.canBuild) return;
    app.state.buildMode = true;
    app.state.buildRemoveMode = false;
    ensureSelection(app);
    renderInventory(app);
  };

  app.el.buildToggle.onclick = () => {
    app.state.buildMode = false;
    app.state.buildRemoveMode = false;
    renderInventory(app);
  };

  app.el.buildRemoveToggle.onclick = () => {
    if (!app.state.canBuild || !app.state.buildMode) return;
    app.state.buildRemoveMode = !app.state.buildRemoveMode;
    renderInventory(app);
  };

  app.el.buildClear.onclick = () => {
    if (!app.state.canBuild || !app.state.buildMode || app.state.items.length === 0) return;
    if (window.confirm("Clear all items from this space?")) app.send({ type: "items.clear" });
  };

  window.addEventListener("keydown", event => {
    if (event.key === "Escape" && app.state.buildMode) {
      app.state.buildMode = false;
      app.state.buildRemoveMode = false;
      renderInventory(app);
    }
  });

  return {
    refresh() { renderInventory(app); },
    handle(message: Message) {
      if (message.type === "inventory.list") {
        if (Array.isArray(message.catalog)) app.state.catalog = message.catalog.filter(isCatalogItem);
        if (Array.isArray(message.items)) app.state.items = message.items.filter(isRoomItem);
        app.state.canBuild = message.can_build === true;
        if (!app.state.canBuild) {
          app.state.buildMode = false;
          app.state.buildRemoveMode = false;
        }
        ensureSelection(app);
        renderInventory(app);
        return true;
      }

      if (message.type === "item.placed") {
        const placed = message.item;
        if (!isRoomItem(placed)) return true;
        app.state.items = app.state.items.filter(item => item.id !== placed.id);
        app.state.items.push(placed);
        renderInventory(app);
        return true;
      }

      if (message.type === "item.removed" && typeof message.id === "string") {
        app.state.items = app.state.items.filter(item => item.id !== message.id);
        renderInventory(app);
        return true;
      }

      if (message.type === "items.cleared") {
        app.state.items = [];
        renderInventory(app);
        return true;
      }

      return false;
    },
  };
}
