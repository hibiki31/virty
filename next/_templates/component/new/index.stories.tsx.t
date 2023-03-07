---
to: "<%= storybook ? `${path}/${name}/index.stories.tsx` : null %>"
---

import { ComponentMeta } from '@storybook/react';
import { <%= name %> } from '.';

export default {
  title: '<%= name %>',
  component: <%= name %>,
} as ComponentMeta<typeof <%= name %>>;

export const Default = {
  args: {},
};
