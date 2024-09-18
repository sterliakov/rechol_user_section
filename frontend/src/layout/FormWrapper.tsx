import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import type { PropsWithChildren, ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

interface WrapperProps {
  width?: 'sm' | 'md' | 'lg' | string;
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
    <Grid
      container
      maxWidth={width}
      sx={{ width: ['sm', 'md', 'lg'].includes(width) ? undefined : width }}
      mt={{ sm: 0, md: 3 }}
    >
      <Card sx={{ minWidth, flexGrow: 1 }}>
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
