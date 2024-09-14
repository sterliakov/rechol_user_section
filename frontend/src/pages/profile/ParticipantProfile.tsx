import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import Grid from '@mui/material/Grid2';
import { Formik } from 'formik';
import { useEffect, useState } from 'react';
import { FormattedMessage } from 'react-intl';
import * as Yup from 'yup';

import CheckboxInput from 'components/fields/CheckboxInput';
import CountryInput from 'components/fields/CountryInput';
import DateInput from 'components/fields/DateInput';
import PasswordInput from 'components/fields/PasswordInput';
import PhoneInput from 'components/fields/PhoneInput';
import SelectInput from 'components/fields/SelectInput';
import TextInput from 'components/fields/TextInput';
import type { User } from 'contexts/AuthContext';
import useConfig from 'contexts/ConfigContext';
import useVenues from 'contexts/VenuesContext';
import FormWrapper from 'layout/FormWrapper';
import axios from 'utils/axios';
import { getErrors } from 'utils/errors';

type SupportedForm = 8 | 9 | 10 | 11;
const SUPPORTED_FORMS: SupportedForm[] = [8, 9, 10, 11];

export interface Participant extends User {
  passport: string;
  birth_date: string;
  gender: 'm' | 'f' | null;
  country: string;
  city: string;
  school: string;
  phone: string;
  actual_form: SupportedForm | 1 | null;
  participation_form: SupportedForm | null;
  vk_link: string;
  telegram_nickname: string;
  venue_selected: string | null;
  online_selected: boolean;
}

interface FormState extends Participant {
  password1: string;
  password2: string;
  submit: string | null;
}

const initialState: FormState = {
  email: '',
  first_name: '',
  last_name: '',
  patronymic_name: '',
  passport: '',
  birth_date: '',
  gender: null,
  country: '',
  city: '',
  school: '',
  phone: '',
  actual_form: null,
  participation_form: null,
  vk_link: '',
  telegram_nickname: '',
  venue_selected: null,
  online_selected: false,
  password1: '',
  password2: '',
  submit: null,
};

const today = new Date();
const earlieastBirthDate = new Date(+today - 21 * 365 * 24 * 60 * 60 * 1000);
const latestBirthDate = new Date(+today - 12 * 365 * 24 * 60 * 60 * 1000);
const editSchema = Yup.object().shape({
  email: Yup.string().max(255).required('required-field'),
  first_name: Yup.string().max(255).required('required-field'),
  last_name: Yup.string().max(255).required('required-field'),
  patronymic_name: Yup.string().max(255),
  passport: Yup.string().max(15).required('required-field'),
  birth_date: Yup.date()
    .min(earlieastBirthDate.toDateString(), 'birth-date-too-old')
    .max(latestBirthDate.toDateString(), 'birth-date-too-young')
    .required('required-field'),
  participation_form: Yup.number()
    .required('required-field')
    .when('actual_form', ([val], schema) => {
      if (!val) return schema;
      return schema.min(val, 'actual-form-above-participation');
    }),
});
const signupSchema = editSchema.concat(
  Yup.object().shape({
    password1: Yup.string().min(8, 'password-too-short').required('required-field'),
    password2: Yup.string().when('password1', ([val]) => {
      return val && val.length > 0
        ? Yup.string().oneOf([Yup.ref('password1')], 'passwords-dont-match')
        : Yup.string();
    }),
  })
);

async function readProfile(): Promise<Participant> {
  const response = await axios.get('/api/v1/profile/me/');
  return response.data;
}
async function registerParticipant(params: any): Promise<void> {
  await axios.post('/api/v1/register/', params);
}

export default function ParticipantProfile({ mode }: { mode: 'signup' | 'edit' }) {
  const [fullProfile, setFullProfile] = useState<Participant>();
  const { venues } = useVenues();
  const { config } = useConfig();

  useEffect(() => {
    if (mode === 'signup') return;
    readProfile().then(setFullProfile);
  }, [mode]);

  const formOptions = SUPPORTED_FORMS.map((f) => ({ id: f, value: f }));

  return (
    <FormWrapper
      width="min(1200px, 100vw)"
      titleId={mode === 'signup' ? 'sign-up' : 'profile'}
      minWidth="300px"
    >
      <Formik
        initialValues={fullProfile ? { ...fullProfile, submit: null } : initialState}
        validationSchema={mode === 'edit' ? editSchema : signupSchema}
        onSubmit={async (values, { setErrors }) => {
          values = {
            ...values,
            birth_date: new Date(values.birth_date).toISOString().slice(0, 10),
          };
          try {
            await registerParticipant(values);
          } catch (err: any) {
            setErrors(getErrors(err?.response?.data));
          }
        }}
        enableReinitialize
      >
        {({ errors, handleSubmit, isSubmitting }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container>
              <Grid size={{ xs: 12 }}>
                <TextInput
                  fieldName="email"
                  id="email"
                  labelKey="email-address"
                  required
                  autoComplete="email"
                  fullWidth
                  readOnly={mode === 'edit'}
                />
              </Grid>
            </Grid>
            {mode === 'signup' && (
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
            )}
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 4 }}>
                <TextInput
                  fieldName="first_name"
                  id="first_name"
                  labelKey="first-name"
                  required
                  autoComplete="given-name"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 4 }}>
                <TextInput
                  fieldName="last_name"
                  id="last_name"
                  labelKey="last-name"
                  required
                  autoComplete="family-name"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 4 }}>
                <TextInput
                  fieldName="patronymic_name"
                  id="patronymic_name"
                  labelKey="patronymic-name"
                  fullWidth
                />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 4 }}>
                <TextInput
                  fieldName="passport"
                  id="passport"
                  labelKey="passport"
                  required
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 4 }}>
                <DateInput
                  fieldName="birth_date"
                  id="birth_date"
                  labelKey="birth-date"
                  required
                  disableFuture
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 4 }}>
                <SelectInput
                  fieldName="gender"
                  id="gender"
                  labelKey="gender"
                  options={[
                    { id: 'm', value: <FormattedMessage id="male" /> },
                    { id: 'f', value: <FormattedMessage id="female" /> },
                  ]}
                  required
                />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <CountryInput
                  fieldName="country"
                  id="country"
                  labelKey="country"
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }}>
                <TextInput
                  fieldName="city"
                  id="city"
                  labelKey="city"
                  fullWidth
                  required
                />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 8 }}>
                <TextInput
                  fieldName="school"
                  id="school"
                  labelKey="school"
                  fullWidth
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 4 }}>
                <PhoneInput fieldName="phone" id="phone" labelKey="phone" required />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <SelectInput
                  fieldName="participation_form"
                  id="participation_form"
                  labelKey="participation-form"
                  options={formOptions}
                  required
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }}>
                <SelectInput
                  fieldName="actual_form"
                  id="actual_form"
                  labelKey="actual-form"
                  options={[
                    ...formOptions,
                    { id: 1, value: <FormattedMessage id="other" /> },
                  ]}
                  required
                />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <TextInput
                  fieldName="vk_link"
                  id="vk_link"
                  labelKey="vk-link"
                  fullWidth
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }}>
                <TextInput
                  fieldName="telegram_nickname"
                  id="telegram_nickname"
                  labelKey="telegram-nickname"
                  fullWidth
                />
              </Grid>
            </Grid>
            <Grid container pt={2} spacing={2}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <SelectInput
                  fieldName="venue_selected"
                  id="venue_selected"
                  labelKey="venue-selected"
                  disabled={!config?.forbid_venue_change}
                  options={(venues ?? []).map((v) => ({
                    id: v.id,
                    value: v.short_name,
                    disabled: v.is_full,
                  }))}
                />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="center">
                <CheckboxInput fieldName="online_selected" labelKey="online-selected" />
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
