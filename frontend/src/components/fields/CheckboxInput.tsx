import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';
import { useField } from 'formik';
import type { ReactNode } from 'react';

import { useReadOnlyForm } from 'contexts/ReadOnlyFormContext';

import { ExtendedError, ExtendedLabel } from './_parts';

export interface CheckboxInputProps {
  fieldName: string;
  labelKey: string;
  required?: boolean;
  readOnly?: boolean;
}

export default function CheckboxInput({
  fieldName,
  labelKey,
  required,
  readOnly,
}: CheckboxInputProps): ReactNode {
  const [field, meta, helper] = useField<boolean>(fieldName);
  const allReadonly = useReadOnlyForm();
  return (
    <>
      <FormControlLabel
        control={
          <Checkbox
            checked={field.value}
            onChange={(event) => {
              void helper.setValue(event.target.checked);
            }}
            name={fieldName}
            color="primary"
            readOnly={readOnly ?? allReadonly}
          />
        }
        label={<ExtendedLabel {...{ labelKey, required }} />}
      />
      {meta.touched && <ExtendedError error={meta.error} />}
    </>
  );
}
