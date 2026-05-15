import React from "react";
import { useI18n } from "./I18nProvider.jsx";

const NAMES = {
  en: "English",
  de: "Deutsch",
  fr: "Français",
  es: "Español",
  it: "Italiano",
  nl: "Nederlands",
  pl: "Polski",
  sv: "Svenska",
};

export default function LanguageSwitcher() {
  const { locale, setLocale, supported, t } = useI18n();
  return (
    <div className="lang-switcher">
      <label>{t("ui.language", "Language")}</label>
      <select value={locale} onChange={(e) => setLocale(e.target.value)}>
        {supported.map((l) => (
          <option key={l} value={l}>
            {NAMES[l] || l}
          </option>
        ))}
      </select>
    </div>
  );
}
