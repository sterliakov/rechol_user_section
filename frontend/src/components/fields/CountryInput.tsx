import Box from '@mui/material/Box';
import type { Country } from 'country-code-lookup';
import { countries } from 'country-code-lookup';
import type { ReactNode } from 'react';

import AutocompleteInput from './AutocompleteInput';

function getCountryFlagSrc(code: string, width = 20): string {
  return `https://flagcdn.com/w${width}/${code.toLowerCase()}.png`;
}

export interface CountryInputProps {
  fieldName: string;
  labelKey: string;
  id: string;
  required?: boolean;
  readOnly?: boolean;
}

export default function CountryInput({
  fieldName,
  labelKey,
  id,
  required = false,
  readOnly,
}: CountryInputProps): ReactNode {
  return (
    <AutocompleteInput<Country>
      fieldName={fieldName}
      labelKey={labelKey}
      id={id}
      required={required}
      options={countries}
      getOptionLabel={(country) => country.country}
      getOptionValue={(country) => country.iso2}
      readOnly={readOnly}
      renderOption={(props, option: Country) => (
        <Box
          component="li"
          sx={{
            '& > img': {
              mr: 2,
              flexShrink: 0,
            },
          }}
          {...props}
        >
          <img
            loading="lazy"
            width="20"
            src={getCountryFlagSrc(option.iso2)}
            srcSet={`${getCountryFlagSrc(option.iso2, 40)} 2x`}
            alt=""
          />
          {option.country}
        </Box>
      )}
      autoComplete="country-name"
    />
  );
}
