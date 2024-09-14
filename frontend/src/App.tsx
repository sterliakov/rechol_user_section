import CssBaseline from '@mui/material/CssBaseline';
import StyledEngineProvider from '@mui/material/StyledEngineProvider';
import { ThemeProvider } from '@mui/material/styles';
import { useMemo, type ReactNode } from 'react';

import { AuthProvider } from 'contexts/AuthContext';
import { ConfigProvider } from 'contexts/ConfigContext';
import { CustomizationProvider } from 'contexts/CustomizationContext';
import { VenuesProvider } from 'contexts/VenuesContext';
import Locales from 'locales';
import Routes from 'routes';
import createCustomTheme from 'theme';

export default function App(): ReactNode {
  const theme = useMemo(createCustomTheme, []);
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Locales>
          <AuthProvider>
            <CustomizationProvider>
              <VenuesProvider>
                <ConfigProvider>
                  <Routes />
                </ConfigProvider>
              </VenuesProvider>
            </CustomizationProvider>
          </AuthProvider>
        </Locales>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}
