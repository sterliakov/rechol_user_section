import UploadIcon from '@mui/icons-material/Upload';
import FormControl from '@mui/material/FormControl';
import InputAdornment from '@mui/material/InputAdornment';
import InputLabel from '@mui/material/InputLabel';
import { useField } from 'formik';
import { MuiFileInput } from 'mui-file-input';
import type { ReactNode } from 'react';

import { ExtendedError, ExtendedLabel } from './_parts';

export interface FileInputProps {
  fieldName: string;
  labelKey: string;
  id: string;
  required?: boolean;
  helperText?: ReactNode;
}

export default function FileInput({
  fieldName,
  id,
  labelKey,
  required,
  helperText,
}: FileInputProps): ReactNode {
  const [field, meta, helper] = useField<File | null>(fieldName);

  const label = <ExtendedLabel {...{ labelKey, required }} />;
  const isNewFile = meta.value instanceof File;
  const fakeFile =
    isNewFile || meta.value == null
      ? null
      : new File([], (meta.value as any as string).split('/').at(-1)!);

  return (
    <FormControl fullWidth error={Boolean(meta.touched && meta.error)}>
      <InputLabel htmlFor={id} shrink>
        {label}
      </InputLabel>
      <MuiFileInput
        onChange={(file: File | null) => {
          helper.setValue(file);
        }}
        value={fakeFile ?? meta.value}
        getInputText={(value: File | null) => value?.name ?? fakeFile?.name}
        InputProps={{
          id,
          label,
          startAdornment: (
            <InputAdornment position="start">
              <UploadIcon />
            </InputAdornment>
          ),
          name: field.name,
          onBlur: field.onBlur,
        }}
        hideSizeText={!isNewFile}
      />
      {meta.touched && <ExtendedError error={meta.error} />}
      {helperText}
    </FormControl>
  );
}
