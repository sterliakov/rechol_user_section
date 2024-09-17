import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid2';
import { Formik } from 'formik';
import { FormattedMessage } from 'react-intl';
import { Link, useNavigate } from 'react-router-dom';
import * as Yup from 'yup';

import PasswordInput from 'components/fields/PasswordInput';
import TextInput from 'components/fields/TextInput';
import type { FullRole } from 'contexts/AuthContext';
import FormWrapper from 'layout/FormWrapper';
import axios from 'utils/axios';
import { getErrors } from 'utils/errors';

interface FormState {
  email: string;
  first_name: string;
  last_name: string;
  patronymic_name: string;
  password1: string;
  password2: string;
  submit: string | null;
}
const initialState: FormState = {
  email: '',
  first_name: '',
  last_name: '',
  patronymic_name: '',
  password1: '',
  password2: '',
  submit: null,
};

const schema = Yup.object().shape({
  email: Yup.string().max(255).required('required-field'),
  first_name: Yup.string().max(255).required('required-field'),
  last_name: Yup.string().max(255).required('required-field'),
  patronymic_name: Yup.string().max(255),
  password1: Yup.string().min(8, 'password-too-short').required('required-field'),
  password2: Yup.string().when('password1', ([val]) => {
    return val && val.length > 0
      ? Yup.string().oneOf([Yup.ref('password1')], 'passwords-dont-match')
      : Yup.string();
  }),
});

async function signUp(
  params: Omit<FormState, 'submit'>,
  role: FullRole
): Promise<void> {
  await axios.post(`/api/v1/register/${role}/`, params);
}

export default function SignUp({ role }: { role: FullRole }) {
  const navigate = useNavigate();

  return (
    <FormWrapper width="sm" titleId="sign-up" minWidth="450px">
      <Formik
        initialValues={initialState}
        validationSchema={schema}
        onSubmit={async (values, { setErrors }) => {
          try {
            await signUp(values, role);
            navigate(`/profile/${role}`);
          } catch (err: any) {
            setErrors(getErrors(err?.response?.data));
          }
        }}
      >
        {({ errors, handleSubmit, isSubmitting }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12 }}>
                <TextInput
                  fieldName="email"
                  id="email"
                  labelKey="email-address"
                  required
                  autoComplete="email"
                  fullWidth
                />
              </Grid>
            </Grid>

            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <PasswordInput
                  fieldName="password1"
                  id="new-password-1"
                  labelKey="new-password"
                  required
                  autoComplete="new-password"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }}>
                <PasswordInput
                  fieldName="password2"
                  id="new-password-2"
                  labelKey="new-password-confirm"
                  required
                  autoComplete="new-password"
                  fullWidth
                />
              </Grid>
            </Grid>

            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12 }}>
                <TextInput
                  fieldName="first_name"
                  id="first_name"
                  labelKey="first-name"
                  required
                  autoComplete="given-name"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextInput
                  fieldName="last_name"
                  id="last_name"
                  labelKey="last-name"
                  required
                  autoComplete="family-name"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextInput
                  fieldName="patronymic_name"
                  id="patronymic_name"
                  labelKey="patronymic-name"
                  fullWidth
                />
              </Grid>
            </Grid>

            <Box sx={{ my: 2 }} display="flex" justifyContent="end">
              <Link to="/auth/login">
                <FormattedMessage id="already-have-an-account-q" />
              </Link>
            </Box>

            {errors.submit && (
              <Box sx={{ mt: 3 }}>
                <FormHelperText error>{errors.submit}</FormHelperText>
              </Box>
            )}
            <Box sx={{ mt: 3 }}>
              <Button
                disableElevation
                disabled={isSubmitting}
                fullWidth
                size="large"
                type="submit"
                variant="contained"
                color="primary"
              >
                <FormattedMessage id="sign-up" />
              </Button>
            </Box>
          </form>
        )}
      </Formik>
    </FormWrapper>
  );
}
