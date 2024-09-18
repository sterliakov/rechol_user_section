import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

import axios from 'utils/axios';

export interface Config {
  registration_start: string;
  registration_end: string;
  venue_registration_start: string;
  venue_registration_end: string;
  offline_appeal_start: string;
  offline_appeal_end: string;
  online_appeal_start: string;
  online_appeal_end: string;
  forbid_venue_change: boolean;
  show_offline_problems: boolean;
}

interface ConfigState {
  config: Config | null;
  refreshConfig: () => void;
}
const ConfigContext = createContext<ConfigState>({
  config: null,
  refreshConfig() {
    throw new Error('Not initialized');
  },
});

async function getConfig(): Promise<Config> {
  const response = await axios.get('/api/v1/config/');
  return response.data;
}

export const ConfigProvider = ({ children }: { children: ReactNode }) => {
  const [config, setConfig] = useState<Config | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const refreshConfig = useCallback((): void => {
    setRefreshKey((k) => k + 1);
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: using to refresh
  useEffect(() => {
    getConfig().then(setConfig);
  }, [refreshKey]);

  return (
    <ConfigContext.Provider value={{ config, refreshConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export default function useConfig(): ConfigState {
  const context = useContext(ConfigContext);
  if (!context) throw new Error('context must be use inside provider');
  return context;
}
