import type { App } from "../app";
import { isMember } from "../guards";
import type { Feature } from "../features";
import type { Message } from "../types";

const TOKEN_KEY = "atrium_token";

export function setupAuth(app: App): Feature {
  function showError(message: string) {
    app.el.authError.textContent = message;
  }

  function finishAuth(message: Message) {
    if (typeof message.token === "string") {
      localStorage.setItem(TOKEN_KEY, message.token);
    }

    if (isMember(message.member)) {
      app.state.me = message.member;
      app.state.saveMember(message.member);
    }

    app.el.authScreen.hidden = true;
    app.el.status.textContent = "online";

    if (!app.state.me?.space) {
      app.send({ type: "space.join", space: app.state.currentSpace || "main" });
    }
  }

  app.el.authLoginForm.onsubmit = event => {
    event.preventDefault();
    showError("");

    app.send({
      type: "auth.login",
      name: app.el.authLoginName.value,
      password: app.el.authLoginPassword.value,
    });
  };

  app.el.authRegisterForm.onsubmit = event => {
    event.preventDefault();
    showError("");

    app.send({
      type: "auth.register",
      name: app.el.authRegisterName.value,
      email: app.el.authRegisterEmail.value,
      password: app.el.authRegisterPassword.value,
    });
  };

  window.setTimeout(() => app.el.authLoginName.focus());

  return {
    handle(message: Message) {
      if (message.type === "server.ready") {
        const token = localStorage.getItem(TOKEN_KEY);
        if (token) app.send({ type: "auth.resume", token });
        return false;
      }

      if (message.type === "identity.required") {
        if (!app.state.hasName()) {
          app.el.authScreen.hidden = false;
          app.el.authLoginName.focus();
        }
        return false;
      }

      if (message.type === "auth.accepted") {
        finishAuth(message);
        return true;
      }

      if (message.type === "auth.rejected") {
        localStorage.removeItem(TOKEN_KEY);
        app.el.authScreen.hidden = false;
        showError(String(message.message ?? "login failed"));
        return true;
      }

      return false;
    },
  };
}
