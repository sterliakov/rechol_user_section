import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import { useField } from 'formik';
import type { MuiTelInputCountry } from 'mui-tel-input';
import { MuiTelInput } from 'mui-tel-input';
import { FormattedMessage } from 'react-intl';

import type { TextInputProps } from './TextInput';

type PhoneInputProps = Pick<
  TextInputProps,
  'fieldName' | 'id' | 'labelKey' | 'required'
> & {
  defaultCountry?: MuiTelInputCountry;
};

const PhoneInput = ({
  fieldName,
  id,
  labelKey,
  required,
  defaultCountry,
}: PhoneInputProps) => {
  const [field, meta, helper] = useField<string>(fieldName);

  const label = (
    <>
      <FormattedMessage id={labelKey} />
      {required && ' *'}
    </>
  );

  return (
    <FormControl fullWidth error={Boolean(meta.touched && meta.error)}>
      <MuiTelInput
        id={id}
        value={meta.value}
        name={field.name}
        onBlur={field.onBlur}
        onChange={(value: string) => {
          void helper.setValue(value);
        }}
        label={label}
        defaultCountry={defaultCountry}
      />
      {meta.touched && meta.error && (
        <FormHelperText error>{meta.error}</FormHelperText>
      )}
    </FormControl>
  );
};

export default PhoneInput;
