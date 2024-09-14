import MenuIcon from '@mui/icons-material/Menu';
import AppBar from '@mui/material/AppBar';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import Toolbar from '@mui/material/Toolbar';
import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { FormattedMessage } from 'react-intl';
import { Link } from 'react-router-dom';

import Logo from 'assets/images/logo.png';
import useAuth from 'contexts/AuthContext';

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
      <AppBar>
        <Toolbar>
          <Grid
            container
            flexDirection="row"
            justifyContent="space-between"
            alignItems="center"
            sx={{ width: '100%' }}
          >
            <Box display="flex">
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
            </Box>
            <LogOutSection />
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

function LogOutSection() {
  const { user, logout } = useAuth();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return user == null ? (
    <Box display="flex" gap={1}>
      <Button color="secondary" to="/auth/signup" component={Link} variant="contained">
        <FormattedMessage id="sign-up" />
      </Button>
      <Button
        color="primary"
        to="/auth/login"
        component={Link}
        variant="outlined"
        sx={{ color: '#fff', borderColor: '#fff' }}
      >
        <FormattedMessage id="sign-in" />
      </Button>
    </Box>
  ) : (
    <div>
      <Button
        id="profile-menu-btn"
        aria-controls={open ? 'profile-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        onClick={handleClick}
        sx={{ color: 'inherit' }}
      >
        <Box display="flex" gap={2} alignItems="center">
          <FormattedMessage id="user-info" values={{ email: user.email }} />
          <Avatar>H</Avatar>
        </Box>
      </Button>
      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'profile-menu-btn',
        }}
        slotProps={{
          paper: {
            elevation: 0,
            sx: {
              overflow: 'visible',
              filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
              mt: 1.5,
              '& .MuiAvatar-root': {
                width: 32,
                height: 32,
                ml: -0.5,
                mr: 1,
              },
              '&::before': {
                content: '""',
                display: 'block',
                position: 'absolute',
                top: 0,
                right: 14,
                width: 10,
                height: 10,
                bgcolor: 'background.paper',
                transform: 'translateY(-50%) rotate(45deg)',
                zIndex: 0,
              },
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem component={Link} to="/profile">
          Profile
        </MenuItem>
        <MenuItem
          onClick={() => {
            void logout();
          }}
        >
          <FormattedMessage id="sign-out" />
        </MenuItem>
      </Menu>
    </div>
  );
}
