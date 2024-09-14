import type { SelectProps } from '@mui/material';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { useField } from 'formik';
import type { ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

import type { TextInputProps } from './TextInput';

export interface Option<ID = string> {
  id: ID;
  value: string | ReactNode;
  disabled?: boolean;
}

type SelectInputProps<ID> = Pick<
  TextInputProps,
  'fieldName' | 'id' | 'labelKey' | 'required' | 'disabled'
> & {
  options: Array<Option<ID>>;
  onChange?: SelectProps<string>['onChange'];
  helperText?: ReactNode;
};

export default function SelectInput<ID extends string | number = string>({
  fieldName,
  id,
  labelKey,
  required,
  options,
  onChange,
  disabled,
  helperText,
}: SelectInputProps<ID>) {
  const [field, meta] = useField<string>(fieldName);
  const labelId = `${id}-label`;
  const label = (
    <>
      <FormattedMessage id={labelKey} />
      {required && ' *'}
    </>
  );

  return (
    <FormControl fullWidth>
      <InputLabel id={labelId}>{label}</InputLabel>
      <Select
        id={id}
        labelId={labelId}
        value={options.some(({ id }) => meta.value === id) ? meta.value : ''}
        label={label}
        onChange={(event, node) => {
          if (onChange) {
            onChange(event, node);
          } else {
            field.onChange(event);
          }
        }}
        onBlur={field.onBlur}
        error={!!(meta.touched && meta.error)}
        name={field.name}
        disabled={disabled}
      >
        <MenuItem value="">
          <FormattedMessage id="not-selected" />
        </MenuItem>
        {options.map((option) => (
          <MenuItem key={option.id} value={option.id} disabled={option.disabled}>
            {option.value}
          </MenuItem>
        ))}
      </Select>
      {meta.touched && meta.error && (
        <FormHelperText error>
          <FormattedMessage id={meta.error} defaultMessage={meta.error} />
        </FormHelperText>
      )}
      {helperText}
    </FormControl>
  );
}
