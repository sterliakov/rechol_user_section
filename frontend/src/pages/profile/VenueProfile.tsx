import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import { Formik } from 'formik';
import { useEffect, useState } from 'react';
import { FormattedMessage } from 'react-intl';
import * as Yup from 'yup';

import FileInput from 'components/fields/FileInput';
import PhoneInput from 'components/fields/PhoneInput';
import TextInput from 'components/fields/TextInput';
import useConfig from 'contexts/ConfigContext';
import { ReadOnlyFormProvider } from 'contexts/ReadOnlyFormContext';
import type { Venue } from 'contexts/VenuesContext';
import useAlerts from 'hooks/useAlerts';
import FormWrapper from 'layout/FormWrapper';
import axios from 'utils/axios';
import { getErrors } from 'utils/errors';

interface FormState extends Omit<Venue, 'id' | 'is_full'> {
  is_confirmed: boolean;
  confirmation_letter: File | null;
  submit: string | null;
}

const initialState: FormState = {
  city: '',
  short_name: '',
  full_name: '',
  full_address: '',
  contact_phone: '',
  confirmation_letter: null,
  is_confirmed: false,
  submit: null,
};

const profileSchema = Yup.object().shape({
  city: Yup.string().max(63).required('required-field'),
  short_name: Yup.string().max(63).required('required-field'),
  full_name: Yup.string().max(255).required('required-field'),
  full_address: Yup.string().max(255).required('required-field'),
  contact_phone: Yup.string().phone().required('required-field'),
});

async function readProfile(): Promise<FormState> {
  const response = await axios.get('/api/v1/profile/venue/');
  return { ...response.data, submit: null };
}
async function updateProfile(
  params: Omit<FormState, 'submit' | 'is_confirmed'>,
): Promise<void> {
  const formData = new FormData();
  for (const [key, value] of Object.entries(params)) {
    if (value != null) {
      formData.append(key, value);
    }
  }
  await axios.put('/api/v1/profile/venue/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

export default function VenueProfile() {
  const [fullProfile, setFullProfile] = useState<FormState>();
  const { config } = useConfig();
  const { showAlert } = useAlerts();

  useEffect(() => {
    readProfile().then(setFullProfile);
  }, []);

  const now = new Date();
  const registrationEnded =
    config != null && new Date(config.venue_registration_end) < now;
  const registrationNotStarted =
    config != null && new Date(config.venue_registration_start) > now;

  return (
    <FormWrapper width="min(1200px, 100vw)" titleId="profile" minWidth="300px">
      {config == null ? (
        <Box
          width="100%"
          display="flex"
          alignItems="center"
          justifyContent="center"
          py={4}
        >
          <CircularProgress />
        </Box>
      ) : registrationNotStarted ? (
        <Typography variant="h4" component="p" pb={3} width="100%" textAlign="center">
          <FormattedMessage id="registration-not-started" />
        </Typography>
      ) : (
        <Formik<FormState>
          initialValues={fullProfile ?? initialState}
          validationSchema={profileSchema}
          onSubmit={async ({ submit, is_confirmed: _, ...values }, { setErrors }) => {
            try {
              await updateProfile(values);
              showAlert('success', 'alert-profile-updated');
            } catch (err: any) {
              setErrors(getErrors(err?.response?.data));
            }
          }}
          enableReinitialize
        >
          {({ errors, handleSubmit, isSubmitting }) => (
            <ReadOnlyFormProvider readonly={registrationEnded}>
              <form noValidate onSubmit={handleSubmit}>
                {registrationEnded && (
                  <Typography
                    variant="h4"
                    component="p"
                    pb={3}
                    width="100%"
                    textAlign="center"
                  >
                    <FormattedMessage id="registration-ended" />
                  </Typography>
                )}
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, lg: 6 }}>
                    <TextInput
                      fieldName="city"
                      id="city"
                      labelKey="city"
                      fullWidth
                      required
                    />
                  </Grid>
                  <Grid size={{ xs: 12, lg: 6 }}>
                    <PhoneInput
                      fieldName="contact_phone"
                      id="phone"
                      labelKey="phone"
                      required
                    />
                  </Grid>
                </Grid>

                <Grid container pt={2} spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    <TextInput
                      fieldName="full_name"
                      id="full_name"
                      labelKey="venue-full-name"
                      required
                    />
                  </Grid>
                </Grid>

                <Grid container pt={2} spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    <TextInput
                      fieldName="short_name"
                      id="short_name"
                      labelKey="venue-short-name"
                      required
                      helperText={
                        <FormHelperText>
                          <FormattedMessage id="venue-short-name-explained" />
                        </FormHelperText>
                      }
                    />
                  </Grid>
                </Grid>

                <Grid container pt={2} spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    <TextInput
                      fieldName="full_address"
                      id="full_address"
                      labelKey="venue-full-address"
                      required
                    />
                  </Grid>
                </Grid>

                <Grid container pt={2} spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    <FileInput
                      fieldName="confirmation_letter"
                      id="confirmation_letter"
                      labelKey="venue-confirmation-letter"
                      required
                      helperText={
                        <FormHelperText>
                          <FormattedMessage id="venue-confirmation-letter-explained" />
                        </FormHelperText>
                      }
                    />
                  </Grid>
                </Grid>

                <Grid container pt={2} spacing={2}>
                  <Grid size={{ xs: 12 }}>
                    {fullProfile?.is_confirmed ? (
                      <Typography variant="body2" color="success.dark">
                        <FormattedMessage id="venue-confirmed" />
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="error.dark">
                        <FormattedMessage id="venue-wait-for-confirmation" />
                      </Typography>
                    )}
                  </Grid>
                </Grid>

                {errors.submit && (
                  <Box sx={{ mt: 3 }}>
                    <FormHelperText error>{errors.submit}</FormHelperText>
                  </Box>
                )}
                <Box sx={{ mt: 3 }}>
                  <Button
                    disableElevation
                    disabled={
                      isSubmitting || registrationNotStarted || registrationEnded
                    }
                    fullWidth
                    size="large"
                    type="submit"
                    variant="contained"
                    color="primary"
                  >
                    <FormattedMessage id="save" />
                  </Button>
                </Box>
              </form>
            </ReadOnlyFormProvider>
          )}
        </Formik>
      )}
    </FormWrapper>
  );
}
