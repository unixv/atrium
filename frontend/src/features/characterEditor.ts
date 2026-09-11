import { App } from "../app";
import type { Avatar, Message } from "../types";
import { isMember } from "../guards";
import { drawAvatarPreview } from "../game/characterSprite";

const DEFAULT_AVATAR: Required<Avatar> = {
  avatar_preset: "spiky_red",
  skin_color: "#b8754c",
  hair_style: "short",
  hair_color: "#211513",
  shirt_style: "tee",
  shirt_color: "#4d8fd6",
  pants_style: "straight",
  pants_color: "#263247",
  shoe_style: "sneakers",
  shoe_color: "#111722",
};

const OPTIONS = {
  avatarPreset: [
    ["spiky_red", "classic"],
    ["pony_black", "slim"],
    ["messy_blue", "casual"],
    ["mohawk_skull", "sharp"],
    ["hood_green", "relaxed"],
    ["blonde_pink", "soft"],
    ["curly_coat", "broad"],
    ["blue_bob", "compact"],
  ],
  hairStyle: [["short", "short"], ["side_part", "side part"], ["curly", "curly"], ["spiky", "spiky"], ["bob", "bob"], ["buzz", "buzz"]],
  shirtStyle: [["tee", "tee"], ["jacket", "jacket"], ["hoodie", "hoodie"], ["stripe", "striped"]],
  pantsStyle: [["straight", "straight"], ["cuffed", "cuffed"], ["shorts", "shorts"]],
  shoeStyle: [["sneakers", "sneakers"], ["boots", "boots"], ["loafers", "loafers"]],
};

function avatar(value?: Avatar): Required<Avatar> {
  return { ...DEFAULT_AVATAR, ...(value ?? {}) };
}

function fillSelect(select: HTMLSelectElement, values: string[] | string[][]) {
  select.innerHTML = "";
  for (const value of values) {
    const option = document.createElement("option");
    if (Array.isArray(value)) {
      option.value = value[0];
      option.textContent = value[1];
    } else {
      option.value = value;
      option.textContent = value.replace(/_/g, " ");
    }
    select.appendChild(option);
  }
}

function formAvatar(app: App): Required<Avatar> {
  return {
    avatar_preset: app.el.avatarPreset.value,
    skin_color: app.el.avatarSkinColor.value,
    hair_style: app.el.avatarHairStyle.value,
    hair_color: app.el.avatarHairColor.value,
    shirt_style: app.el.avatarShirtStyle.value,
    shirt_color: app.el.avatarShirtColor.value,
    pants_style: app.el.avatarPantsStyle.value,
    pants_color: app.el.avatarPantsColor.value,
    shoe_style: app.el.avatarShoeStyle.value,
    shoe_color: app.el.avatarShoeColor.value,
  };
}

export function setupCharacterEditor(app: App) {
  fillSelect(app.el.avatarPreset, OPTIONS.avatarPreset);
  fillSelect(app.el.avatarHairStyle, OPTIONS.hairStyle);
  fillSelect(app.el.avatarShirtStyle, OPTIONS.shirtStyle);
  fillSelect(app.el.avatarPantsStyle, OPTIONS.pantsStyle);
  fillSelect(app.el.avatarShoeStyle, OPTIONS.shoeStyle);

  const wrap = document.createElement("div");
  wrap.className = "character-summary";

  const preview = document.createElement("canvas");
  preview.className = "character-panel-preview";
  preview.width = 86;
  preview.height = 112;

  const details = document.createElement("div");
  details.className = "character-details";
  const name = document.createElement("div");
  name.className = "character-name";
  const presetName = document.createElement("div");
  presetName.className = "character-preset-name";
  details.append(name, presetName);

  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "edit look";

  wrap.append(preview, details, button);
  app.el.avatarControls.appendChild(wrap);

  function openEditor() {
    if (!app.state.hasName()) return app.needsName();
    const a = avatar(app.state.me?.avatar);
    app.el.avatarPreset.value = a.avatar_preset;
    app.el.avatarSkinColor.value = a.skin_color;
    app.el.avatarHairStyle.value = a.hair_style;
    app.el.avatarHairColor.value = a.hair_color;
    app.el.avatarShirtStyle.value = a.shirt_style;
    app.el.avatarShirtColor.value = a.shirt_color;
    app.el.avatarPantsStyle.value = a.pants_style;
    app.el.avatarPantsColor.value = a.pants_color;
    app.el.avatarShoeStyle.value = a.shoe_style;
    app.el.avatarShoeColor.value = a.shoe_color;
    app.el.avatarEditor.hidden = false;
    drawAvatarPreview(app.el.avatarPreview, formAvatar(app));
  }

  function closeEditor() { app.el.avatarEditor.hidden = true; }

  button.onclick = openEditor;
  app.el.avatarEditorClose.onclick = closeEditor;
  app.el.avatarEditor.addEventListener("click", event => { if (event.target === app.el.avatarEditor) closeEditor(); });

  const previewInputs = [
    app.el.avatarPreset,
    app.el.avatarSkinColor, app.el.avatarHairStyle, app.el.avatarHairColor,
    app.el.avatarShirtStyle, app.el.avatarShirtColor, app.el.avatarPantsStyle,
    app.el.avatarPantsColor, app.el.avatarShoeStyle, app.el.avatarShoeColor,
  ];
  for (const input of previewInputs) {
    input.addEventListener("input", () => drawAvatarPreview(app.el.avatarPreview, formAvatar(app)));
    input.addEventListener("change", () => drawAvatarPreview(app.el.avatarPreview, formAvatar(app)));
  }

  app.el.avatarEditorForm.onsubmit = event => {
    event.preventDefault();
    if (!app.state.hasName()) return app.needsName();
    app.send({ type: "avatar.update", avatar: formAvatar(app) });
    closeEditor();
  };

  return {
    refresh() {
      const named = app.state.hasName();
      const a = avatar(app.state.me?.avatar);
      name.textContent = app.state.me?.name || "not signed in";
      const label = OPTIONS.avatarPreset.find(([id]) => id === a.avatar_preset)?.[1] ?? "custom";
      presetName.textContent = `${label} · ${a.hair_style.replace(/_/g, " ")} · ${a.shirt_style}`;
      drawAvatarPreview(preview, a);
      button.disabled = !named;
      if (!app.el.avatarEditor.hidden) drawAvatarPreview(app.el.avatarPreview, formAvatar(app));
    },

    handle(message: Message) {
      if (message.type !== "avatar.updated" && message.type !== "avatar.hair_color_updated") return false;
      if (!isMember(message.member)) return true;
      app.state.saveMember(message.member);
      if (app.state.me?.id === message.member.id) app.state.me = message.member;
      this.refresh();
      return true;
    },
  };
}
