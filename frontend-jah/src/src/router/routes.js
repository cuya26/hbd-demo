
const routes = [
  {
    path: '/',
    component: () => import('frontend-jah/src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('frontend-jah/src/pages/IndexPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('frontend-jah/src/pages/ErrorNotFound.vue')
  }
]

export default routes
