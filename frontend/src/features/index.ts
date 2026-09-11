import { App } from "../app";
import type { Message } from "../types";
import { setupAuth } from "../ui/auth";
import { setupCharacterEditor } from "./characterEditor";
import { setupInventory } from "./inventory";

export type Feature = {
  refresh?: () => void;
  handle?: (message: Message) => boolean;
};

export function setupFeatures(app: App): Feature[] {
  return [
    setupAuth(app),
    setupCharacterEditor(app),
    setupInventory(app),
  ];
}
