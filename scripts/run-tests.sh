#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [TEST_ARGS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -u, --unit          Run unit tests only"
    echo "  -i, --integration   Run integration tests only"
    echo "  -a, --api           Run API tests only"
    echo "  -s, --sync          Run sync tests only"
    echo "  -b, --bulk          Run bulk upload tests only"
    echo "  -c, --coverage      Run tests with coverage"
    echo "  -v, --verbose       Run tests with verbose output"
    echo "  -d, --down          Stop test containers after running"
    echo "  --setup             Setup test environment only"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 -u                 # Run unit tests only"
    echo "  $0 -i -v              # Run integration tests with verbose output"
    echo "  $0 -c --coverage      # Run all tests with coverage"
    echo "  $0 tests/test_unit.py # Run specific test file"
    echo "  $0 -k 'test_employee' # Run tests matching pattern"
}

# Default values
TEST_TYPE="all"
VERBOSE=""
COVERAGE=""
STOP_AFTER=""
TEST_ARGS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--unit)
            TEST_TYPE="unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            shift
            ;;
        -a|--api)
            TEST_TYPE="api"
            shift
            ;;
        -s|--sync)
            TEST_TYPE="sync"
            shift
            ;;
        -b|--bulk)
            TEST_TYPE="bulk"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=apps --cov-report=html --cov-report=term"
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -d|--down)
            STOP_AFTER="--down"
            shift
            ;;
        --setup)
            TEST_TYPE="setup"
            shift
            ;;
        -*)
            print_error "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            TEST_ARGS="$TEST_ARGS $1"
            shift
            ;;
    esac
done

# Function to setup test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Start test containers
    docker-compose -f docker-compose.test.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose -f docker-compose.test.yml exec test-runner python manage.py migrate
    
    # Create test superuser
    print_status "Creating test superuser..."
    docker-compose -f docker-compose.test.yml exec test-runner python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='testadmin').exists():
    User.objects.create_superuser('testadmin', 'admin@test.com', 'testpass123')
    print('Test superuser created')
else:
    print('Test superuser already exists')
"
    
    print_success "Test environment setup complete!"
}

# Function to run tests
run_tests() {
    local test_command="pytest"
    
    case $TEST_TYPE in
        "unit")
            test_command="$test_command -m unit"
            print_status "Running unit tests..."
            ;;
        "integration")
            test_command="$test_command -m integration"
            print_status "Running integration tests..."
            ;;
        "api")
            test_command="$test_command -m api"
            print_status "Running API tests..."
            ;;
        "sync")
            test_command="$test_command -m sync"
            print_status "Running sync tests..."
            ;;
        "bulk")
            test_command="$test_command -m bulk_upload"
            print_status "Running bulk upload tests..."
            ;;
        "all")
            print_status "Running all tests..."
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # Add coverage if requested
    if [[ -n "$COVERAGE" ]]; then
        test_command="$test_command $COVERAGE"
    fi
    
    # Add verbose if requested
    if [[ -n "$VERBOSE" ]]; then
        test_command="$test_command $VERBOSE"
    fi
    
    # Add test arguments if provided
    if [[ -n "$TEST_ARGS" ]]; then
        test_command="$test_command $TEST_ARGS"
    fi
    
    print_status "Executing: $test_command"
    
    # Run tests
    docker-compose -f docker-compose.test.yml exec test-runner $test_command
    
    # Check exit code
    if [[ $? -eq 0 ]]; then
        print_success "Tests completed successfully!"
    else
        print_error "Tests failed!"
        exit 1
    fi
}

# Function to cleanup
cleanup() {
    if [[ "$STOP_AFTER" == "--down" ]]; then
        print_status "Stopping test containers..."
        docker-compose -f docker-compose.test.yml down
        print_success "Test containers stopped!"
    fi
}

# Main execution
main() {
    print_status "Starting test runner..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Setup test environment
    setup_test_env
    
    # Run tests if not just setup
    if [[ "$TEST_TYPE" != "setup" ]]; then
        run_tests
    fi
    
    # Cleanup
    cleanup
    
    print_success "Test runner completed!"
}

# Run main function
main "$@"