import "./styles.css";
import { App } from "./app";
import { Connection } from "./connection";
import { getElements } from "./dom";
import { handleMessage } from "./events";
import { setupFeatures } from "./features";
import { RoomRenderer } from "./game/roomRenderer";
import { setupMovement } from "./game/movement";
import { State } from "./state";
import { setupChat } from "./ui/chat";
import { updateControls } from "./ui/controls";
import { setupSpaces } from "./ui/spaces";

const state = new State();
const el = getElements();
let app: App;
let features = [] as ReturnType<typeof setupFeatures>;

const connection = new Connection(
  message => handleMessage(app, features, message),
  status => { el.status.textContent = status; },
);

app = new App(state, el, connection);
features = setupFeatures(app);

setupSpaces(app);
setupChat(app);

const renderer = new RoomRenderer(el.canvas, state);
setupMovement(app, renderer);
renderer.start();

updateControls(app);
for (const feature of features) feature.refresh?.();
connection.connect();
