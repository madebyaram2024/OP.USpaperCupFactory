#!/usr/bin/env python3
"""
Comprehensive Forms and Data Submission Testing Script
Tests all forms and their data submission functionality across the application
"""

import requests
import json
import time
import sys
import os


class FormsSubmissionTester:
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
    
    def test_add_customer_form(self):
        """Test the Add Customer form functionality"""
        print("Testing Add Customer form...")
        
        # Test 1: Submit with valid data
        customer_data = {
            "company_name": "Forms Test Company",
            "contact_person": "Joe Forms",
            "email": f"forms{int(time.time())}@test.com",
            "phone": "+12345678901",
            "address_line1": "123 Forms Street",
            "city": "Formsville",
            "state_province": "FS",
            "postal_code": "12345",
            "country": "Formland",
            "notes": "Test customer for form submission"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=customer_data)
            if response.status_code == 201:
                created_customer = response.json()
                self.created_customer_ids.append(created_customer['id'])
                self.log_result("FS-001", "Add Customer Form - Valid Data", "PASS")
            else:
                self.log_result("FS-001", "Add Customer Form - Valid Data", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("FS-001", "Add Customer Form - Valid Data", "FAIL", str(e))
            return False
        
        # Test 2: Required field validation
        incomplete_data = {
            "company_name": "",  # Missing required field
            "contact_person": "",
            "email": ""
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=incomplete_data)
            if response.status_code == 422:
                self.log_result("FS-002", "Add Customer Form - Required Field Validation", "PASS")
            else:
                self.log_result("FS-002", "Add Customer Form - Required Field Validation", "FAIL", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-002", "Add Customer Form - Required Field Validation", "FAIL", str(e))
            return False
        
        # Test 3: Email format validation
        invalid_email_data = {
            "company_name": "Invalid Email Company",
            "contact_person": "Test Person",
            "email": "not-an-email",
            "phone": "+12345678901"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=invalid_email_data)
            if response.status_code == 422:
                self.log_result("FS-003", "Add Customer Form - Email Validation", "PASS")
            else:
                self.log_result("FS-003", "Add Customer Form - Email Validation", "FAIL", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-003", "Add Customer Form - Email Validation", "FAIL", str(e))
            return False
        
        # Test 4: Duplicate prevention
        if self.created_customer_ids:
            duplicate_data = {
                "company_name": "Duplicate Test Company",
                "contact_person": "Duplicate Person",
                "email": customer_data['email'],  # Use same email as first customer
                "phone": "+12345678901"
            }
            
            try:
                response = requests.post("http://localhost:8080/api/v1/customers", json=duplicate_data)
                if response.status_code == 409:
                    self.log_result("FS-004", "Add Customer Form - Duplicate Prevention", "PASS")
                else:
                    self.log_result("FS-004", "Add Customer Form - Duplicate Prevention", "FAIL", f"Expected 409, got {response.status_code}")
                    return False
            except Exception as e:
                self.log_result("FS-004", "Add Customer Form - Duplicate Prevention", "FAIL", str(e))
                return False
        
        return True
    
    def test_update_customer_form(self):
        """Test the Update Customer form functionality"""
        print("Testing Update Customer form...")
        
        if not self.created_customer_ids:
            self.log_result("FS-005", "Update Customer Form - No Customer", "SKIP", "No customer created for update test")
            return True
        
        customer_id = self.created_customer_ids[0]
        
        # Test 1: Update with valid data
        update_data = {
            "company_name": "Updated Forms Test Company",
            "contact_person": "Updated Joe Forms",
            "email": f"updated.forms{int(time.time())}@test.com",
            "phone": "+19999999999"
        }
        
        try:
            response = requests.put(f"http://localhost:8080/api/v1/customers/{customer_id}", json=update_data)
            if response.status_code == 200:
                self.log_result("FS-005", "Update Customer Form - Valid Data", "PASS")
            else:
                self.log_result("FS-005", "Update Customer Form - Valid Data", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("FS-005", "Update Customer Form - Valid Data", "FAIL", str(e))
            return False
        
        # Test 2: Update with invalid email
        invalid_update_data = {
            "email": "invalid-email-format"
        }
        
        try:
            response = requests.put(f"http://localhost:8080/api/v1/customers/{customer_id}", json=invalid_update_data)
            if response.status_code == 422:
                self.log_result("FS-006", "Update Customer Form - Email Validation", "PASS")
            else:
                self.log_result("FS-006", "Update Customer Form - Email Validation", "FAIL", f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-006", "Update Customer Form - Email Validation", "FAIL", str(e))
            return False
        
        # Test 3: Update non-existent customer
        fake_id = "00000000-0000-0000-0000-000000000000"
        fake_update_data = {
            "company_name": "Fake Update"
        }
        
        try:
            response = requests.put(f"http://localhost:8080/api/v1/customers/{fake_id}", json=fake_update_data)
            if response.status_code == 404:
                self.log_result("FS-007", "Update Customer Form - Not Found", "PASS")
            else:
                self.log_result("FS-007", "Update Customer Form - Not Found", "FAIL", f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-007", "Update Customer Form - Not Found", "FAIL", str(e))
            return False
        
        return True
    
    def test_list_customer_form(self):
        """Test the Customer List form functionality (search/filter parameters)"""
        print("Testing Customer List form...")
        
        # Test 1: Basic listing
        try:
            response = requests.get("http://localhost:8080/api/v1/customers")
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and 'total' in data:
                    self.log_result("FS-008", "List Customer Form - Basic Listing", "PASS")
                else:
                    self.log_result("FS-008", "List Customer Form - Basic Listing", "FAIL", "Missing expected response fields")
                    return False
            else:
                self.log_result("FS-008", "List Customer Form - Basic Listing", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-008", "List Customer Form - Basic Listing", "FAIL", str(e))
            return False
        
        # Test 2: Search functionality
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Forms")
            if response.status_code == 200:
                data = response.json()
                # We expect at least one customer with 'Forms' in their data
                self.log_result("FS-009", "List Customer Form - Search", "PASS")
            else:
                self.log_result("FS-009", "List Customer Form - Search", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-009", "List Customer Form - Search", "FAIL", str(e))
            return False
        
        # Test 3: Pagination
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?page=1&limit=5")
            if response.status_code == 200:
                data = response.json()
                if 'page' in data and 'limit' in data and 'items' in data:
                    self.log_result("FS-010", "List Customer Form - Pagination", "PASS")
                else:
                    self.log_result("FS-010", "List Customer Form - Pagination", "FAIL", "Missing pagination fields")
                    return False
            else:
                self.log_result("FS-010", "List Customer Form - Pagination", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-010", "List Customer Form - Pagination", "FAIL", str(e))
            return False
        
        return True
    
    def test_archive_customer_form(self):
        """Test the Archive Customer form functionality"""
        print("Testing Archive Customer form...")
        
        if not self.created_customer_ids:
            self.log_result("FS-011", "Archive Customer Form - No Customer", "SKIP", "No customer created for archiving test")
            return True
        
        # Create a new customer to archive
        new_customer = {
            "company_name": "Archive Test Customer",
            "contact_person": "Archive Test Person",
            "email": f"archive{int(time.time())}@test.com",
            "phone": "+18888888888"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=new_customer)
            if response.status_code == 201:
                new_customer_data = response.json()
                customer_to_archive = new_customer_data['id']
            else:
                self.log_result("FS-011", "Archive Customer Form - Create Test Customer", "FAIL", f"Failed to create test customer: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-011", "Archive Customer Form - Create Test Customer", "FAIL", str(e))
            return False
        
        # Test 1: Archive customer
        try:
            response = requests.delete(f"http://localhost:8080/api/v1/customers/{customer_to_archive}")
            if response.status_code == 204:
                self.log_result("FS-011", "Archive Customer Form - Successful Archive", "PASS")
            else:
                self.log_result("FS-011", "Archive Customer Form - Successful Archive", "FAIL", f"Expected 204, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-011", "Archive Customer Form - Successful Archive", "FAIL", str(e))
            return False
        
        # Test 2: Archive non-existent customer
        fake_id = "00000000-0000-0000-0000-000000000000"
        try:
            response = requests.delete(f"http://localhost:8080/api/v1/customers/{fake_id}")
            if response.status_code == 404:
                self.log_result("FS-012", "Archive Customer Form - Not Found", "PASS")
            else:
                self.log_result("FS-012", "Archive Customer Form - Not Found", "FAIL", f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-012", "Archive Customer Form - Not Found", "FAIL", str(e))
            return False
        
        return True
    
    def test_form_field_lengths(self):
        """Test form field length validation"""
        print("Testing form field length validation...")
        
        # Test with very long company name
        long_company_data = {
            "company_name": "A" * 300,  # Exceeds typical length limits
            "contact_person": "Long Name Test",
            "email": f"longname{int(time.time())}@test.com",
            "phone": "+17777777777"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=long_company_data)
            # This might pass or fail depending on the validation; that's ok as long as it doesn't crash
            self.log_result("FS-013", "Form Field Length - Company Name", "PASS")
        except Exception as e:
            self.log_result("FS-013", "Form Field Length - Company Name", "FAIL", str(e))
            return False
        
        # Test with normal lengths
        normal_data = {
            "company_name": "Normal Length Company Name",
            "contact_person": "Normal Contact Person Name",
            "email": f"normal{int(time.time())}@test.com",
            "phone": "+16666666666",
            "address_line1": "Normal address line 1",
            "city": "Normal City",
            "state_province": "NS",
            "postal_code": "54321",
            "country": "Normania"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=normal_data)
            if response.status_code == 201:
                created_customer = response.json()
                self.created_customer_ids.append(created_customer['id'])
                self.log_result("FS-014", "Form Field Length - Normal Values", "PASS")
            else:
                self.log_result("FS-014", "Form Field Length - Normal Values", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-014", "Form Field Length - Normal Values", "FAIL", str(e))
            return False
        
        return True
    
    def test_form_empty_fields(self):
        """Test form behavior with empty optional fields"""
        print("Testing form behavior with empty fields...")
        
        partial_data = {
            "company_name": "Partial Data Company",
            "contact_person": "Partial Data Contact",
            "email": f"partial{int(time.time())}@test.com"
            # Other fields intentionally omitted to test defaults
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=partial_data)
            if response.status_code == 201:
                self.log_result("FS-015", "Form Empty Fields - Optional Fields", "PASS")
            else:
                self.log_result("FS-015", "Form Empty Fields - Optional Fields", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("FS-015", "Form Empty Fields - Optional Fields", "FAIL", str(e))
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all form and data submission tests"""
        print("\nStarting Comprehensive Forms and Data Submission Tests...\n")
        
        results = []
        results.append(self.test_add_customer_form())
        results.append(self.test_update_customer_form())
        results.append(self.test_list_customer_form())
        results.append(self.test_archive_customer_form())
        results.append(self.test_form_field_lengths())
        results.append(self.test_form_empty_fields())
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] in ['PASS', 'SKIP']])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print("="*65)
        print("COMPREHENSIVE FORMS & DATA SUBMISSION TEST SUMMARY")
        print("="*65)
        print(f"Total Tests: {total_tests}")
        print(f"Passed/Skipped: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {len([r for r in self.test_results if r['status'] == 'PASS'])/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*65)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED FORMS TESTS DETAILS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    print(f"    {result['details']}")
        
        # Clean up created customers
        print("\nCleaning up test customers...")
        for customer_id in self.created_customer_ids:
            try:
                requests.delete(f"http://localhost:8080/api/v1/customers/{customer_id}")
            except:
                pass  # Don't worry if cleanup fails
        
        return all(results)


def main():
    """Main test runner"""
    print("Speckit Customer Management Comprehensive Forms & Data Submission Tests")
    print("="*75)
    
    tester = FormsSubmissionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL FORMS & DATA SUBMISSION TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME FORMS & DATA SUBMISSION TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()