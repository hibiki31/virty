import "vue-router";

declare module "vue-router" {
  interface RouteMeta {
    requiresAdmin?: boolean;
    projectFilter?: boolean;
    titleKey?: string;
  }
}
