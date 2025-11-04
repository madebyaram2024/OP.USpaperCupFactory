#!/usr/bin/env python3
"""
End-to-End Customer Management Testing Script
Tests the entire customer management flow from frontend to backend
"""

import requests
import json
import time
import sys
import os

# Configuration
BASE_URL = "http://localhost:8080"
API_BASE = f"{BASE_URL}/api/v1/customers"

class EndToEndTester:
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
    
    def test_customer_lifecycle(self):
        """Test complete customer lifecycle: Create -> Read -> Update -> Archive"""
        print("Testing complete customer lifecycle...")
        
        # Step 1: Create a customer
        customer_data = {
            "company_name": "End-to-End Test Company",
            "contact_person": "John E2E Doe",
            "email": f"e2e{int(time.time())}@testcompany.com",
            "phone": "+19999999999",
            "address_line1": "999 E2E Test Street",
            "city": "E2E Test City",
            "state_province": "ET",
            "postal_code": "99999",
            "country": "E2E Test Country",
            "notes": "End-to-end testing customer"
        }
        
        try:
            response = requests.post(API_BASE, json=customer_data)
            if response.status_code == 201:
                created_customer = response.json()
                customer_id = created_customer['id']
                self.created_customer_ids.append(customer_id)
                self.log_result("E2E-001", "Customer Creation - Complete Lifecycle", "PASS")
            else:
                self.log_result("E2E-001", "Customer Creation - Complete Lifecycle", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("E2E-001", "Customer Creation - Complete Lifecycle", "FAIL", str(e))
            return False
        
        # Step 2: Retrieve the customer and verify data
        try:
            response = requests.get(f"{API_BASE}/{customer_id}")
            if response.status_code == 200:
                retrieved_customer = response.json()
                if (retrieved_customer['company_name'] == customer_data['company_name'] and 
                    retrieved_customer['email'] == customer_data['email']):
                    self.log_result("E2E-002", "Customer Retrieval - Verify Created Data", "PASS")
                else:
                    self.log_result("E2E-002", "Customer Retrieval - Verify Created Data", "FAIL", "Retrieved data doesn't match created data")
                    return False
            else:
                self.log_result("E2E-002", "Customer Retrieval - Verify Created Data", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-002", "Customer Retrieval - Verify Created Data", "FAIL", str(e))
            return False
        
        # Step 3: Update the customer
        update_data = {
            "company_name": "Updated E2E Test Company",
            "contact_person": "Jane E2E Updated",
            "email": f"updated-e2e{int(time.time())}@testcompany.com"
        }
        
        try:
            response = requests.put(f"{API_BASE}/{customer_id}", json=update_data)
            if response.status_code == 200:
                updated_customer = response.json()
                if updated_customer['company_name'] == update_data['company_name']:
                    self.log_result("E2E-003", "Customer Update - Modify Data", "PASS")
                else:
                    self.log_result("E2E-003", "Customer Update - Modify Data", "FAIL", "Updated data doesn't match expected values")
                    return False
            else:
                self.log_result("E2E-003", "Customer Update - Modify Data", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("E2E-003", "Customer Update - Modify Data", "FAIL", str(e))
            return False
        
        # Step 4: Retrieve again to verify update
        try:
            response = requests.get(f"{API_BASE}/{customer_id}")
            if response.status_code == 200:
                retrieved_after_update = response.json()
                if retrieved_after_update['company_name'] == update_data['company_name']:
                    self.log_result("E2E-004", "Customer Retrieval - Verify Updated Data", "PASS")
                else:
                    self.log_result("E2E-004", "Customer Retrieval - Verify Updated Data", "FAIL", "Data not updated properly")
                    return False
            else:
                self.log_result("E2E-004", "Customer Retrieval - Verify Updated Data", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-004", "Customer Retrieval - Verify Updated Data", "FAIL", str(e))
            return False
        
        # Step 5: Archive the customer
        try:
            response = requests.delete(f"{API_BASE}/{customer_id}")
            if response.status_code == 204:
                self.log_result("E2E-005", "Customer Archive - Complete Lifecycle", "PASS")
            else:
                self.log_result("E2E-005", "Customer Archive - Complete Lifecycle", "FAIL", f"Expected 204, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-005", "Customer Archive - Complete Lifecycle", "FAIL", str(e))
            return False
        
        # Step 6: Try to retrieve archived customer (should still be accessible but with archived status)
        try:
            response = requests.get(f"{API_BASE}/{customer_id}")
            if response.status_code == 200:
                final_customer = response.json()
                # Note: The status might be archived if properly implemented
                self.log_result("E2E-006", "Customer Retrieval - After Archive", "PASS")
            else:
                self.log_result("E2E-006", "Customer Retrieval - After Archive", "FAIL", f"Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-006", "Customer Retrieval - After Archive", "FAIL", str(e))
            return False
        
        return True
    
    def test_customer_search_and_filter(self):
        """Test search and filtering functionality"""
        print("Testing search and filtering functionality...")
        
        # Create multiple test customers
        customers_to_create = [
            {
                "company_name": "Test Search Company Alpha",
                "contact_person": "Alpha Contact",
                "email": f"alpha{int(time.time())}@testsearch.com",
                "phone": "+11111111111"
            },
            {
                "company_name": "Test Search Company Beta",
                "contact_person": "Beta Contact", 
                "email": f"beta{int(time.time())}@testsearch.com",
                "phone": "+22222222222"
            },
            {
                "company_name": "Test Search Company Gamma",
                "contact_person": "Gamma Contact",
                "email": f"gamma{int(time.time())}@testsearch.com", 
                "phone": "+33333333333"
            }
        ]
        
        created_ids = []
        for customer_data in customers_to_create:
            try:
                response = requests.post(API_BASE, json=customer_data)
                if response.status_code == 201:
                    customer = response.json()
                    created_ids.append(customer['id'])
                else:
                    self.log_result("E2E-007", "Bulk Customer Creation for Search Test", "FAIL", f"Failed to create customer: {response.status_code}")
                    return False
            except Exception as e:
                self.log_result("E2E-007", "Bulk Customer Creation for Search Test", "FAIL", str(e))
                return False
        
        # Test search functionality
        try:
            response = requests.get(f"{API_BASE}?search=Alpha")
            if response.status_code == 200:
                data = response.json()
                if data['total'] >= 1:
                    self.log_result("E2E-008", "Customer Search Functionality", "PASS")
                else:
                    self.log_result("E2E-008", "Customer Search Functionality", "FAIL", f"Expected at least 1 result for 'Alpha', got {data['total']}")
                    return False
            else:
                self.log_result("E2E-008", "Customer Search Functionality", "FAIL", f"Search returned {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-008", "Customer Search Functionality", "FAIL", str(e))
            return False
        
        # Test pagination
        try:
            response = requests.get(f"{API_BASE}?page=1&limit=2")
            if response.status_code == 200:
                data = response.json()
                if len(data['items']) <= 2 and 'total' in data:
                    self.log_result("E2E-009", "Customer Pagination", "PASS")
                else:
                    self.log_result("E2E-009", "Customer Pagination", "FAIL", "Pagination not working correctly")
                    return False
            else:
                self.log_result("E2E-009", "Customer Pagination", "FAIL", f"Pagination returned {response.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-009", "Customer Pagination", "FAIL", str(e))
            return False
        
        # Clean up created customers
        for customer_id in created_ids:
            try:
                requests.delete(f"{API_BASE}/{customer_id}")
            except:
                pass  # Don't worry if cleanup fails
        
        return True
    
    def test_duplicate_prevention(self):
        """Test that duplicate emails are prevented"""
        print("Testing duplicate prevention...")
        
        # Create a customer
        customer_data = {
            "company_name": "Duplicate Prevention Test",
            "contact_person": "Duplicate Contact",
            "email": "duplicate@test.com",
            "phone": "+44444444444"
        }
        
        try:
            # First creation should succeed
            response1 = requests.post(API_BASE, json=customer_data)
            
            if response1.status_code == 201:
                # Second creation with same email should fail
                response2 = requests.post(API_BASE, json=customer_data)
                
                if response2.status_code == 409:
                    self.log_result("E2E-010", "Duplicate Email Prevention", "PASS")
                    
                    # Clean up the created customer
                    created_customer = response1.json()
                    requests.delete(f"{API_BASE}/{created_customer['id']}")
                    
                    return True
                else:
                    self.log_result("E2E-010", "Duplicate Email Prevention", "FAIL", f"Expected 409 conflict, got {response2.status_code}")
                    return False
            else:
                self.log_result("E2E-010", "Duplicate Email Prevention", "FAIL", f"First creation failed with {response1.status_code}")
                return False
        except Exception as e:
            self.log_result("E2E-010", "Duplicate Email Prevention", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Run all end-to-end tests"""
        print("Starting End-to-End Customer Management Tests...\n")
        
        results = []
        results.append(self.test_customer_lifecycle())
        results.append(self.test_customer_search_and_filter())
        results.append(self.test_duplicate_prevention())
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print("="*60)
        print("E2E TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*60)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED E2E TESTS DETAILS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    print(f"    {result['details']}")
        
        return all(results)


def main():
    """Main test runner"""
    print("Speckit Customer Management End-to-End Testing Suite")
    print("="*55)
    
    tester = EndToEndTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL END-TO-END TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME END-TO-END TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()