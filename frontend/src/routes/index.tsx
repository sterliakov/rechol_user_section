import { lazy } from 'react';
import { useRoutes } from 'react-router-dom';

import Loadable from 'components/Loadable';
import BaseLayout from 'layout/BaseLayout';

import { Anonymous, Authenticated } from './auth-guards';

// import AuthenticationRoutes from './AuthenticationRoutes';
// import LoginRoutes from './LoginRoutes';
// import MainRoutes from './MainRoutes';

const NotFound = Loadable(lazy(async () => await import('pages/technical/NotFound')));
const Login = Loadable(lazy(async () => await import('pages/auth/Login')));
const Profile = Loadable(lazy(async () => await import('pages/profile')));
const ResetPassword = Loadable(
  lazy(async () => await import('pages/auth/ResetPassword'))
);
const ConfirmResetPassword = Loadable(
  lazy(async () => await import('pages/auth/ConfirmResetPassword'))
);
const ParticipantProfile = Loadable(
  lazy(async () => await import('pages/profile/ParticipantProfile'))
);

export default function ThemeRoutes() {
  return useRoutes([
    {
      path: '/auth',
      element: (
        <Anonymous>
          <BaseLayout />
        </Anonymous>
      ),
      children: [
        { path: 'login', element: <Login /> },
        { path: 'signup', element: <ParticipantProfile mode="signup" /> },
        { path: 'reset-password/begin', element: <ResetPassword /> },
        {
          path: 'reset-password/confirm/:uid/:token',
          element: <ConfirmResetPassword />,
        },
      ],
    },
    {
      path: '/profile',
      element: (
        <Authenticated>
          <BaseLayout />
        </Authenticated>
      ),
      children: [{ path: 'participant', element: <Profile /> }],
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
