import { lazy } from 'react';
import { useRoutes } from 'react-router-dom';

import Loadable from 'components/Loadable';
import BaseLayout from 'layout/BaseLayout';

// import AuthenticationRoutes from './AuthenticationRoutes';
// import LoginRoutes from './LoginRoutes';
// import MainRoutes from './MainRoutes';

const NotFound = Loadable(lazy(async () => await import('pages/technical/NotFound')));
const Login = Loadable(lazy(async () => await import('pages/auth/Login')));

export default function ThemeRoutes() {
  return useRoutes([
    {
      path: '/auth',
      element: <BaseLayout />,
      children: [{ path: 'login', element: <Login /> }],
    },
    // AuthenticationRoutes,
    // LoginRoutes,
    // ...MainRoutes,
    {
      path: '*',
      element: <NotFound />,
    },
  ]);
}
