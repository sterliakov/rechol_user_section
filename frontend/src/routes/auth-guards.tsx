import type { PropsWithChildren, ReactNode } from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import useAuth from 'contexts/AuthContext';

export function Authenticated({
  children,
}: PropsWithChildren<Record<never, never>>): ReactNode {
  const { user } = useAuth();
  console.log(user);
  const navigate = useNavigate();
  useEffect(() => {
    if (user == null) {
      navigate('/auth/login');
    }
  }, [user, navigate]);
  if (user == null) {
    return null;
  }
  return children;
}

export function Anonymous({
  children,
}: PropsWithChildren<Record<never, never>>): ReactNode {
  const { user } = useAuth();
  console.log(user);
  const navigate = useNavigate();
  useEffect(() => {
    if (user != null) {
      navigate('/profile/participant');
    }
  }, [user, navigate]);
  if (user != null) {
    return null;
  }
  return children;
}
