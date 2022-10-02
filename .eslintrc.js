module.exports = {
  'env': {
    'browser': true,
    'commonjs': true,
    'jquery': true,
    'es2021': true,
  },
  'globals': {
    'gettext': 'readonly',
    'TableFilter': 'readonly',
    'Awesomplete': 'readonly',
    'moment': 'readonly',
    'inputDialog': 'readonly',
    'showAlert': 'writeable',
  },
  'extends': 'eslint:recommended',
  'parserOptions': {
    'ecmaVersion': 13,
  },
  'root': true,
  'rules': {
    'indent': [1, 2, {
      'SwitchCase': 1,
      'FunctionDeclaration': {'parameters': 'first'},
      'FunctionExpression': {'parameters': 'first'},
      'offsetTernaryExpressions': true,
      'MemberExpression': 'off',
      'CallExpression': {'arguments': 'first'},
    }],
    'linebreak-style': [2,'unix'],
    'quotes': [2, 'single'],
    'semi': [2, 'always'],
    'max-len': [1, 82, 2, {'ignoreUrls': true}],
    'no-trailing-spaces': 2,
    'no-multi-spaces': 2,
    'array-bracket-spacing': 2,
    'keyword-spacing': ['error', {'after': true, 'before': true}],
    'max-depth': [2, 7],
    'max-statements': [2, 133],
    'complexity': [2, 45],
    'no-unused-vars': 2,
    'no-eval': 2,
    'no-underscore-dangle': 0,
    'no-loop-func': 2,
    'no-floating-decimal': 2,
    'eqeqeq': [2, 'smart'],
    'new-cap': 2,
    'no-empty': 0,
    'space-infix-ops': 2,
    'comma-dangle': ['error', 'always-multiline'],
  },
};
