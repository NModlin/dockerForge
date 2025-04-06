/**
 * DockerForge End-to-End Tests - Monitoring Dashboard
 */

describe('Monitoring Dashboard', () => {
  beforeEach(() => {
    // Log in before each test
    cy.visit('/login');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="password"]').type('testpassword');
    cy.get('button[type="submit"]').click();
    
    // Wait for login to complete
    cy.url().should('include', '/dashboard');
    
    // Navigate to the monitoring dashboard
    cy.visit('/monitoring');
  });
  
  it('displays the monitoring dashboard', () => {
    // Check that the monitoring dashboard is displayed
    cy.get('.monitoring-dashboard').should('be.visible');
    cy.get('.system-metrics').should('be.visible');
    cy.get('.container-resources').should('be.visible');
    cy.get('.alerts').should('be.visible');
  });
  
  it('displays system metrics', () => {
    // Check that the system metrics are displayed
    cy.get('.system-metrics').should('be.visible');
    cy.get('.system-metrics .cpu-usage').should('be.visible');
    cy.get('.system-metrics .memory-usage').should('be.visible');
    cy.get('.system-metrics .disk-usage').should('be.visible');
    cy.get('.system-metrics .network-usage').should('be.visible');
  });
  
  it('displays container resources', () => {
    // Check that the container resources are displayed
    cy.get('.container-resources').should('be.visible');
    cy.get('.container-resources .container-list').should('be.visible');
    
    // Check that at least one container is displayed
    cy.get('.container-resources .container-item').should('have.length.at.least', 1);
  });
  
  it('displays container metrics when a container is clicked', () => {
    // Click on the first container
    cy.get('.container-resources .container-item').first().click();
    
    // Check that the container metrics dialog is displayed
    cy.get('.container-metrics-dialog').should('be.visible');
    cy.get('.container-metrics-dialog .container-name').should('be.visible');
    cy.get('.container-metrics-dialog .container-id').should('be.visible');
    cy.get('.container-metrics-dialog .container-metrics').should('be.visible');
    
    // Check that the metrics tabs are displayed
    cy.get('.container-metrics-dialog .metrics-tabs').should('be.visible');
    cy.get('.container-metrics-dialog .metrics-tabs .tab').should('have.length', 4);
    
    // Check that the CPU metrics are displayed by default
    cy.get('.container-metrics-dialog .cpu-metrics').should('be.visible');
    cy.get('.container-metrics-dialog .cpu-chart').should('be.visible');
    
    // Click on the memory tab
    cy.get('.container-metrics-dialog .metrics-tabs .tab').eq(1).click();
    
    // Check that the memory metrics are displayed
    cy.get('.container-metrics-dialog .memory-metrics').should('be.visible');
    cy.get('.container-metrics-dialog .memory-chart').should('be.visible');
    
    // Click on the network tab
    cy.get('.container-metrics-dialog .metrics-tabs .tab').eq(2).click();
    
    // Check that the network metrics are displayed
    cy.get('.container-metrics-dialog .network-metrics').should('be.visible');
    cy.get('.container-metrics-dialog .network-chart').should('be.visible');
    
    // Click on the disk tab
    cy.get('.container-metrics-dialog .metrics-tabs .tab').eq(3).click();
    
    // Check that the disk metrics are displayed
    cy.get('.container-metrics-dialog .disk-metrics').should('be.visible');
    cy.get('.container-metrics-dialog .disk-chart').should('be.visible');
    
    // Close the dialog
    cy.get('.container-metrics-dialog .close-button').click();
    
    // Check that the dialog is closed
    cy.get('.container-metrics-dialog').should('not.exist');
  });
  
  it('displays alerts', () => {
    // Check that the alerts section is displayed
    cy.get('.alerts').should('be.visible');
    
    // If there are alerts, check their structure
    cy.get('.alerts .alert-item').then(($alerts) => {
      if ($alerts.length > 0) {
        // Check the first alert
        cy.get('.alerts .alert-item').first().within(() => {
          cy.get('.alert-title').should('be.visible');
          cy.get('.alert-description').should('be.visible');
          cy.get('.alert-severity').should('be.visible');
          cy.get('.alert-timestamp').should('be.visible');
          cy.get('.alert-actions').should('be.visible');
          cy.get('.alert-actions .acknowledge-button').should('be.visible');
          cy.get('.alert-actions .resolve-button').should('be.visible');
        });
      }
    });
  });
  
  it('acknowledges an alert', () => {
    // If there are alerts, acknowledge the first one
    cy.get('.alerts .alert-item').then(($alerts) => {
      if ($alerts.length > 0) {
        // Check if the alert is already acknowledged
        cy.get('.alerts .alert-item').first().then(($alert) => {
          if (!$alert.find('.alert-acknowledged').length) {
            // Acknowledge the alert
            cy.get('.alerts .alert-item').first().find('.alert-actions .acknowledge-button').click();
            
            // Check that the alert is acknowledged
            cy.get('.alerts .alert-item').first().find('.alert-acknowledged').should('be.visible');
          }
        });
      }
    });
  });
  
  it('resolves an alert', () => {
    // If there are alerts, resolve the first one
    cy.get('.alerts .alert-item').then(($alerts) => {
      if ($alerts.length > 0) {
        // Get the number of alerts before resolving
        const alertCount = $alerts.length;
        
        // Resolve the first alert
        cy.get('.alerts .alert-item').first().find('.alert-actions .resolve-button').click();
        
        // Check that the alert is removed
        cy.wait(500); // Wait for the alert to be removed
        cy.get('.alerts .alert-item').should('have.length', alertCount - 1);
      }
    });
  });
  
  it('refreshes monitoring data automatically', () => {
    // Wait for the auto-refresh interval
    cy.wait(30000); // 30 seconds
    
    // Check that the monitoring data is refreshed
    cy.get('.system-metrics .last-updated').should('contain', 'Last updated:');
  });
});
