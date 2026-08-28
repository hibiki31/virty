import "vue-router";

declare module "vue-router" {
  interface RouteMeta {
    requiresAdmin?: boolean;
    titleKey?: string;
  }
}
