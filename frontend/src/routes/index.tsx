import { lazy } from 'react';
import { useRoutes } from 'react-router-dom';

import Loadable from 'components/Loadable';
import BaseLayout from 'layout/BaseLayout';
import SignUp from 'pages/auth/SignUp';

import { Anonymous, Authenticated } from './auth-guards';

const NotFound = Loadable(lazy(async () => await import('pages/technical/NotFound')));
const Login = Loadable(lazy(async () => await import('pages/auth/Login')));
const ParticipantProfile = Loadable(
  lazy(async () => await import('pages/profile/ParticipantProfile'))
);
const VenueProfile = Loadable(
  lazy(async () => await import('pages/profile/VenueProfile'))
);
const ResetPassword = Loadable(
  lazy(async () => await import('pages/auth/ResetPassword'))
);
const ConfirmResetPassword = Loadable(
  lazy(async () => await import('pages/auth/ConfirmResetPassword'))
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
        { path: 'signup/participant', element: <SignUp role="participant" /> },
        { path: 'signup/venue', element: <SignUp role="venue" /> },
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
      children: [
        { path: 'participant', element: <ParticipantProfile /> },
        { path: 'venue', element: <VenueProfile /> },
      ],
    },
    {
      path: '*',
      element: <NotFound />,
    },
  ]);
}
