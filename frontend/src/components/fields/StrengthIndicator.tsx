/**
 * Password validator for login pages
 */
import { useTheme } from '@mui/material';
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
  colorLabel: string;
}
// set color based on password strength
function strengthColor(count: number): PasswordQuality {
  if (count < 2) return { label: 'Poor', colorLabel: 'error.main' };
  if (count < 3) return { label: 'Weak', colorLabel: 'warning.light' };
  if (count < 4) return { label: 'Normal', colorLabel: 'warning.main' };
  if (count < 5) return { label: 'Good', colorLabel: 'success.main' };
  if (count < 6) return { label: 'Strong', colorLabel: 'success.dark' };
  return { label: 'Poor', colorLabel: 'error.main' };
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
  const theme = useTheme();
  const strength = strengthIndicator(password);
  const { label, colorLabel } = strengthColor(strength);
  const [colorName, colorLevel] = colorLabel.split('.');
  // @ts-expect-error I don't want to do trash typing for these labels
  const color = theme.palette[colorName][colorLevel ?? 'main'];
  console.log(theme.palette, colorName, colorLevel);

  return strength !== 0 ? (
    <FormControl fullWidth>
      <Box>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Box
              sx={{
                backgroundColor: color,
                width: 85,
                height: 8,
                borderRadius: '7px',
              }}
            />
          </Grid>
          <Grid item>
            <Typography variant="subtitle1" fontSize="0.75rem">
              {label}
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </FormControl>
  ) : null;
};

export default StrengthIndicator;
