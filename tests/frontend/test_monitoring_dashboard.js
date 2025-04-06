/**
 * DockerForge Frontend Tests - Monitoring Dashboard
 */

import { mount } from '@vue/test-utils';
import { createStore } from 'vuex';
import MonitoringDashboard from '@/views/monitoring/MonitoringDashboard.vue';
import axios from 'axios';
import Chart from 'chart.js/auto';

// Mock axios
jest.mock('axios');

// Mock chart.js
jest.mock('chart.js/auto', () => {
  return {
    __esModule: true,
    default: jest.fn().mockImplementation(() => {
      return {
        update: jest.fn(),
        destroy: jest.fn()
      };
    })
  };
});

// Mock the monitoring service
jest.mock('@/services/monitoring', () => {
  return {
    getHostMetrics: jest.fn().mockResolvedValue({
      timestamp: '2023-01-01T00:00:00Z',
      cpu: {
        percent: 10.5,
        count: 8,
        physical_count: 4,
        frequency: {
          current: 2500,
          min: 800,
          max: 3500
        },
        times: {
          user: 5.0,
          system: 3.0,
          idle: 92.0
        }
      },
      memory: {
        virtual: {
          total: 16 * 1024 * 1024 * 1024,
          available: 8 * 1024 * 1024 * 1024,
          used: 8 * 1024 * 1024 * 1024,
          free: 8 * 1024 * 1024 * 1024,
          percent: 50.0
        },
        swap: {
          total: 8 * 1024 * 1024 * 1024,
          used: 1 * 1024 * 1024 * 1024,
          free: 7 * 1024 * 1024 * 1024,
          percent: 12.5
        }
      },
      disk: {
        usage: {
          '/': {
            total: 500 * 1024 * 1024 * 1024,
            used: 250 * 1024 * 1024 * 1024,
            free: 250 * 1024 * 1024 * 1024,
            percent: 50.0
          }
        },
        io: {
          read_count: 1000,
          write_count: 500,
          read_bytes: 1024 * 1024 * 1024,
          write_bytes: 512 * 1024 * 1024
        }
      },
      network: {
        io: {
          bytes_sent: 1024 * 1024 * 1024,
          bytes_recv: 2 * 1024 * 1024 * 1024,
          packets_sent: 10000,
          packets_recv: 20000
        }
      }
    }),
    getHostMetricsHistory: jest.fn().mockResolvedValue([
      {
        timestamp: '2023-01-01T00:00:00Z',
        data: {
          cpu_percent: 10.5,
          memory_percent: 50.0
        }
      },
      {
        timestamp: '2023-01-01T00:01:00Z',
        data: {
          cpu_percent: 15.2,
          memory_percent: 55.3
        }
      },
      {
        timestamp: '2023-01-01T00:02:00Z',
        data: {
          cpu_percent: 20.1,
          memory_percent: 60.7
        }
      }
    ]),
    getContainerMetrics: jest.fn().mockResolvedValue({
      cpu_percent: 10.5,
      memory_percent: 50.0,
      memory_usage: 1024 * 1024 * 1024,
      network_rx: 1024 * 1024 * 1024,
      network_tx: 512 * 1024 * 1024,
      block_read: 1024 * 1024 * 1024,
      block_write: 512 * 1024 * 1024
    }),
    getContainerMetricsHistory: jest.fn().mockResolvedValue([
      {
        timestamp: '2023-01-01T00:00:00Z',
        data: {
          cpu_percent: 10.5,
          memory_percent: 50.0
        }
      },
      {
        timestamp: '2023-01-01T00:01:00Z',
        data: {
          cpu_percent: 15.2,
          memory_percent: 55.3
        }
      },
      {
        timestamp: '2023-01-01T00:02:00Z',
        data: {
          cpu_percent: 20.1,
          memory_percent: 60.7
        }
      }
    ])
  };
});

// Mock the WebSocket
global.WebSocket = jest.fn().mockImplementation(() => {
  return {
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn()
  };
});

// Create a mock store
const createMockStore = () => {
  return createStore({
    state: {
      auth: {
        token: 'test-token',
        user: {
          id: 1,
          username: 'testuser'
        }
      }
    },
    getters: {
      'auth/isAuthenticated': () => true,
      'auth/token': () => 'test-token',
      'auth/user': () => ({
        id: 1,
        username: 'testuser'
      })
    }
  });
};

describe('MonitoringDashboard.vue', () => {
  let wrapper;
  let store;

  beforeEach(() => {
    // Create a fresh store for each test
    store = createMockStore();

    // Mock axios response for container list
    axios.get.mockResolvedValue({
      data: [
        {
          id: 'container1',
          name: 'container1',
          status: 'running'
        },
        {
          id: 'container2',
          name: 'container2',
          status: 'running'
        }
      ]
    });

    // Mount the component
    wrapper = mount(MonitoringDashboard, {
      global: {
        plugins: [store],
        stubs: ['router-link', 'router-view']
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
    jest.clearAllMocks();
  });

  test('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.monitoring-dashboard').exists()).toBe(true);
    expect(wrapper.find('.system-metrics').exists()).toBe(true);
    expect(wrapper.find('.container-resources').exists()).toBe(true);
    expect(wrapper.find('.alerts').exists()).toBe(true);
  });

  test('fetches monitoring data on mount', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Check that the monitoring data was fetched
    expect(axios.get).toHaveBeenCalled();
    expect(wrapper.vm.systemMetrics).toBeDefined();
    expect(wrapper.vm.containerResources).toBeDefined();
    expect(wrapper.vm.alerts).toBeDefined();
  });

  test('initializes charts correctly', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Check that the charts were initialized
    expect(Chart).toHaveBeenCalled();
    expect(wrapper.vm.charts.cpu).toBeDefined();
    expect(wrapper.vm.charts.memory).toBeDefined();
    expect(wrapper.vm.charts.disk).toBeDefined();
    expect(wrapper.vm.charts.network).toBeDefined();
  });

  test('shows container metrics dialog when a container is clicked', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Find the first container in the list
    const container = wrapper.vm.containerResources[0];

    // Show container metrics
    wrapper.vm.showContainerMetrics(container);

    // Check that the dialog is shown
    expect(wrapper.vm.containerMetricsDialog).toBe(true);
    expect(wrapper.vm.selectedContainer).toBe(container);
  });

  test('acknowledges an alert', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Add a mock alert
    wrapper.vm.alerts = [
      {
        id: 'alert1',
        title: 'Test Alert',
        description: 'This is a test alert',
        severity: 'warning',
        timestamp: '2023-01-01T00:00:00Z',
        acknowledged: false,
        resolved: false
      }
    ];

    // Mock the axios post response
    axios.post.mockResolvedValue({
      data: {
        status: 'success',
        message: 'Alert acknowledged'
      }
    });

    // Acknowledge the alert
    await wrapper.vm.acknowledgeAlert(wrapper.vm.alerts[0]);

    // Check that the alert was acknowledged
    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/monitoring/alerts/alert1/acknowledge'),
      expect.any(Object),
      expect.any(Object)
    );
    expect(wrapper.vm.alerts[0].acknowledged).toBe(true);
  });

  test('resolves an alert', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Add a mock alert
    wrapper.vm.alerts = [
      {
        id: 'alert1',
        title: 'Test Alert',
        description: 'This is a test alert',
        severity: 'warning',
        timestamp: '2023-01-01T00:00:00Z',
        acknowledged: false,
        resolved: false
      }
    ];

    // Mock the axios post response
    axios.post.mockResolvedValue({
      data: {
        status: 'success',
        message: 'Alert resolved'
      }
    });

    // Resolve the alert
    await wrapper.vm.resolveAlert(wrapper.vm.alerts[0]);

    // Check that the alert was resolved
    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/monitoring/alerts/alert1/resolve'),
      expect.any(Object),
      expect.any(Object)
    );
    expect(wrapper.vm.alerts[0].resolved).toBe(true);

    // Wait for the alert to be removed
    jest.advanceTimersByTime(500);
    await wrapper.vm.$nextTick();

    // Check that the alert was removed
    expect(wrapper.vm.alerts.length).toBe(0);
  });

  test('closes WebSocket connection when dialog is closed', async () => {
    // Wait for the component to finish mounting
    await wrapper.vm.$nextTick();

    // Find the first container in the list
    const container = wrapper.vm.containerResources[0];

    // Show container metrics
    wrapper.vm.showContainerMetrics(container);

    // Check that the dialog is shown
    expect(wrapper.vm.containerMetricsDialog).toBe(true);
    expect(wrapper.vm.selectedContainer).toBe(container);

    // Create a mock WebSocket
    wrapper.vm.containerWebSocket = {
      close: jest.fn()
    };

    // Close the dialog
    wrapper.vm.containerMetricsDialog = false;

    // Wait for the watcher to run
    await wrapper.vm.$nextTick();

    // Check that the WebSocket was closed
    expect(wrapper.vm.containerWebSocket.close).toHaveBeenCalled();
    expect(wrapper.vm.containerWebSocket).toBe(null);
  });
});
