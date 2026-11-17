import tcsEslint from '@typescript-eslint/eslint-plugin';
import parser from '@typescript-eslint/parser';

const eslintConfig = [
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      },
      rules: {
        'react/react-in-jsx-scope': 'off',
        'import/no-extraneous-dependencies': 'off'
      }
    },
    plugins: ['react', 'typescript', 'import', 'tailwindcss', 'stylistic'],
    settings: {
      react: {
        version: '18.3'
      },
      'import/parsers': {
        '@typescript-eslint/parser': ['.ts', '.tsx']
      },
      'import/resolver': {
        node: {
          extensions: ['.js', '.jsx', '.ts', '.tsx']
        }
      }
    }
  },
  {
    files: ['**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx'],
    rules: {
      'stylistic/indent': ['error', 2],
      'stylistic/semi': ['error', 'always'],
      'stylistic/quotes': ['error', 'double'],
      'tailwindcss/class-name': ['error', {
        'regex': '(^|[\\s/])(bg|text|border|px|py|px)[(\\s]',
        'exactMatch': true
      }]
    }
  }
];

export default eslintConfig;