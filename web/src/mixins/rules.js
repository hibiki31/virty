import Vue from 'vue';

Vue.mixin({
  methods: {
    // 必須
    $required: (value) => !!value || 'Required.',
    // 64文字以下
    $limitLength64: (value) => value.length <= 64 || '64 characters maximum.',
    // 文字種制限
    $characterRestrictions(value) {
      const regex = /^[A-Za-z0-9-_]*$/;
      return regex.test(value) || 'Can use character A-Z, a-z, 0-9, -, _';
    },
    // 先頭文字制限
    $firstCharacterRestrictions(value) {
      const regex = /^[A-Za-z].*/;
      return regex.test(value) || 'Can use first character A-Z, a-z';
    },
    // 数字だけ
    $intValueRestrictions(value) {
      const regex = /^[0-9]*$/;
      return regex.test(value) || 'Only Int value';
    },
    $hostNameCharacter(value) {
      const regex = /^[A-Za-z0-9-]*$/;
      return regex.test(value) || 'Can use character A-Z, a-z, 0-9, -';
    }
  }
});
