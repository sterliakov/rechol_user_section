/**
 * Password validator for login pages
 */
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import type { ReactNode } from 'react';

// has number
const hasNumber = (passwd: string): boolean => /[0-9]/.test(passwd);

// has mix of small and capitals
const hasMixed = (passwd: string): boolean =>
  /[a-z]/.test(passwd) && /[A-Z]/.test(passwd);

// has special chars
const hasSpecial = (passwd: string): boolean => /[!#@$%^&*)(+=._-]/.test(passwd);

interface PasswordQuality {
  label: string;
  color: string;
}
// set color based on password strength
function strengthColor(count: number): PasswordQuality {
  if (count < 2) return { label: 'Poor', color: 'error' };
  if (count < 3) return { label: 'Weak', color: 'warning' };
  if (count < 4) return { label: 'Normal', color: 'orange' };
  if (count < 5) return { label: 'Good', color: 'success' };
  if (count < 6) return { label: 'Strong', color: 'success.dark' };
  return { label: 'Poor', color: 'error' };
}

// password strength indicator
function strengthIndicator(passwd: string): number {
  let strengths = 0;
  if (passwd.length > 5) strengths += 1;
  if (passwd.length > 7) strengths += 1;
  if (hasNumber(passwd)) strengths += 1;
  if (hasSpecial(passwd)) strengths += 1;
  if (hasMixed(passwd)) strengths += 1;
  return strengths;
}

interface StrengthIndicatorProps {
  password: string;
}

const StrengthIndicator = ({ password }: StrengthIndicatorProps): ReactNode => {
  const strength = strengthIndicator(password);
  const level = strengthColor(strength);

  return strength !== 0 ? (
    <FormControl fullWidth>
      <Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Box
              sx={{
                backgroundColor: level?.color,
                width: 85,
                height: 8,
                borderRadius: '7px',
              }}
            />
          </Grid>
          <Grid item>
            <Typography variant="subtitle1" fontSize="0.75rem">
              {level?.label}
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </FormControl>
  ) : null;
};

export default StrengthIndicator;
