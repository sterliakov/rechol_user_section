import type { AutocompleteProps } from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import FormControl from '@mui/material/FormControl';
import TextField from '@mui/material/TextField';
import { useField } from 'formik';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';

import type { TextInputProps } from './TextInput';
import { ExtendedError, ExtendedLabel } from './_parts';

type AutocompleteInputProps<Option> = Pick<
  TextInputProps,
  'fieldName' | 'id' | 'labelKey' | 'required' | 'readOnly'
> & {
  options: Option[];
  getOptionLabel?: (option: Option) => string;
  getOptionValue?: (option: Option) => string;
  autoComplete?: string;
} & {
  renderOption?: AutocompleteProps<any, undefined, undefined, false>['renderOption'];
};

const hasLabel = (obj: any): obj is { label: string } => {
  return 'label' in obj;
};

const hasValue = (obj: any): obj is { value: string } => {
  return 'value' in obj;
};

export default function AutocompleteInput<Option>({
  fieldName,
  id,
  labelKey,
  required,
  options,
  getOptionLabel = (option) => (hasLabel(option) ? option.label : ''),
  getOptionValue = (option) => (hasValue(option) ? option.value : ''),
  readOnly,
  renderOption,
}: AutocompleteInputProps<Option>) {
  const [field, meta, helper] = useField<string>(fieldName);
  const allReadonly = useReadOnlyForm();

  const value = options.find((option) => getOptionValue(option) === meta.value) ?? null;

  const label = <ExtendedLabel {...{ labelKey, required }} />;
  return (
    <FormControl fullWidth>
      <Autocomplete
        value={value}
        onChange={(_, newValue) => {
          // Formik has problems with React 18 when we have a dependent field.
          // Likely https://github.com/jaredpalmer/formik/issues/3602
          // Without setTimeout we end up in an infinite loop.
          setTimeout(() => {
            void helper.setValue(newValue ? getOptionValue(newValue) : '');
          });
        }}
        onBlur={field.onBlur}
        options={options}
        getOptionLabel={getOptionLabel}
        renderInput={(params) => (
          <TextField {...params} label={label} name={field.name} id={id} />
        )}
        renderOption={renderOption}
        readOnly={readOnly ?? allReadonly}
      />
      {meta.touched && <ExtendedError error={meta.error} />}
    </FormControl>
  );
}
