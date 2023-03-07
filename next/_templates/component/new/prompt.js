module.exports = [
  {
    type: 'input',
    name: 'name',
    message: 'What is the name of the component? (e.g. MyButton)',
    required: true,
  },
  {
    type: 'input',
    name: 'path',
    message: 'Where is the directory of the component? (e.g. components/buttons)',
    initial: 'components',
  },
  {
    type: 'toggle',
    name: 'storybook',
    message: 'Do you want to create a storybook for this component?',
    enabled: 'Yes',
    disabled: 'No',
    initial: 'Yes',
  },
];
