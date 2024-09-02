import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useState } from 'react';

type Locale = 'en' | 'ru';

interface CustomizationState {
  locale: Locale;
}
interface Customization extends CustomizationState {
  setLocale: (locale: Locale) => void;
}
const DEFAULT_LOCALE: Locale = 'ru';
const CustomizationContext = createContext<Customization>({
  locale: DEFAULT_LOCALE,
  setLocale() {
    throw new Error('Not initialized');
  },
});

export const CustomizationProvider = ({ children }: { children: ReactNode }) => {
  const [customization, setCustomization] = useState<CustomizationState>({
    locale: DEFAULT_LOCALE,
  });
  const setLocale = useCallback((locale: Locale): void => {
    setCustomization((c) => ({ ...c, locale }));
  }, []);
  return (
    <CustomizationContext.Provider value={{ ...customization, setLocale }}>
      {children}
    </CustomizationContext.Provider>
  );
};

export default function useCustomization(): Customization {
  const context = useContext(CustomizationContext);
  if (!context) throw new Error('context must be use inside provider');
  return context;
}
