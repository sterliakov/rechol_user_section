import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

import axios from 'utils/axios';

export interface Venue {
  id: string;
  city: string;
  short_name: string;
  full_name: string;
  full_address: string;
  contact_phone: string;
  is_full: boolean;
}

interface VenuesState {
  venues: Venue[];
  refreshVenues: () => void;
}
const VenuesContext = createContext<VenuesState>({
  venues: [],
  refreshVenues() {
    throw new Error('Not initialized');
  },
});

async function getVenues(): Promise<Venue[]> {
  const response = await axios.get('/api/v1/venues/');
  return response.data;
}

export const VenuesProvider = ({ children }: { children: ReactNode }) => {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const refreshVenues = useCallback((): void => {
    setRefreshKey((k) => k + 1);
  }, []);

  // biome-ignore lint/correctness/useExhaustiveDependencies: using to refresh
  useEffect(() => {
    getVenues().then(setVenues);
  }, [refreshKey]);

  return (
    <VenuesContext.Provider value={{ venues, refreshVenues }}>
      {children}
    </VenuesContext.Provider>
  );
};

export default function useVenues(): VenuesState {
  const context = useContext(VenuesContext);
  if (!context) throw new Error('context must be use inside provider');
  return context;
}
