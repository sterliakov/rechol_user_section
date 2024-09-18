import { readFileSync } from 'node:fs';
import react from '@vitejs/plugin-react';
import { createFilter, defineConfig, transformWithEsbuild } from 'vite';
import checker from 'vite-plugin-checker';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths(),
    importPrefixPlugin(),
    svgrPlugin(),
    checker({ typescript: true }),
  ],
});

/**
 * To resolve modules from node_modules, you can prefix paths with ~
 *
 * https://create-react-app.dev/docs/adding-a-sass-stylesheet
 **/
function importPrefixPlugin() {
  return {
    name: 'import-prefix-plugin',
    config() {
      return {
        resolve: {
          alias: [{ find: /^~([^/])/, replacement: '$1' }],
        },
      };
    },
  };
}

/**
 * Support loading svg files as components
 **/
function svgrPlugin() {
  const filter = createFilter('**/*.svg');
  const postfixRE = /[?#].*$/s;

  return {
    name: 'svgr-plugin',
    async transform(code, id) {
      if (filter(id)) {
        const { transform } = await import('@svgr/core');
        const { default: jsx } = await import('@svgr/plugin-jsx');

        const filePath = id.replace(postfixRE, '');
        const svgCode = readFileSync(filePath, 'utf8');

        const componentCode = await transform(svgCode, undefined, {
          filePath,
          caller: {
            previousExport: code,
            defaultPlugins: [jsx],
          },
        });

        const res = await transformWithEsbuild(componentCode, id, {
          loader: 'jsx',
        });

        return {
          code: res.code,
          map: null,
        };
      }
    },
  };
}
