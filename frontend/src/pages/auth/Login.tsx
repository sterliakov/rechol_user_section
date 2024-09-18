import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import { Formik } from 'formik';
import { FormattedMessage } from 'react-intl';
import { Link, useNavigate } from 'react-router-dom';
import * as Yup from 'yup';

import PasswordInput from 'components/fields/PasswordInput';
import TextInput from 'components/fields/TextInput';
import useAuth from 'contexts/AuthContext';
import FormWrapper from 'layout/FormWrapper';
import { getErrors } from 'utils/errors';

interface FormState {
  email: string;
  password: string;
  submit: string | null;
}
const initialState: FormState = {
  email: '',
  password: '',
  submit: null,
};

const schema = Yup.object().shape({
  email: Yup.string().email('email-invalid').max(255).required('required-field'),
  password: Yup.string().max(255).required('required-field'),
});

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  return (
    <FormWrapper width="sm" titleId="sign-in" minWidth="min(100vw,450px)">
      <Formik
        initialValues={initialState}
        validationSchema={schema}
        onSubmit={async (values, { setErrors }) => {
          try {
            const user = await login(values);
            navigate(`/profile/${user.fullRole}`);
          } catch (err: any) {
            setErrors(getErrors(err?.response?.data));
          }
        }}
      >
        {({ errors, handleSubmit, isSubmitting }) => (
          <form noValidate onSubmit={handleSubmit}>
            <TextInput
              fieldName="email"
              id="email"
              labelKey="email-address"
              required
              autoComplete="email"
              fullWidth
            />

            <Box sx={{ mt: 3 }} />

            <PasswordInput
              fieldName="password"
              id="password"
              labelKey="password"
              required
              autoComplete="current-password"
              fullWidth
            />

            <Box sx={{ my: 2 }} display="flex" justifyContent="end">
              <Link to="/auth/reset-password/begin">
                <FormattedMessage id="forgot-password-q" />
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
                <FormattedMessage id="sign-in" />
              </Button>
            </Box>
          </form>
        )}
      </Formik>
    </FormWrapper>
  );
}
