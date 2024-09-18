import FormControl from '@mui/material/FormControl';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useField } from 'formik';
import type { ComponentProps } from 'react';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';
import { toEndOfDay, toStartOfDay } from 'utils/date';

import { ExtendedError, ExtendedLabel } from './_parts';

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
  readOnly,
  ...props
}: DateInputProps) {
  const [field, meta, helper] = useField<string>(fieldName);
  const allReadonly = useReadOnlyForm();

  const label = <ExtendedLabel {...{ labelKey, required }} />;
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
          onChange={(value: Date | null) => {
            void helper.setValue(performNormalize(value));
          }}
          readOnly={readOnly ?? allReadonly}
          {...props}
        />
      </LocalizationProvider>
      {meta.touched && <ExtendedError error={meta.error} />}
    </FormControl>
  );
}
