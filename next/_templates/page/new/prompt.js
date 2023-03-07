module.exports = [
  {
    type: 'input',
    name: 'url',
    message: 'What is the URL of the page? (e.g. users/[id])',
    required: true,
  },
  {
    type: 'select',
    name: 'pageType',
    message: 'What type of page is this?',
    choices: ['login', 'logout', 'simple'],
    initial: 'login',
  },
];
