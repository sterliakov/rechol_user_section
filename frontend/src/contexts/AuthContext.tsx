import type { ReactNode } from 'react';
import { createContext, useContext, useEffect, useState } from 'react';

import axios from 'utils/axios';

interface User {
  email: string;
  first_name: string;
  last_name: string;
}
interface LoginDetails {
  email: string;
  password: string;
}

interface AuthState {
  user: User | null;
  login: (login: LoginDetails) => Promise<void>;
  // signup(info: LoginDetails): Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const isLoggedIn = user != null;
  const serviceToken = window.localStorage.getItem('serviceToken');

  // HACK: /api/accounts/me is handled inside `_mockApis/account`.
  const refreshUserInfo = async () => {
    const response = await axios.get('/api/account/me');
    const { user } = response.data;
    setUser(user);
  };
  const performLogout = async () => {
    setUser(null);
    await axios.post('/api/account/logout');
  };

  useEffect(() => {
    const init = async () => {
      try {
        if (serviceToken) {
          await refreshUserInfo();
        } else {
          await performLogout();
        }
      } catch (err: any) {
        // StrictMode artifact - nothing harmful
        if (err.toString().includes('removeChild')) return;
        console.info('Authorization token malformed or expired', err);
        await performLogout();
      }
    };
    init();
  }, [serviceToken]);

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
  }, [isLoggedIn]);

  const login = async (payload: LoginDetails): Promise<void> => {
    await axios.post('/api/account/login', payload);
    await refreshUserInfo();
  };

  const providerOptions: AuthState = {
    user,
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
