import type { OutlinedInputProps } from '@mui/material';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormHelperText from '@mui/material/FormHelperText';
import { useField } from 'formik';
import type { ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

export interface TextInputProps extends OutlinedInputProps {
  fieldName: string;
  labelKey: string;
  required?: boolean;
}

export default function CheckboxInput({
  fieldName,
  labelKey,
  required,
}: TextInputProps): ReactNode {
  const [field, meta, helper] = useField<boolean>(fieldName);
  return (
    <>
      <FormControlLabel
        control={
          <Checkbox
            checked={field.value}
            onChange={(event) => {
              void helper.setValue(event.target.checked);
            }}
            name="tos-consent"
            color="primary"
          />
        }
        label={
          <>
            <FormattedMessage id={labelKey} />
            {required && ' *'}
          </>
        }
      />

      {meta.touched && meta.error && (
        <FormHelperText error>
          <FormattedMessage id={meta.error} defaultMessage={meta.error} />
        </FormHelperText>
      )}
    </>
  );
}
