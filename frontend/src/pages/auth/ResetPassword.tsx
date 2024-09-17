import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid2';
import { Formik } from 'formik';
import { FormattedMessage } from 'react-intl';
import * as Yup from 'yup';

import TextInput from 'components/fields/TextInput';
import FormWrapper from 'layout/FormWrapper';
import axios from 'utils/axios';
import { getErrors } from 'utils/errors';

interface FormState {
  email: string;
  submit: string | null;
}
const initialState: FormState = {
  email: '',
  submit: null,
};

const schema = Yup.object().shape({
  email: Yup.string().email('email-invalid').max(255).required('required-field'),
});

async function resetPassword(email: string): Promise<void> {
  await axios.post('/api/auth/password/reset/', { email });
}

export default function ResetPassword() {
  return (
    <FormWrapper width="sm" titleId="reset-password" minWidth="450px">
      <Formik
        initialValues={initialState}
        validationSchema={schema}
        onSubmit={async (values, { setErrors }) => {
          try {
            await resetPassword(values.email);
            // FIXME: show alert and redirect to /
          } catch (err: any) {
            setErrors(getErrors(err?.response?.data));
          }
        }}
      >
        {({ errors, handleSubmit, isSubmitting }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid size={12}>
                <TextInput
                  fieldName="email"
                  id="email"
                  labelKey="email-address"
                  required
                  autoComplete="email"
                  fullWidth
                />
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
