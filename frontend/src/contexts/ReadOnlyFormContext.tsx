import type { ReactNode } from 'react';
import { createContext, useContext } from 'react';

const ReadOnlyFormContext = createContext<boolean>(false);

export function ReadOnlyFormProvider({
  children,
  readonly = false,
}: {
  children: ReactNode;
  readonly: boolean;
}): ReactNode {
  return (
    <ReadOnlyFormContext.Provider value={readonly}>
      {children}
    </ReadOnlyFormContext.Provider>
  );
}

export function useReadOnlyForm(): boolean {
  const context = useContext(ReadOnlyFormContext);
  return context ?? false;
}
