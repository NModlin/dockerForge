// Router configuration for DockerForge Web UI

// Import Dashboard component
import Dashboard from './views/Dashboard.vue';

// Define routes
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/change-password',
    name: 'PasswordChange',
    component: () => import('./views/user/PasswordChange.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/containers',
    name: 'Containers',
    component: () => import('./views/containers/ContainerList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/containers/:id',
    name: 'ContainerDetail',
    component: () => import('./views/containers/ContainerDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/images',
    name: 'Images',
    component: () => import('./views/images/ImageList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/images/:id',
    name: 'ImageDetail',
    component: () => import('./views/images/ImageDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/images/:id/security/:scanId',
    name: 'ImageSecurity',
    component: () => import('./views/images/ImageSecurity.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/volumes',
    name: 'Volumes',
    component: () => import('./views/volumes/VolumeList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/volumes/:id',
    name: 'VolumeDetail',
    component: () => import('./views/volumes/VolumeDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/networks',
    name: 'Networks',
    component: () => import('./views/networks/NetworkList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/networks/:id',
    name: 'NetworkDetail',
    component: () => import('./views/networks/NetworkDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/compose',
    name: 'Compose',
    component: () => import('./views/compose/ComposeList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/compose/:id',
    name: 'ComposeDetail',
    component: () => import('./views/compose/ComposeDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/security',
    name: 'Security',
    component: () => import('./views/security/SecurityDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/backup',
    name: 'Backup',
    component: () => import('./views/backup/BackupList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('./views/monitoring/MonitoringDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/settings/Settings.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('./views/NotFound.vue'),
  },
];

export default routes;
