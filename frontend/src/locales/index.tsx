import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { IntlProvider } from 'react-intl';

import useCustomization from 'contexts/CustomizationContext';

type TranslationMap = Record<string, string>;
const loadLocaleData = async (locale: string): Promise<{ default: TranslationMap }> => {
  switch (locale) {
    case 'ru':
      return (await import('./ru.json')) as any;
    default:
      return (await import('./en.json')) as any;
  }
};

export default function Locales({ children }: { children: ReactNode }): ReactNode {
  const customization = useCustomization();
  const [messages, setMessages] = useState<TranslationMap>();

  useEffect(() => {
    loadLocaleData(customization.locale).then((d) => {
      setMessages(d.default);
    });
  }, [customization.locale]);

  return (
    <>
      {messages && (
        <IntlProvider
          locale={customization.locale}
          defaultLocale="en"
          messages={messages}
        >
          {children}
        </IntlProvider>
      )}
    </>
  );
}
