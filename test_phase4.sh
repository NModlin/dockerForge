#!/bin/bash

# Test script for Phase 4 of DockerForge
# This script tests the notification and fix functionality

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if DockerForge is installed
check_installation() {
    print_header "Checking DockerForge Installation"
    
    if ! command -v dockerforge &> /dev/null; then
        print_error "DockerForge is not installed or not in PATH"
        exit 1
    fi
    
    print_success "DockerForge is installed"
}

# Test notification functionality
test_notifications() {
    print_header "Testing Notification Functionality"
    
    # Test sending a notification
    print_info "Sending a test notification..."
    dockerforge notify send --title "Test Notification" --message "This is a test notification from the test script" --severity info
    
    if [ $? -eq 0 ]; then
        print_success "Notification sent successfully"
    else
        print_error "Failed to send notification"
    fi
    
    # Test listing notifications
    print_info "Listing notifications..."
    dockerforge notify list --limit 5
    
    if [ $? -eq 0 ]; then
        print_success "Listed notifications successfully"
    else
        print_error "Failed to list notifications"
    fi
}

# Test fix functionality
test_fixes() {
    print_header "Testing Fix Functionality"
    
    # Create a test issue ID
    ISSUE_ID="test-issue-$(date +%s)"
    
    # Test creating a fix proposal
    print_info "Creating a test fix proposal..."
    FIX_OUTPUT=$(dockerforge notify fix create --issue "$ISSUE_ID" --title "Test Fix" --description "This is a test fix proposal" --risk low --step "Test Step 1|This is a test step|echo 'Hello from test step 1'" --step "Test Step 2|This is another test step|echo 'Hello from test step 2'")
    
    # Extract fix ID from output
    FIX_ID=$(echo "$FIX_OUTPUT" | grep "Fix proposal created" | grep -o "fix_[a-z0-9]*")
    
    if [ -n "$FIX_ID" ]; then
        print_success "Fix proposal created successfully with ID: $FIX_ID"
        echo "Extracted fix ID: $FIX_ID" # Print the actual ID for debugging
    else
        print_error "Failed to create fix proposal or extract fix ID"
        return
    fi
    
    # Test listing fixes
    print_info "Listing fixes..."
    dockerforge notify fix list
    
    if [ $? -eq 0 ]; then
        print_success "Listed fixes successfully"
    else
        print_error "Failed to list fixes"
    fi
    
    # Test showing fix details
    print_info "Showing fix details..."
    echo "Using fix ID: $FIX_ID" # Print the ID being used
    dockerforge notify fix show "$FIX_ID"
    
    if [ $? -eq 0 ]; then
        print_success "Showed fix details successfully"
    else
        print_error "Failed to show fix details"
    fi
    
    # Test approving a fix
    print_info "Approving fix..."
    echo "Using fix ID: $FIX_ID" # Print the ID being used
    dockerforge notify fix approve "$FIX_ID" --user "test-user"
    
    if [ $? -eq 0 ]; then
        print_success "Approved fix successfully"
    else
        print_error "Failed to approve fix"
    fi
    
    # Test applying a fix (dry run)
    print_info "Applying fix (dry run)..."
    echo "Using fix ID: $FIX_ID" # Print the ID being used
    dockerforge notify fix apply "$FIX_ID" --dry-run
    
    if [ $? -eq 0 ]; then
        print_success "Applied fix (dry run) successfully"
    else
        print_error "Failed to apply fix (dry run)"
    fi
}

# Test notification preferences
test_preferences() {
    print_header "Testing Notification Preferences"
    
    # Test setting notification preferences
    print_info "This would test setting notification preferences, but requires UI interaction"
    print_info "Skipping preference tests for automated testing"
}

# Test notification templates
test_templates() {
    print_header "Testing Notification Templates"
    
    # Test rendering a template
    print_info "This would test rendering notification templates"
    print_info "Skipping template tests for automated testing"
}

# Main function
main() {
    echo -e "${BLUE}DockerForge Phase 4 Test Script${NC}"
    echo -e "${YELLOW}Testing notification and fix functionality${NC}\n"
    
    # Check installation
    check_installation
    
    # Run tests
    test_notifications
    test_fixes
    test_preferences
    test_templates
    
    print_header "Test Summary"
    echo -e "${GREEN}Phase 4 testing completed${NC}"
}

# Run main function
main
