import eslintJsConfig from '@eslint/js';
import loveBaseLine from 'eslint-config-love';
import prettierConfig from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';
import muiPathImports from 'eslint-plugin-mui-path-imports';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';
import globals from 'globals';

const JS_FILES = ['*.js', '*.cjs', '*.mjs'];

export default [
  {
    files: JS_FILES,
    plugins: { import: importPlugin },
    rules: {
      ...eslintJsConfig.configs.recommended.rules,
      ...prettierConfig.rules,
      'import/export': ['error'],
      'import/first': ['error'],
      'import/no-absolute-path': [
        'error',
        { esmodule: true, commonjs: true, amd: false },
      ],
      'import/no-duplicates': ['error'],
      'import/no-named-default': ['error'],
      'import/no-webpack-loader-syntax': ['error'],
      'import/order': [
        'error',
        {
          alphabetize: {
            order: 'asc',
            orderImportKind: 'asc',
          },
        },
      ],
    },
    languageOptions: {
      globals: { ...globals.node },
    },
  },
  {
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
    },
    languageOptions: {
      ...loveBaseLine.languageOptions,
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      'react/no-unescaped-entities': 'off',
      'react-hooks/exhaustive-deps': 'error',
    },
    ignores: JS_FILES,
  },
  {
    ...loveBaseLine,
    files: ['src/**/*.ts', 'src/**/*.tsx'],
    settings: {
      'import/resolver': {
        typescript: {
          paths: 'src',
        },
      },
    },
    plugins: {
      ...loveBaseLine.plugins,
      'mui-path-imports': muiPathImports,
    },
    rules: {
      ...loveBaseLine.rules,
      ...prettierConfig.rules,
      'mui-path-imports/mui-path-imports': 'error',
      // My stylistic preferences
      'import/order': [
        'error',
        {
          groups: ['builtin', 'external', 'internal', ['parent', 'sibling', 'index']],
          'newlines-between': 'always',

          alphabetize: {
            order: 'asc',
            orderImportKind: 'asc',
          },
        },
      ],
      'prefer-regex-literals': 'off',
      '@typescript-eslint/consistent-type-imports': [
        'error',
        {
          fixStyle: 'separate-type-imports',
        },
      ],
      // Stricter than default
      '@typescript-eslint/no-import-type-side-effects': 'error',
      // Too strict or just meaningless
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/init-declarations': 'off',
      //
      '@typescript-eslint/strict-boolean-expressions': 'off',
      '@typescript-eslint/explicit-function-return-type': 'off',
    },
    ignores: JS_FILES,
  },
];
