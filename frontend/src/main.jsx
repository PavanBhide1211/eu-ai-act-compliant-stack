import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { I18nProvider } from "./i18n/I18nProvider.jsx";

const browserLocale = (
  navigator.language || navigator.userLanguage || "en"
)
  .toLowerCase()
  .split("-")[0];

createRoot(document.getElementById("root")).render(
  <I18nProvider defaultLocale={browserLocale}>
    <App />
  </I18nProvider>
);
