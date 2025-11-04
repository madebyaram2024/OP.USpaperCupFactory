#!/usr/bin/env python3
"""
Automated Backend API Testing Script
Tests all endpoints of the Speckit Customer Management API
"""

import requests
import json
import uuid
import time
import sys
import os

# Configuration
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1/customers"

class APITester:
    def __init__(self):
        self.test_results = []
        self.created_customer_ids = []
        
    def log_result(self, test_id, test_name, status, details=""):
        """Log test result"""
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"TEST {test_id}: {test_name} - {status}")
        if details:
            print(f"  Details: {details}")
        print()
    
    def run_health_check(self):
        """Test API health endpoints"""
        print("Running health check tests...")
        
        # Test 1: Root endpoint
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200 and "Customer Management API" in response.text:
                self.log_result("API-001", "Health Check - Root", "PASS")
            else:
                self.log_result("API-001", "Health Check - Root", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("API-001", "Health Check - Root", "FAIL", str(e))
        
        # Test 2: Health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200 and response.json().get("status") == "healthy":
                self.log_result("API-002", "Health Check - /health", "PASS")
            else:
                self.log_result("API-002", "Health Check - /health", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("API-002", "Health Check - /health", "FAIL", str(e))
    
    def run_customer_creation_tests(self):
        """Test customer creation functionality"""
        print("Running customer creation tests...")
        
        # Test 3: Valid customer creation
        test_customer = {
            "company_name": "Test Company API",
            "contact_person": "John API Doe",
            "email": f"test{int(time.time())}@testcompany.com",
            "phone": "+11234567890",
            "address_line1": "123 API Test Street",
            "city": "API Test City",
            "state_province": "AP",
            "postal_code": "12345",
            "country": "API Country",
            "notes": "API testing customer"
        }
        
        try:
            response = requests.post(API_BASE, json=test_customer)
            if response.status_code == 201:
                customer_data = response.json()
                self.created_customer_ids.append(customer_data['id'])
                self.log_result("API-003", "Create Customer - Valid Data", "PASS")
            else:
                self.log_result("API-003", "Create Customer - Valid Data", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("API-003", "Create Customer - Valid Data", "FAIL", str(e))
        
        # Test 4: Invalid email validation
        invalid_customer = {
            "company_name": "Invalid Email Company",
            "contact_person": "Jane Invalid",
            "email": "not-an-email",
            "phone": "+11234567890"
        }
        
        try:
            response = requests.post(API_BASE, json=invalid_customer)
            if response.status_code == 422:
                self.log_result("API-004", "Create Customer - Invalid Email", "PASS")
            else:
                self.log_result("API-004", "Create Customer - Invalid Email", "FAIL", f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("API-004", "Create Customer - Invalid Email", "FAIL", str(e))
        
        # Test 5: Missing required fields
        incomplete_customer = {
            "company_name": "",
            "contact_person": "",
            "email": ""
        }
        
        try:
            response = requests.post(API_BASE, json=incomplete_customer)
            if response.status_code == 422:
                self.log_result("API-005", "Create Customer - Missing Required Fields", "PASS")
            else:
                self.log_result("API-005", "Create Customer - Missing Required Fields", "FAIL", f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("API-005", "Create Customer - Missing Required Fields", "FAIL", str(e))
    
    def run_customer_retrieval_tests(self):
        """Test customer retrieval functionality"""
        print("Running customer retrieval tests...")
        
        # Test 6: Get all customers
        try:
            response = requests.get(f"{API_BASE}")
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and 'total' in data:
                    self.log_result("API-006", "Get All Customers", "PASS")
                else:
                    self.log_result("API-006", "Get All Customers", "FAIL", "Response missing expected fields")
            else:
                self.log_result("API-006", "Get All Customers", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-006", "Get All Customers", "FAIL", str(e))
        
        # Test 7 & 8: Get specific customer (requires a created customer)
        if self.created_customer_ids:
            customer_id = self.created_customer_ids[0]
            
            # Test 7: Get existing customer
            try:
                response = requests.get(f"{API_BASE}/{customer_id}")
                if response.status_code == 200:
                    self.log_result("API-007", "Get Single Customer - Exists", "PASS")
                else:
                    self.log_result("API-007", "Get Single Customer - Exists", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("API-007", "Get Single Customer - Exists", "FAIL", str(e))
            
            # Test 8: Get non-existent customer
            fake_id = str(uuid.uuid4())
            try:
                response = requests.get(f"{API_BASE}/{fake_id}")
                if response.status_code == 404:
                    self.log_result("API-008", "Get Single Customer - Not Found", "PASS")
                else:
                    self.log_result("API-008", "Get Single Customer - Not Found", "FAIL", f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_result("API-008", "Get Single Customer - Not Found", "FAIL", str(e))
        else:
            self.log_result("API-007", "Get Single Customer - Exists", "SKIPPED", "No customer created for test")
            self.log_result("API-008", "Get Single Customer - Not Found", "SKIPPED", "No customer created for test")
    
    def run_customer_update_tests(self):
        """Test customer update functionality"""
        print("Running customer update tests...")
        
        if self.created_customer_ids:
            customer_id = self.created_customer_ids[0]
            
            # Test 9: Update customer
            update_data = {
                "company_name": "Updated Test Company API",
                "contact_person": "John API Updated",
                "email": f"updated{int(time.time())}@testcompany.com"
            }
            
            try:
                response = requests.put(f"{API_BASE}/{customer_id}", json=update_data)
                if response.status_code == 200:
                    self.log_result("API-009", "Update Customer", "PASS")
                else:
                    self.log_result("API-009", "Update Customer", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("API-009", "Update Customer", "FAIL", str(e))
            
            # Test 10: Update with invalid data
            invalid_update = {
                "email": "invalid-email-format"
            }
            
            try:
                response = requests.put(f"{API_BASE}/{customer_id}", json=invalid_update)
                if response.status_code == 422:
                    self.log_result("API-010", "Update Customer - Invalid Data", "PASS")
                else:
                    self.log_result("API-010", "Update Customer - Invalid Data", "FAIL", f"Expected 422, got {response.status_code}")
            except Exception as e:
                self.log_result("API-010", "Update Customer - Invalid Data", "FAIL", str(e))
        else:
            self.log_result("API-009", "Update Customer", "SKIPPED", "No customer created for test")
            self.log_result("API-010", "Update Customer - Invalid Data", "SKIPPED", "No customer created for test")
    
    def run_customer_archive_tests(self):
        """Test customer archiving functionality"""
        print("Running customer archiving tests...")
        
        if self.created_customer_ids:
            customer_id = self.created_customer_ids[0]
            
            # Test 11: Archive customer
            try:
                response = requests.delete(f"{API_BASE}/{customer_id}")
                if response.status_code == 204:
                    self.log_result("API-011", "Archive Customer", "PASS")
                else:
                    self.log_result("API-011", "Archive Customer", "FAIL", f"Expected 204, got {response.status_code}")
            except Exception as e:
                self.log_result("API-011", "Archive Customer", "FAIL", str(e))
            
            # Test 12: Archive non-existent customer
            fake_id = str(uuid.uuid4())
            try:
                response = requests.delete(f"{API_BASE}/{fake_id}")
                if response.status_code == 404:
                    self.log_result("API-012", "Archive Customer - Not Found", "PASS")
                else:
                    self.log_result("API-012", "Archive Customer - Not Found", "FAIL", f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_result("API-012", "Archive Customer - Not Found", "FAIL", str(e))
        else:
            self.log_result("API-011", "Archive Customer", "SKIPPED", "No customer created for test")
            self.log_result("API-012", "Archive Customer - Not Found", "SKIPPED", "No customer created for test")
    
    def run_search_filter_tests(self):
        """Test search and filter functionality"""
        print("Running search and filter tests...")
        
        # Test 13: Search customers
        try:
            response = requests.get(f"{API_BASE}?search=Test")
            if response.status_code == 200:
                self.log_result("API-013", "Search Customers", "PASS")
            else:
                self.log_result("API-013", "Search Customers", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-013", "Search Customers", "FAIL", str(e))
        
        # Test 14: Filter by status
        try:
            response = requests.get(f"{API_BASE}?status=active")
            if response.status_code == 200:
                self.log_result("API-014", "Filter Customers by Status", "PASS")
            else:
                self.log_result("API-014", "Filter Customers by Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-014", "Filter Customers by Status", "FAIL", str(e))
        
        # Test 15: Pagination
        try:
            response = requests.get(f"{API_BASE}?page=1&limit=10")
            if response.status_code == 200:
                self.log_result("API-015", "Pagination", "PASS")
            else:
                self.log_result("API-015", "Pagination", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-015", "Pagination", "FAIL", str(e))
    
    def run_duplicate_prevention_test(self):
        """Test duplicate email prevention"""
        print("Running duplicate prevention tests...")
        
        # Create a customer first
        duplicate_customer = {
            "company_name": "Duplicate Test Company",
            "contact_person": "Duplicate Person",
            "email": "duplicate@test.com",
            "phone": "+12222222222"
        }
        
        try:
            # First request - should succeed
            response1 = requests.post(API_BASE, json=duplicate_customer)
            
            if response1.status_code == 201:
                # Second request with same email - should fail
                response2 = requests.post(API_BASE, json=duplicate_customer)
                
                if response2.status_code == 409:
                    self.log_result("API-018", "Duplicate Email Prevention", "PASS")
                else:
                    self.log_result("API-018", "Duplicate Email Prevention", "FAIL", f"Expected 409, got {response2.status_code}")
            else:
                self.log_result("API-018", "Duplicate Email Prevention", "FAIL", f"First request failed with {response1.status_code}")
        except Exception as e:
            self.log_result("API-018", "Duplicate Email Prevention", "FAIL", str(e))
    
    def run_documentation_tests(self):
        """Test API documentation endpoints"""
        print("Running documentation tests...")
        
        # Test 16: API documentation
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200 and "swagger" in response.text.lower():
                self.log_result("API-016", "API Documentation", "PASS")
            else:
                self.log_result("API-016", "API Documentation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-016", "API Documentation", "FAIL", str(e))
        
        # Test 17: OpenAPI schema
        try:
            response = requests.get(f"{BASE_URL}/openapi.json")
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if 'openapi' in json_data or 'swagger' in json_data:
                        self.log_result("API-017", "OpenAPI Schema", "PASS")
                    else:
                        self.log_result("API-017", "OpenAPI Schema", "FAIL", "Response is not a valid OpenAPI schema")
                except:
                    self.log_result("API-017", "OpenAPI Schema", "FAIL", "Response is not valid JSON")
            else:
                self.log_result("API-017", "OpenAPI Schema", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API-017", "OpenAPI Schema", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting Backend API Tests...\n")
        
        self.run_health_check()
        self.run_customer_creation_tests()
        self.run_customer_retrieval_tests()
        self.run_customer_update_tests()
        self.run_customer_archive_tests()
        self.run_search_filter_tests()
        self.run_duplicate_prevention_test()
        self.run_documentation_tests()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIPPED'])
        
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*60)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED TESTS DETAILS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    print(f"    {result['details']}")
        
        return failed_tests == 0


def main():
    """Main test runner"""
    print("Speckit Customer Management API Testing Suite")
    print("="*50)
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()