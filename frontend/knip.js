const config = {
  eslint: true,
  entry: ['src/main.tsx', 'vite.config.js', 'eslint.config.mjs'],
  ignore: ['build/**/*'],
  // Allow e.g. component props type export, even if not used
  ignoreExportsUsedInFile: {
    interface: true,
    type: true,
    enum: true,
  },
};

export default config;
