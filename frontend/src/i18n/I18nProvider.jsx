import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { COMPLIANT_API } from "../config.js";

const I18nContext = createContext(null);

const FALLBACK = {
  ui: { app_title: "EU AI Act compliant AI stack — side-by-side demo" },
};

export function I18nProvider({ children, defaultLocale = "en" }) {
  const [locale, setLocale] = useState(defaultLocale);
  const [supported, setSupported] = useState([defaultLocale]);
  const [dict, setDict] = useState(FALLBACK);
  const [loading, setLoading] = useState(true);

  // List of supported locales on first load.
  useEffect(() => {
    let alive = true;
    fetch(`${COMPLIANT_API}/i18n/locales`)
      .then((r) => r.json())
      .then((d) => {
        if (alive) setSupported(d.supported || [defaultLocale]);
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, [defaultLocale]);

  // Whenever locale changes, fetch its dictionary.
  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetch(`${COMPLIANT_API}/i18n/locales/${locale}`)
      .then((r) => r.json())
      .then((d) => {
        if (alive) {
          setDict(d || FALLBACK);
          setLoading(false);
        }
      })
      .catch(() => {
        if (alive) {
          setDict(FALLBACK);
          setLoading(false);
        }
      });
    return () => {
      alive = false;
    };
  }, [locale]);

  const t = useMemo(() => {
    return (key, fallback) => {
      const parts = key.split(".");
      let cur = dict;
      for (const p of parts) {
        if (cur == null || typeof cur !== "object" || !(p in cur)) {
          return fallback ?? key;
        }
        cur = cur[p];
      }
      return typeof cur === "string" ? cur : fallback ?? key;
    };
  }, [dict]);

  const value = useMemo(
    () => ({ locale, setLocale, supported, t, loading }),
    [locale, supported, t, loading]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx)
    throw new Error("useI18n must be used inside an <I18nProvider>");
  return ctx;
}
