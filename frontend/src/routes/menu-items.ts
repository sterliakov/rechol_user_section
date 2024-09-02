interface MenuItem {
  title: string;
  path: string;
}
const anonymousMenuItems: MenuItem[] = [{ title: 'Sign In', path: '/auth/login' }];

export default anonymousMenuItems;
