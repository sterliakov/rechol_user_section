import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import type { Dispatch, SetStateAction } from 'react';
import { useState } from 'react';

import type { TextInputProps } from './TextInput';
import TextInput from './TextInput';

export function PasswordAdornment({
  showPassword,
  setShowPassword,
}: {
  showPassword: boolean;
  setShowPassword: Dispatch<SetStateAction<boolean>>;
}) {
  const handleMouseDownPassword = (event: React.SyntheticEvent) => {
    event.preventDefault();
  };
  return (
    <InputAdornment position="end">
      <IconButton
        aria-label="toggle password visibility"
        onClick={() => {
          setShowPassword(!showPassword);
        }}
        onMouseDown={handleMouseDownPassword}
        edge="end"
        size="large"
      >
        {showPassword ? <Visibility /> : <VisibilityOff />}
      </IconButton>
    </InputAdornment>
  );
}

export default function PasswordInput(
  props: Omit<TextInputProps, 'type' | 'endAdornment'>,
) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <TextInput
      {...props}
      type={showPassword ? 'text' : 'password'}
      endAdornment={<PasswordAdornment {...{ showPassword, setShowPassword }} />}
    />
  );
}
