import type { ReactNode } from 'react';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';

import { Loader } from 'components/Loadable';
import axios from 'utils/axios';

export type Role = 'p' | 'v' | 'j';
export type FullRole = 'participant' | 'venue' | 'judge';

export interface User {
  pk: number;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  fullRole: FullRole;
}
interface LoginDetails {
  email: string;
  password: string;
}

interface AuthState {
  user: User | null;
  login: (login: LoginDetails) => Promise<User>;
  refreshUserInfo: () => Promise<User>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

function getFullRole(role: Role): FullRole {
  return (
    {
      p: 'participant',
      v: 'venue',
      j: 'judge',
    } as const
  )[role];
}
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [hasLoaded, setHasLoaded] = useState<boolean>(false);
  const isLoggedIn = user != null;

  const refreshUserInfo = async (): Promise<User> => {
    const response = await axios.get('/api/auth/user/');
    const user = {
      ...response.data,
      fullRole: getFullRole(response.data.role),
    };
    setUser(user);
    return user;
  };
  const performLogout = useCallback(async () => {
    if (!isLoggedIn) return;
    setHasLoaded(false);
    setUser(null);
    await axios.post('/api/auth/logout/');
    setHasLoaded(true);
  }, [isLoggedIn]);

  useEffect(() => {
    const init = async () => {
      try {
        await refreshUserInfo();
      } catch (err: any) {
        // StrictMode artifact - nothing harmful
        if (err.toString().includes('removeChild')) return;
        console.info('Authorization token malformed or expired', err);
        await performLogout();
      } finally {
        setHasLoaded(true);
      }
    };
    void init();
  }, [performLogout]);

  useEffect(() => {
    const interceptorId = axios.interceptors.response.use(undefined, (error) => {
      const { status, data } = error.response ?? {};
      // data may be either {code, ...} or {errors: {code, ...}}
      // TODO: this looks like a backend bug, should be `{non_field_errors: [...]}`
      // or `{errors: {err_1: {code, ...}}}`.
      if (
        status === 401 &&
        (data?.errors ?? data)?.code === 'token_not_valid' &&
        isLoggedIn
      ) {
        console.info('Token is invalid or expired. Logging out...');
        performLogout();
      }

      throw error;
    });

    return () => {
      axios.interceptors.response.eject(interceptorId);
    };
  }, [isLoggedIn, performLogout]);

  const login = async (payload: LoginDetails): Promise<User> => {
    await axios.post('/api/auth/login/', payload);
    return await refreshUserInfo();
  };

  if (!hasLoaded) {
    return <Loader />;
  }

  const providerOptions: AuthState = {
    user,
    refreshUserInfo,
    login,
    logout: performLogout,
  };
  return (
    <AuthContext.Provider value={providerOptions}>{children}</AuthContext.Provider>
  );
};

export default function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error('context must be use inside provider');
  return context;
}
