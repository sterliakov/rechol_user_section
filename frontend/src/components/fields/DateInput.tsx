import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useField } from 'formik';
import type { ComponentProps } from 'react';
import { FormattedMessage } from 'react-intl';

import { toEndOfDay, toStartOfDay } from 'utils/date';

export interface DateInputProps
  extends Omit<
    ComponentProps<typeof DatePicker>,
    'label' | 'value' | 'InputProps' | 'renderInput' | 'onChange'
  > {
  fieldName: string;
  labelKey: string;
  id: string;
  required?: boolean;
  /**
   * Since this is a date input, decide how to deal with time.
   *
   * DAY_START: set to start of day in local TZ
   * DAY_END: set to end of day in local TZ
   * null: Set to current time
   */
  normalize?: 'DAY_START' | 'DAY_END' | null;
}

export default function DateInput({
  fieldName,
  id,
  labelKey,
  required,
  normalize,
  ...props
}: DateInputProps) {
  const [field, meta, helper] = useField<string>(fieldName);

  const label = (
    <>
      <FormattedMessage id={labelKey} />
      {required && ' *'}
    </>
  );

  const performNormalize = (value: Date | null) => {
    if (!value || Number.isNaN(value.getDate())) {
      return '';
    }
    switch (normalize) {
      case 'DAY_START':
        return toStartOfDay(value).toISOString();
      case 'DAY_END':
        return toEndOfDay(value).toISOString();
      default:
        return value.toISOString();
    }
  };

  return (
    <FormControl fullWidth error={Boolean(meta.touched && meta.error)}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <DatePicker
          label={label}
          value={meta.value ? new Date(meta.value) : null}
          slotProps={{
            textField: {
              id,
              name: field.name,
              onBlur: field.onBlur,
              fullWidth: true,
            },
          }}
          // renderInput={(props: any) => <TextField {...props} helperText="" />}
          onChange={(value: Date | null) => {
            void helper.setValue(performNormalize(value));
          }}
          {...props}
        />
      </LocalizationProvider>
      {meta.touched && meta.error && (
        <FormHelperText error>
          <FormattedMessage id={meta.error} defaultMessage={meta.error} />
        </FormHelperText>
      )}
    </FormControl>
  );
}
