import FormControl from '@mui/material/FormControl';
import { useField } from 'formik';
import type { MuiTelInputCountry } from 'mui-tel-input';
import { MuiTelInput } from 'mui-tel-input';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';

import type { TextInputProps } from './TextInput';
import { ExtendedError, ExtendedLabel } from './_parts';

type PhoneInputProps = Pick<
  TextInputProps,
  'fieldName' | 'id' | 'labelKey' | 'required' | 'readOnly'
> & {
  defaultCountry?: MuiTelInputCountry;
};

const PhoneInput = ({
  fieldName,
  id,
  labelKey,
  required,
  readOnly,
  defaultCountry,
}: PhoneInputProps) => {
  const [field, meta, helper] = useField<string>(fieldName);
  const allReadonly = useReadOnlyForm();

  const label = <ExtendedLabel {...{ labelKey, required }} />;
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
        error={meta.error}
        label={label}
        readOnly={readOnly ?? allReadonly}
        defaultCountry={defaultCountry}
      />
      {meta.touched && <ExtendedError error={meta.error} />}
    </FormControl>
  );
};

export default PhoneInput;
