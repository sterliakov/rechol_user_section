import MenuIcon from '@mui/icons-material/Menu';
import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid2';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Toolbar from '@mui/material/Toolbar';
import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';

import Logo from 'assets/images/logo.png';

type RoutesComponent = (props: { direction: 'row' | 'column' }) => ReactNode;

export default function ResAppBar({
  routes: Routes,
  maxWidth = 600,
}: {
  routes: RoutesComponent;
  maxWidth?: number;
}) {
  const [hasDrawer, setHasDrawer] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const closeDrawer = () => {
    setDrawerOpen(false);
  };
  const openDrawer = () => {
    setDrawerOpen(true);
  };

  const width = window.innerWidth;
  useEffect(() => {
    if (width <= maxWidth) {
      setHasDrawer(true);
    }
    const handler = () => {
      setHasDrawer(width <= maxWidth);
    };
    window.addEventListener('resize', handler);
    return () => {
      window.removeEventListener('resize', handler);
    };
  }, [width, maxWidth]);

  return (
    <>
      <AppBar sx={{position: 'relative'}}>
        <Toolbar>
          <Grid
            container
            flexDirection="row"
            justifyContent="space-between"
            alignItems="center"
          >
            {hasDrawer ? (
              <MenuIcon onClick={openDrawer} />
            ) : (
              <img
                src={Logo}
                width="150"
                style={{ paddingTop: '6px', paddingBottom: '6px' }}
              />
            )}
            {!hasDrawer && <Routes direction="row" />}
          </Grid>
        </Toolbar>
      </AppBar>

      {hasDrawer && (
        <SwipeableDrawer open={drawerOpen} onClose={closeDrawer} onOpen={openDrawer}>
          <div tabIndex={0} role="button" onClick={closeDrawer} onKeyDown={closeDrawer}>
            <Routes direction="column" />
          </div>
        </SwipeableDrawer>
      )}
    </>
  );
}
