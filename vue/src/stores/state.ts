import { defineStore } from "pinia";

export const useStateStore = defineStore("state", {
  state: () => ({
    pageIndex: 1,
    showSideDrawer: true,
  }),
  actions: {},
});
