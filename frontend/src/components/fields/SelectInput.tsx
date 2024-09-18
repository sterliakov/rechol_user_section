import type { SelectProps } from '@mui/material';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { useField } from 'formik';
import type { ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';

import type { TextInputProps } from './TextInput';
import { ExtendedError, ExtendedLabel } from './_parts';

export interface Option<ID = string> {
  id: ID;
  value: string | ReactNode;
  disabled?: boolean;
}

type SelectInputProps<ID> = Pick<
  TextInputProps,
  'fieldName' | 'id' | 'labelKey' | 'required' | 'disabled' | 'readOnly'
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
  readOnly,
  helperText,
}: SelectInputProps<ID>) {
  const [field, meta] = useField<string>(fieldName);
  const allReadonly = useReadOnlyForm();
  const labelId = `${id}-label`;
  const label = <ExtendedLabel {...{ labelKey, required }} />;

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
        readOnly={readOnly ?? allReadonly}
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
      {meta.touched && <ExtendedError error={meta.error} />}
      {helperText}
    </FormControl>
  );
}
