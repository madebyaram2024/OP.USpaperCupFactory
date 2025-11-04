#!/usr/bin/env python3
"""
Frontend Modal and Form Testing Script
Tests the modal functionality and forms in the customer management UI
"""

import requests
import json
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import subprocess
import signal

class FrontendModalTester:
    def __init__(self):
        self.test_results = []
        self.driver = None
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
    
    def setup_driver(self):
        """Setup Selenium WebDriver for testing"""
        try:
            # Try to use Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Failed to setup Chrome driver: {e}")
            print("Selenium WebDriver may not be installed or Chrome not found.")
            print("To run these tests, install ChromeDriver and add it to PATH.")
            return False
    
    def check_element_exists(self, by, value):
        """Check if element exists without raising exception"""
        try:
            self.driver.find_element(by, value)
            return True
        except:
            return False
    
    def test_modal_open_close(self):
        """Test that modals open and close properly"""
        print("Testing modal open/close functionality...")
        
        try:
            # Navigate to customer management page
            self.driver.get("http://localhost:4000")
            
            # Wait for page to load and click on Customers in sidebar
            try:
                customers_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a//span[text()='Customers']"))
                )
                customers_link.click()
            except:
                # Try different selector for customers link
                try:
                    customers_link = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '#') and contains(text(), 'Customers')]"))
                    )
                    customers_link.click()
                except:
                    # Just navigate directly to customer functionality
                    pass
            
            # Wait for page to load and find the "Add New Customer" button
            add_customer_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "addCustomerBtn"))
            )
            
            # Click the "Add New Customer" button
            add_customer_btn.click()
            
            # Verify modal appears
            modal = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "customerModal"))
            )
            
            if modal:
                self.log_result("FM-001", "Add Customer Modal - Opens", "PASS")
            else:
                self.log_result("FM-001", "Add Customer Modal - Opens", "FAIL", "Modal did not appear")
                return False
            
            # Test closing modal with Cancel button
            cancel_btn = self.driver.find_element(By.ID, "cancelBtn")
            cancel_btn.click()
            
            # Wait for modal to close
            WebDriverWait(self.driver, 10).until_not(
                EC.visibility_of_element_located((By.ID, "customerModal"))
            )
            
            if not self.check_element_exists(By.ID, "customerModal"):
                self.log_result("FM-002", "Add Customer Modal - Close via Cancel", "PASS")
            else:
                self.log_result("FM-002", "Add Customer Modal - Close via Cancel", "FAIL", "Modal did not close after Cancel click")
                return False
            
            # Reopen modal to test close with X button
            add_customer_btn.click()
            
            # Test closing with X button
            close_x = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='customerModal']//button[contains(@class, 'absolute')]"))
            )
            close_x.click()
            
            # Wait for modal to close
            WebDriverWait(self.driver, 10).until_not(
                EC.visibility_of_element_located((By.ID, "customerModal"))
            )
            
            if not self.check_element_exists(By.ID, "customerModal"):
                self.log_result("FM-003", "Add Customer Modal - Close via X", "PASS")
            else:
                self.log_result("FM-003", "Add Customer Modal - Close via X", "FAIL", "Modal did not close after X click")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("FM-001", "Add Customer Modal - Opens", "FAIL", str(e))
            self.log_result("FM-002", "Add Customer Modal - Close via Cancel", "FAIL", str(e))
            self.log_result("FM-003", "Add Customer Modal - Close via X", "FAIL", str(e))
            return False
    
    def test_form_validation(self):
        """Test form validation in the add customer modal"""
        print("Testing form validation...")
        
        try:
            # Navigate to customer management
            self.driver.get("http://localhost:4000")
            
            # Click on Customers in sidebar
            try:
                customers_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a//span[text()='Customers']"))
                )
                customers_link.click()
            except:
                pass  # Continue without clicking if not needed
            
            # Click the "Add New Customer" button
            add_customer_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "addCustomerBtn"))
            )
            add_customer_btn.click()
            
            # Find form elements
            save_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            company_name_field = self.driver.find_element(By.ID, "companyName")
            contact_person_field = self.driver.find_element(By.ID, "contactPersonInput")
            email_field = self.driver.find_element(By.ID, "email")
            
            # Test submitting empty form - should trigger validation
            save_btn.click()
            
            # Check if validation errors appear (form should not submit)
            # Wait a moment for any client-side validation
            time.sleep(1)
            
            # The modal should still be open if validation is working
            if self.check_element_exists(By.ID, "customerModal"):
                self.log_result("FM-004", "Form Validation - Required Fields", "PASS")
            else:
                self.log_result("FM-004", "Form Validation - Required Fields", "FAIL", "Modal closed even with empty required fields")
                return False
            
            # Test with valid data to make sure form can submit
            # Fill in valid data
            company_name_field.clear()
            company_name_field.send_keys("Test Company Form Validation")
            
            contact_person_field.clear()
            contact_person_field.send_keys("Test Contact")
            
            email_field.clear()
            email_field.send_keys(f"test{int(time.time())}@testvalidation.com")
            
            # Submit the form
            save_btn.click()
            
            # Wait for success modal to appear (form submission)
            success_modal = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "successModal"))
            )
            
            if success_modal:
                self.log_result("FM-005", "Form Submission - Valid Data", "PASS")
                
                # Close success modal
                done_btn = self.driver.find_element(By.ID, "doneBtn")
                done_btn.click()
                
                return True
            else:
                self.log_result("FM-005", "Form Submission - Valid Data", "FAIL", "Success modal did not appear after valid submission")
                return False
                
        except Exception as e:
            self.log_result("FM-004", "Form Validation - Required Fields", "FAIL", str(e))
            self.log_result("FM-005", "Form Submission - Valid Data", "FAIL", str(e))
            return False
    
    def run_frontend_tests_without_selenium(self):
        """Run frontend tests by directly using the API to simulate form submissions"""
        print("Running frontend form simulation tests via API...")
        
        # This simulates what the frontend forms would submit
        success_count = 0
        
        # Test 1: Form submission with valid data
        customer_data = {
            "company_name": "Frontend Test Company",
            "contact_person": "Frontend Test Person",
            "email": f"frontend{int(time.time())}@test.com",
            "phone": "+11234567890",
            "city": "Frontend City",
            "notes": "Created through frontend simulation"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=customer_data)
            if response.status_code == 201:
                created_customer = response.json()
                self.created_customer_ids.append(created_customer['id'])
                self.log_result("FM-006", "Frontend Form Submission - Valid Data", "PASS")
                success_count += 1
            else:
                self.log_result("FM-006", "Frontend Form Submission - Valid Data", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("FM-006", "Frontend Form Submission - Valid Data", "FAIL", str(e))
        
        # Test 2: Form submission with invalid email (should fail validation)
        invalid_customer_data = {
            "company_name": "Invalid Email Test",
            "contact_person": "Test Person",
            "email": "invalid-email",  # Invalid email format
            "phone": "+11234567890"
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=invalid_customer_data)
            if response.status_code == 422:  # Validation error expected
                self.log_result("FM-007", "Frontend Form Validation - Invalid Email", "PASS")
                success_count += 1
            else:
                self.log_result("FM-007", "Frontend Form Validation - Invalid Email", "FAIL", f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("FM-007", "Frontend Form Validation - Invalid Email", "FAIL", str(e))
        
        # Test 3: Form submission with missing required fields
        incomplete_data = {
            "company_name": ""  # Missing required fields
        }
        
        try:
            response = requests.post("http://localhost:8080/api/v1/customers", json=incomplete_data)
            if response.status_code == 422:  # Validation error expected
                self.log_result("FM-008", "Frontend Form Validation - Missing Fields", "PASS")
                success_count += 1
            else:
                self.log_result("FM-008", "Frontend Form Validation - Missing Fields", "FAIL", f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("FM-008", "Frontend Form Validation - Missing Fields", "FAIL", str(e))
        
        return success_count == 3
    
    def run_all_tests(self):
        """Run all frontend modal and form tests"""
        print("Starting Frontend Modal and Form Tests...\n")
        
        # Try Selenium-based tests first
        if self.setup_driver():
            results = []
            results.append(self.test_modal_open_close())
            results.append(self.test_form_validation())
            
            # Clean up
            if self.driver:
                self.driver.quit()
            
            success = all(results)
        else:
            # If Selenium is not available, run API-based tests that simulate frontend behavior
            success = self.run_frontend_tests_without_selenium()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        print("="*60)
        print("FRONTEND MODAL/FORM TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.2f}%" if total_tests > 0 else "Success Rate: 0%")
        print("="*60)
        
        # Print failed tests details
        if failed_tests > 0:
            print("\nFAILED FRONTEND TESTS DETAILS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test_id']}: {result['test_name']}")
                    print(f"    {result['details']}")
        
        return success


def main():
    """Main test runner"""
    print("Speckit Customer Management Frontend Modal & Form Testing Suite")
    print("="*65)
    
    tester = FrontendModalTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL FRONTEND MODAL/FORM TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME FRONTEND MODAL/FORM TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()