# Django Form Creator API - Test Execution Plan

## Overview
This document provides a comprehensive test execution plan for the Django Form Creator API collection. Since the Django server is not currently running on localhost:8000, this plan outlines the steps to start the server and execute the API tests.

## Prerequisites

### 1. Server Setup
Before running the collection tests, ensure the Django development server is running:

```bash
# Navigate to the backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run Django migrations (if needed)
python manage.py migrate

# Start the Django development server
python manage.py runserver
```

The server should be accessible at: `http://localhost:8000`

### 2. Database Requirements
- **MongoDB**: Ensure MongoDB is running and accessible
- **Firebase**: Firebase authentication service should be configured
- **Environment Variables**: Check that all required environment variables are set

### 3. Collection Variables
The collection uses the following variables (defined in `.resources/definition.yaml`):
- `base_url`: http://localhost:8000
- `firebase_token`: (empty - to be set during authentication)
- `user_id`: (empty - populated after user operations)
- `form_id`: (empty - populated after form creation)
- `response_id`: (empty - populated after response creation)

## Test Execution Order

### Phase 1: Basic Connectivity Tests
1. **Hello Test** (`Users/hello-test.request.yaml`)
   - **Purpose**: Verify basic server connectivity
   - **Expected Result**: 200 OK with welcome message
   - **Dependencies**: None

### Phase 2: Authentication Flow
2. **Firebase Auth Sync** (`Authentication/firebase-auth-sync.request.yaml`)
   - **Purpose**: Synchronize Firebase authentication
   - **Expected Result**: 200 OK with authentication confirmation
   - **Dependencies**: Firebase service running

3. **User Login** (`Users/user-login.request.yaml`)
   - **Purpose**: Authenticate user and obtain token
   - **Expected Result**: 200 OK with authentication token
   - **Post-condition**: Sets `firebase_token` variable

### Phase 3: User Management
4. **Create User** (`Users/create-user.request.yaml`)
   - **Purpose**: Create a new user account
   - **Expected Result**: 201 Created with user details
   - **Post-condition**: Sets `user_id` variable

5. **Get User Details** (`Users/get-user-details.request.yaml`)
   - **Purpose**: Retrieve user information
   - **Expected Result**: 200 OK with user data
   - **Dependencies**: Valid `user_id`

6. **List Users** (`Users/list-users.request.yaml`)
   - **Purpose**: Get all users (admin function)
   - **Expected Result**: 200 OK with users array
   - **Dependencies**: Admin authentication

7. **Protected Test** (`Users/protected-test.request.yaml`)
   - **Purpose**: Test authentication-protected endpoint
   - **Expected Result**: 200 OK if authenticated, 401 if not
   - **Dependencies**: Valid `firebase_token`

### Phase 4: Form Management
8. **Create Form** (`Forms/create-form.request.yaml`)
   - **Purpose**: Create a new form
   - **Expected Result**: 201 Created with form details
   - **Post-condition**: Sets `form_id` variable
   - **Dependencies**: Authenticated user

9. **Get Form Details** (`Forms/get-form-details.request.yaml`)
   - **Purpose**: Retrieve specific form information
   - **Expected Result**: 200 OK with form data
   - **Dependencies**: Valid `form_id`

10. **List Forms** (`Forms/list-forms.request.yaml`)
    - **Purpose**: Get all forms for authenticated user
    - **Expected Result**: 200 OK with forms array
    - **Dependencies**: Authenticated user

11. **Update Form** (`Forms/update-form.request.yaml`)
    - **Purpose**: Modify existing form
    - **Expected Result**: 200 OK with updated form data
    - **Dependencies**: Valid `form_id`, form ownership

12. **Check Form Access** (`Forms/check-form-access.request.yaml`)
    - **Purpose**: Verify user access permissions to form
    - **Expected Result**: 200 OK with access status
    - **Dependencies**: Valid `form_id`

### Phase 5: Form Collaboration
13. **Add Authorized User** (`Forms/add-authorized-user.request.yaml`)
    - **Purpose**: Grant form access to another user
    - **Expected Result**: 200 OK with confirmation
    - **Dependencies**: Form ownership, valid target user

14. **List Authorized Users** (`Forms/list-authorized-users.request.yaml`)
    - **Purpose**: Get all users with form access
    - **Expected Result**: 200 OK with users array
    - **Dependencies**: Form access permissions

15. **Send Invitations** (`Forms/send-invitations.request.yaml`)
    - **Purpose**: Send email invitations for form collaboration
    - **Expected Result**: 200 OK with invitation status
    - **Dependencies**: Email service configuration

16. **Remove Authorized User** (`Forms/remove-authorized-user.request.yaml`)
    - **Purpose**: Revoke form access from user
    - **Expected Result**: 200 OK with confirmation
    - **Dependencies**: Form ownership

### Phase 6: Response Management
17. **Create Response** (`Responses/create-response.request.yaml`)
    - **Purpose**: Submit a form response
    - **Expected Result**: 201 Created with response details
    - **Post-condition**: Sets `response_id` variable
    - **Dependencies**: Valid `form_id`, form access

18. **Get Response Details** (`Responses/get-response-details.request.yaml`)
    - **Purpose**: Retrieve specific response information
    - **Expected Result**: 200 OK with response data
    - **Dependencies**: Valid `response_id`

19. **List Responses** (`Responses/list-responses.request.yaml`)
    - **Purpose**: Get all responses for a form
    - **Expected Result**: 200 OK with responses array
    - **Dependencies**: Form access permissions

20. **Update Response** (`Responses/update-response.request.yaml`)
    - **Purpose**: Modify existing response
    - **Expected Result**: 200 OK with updated response
    - **Dependencies**: Valid `response_id`, response ownership

### Phase 7: Analytics and Export
21. **Get Form Statistics** (`Forms/get-form-statistics.request.yaml`)
    - **Purpose**: Retrieve form analytics and metrics
    - **Expected Result**: 200 OK with statistics data
    - **Dependencies**: Form ownership

22. **Export Form Data** (`Forms/export-form-data.request.yaml`)
    - **Purpose**: Export form responses in various formats
    - **Expected Result**: 200 OK with exported data
    - **Dependencies**: Form ownership

### Phase 8: Cleanup Operations
23. **Delete Response** (`Responses/delete-response.request.yaml`)
    - **Purpose**: Remove a form response
    - **Expected Result**: 204 No Content
    - **Dependencies**: Valid `response_id`, appropriate permissions

24. **Delete Form** (`Forms/delete-form.request.yaml`)
    - **Purpose**: Remove a form and all associated data
    - **Expected Result**: 204 No Content
    - **Dependencies**: Form ownership

25. **Update User** (`Users/update-user.request.yaml`)
    - **Purpose**: Modify user profile information
    - **Expected Result**: 200 OK with updated user data
    - **Dependencies**: User authentication

26. **Reset Password** (`Users/reset-password.request.yaml`)
    - **Purpose**: Initiate password reset process
    - **Expected Result**: 200 OK with reset confirmation
    - **Dependencies**: Valid user email

27. **Delete User** (`Users/delete-user.request.yaml`)
    - **Purpose**: Remove user account
    - **Expected Result**: 204 No Content
    - **Dependencies**: User authentication or admin privileges

## Expected Test Results

### Success Scenarios
- **Authentication**: All auth-related requests should return 200/201 with proper tokens
- **CRUD Operations**: Create (201), Read (200), Update (200), Delete (204)
- **Access Control**: Proper 403 responses for unauthorized access attempts
- **Data Validation**: 400 responses for invalid input data

### Common Error Scenarios
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions for the requested operation
- **404 Not Found**: Requested resource doesn't exist
- **400 Bad Request**: Invalid request data or missing required fields
- **500 Internal Server Error**: Server-side issues (database connection, etc.)

## Test Validation Scripts

Each request includes test scripts that validate:
1. **Status Code**: Ensures correct HTTP response codes
2. **Response Structure**: Validates JSON schema and required fields
3. **Data Integrity**: Checks that returned data matches expected formats
4. **Variable Setting**: Automatically captures IDs for subsequent requests
5. **Business Logic**: Validates application-specific rules and constraints

## Troubleshooting Guide

### Server Not Starting
- Check Python version compatibility
- Verify all dependencies are installed
- Ensure MongoDB is running and accessible
- Check for port conflicts (8000 already in use)

### Authentication Failures
- Verify Firebase configuration and credentials
- Check that Firebase service account key is properly configured
- Ensure Firebase project settings match the application configuration

### Database Connection Issues
- Confirm MongoDB is running on the expected port
- Check database connection strings in Django settings
- Verify database permissions and authentication

### Test Failures
- Review test scripts for syntax errors
- Check that environment variables are properly set
- Verify request payloads match API expectations
- Ensure proper test execution order (dependencies)

## Running the Collection

### Using Postman Desktop
1. Import the collection from the file system
2. Set up the environment variables
3. Run requests individually or use the Collection Runner
4. Monitor test results in the Test Results tab

### Using Newman (CLI)
```bash
# Install Newman if not already installed
npm install -g newman

# Run the collection
newman run "postman/collections/Django Form Creator API" \
  --environment "postman/environments/Development.yaml" \
  --reporters cli,json \
  --reporter-json-export results.json
```

## Success Criteria

The test execution is considered successful when:
1. All basic connectivity tests pass (Phase 1)
2. Authentication flow works correctly (Phase 2)
3. Core CRUD operations function properly (Phases 3-6)
4. Access control mechanisms work as expected
5. All test scripts pass without errors
6. No critical server errors (5xx responses) occur

## Next Steps

After successful test execution:
1. Review any failed tests and investigate root causes
2. Update API documentation based on test results
3. Implement any necessary bug fixes
4. Set up automated testing pipeline
5. Create monitoring and alerting for production deployment