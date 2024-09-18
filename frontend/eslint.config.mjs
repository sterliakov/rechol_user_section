import muiPathImports from 'eslint-plugin-mui-path-imports';
import globals from 'globals';
import { parser } from 'typescript-eslint';

export default [
  {
    files: ['src/**/*.ts', 'src/**/*.tsx'],
    settings: {
      'import/resolver': {
        typescript: {
          paths: 'src',
        },
      },
    },
    plugins: {
      'mui-path-imports': muiPathImports,
    },
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      parser,
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      'mui-path-imports/mui-path-imports': 'error',
    },
  },
];
