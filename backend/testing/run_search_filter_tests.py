#!/usr/bin/env python3
"""
Search and Filtering Functionality Testing Script
Tests all customer search and filtering capabilities
"""

import requests
import json
import time
import sys
import os


class SearchFilterTester:
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
    
    def create_test_customers(self):
        """Create a set of test customers for search/filter testing"""
        print("Creating test customers for search/filter testing...")
        
        test_customers = [
            {
                "company_name": "Alpha Industries",
                "contact_person": "Alice Alpha",
                "email": f"alice.alpha{int(time.time())}@alpha.com",
                "phone": "+11111111111",
                "city": "Alpha City",
                "notes": "Alpha test customer"
            },
            {
                "company_name": "Beta Corp",
                "contact_person": "Bob Beta",
                "email": f"bob.beta{int(time.time())}@beta.com",
                "phone": "+22222222222",
                "city": "Beta City",
                "notes": "Beta test customer"
            },
            {
                "company_name": "Gamma LLC",
                "contact_person": "Charlie Gamma",
                "email": f"charlie.gamma{int(time.time())}@gamma.com",
                "phone": "+33333333333",
                "city": "Gamma City",
                "notes": "Gamma test customer"
            },
            {
                "company_name": "Search Test Company",
                "contact_person": "Search Test Person",
                "email": f"search.test{int(time.time())}@search.com",
                "phone": "+44444444444",
                "city": "Searchville",
                "notes": "Customer specifically for search testing"
            }
        ]
        
        created_ids = []
        for customer_data in test_customers:
            try:
                response = requests.post("http://localhost:8080/api/v1/customers", json=customer_data)
                if response.status_code == 201:
                    customer = response.json()
                    created_ids.append(customer['id'])
                    print(f"  Created customer: {customer['company_name']} ({customer['id']})")
                else:
                    print(f"  Failed to create customer: {customer_data['company_name']}, Status: {response.status_code}")
            except Exception as e:
                print(f"  Error creating customer {customer_data['company_name']}: {e}")
        
        print(f"  Created {len(created_ids)} test customers")
        return created_ids
    
    def test_basic_search(self):
        """Test basic search functionality"""
        print("Testing basic search functionality...")
        
        # Test search by company name
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Alpha")
            if response.status_code == 200:
                data = response.json()
                found_alpha = any(c['company_name'].find('Alpha') != -1 for c in data.get('items', []))
                if found_alpha:
                    self.log_result("SF-001", "Search - Company Name", "PASS")
                else:
                    self.log_result("SF-001", "Search - Company Name", "FAIL", f"No Alpha customers found in search results: {data}")
                    return False
            else:
                self.log_result("SF-001", "Search - Company Name", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-001", "Search - Company Name", "FAIL", str(e))
            return False
        
        # Test search by contact person
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Beta")
            if response.status_code == 200:
                data = response.json()
                found_beta = any(c['contact_person'].find('Beta') != -1 for c in data.get('items', []))
                if found_beta:
                    self.log_result("SF-002", "Search - Contact Person", "PASS")
                else:
                    self.log_result("SF-002", "Search - Contact Person", "FAIL", f"No Beta contacts found in search results: {data}")
                    return False
            else:
                self.log_result("SF-002", "Search - Contact Person", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-002", "Search - Contact Person", "FAIL", str(e))
            return False
        
        # Test search by email
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=charlie.gamma")
            if response.status_code == 200:
                data = response.json()
                found_gamma = any(c['email'].find('charlie.gamma') != -1 for c in data.get('items', []))
                if found_gamma:
                    self.log_result("SF-003", "Search - Email", "PASS")
                else:
                    self.log_result("SF-003", "Search - Email", "FAIL", f"No charlie.gamma emails found in search results: {data}")
                    return False
            else:
                self.log_result("SF-003", "Search - Email", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-003", "Search - Email", "FAIL", str(e))
            return False
        
        # Test search by city
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Searchville")
            if response.status_code == 200:
                data = response.json()
                found_search = any(c['city'] and c['city'].find('Searchville') != -1 for c in data.get('items', []))
                if found_search:
                    self.log_result("SF-004", "Search - City", "PASS")
                else:
                    self.log_result("SF-004", "Search - City", "FAIL", f"No Searchville cities found in search results: {data}")
                    return False
            else:
                self.log_result("SF-004", "Search - City", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-004", "Search - City", "FAIL", str(e))
            return False
        
        # Test search that should return no results
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=NonExistentCompany")
            if response.status_code == 200:
                data = response.json()
                if data.get('total', 0) == 0:
                    self.log_result("SF-005", "Search - No Results", "PASS")
                else:
                    self.log_result("SF-005", "Search - No Results", "FAIL", f"Expected 0 results, got {data.get('total', 0)}")
                    return False
            else:
                self.log_result("SF-005", "Search - No Results", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-005", "Search - No Results", "FAIL", str(e))
            return False
        
        return True
    
    def test_case_insensitive_search(self):
        """Test that search is case insensitive"""
        print("Testing case insensitive search...")
        
        # Search with lowercase for uppercase text
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=alpha")
            if response.status_code == 200:
                data = response.json()
                found_alpha = any(c['company_name'].find('Alpha') != -1 for c in data.get('items', []))
                if found_alpha:
                    self.log_result("SF-006", "Search - Case Insensitive", "PASS")
                else:
                    self.log_result("SF-006", "Search - Case Insensitive", "FAIL", f"Case insensitive search failed: {data}")
                    return False
            else:
                self.log_result("SF-006", "Search - Case Insensitive", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-006", "Search - Case Insensitive", "FAIL", str(e))
            return False
        
        return True
    
    def test_partial_search(self):
        """Test that partial matches work"""
        print("Testing partial search functionality...")
        
        # Search using partial company name
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Ind")
            if response.status_code == 200:
                data = response.json()
                found_ind = any('Ind' in c['company_name'] for c in data.get('items', []))
                if found_ind:
                    self.log_result("SF-007", "Search - Partial Match", "PASS")
                else:
                    self.log_result("SF-007", "Search - Partial Match", "FAIL", f"Partial match failed: {data}")
                    return False
            else:
                self.log_result("SF-007", "Search - Partial Match", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-007", "Search - Partial Match", "FAIL", str(e))
            return False
        
        return True
    
    def test_pagination(self):
        """Test pagination functionality"""
        print("Testing pagination functionality...")
        
        # Get first page with limit
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?page=1&limit=2")
            if response.status_code == 200:
                data = response.json()
                if len(data['items']) <= 2 and data['limit'] == 2:
                    self.log_result("SF-008", "Pagination - Limit", "PASS")
                else:
                    self.log_result("SF-008", "Pagination - Limit", "FAIL", f"Pagination limit not working: {data}")
                    return False
            else:
                self.log_result("SF-008", "Pagination - Limit", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-008", "Pagination - Limit", "FAIL", str(e))
            return False
        
        # Test that getting page 2 works
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?page=2&limit=2")
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and 'page' in data:
                    self.log_result("SF-009", "Pagination - Page 2", "PASS")
                else:
                    self.log_result("SF-009", "Pagination - Page 2", "FAIL", f"Pagination response missing fields: {data}")
                    return False
            else:
                self.log_result("SF-009", "Pagination - Page 2", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-009", "Pagination - Page 2", "FAIL", str(e))
            return False
        
        return True
    
    def test_combined_search_and_pagination(self):
        """Test search combined with pagination"""
        print("Testing combined search and pagination...")
        
        try:
            response = requests.get("http://localhost:8080/api/v1/customers?search=Test&page=1&limit=1")
            if response.status_code == 200:
                data = response.json()
                if (len(data['items']) <= 1 and 
                    any('Test' in c['company_name'] or 'Test' in c['contact_person'] for c in data['items']) and 
                    data['limit'] == 1):
                    self.log_result("SF-010", "Search + Pagination", "PASS")
                else:
                    self.log_result("SF-010", "Search + Pagination", "FAIL", f"Combined search/pagination failed: {data}")
                    return False
            else:
                self.log_result("SF-010", "Search + Pagination", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("SF-010", "Search + Pagination", "FAIL", str(e))
            return False
        
        return True
    
    def run_all_tests(self):
        """Create test customers and run all search/filter tests"""
        print("\nSetting up test customers...")
        self.created_customer_ids = self.create_test_customers()
        
        if not self.created_customer_ids:
            self.log_result("SF-SETUP", "Test Customer Creation", "FAIL", "Could not create test customers")
            return False
        
        print("\nStarting Search and Filtering Tests...\n")
        
        results = []
        results.append(self.test_basic_search())
        results.append(self.test_case_insensitive_search())
        results.append(self.test_partial_search())
        results.append(self.test_pagination())
        results.append(self.test_combined_search_and_pagination())
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print("="*60)
        print("SEARCH & FILTERING TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*60)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED SEARCH/FILTER TESTS DETAILS:")
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
    print("Speckit Customer Management Search & Filtering Tests")
    print("="*55)
    
    tester = SearchFilterTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL SEARCH & FILTERING TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME SEARCH & FILTERING TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()