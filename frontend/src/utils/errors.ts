const DEFAULT_ERROR = 'An unknown error occurred, please try again later.';

interface MinimalForm {
  submit: string | null;
}
type NullToUndefined<T> = {
  [K in keyof T]: T[K] extends unknown | null ? Exclude<T[K], null> | undefined : T[K];
};
export function getErrors<T extends MinimalForm>(
  response: any
): NullToUndefined<T | MinimalForm> {
  if (!response) return { submit: DEFAULT_ERROR };

  let errors: MinimalForm = { submit: null };
  for (const [field, value] of Object.entries(response)) {
    if (field === 'errors') {
      const nestedErrors = Object.fromEntries(
        Object.entries(value as any).map(([f, v]: [any, any]) => [f, v.join('; ')])
      );
      errors = {
        ...errors,
        ...nestedErrors,
        submit: [errors.submit, nestedErrors.submit].filter(Boolean).join('; ') || null,
      };
    } else if (field === 'non_field_errors') {
      if (!Array.isArray(value)) throw new Error('Expected array');
      const errString = value.join('; ');
      errors.submit = errors.submit == null ? errString : '; ' + errString;
    } else {
      // @ts-expect-error I don't care about safety of this function
      errors[field] = value;
    }
  }
  return Object.fromEntries(
    Object.entries(errors).map(([k, v]) => [k, v ?? undefined])
  ) as any;
}
