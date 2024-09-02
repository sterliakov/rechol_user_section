import type { OutlinedInputProps } from '@mui/material';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import { useField } from 'formik';
import type { ReactNode } from 'react';
import { FormattedMessage } from 'react-intl';

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
  helperText,
  ...extra
}: TextInputProps) => {
  const [field, meta] = useField<string>(fieldName);

  const label = (
    <FormattedMessage
      id={labelKey}
      values={{
        value: required ? '*' : undefined,
      }}
    />
  );

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
        {...extra}
      />
      {meta.touched && meta.error && (
        <FormHelperText error>{meta.error}</FormHelperText>
      )}
      {helperText}
    </FormControl>
  );
};

export default TextInput;
