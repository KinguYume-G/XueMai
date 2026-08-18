import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";

/** @type {import('eslint').Linter.Config[]} */
export default [
  { files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"] },
  { languageOptions: { globals: globals.browser } },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  pluginReact.configs.flat.recommended,
  {
    settings: {
      react: {
        version: "detect"
      }
    },
    rules: {
      // React 17+ 不需要 import React
      "react/react-in-jsx-scope": "off",
      // TypeScript 项目不需要 PropTypes
      "react/prop-types": "off",
      // 允许 any（可以后续逐步修复）
      "@typescript-eslint/no-explicit-any": "warn",
      // 未使用变量改为警告
      "@typescript-eslint/no-unused-vars": "warn",
      // 空接口允许
      "@typescript-eslint/no-empty-object-type": "off"
    }
  }
];