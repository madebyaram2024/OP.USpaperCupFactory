#!/usr/bin/env python3
"""
Frontend Modal and Form Testing Script (API-based)
Tests the modal and form functionality using API calls to simulate frontend behavior
"""

import requests
import json
import time
import sys
import os


class FrontendAPITester:
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
    
    def test_modal_open_close_simulation(self):
        """Simulate modal open/close functionality"""
        print("Testing modal open/close functionality (simulated)...")
        
        # This test verifies that the API endpoints required by the modals work
        # The frontend would make these API calls when modal opens/closes
        
        try:
            # Test that customer listing API works (what appears when modal closes)
            response = requests.get("http://localhost:8080/api/v1/customers")
            if response.status_code == 200:
                self.log_result("FM-001", "Modal Background - Customer List API", "PASS")
            else:
                self.log_result("FM-001", "Modal Background - Customer List API", "FAIL", f"Status: {response.status_code}")
                return False
                
            # Test that health check works (what might be queried by frontend)
            response = requests.get("http://localhost:8080/health")
            if response.status_code == 200:
                self.log_result("FM-002", "Modal Background - Health Check API", "PASS")
            else:
                self.log_result("FM-002", "Modal Background - Health Check API", "FAIL", f"Status: {response.status_code}")
                return False
                
            return True
        except Exception as e:
            self.log_result("FM-001", "Modal Background - Customer List API", "FAIL", str(e))
            self.log_result("FM-002", "Modal Background - Health Check API", "FAIL", str(e))
            return False
    
    def test_form_submission_simulation(self):
        """Simulate complete form submission process"""
        print("Testing form submission process (simulated)...")
        
        # Test 1: Form submission with valid data
        customer_data = {
            "company_name": "Frontend Simulation Test Company",
            "contact_person": "Frontend Test Person",
            "email": f"simulate{int(time.time())}@test.com",
            "phone": "+11234567890",
            "city": "Simulation City",
            "notes": "Created through frontend form simulation"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=customer_data)
            if response.status_code == 201:
                created_customer = response.json()
                self.created_customer_ids.append(created_customer['id'])
                self.log_result("FM-003", "Form Submission - Valid Data", "PASS")
            else:
                self.log_result("FM-003", "Form Submission - Valid Data", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-003", "Form Submission - Valid Data", "FAIL", str(e))
            return False
        
        # Test 2: Form validation with invalid email (would be caught by frontend validation)
        invalid_customer_data = {
            "company_name": "Invalid Email Test",
            "contact_person": "Test Person",
            "email": "invalid-email",  # Invalid email format
            "phone": "+11234567890"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=invalid_customer_data)
            if response.status_code == 422:  # Validation error expected
                self.log_result("FM-004", "Form Validation - Invalid Email", "PASS")
            else:
                self.log_result("FM-004", "Form Validation - Invalid Email", "FAIL", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-004", "Form Validation - Invalid Email", "FAIL", str(e))
            return False
        
        # Test 3: Form validation with missing required fields
        incomplete_data = {
            "company_name": "",  # Missing required fields
            "contact_person": "",
            "email": ""
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=incomplete_data)
            if response.status_code == 422:  # Validation error expected
                self.log_result("FM-005", "Form Validation - Missing Fields", "PASS")
            else:
                self.log_result("FM-005", "Form Validation - Missing Fields", "FAIL", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-005", "Form Validation - Missing Fields", "FAIL", str(e))
            return False
        
        # Test 4: Form submission that would trigger success modal
        success_customer = {
            "company_name": "Success Modal Test Company",
            "contact_person": "Success Test Person",
            "email": f"success{int(time.time())}@test.com",
            "phone": "+19999999999",
            "notes": "Success modal triggering customer"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=success_customer)
            if response.status_code == 201:
                success_customer_data = response.json()
                self.created_customer_ids.append(success_customer_data['id'])
                self.log_result("FM-006", "Form Success Flow - Triggers Success Modal", "PASS")
            else:
                self.log_result("FM-006", "Form Success Flow - Triggers Success Modal", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-006", "Form Success Flow - Triggers Success Modal", "FAIL", str(e))
            return False
        
        return True
    
    def test_form_update_simulation(self):
        """Simulate form update functionality"""
        print("Testing form update process (simulated)...")
        
        if not self.created_customer_ids:
            self.log_result("FM-007", "Form Update - No Customer Available", "SKIP", "No customer created for update test")
            return True
        
        # Use the first created customer for update test
        customer_id = self.created_customer_ids[0]
        
        update_data = {
            "company_name": "Updated Frontend Test Company",
            "contact_person": "Updated Frontend Test Person",
            "email": f"updated{int(time.time())}@test.com"
        }
        
        try:
            response = requests.put(f"http://localhost:8080/api/v1/customers/{customer_id}", json=update_data)
            if response.status_code == 200:
                self.log_result("FM-007", "Form Update - Modify Customer", "PASS")
            else:
                self.log_result("FM-007", "Form Update - Modify Customer", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-007", "Form Update - Modify Customer", "FAIL", str(e))
            return False
        
        return True
    
    def test_form_search_simulation(self):
        """Simulate search form functionality"""
        print("Testing search form functionality (simulated)...")
        
        try:
            # Test search functionality (what happens when user types in search box)
            response = requests.get("http://localhost:8080/api/v1/customers?search=Test")
            if response.status_code == 200:
                self.log_result("FM-008", "Search Form - API Call", "PASS")
            else:
                self.log_result("FM-008", "Search Form - API Call", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FM-008", "Search Form - API Call", "FAIL", str(e))
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all frontend API-based tests"""
        print("Starting Frontend API-Based Tests (Simulating Modal & Form Behavior)...\n")
        
        results = []
        results.append(self.test_modal_open_close_simulation())
        results.append(self.test_form_submission_simulation())
        results.append(self.test_form_update_simulation())
        results.append(self.test_form_search_simulation())
        
        # Cleanup created test customers
        for customer_id in self.created_customer_ids:
            try:
                requests.delete(f"http://localhost:8080/api/v1/customers/{customer_id}")
            except:
                pass  # Don't worry if cleanup fails
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] in ['PASS', 'SKIP']])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print("="*70)
        print("FRONTEND FORM/MODAL SIMULATION TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed/Skipped: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {len([r for r in self.test_results if r['status'] == 'PASS'])/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*70)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED FRONTEND TESTS DETAILS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    print(f"    {result['details']}")
        
        return all(results)


def main():
    """Main test runner"""
    print("Speckit Customer Management Frontend Form & Modal API Simulation Tests")
    print("="*75)
    
    tester = FrontendAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL FRONTEND SIMULATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME FRONTEND SIMULATION TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()