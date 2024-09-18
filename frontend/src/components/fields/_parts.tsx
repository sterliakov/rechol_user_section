import FormHelperText from '@mui/material/FormHelperText';
import type { ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

export function ExtendedLabel({
  labelKey,
  required,
}: {
  labelKey: string;
  required?: boolean;
}): ReactNode {
  return (
    <>
      <FormattedMessage id={labelKey} />
      {required && ' *'}
    </>
  );
}

export function ExtendedError({ error }: { error?: any }): ReactNode {
  if (!error) return null;
  return (
    <FormHelperText error>
      {typeof error !== 'string' ? (
        <FormattedMessage id={error.id} values={error.values} />
      ) : (
        <FormattedMessage id={error} defaultMessage={error} />
      )}
    </FormHelperText>
  );
}
