import Grid from '@mui/material/Grid2';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import type { ReactNode } from 'react';
import { Link, Outlet } from 'react-router-dom';

import MENU_ITEMS from 'routes/menu-items';

import AppBar from './AppBar';

function Routes({ direction }: { direction: 'row' | 'column' }): ReactNode {
  const horizontalStyle = {
    display: 'flex',
    flexDirection: 'row',
    padding: 0,
  };
  return (
    <List sx={direction === 'row' ? horizontalStyle : undefined}>
      {MENU_ITEMS.map(({ path, title }) => (
        <ListItem key={title}>
          <ListItemText>
            <Link style={{ color: 'inherit' }} to={path}>
              {title}
            </Link>
          </ListItemText>
        </ListItem>
      ))}
    </List>
  );
}

export default function BaseLayout() {
  return (
    <div style={{height: '100%'}}>
      <AppBar routes={Routes} />
      <main>
        <Grid container display="flex" flexDirection="column" justifyContent="center" alignItems="center">
          <Outlet />
        </Grid>
      </main>
    </div>
  );
}
