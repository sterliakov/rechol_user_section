import type { OutlinedInputProps } from '@mui/material';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import { useField } from 'formik';
import type { ReactNode } from 'react';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';

import { ExtendedError, ExtendedLabel } from './_parts';

export interface TextInputProps extends OutlinedInputProps {
  fieldName: string;
  labelKey: string;
  id: string;
  required?: boolean;
  helperText?: ReactNode;
}

const TextInput = ({
  fieldName,
  id,
  labelKey,
  required,
  readOnly,
  helperText,
  ...extra
}: TextInputProps) => {
  const [field, meta] = useField<string>(fieldName);
  const allReadonly = useReadOnlyForm();

  const label = <ExtendedLabel {...{ labelKey, required }} />;
  return (
    <FormControl fullWidth error={Boolean(meta.touched && meta.error)}>
      <InputLabel htmlFor={id}>{label}</InputLabel>
      <OutlinedInput
        id={id}
        value={meta.value}
        name={field.name}
        onBlur={field.onBlur}
        onChange={field.onChange}
        label={label}
        readOnly={readOnly ?? allReadonly}
        {...extra}
      />
      {meta.touched && <ExtendedError error={meta.error} />}
      {helperText}
    </FormControl>
  );
};

export default TextInput;
