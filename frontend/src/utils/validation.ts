import { matchIsValidTel } from 'mui-tel-input';
import * as Yup from 'yup';

Yup.addMethod(Yup.string, 'phone', function (errorMessage) {
  return this.test(`test-phone`, errorMessage, function (value) {
    const { path, createError } = this;

    // Allow phone as non-required field
    if (!value || value.length === 0) {
      return true;
    }

    return matchIsValidTel(value) || createError({ path, message: errorMessage });
  });
});

export class YupErrorExt {
  public id: string;
  public values?: Record<string, any>;

  constructor(id: string, values?: Record<string, any>) {
    this.id = id;
    this.values = values;
  }
}

Yup.setLocale({
  mixed: {
    required: 'required-field',
  },
  string: {
    max: ({ max }) => new YupErrorExt('e-string-max', { max }),
    min: ({ min }) => new YupErrorExt('e-string-min', { min }),
  },
});

declare module 'yup' {
  interface StringSchema {
    phone: () => StringSchema;
  }
}
