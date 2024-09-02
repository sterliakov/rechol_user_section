import Grid from '@mui/material/Grid2';
import type { PropsWithChildren, ReactNode } from 'react';

export default function FormWrapper({
  children,
  width = 'sm',
}: PropsWithChildren<{ width?: 'sm' | 'md' | 'lg' }>): ReactNode {
  return (
    <Grid container justifyContent="center" alignItems="center" maxWidth={width}>
      {children}
    </Grid>
  );
}
