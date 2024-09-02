import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import type { PropsWithChildren, ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

interface WrapperProps {
  width?: 'sm' | 'md' | 'lg';
  minWidth: string | number;
  titleId: string;
}
export default function FormWrapper({
  children,
  titleId,
  minWidth,
  width = 'sm',
}: PropsWithChildren<WrapperProps>): ReactNode {
  return (
    <Grid container maxWidth={width} mt={3}>
      <Card sx={{ minWidth }}>
        <CardHeader
          title={
            <Typography variant="h4" component="h2">
              <FormattedMessage id={titleId} />
            </Typography>
          }
        />
        <CardContent>{children}</CardContent>
      </Card>
    </Grid>
  );
}
