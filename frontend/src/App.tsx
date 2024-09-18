import CssBaseline from '@mui/material/CssBaseline';
import StyledEngineProvider from '@mui/material/StyledEngineProvider';
import { ThemeProvider } from '@mui/material/styles';
import { SnackbarProvider } from 'notistack';
import { useMemo, type ReactNode } from 'react';

import { AuthProvider } from 'contexts/AuthContext';
import { ConfigProvider } from 'contexts/ConfigContext';
import { CustomizationProvider } from 'contexts/CustomizationContext';
import { VenuesProvider } from 'contexts/VenuesContext';
import Locales from 'locales';
import Routes from 'routes';
import createCustomTheme from 'theme';

import 'utils/validation';

export default function App(): ReactNode {
  const theme = useMemo(createCustomTheme, []);
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Locales>
          <AuthProvider>
            <SnackbarProvider
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <CustomizationProvider>
                <VenuesProvider>
                  <ConfigProvider>
                    <Routes />
                  </ConfigProvider>
                </VenuesProvider>
              </CustomizationProvider>
            </SnackbarProvider>
          </AuthProvider>
        </Locales>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}
