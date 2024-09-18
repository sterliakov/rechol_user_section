import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid2';
import { Formik } from 'formik';
import { useState } from 'react';
import { FormattedMessage } from 'react-intl';
import { useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';

import { PasswordAdornment } from 'components/fields/PasswordInput';
import StrengthIndicator from 'components/fields/StrengthIndicator';
import TextInput from 'components/fields/TextInput';
import FormWrapper from 'layout/FormWrapper';
import axios from 'utils/axios';
import { getErrors } from 'utils/errors';

interface FormState {
  new_password1: string;
  new_password2: string;
  submit: string | null;
}
const initialState: FormState = {
  new_password1: '',
  new_password2: '',
  submit: null,
};

const schema = Yup.object().shape({
  new_password1: Yup.string().min(8, 'password-too-short').required('required-field'),
  new_password2: Yup.string().when('new_password1', ([val]) => {
    return val && val.length > 0
      ? Yup.string().oneOf([Yup.ref('new_password1')], 'passwords-dont-match')
      : Yup.string();
  }),
});

interface EndpointParams {
  uid: string;
  token: string;
  new_password1: string;
  new_password2: string;
}
async function confirmResetPassword(params: EndpointParams): Promise<void> {
  await axios.post('/api/auth/password/reset/confirm/', params);
}

export default function ConfirmResetPassword() {
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { uid, token } = useParams();
  if (!uid || !token) throw new Error('Missing params');

  return (
    <FormWrapper width="sm" titleId="reset-password" minWidth="min(100vw,450px)">
      <Formik
        initialValues={initialState}
        validationSchema={schema}
        onSubmit={async (values, { setErrors }) => {
          try {
            await confirmResetPassword({
              new_password1: values.new_password1,
              new_password2: values.new_password2,
              uid,
              token,
            });
            navigate('/auth/login');
          } catch (err: any) {
            setErrors(getErrors(err?.response?.data));
          }
        }}
      >
        {({ values, errors, handleSubmit, isSubmitting }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid size={12}>
                <TextInput
                  fieldName="new_password1"
                  id="new-password"
                  labelKey="new-password"
                  required
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  endAdornment={
                    <PasswordAdornment {...{ showPassword, setShowPassword }} />
                  }
                />
              </Grid>
              <Grid size={12}>
                <TextInput
                  fieldName="new_password2"
                  id="new-password-confirm"
                  labelKey="new-password-confirm"
                  required
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  endAdornment={
                    <PasswordAdornment {...{ showPassword, setShowPassword }} />
                  }
                />
              </Grid>
              <Grid size={12}>
                <StrengthIndicator password={values.new_password1} />
              </Grid>

              {errors.submit && (
                <Grid size={12} mt={2}>
                  <FormHelperText error>{errors.submit}</FormHelperText>
                </Grid>
              )}

              <Grid size={12} justifyContent="center" display="flex">
                <Button
                  disableElevation
                  disabled={isSubmitting}
                  fullWidth
                  size="large"
                  type="submit"
                  variant="contained"
                  color="primary"
                >
                  <FormattedMessage id="reset-password" />
                </Button>
              </Grid>
            </Grid>
          </form>
        )}
      </Formik>
    </FormWrapper>
  );
}
