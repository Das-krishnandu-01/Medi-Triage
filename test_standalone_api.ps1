#!/usr/bin/env powershell
# Test Script for Standalone Appointment Booking API
# Tests all endpoints with complete validation

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  STANDALONE APPOINTMENT BOOKING API - TEST SUITE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BASE_URL = "http://localhost:8001"
$HEADERS = @{
    "Content-Type" = "application/json"
}

# Test counter
$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "[$($testsPassed + $testsFailed + 1)] Testing: $Name" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = "$BASE_URL$Endpoint"
            Method = $Method
            Headers = $HEADERS
        }
        
        if ($Body) {
            $params['Body'] = ($Body | ConvertTo-Json -Compress)
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        $data = $response.Content | ConvertFrom-Json
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "   ✓ PASS" -ForegroundColor Green
            Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
            if ($data.data.appointmentId) {
                Write-Host "   Appointment ID: $($data.data.appointmentId)" -ForegroundColor Gray
                return $data.data.appointmentId
            }
            $script:testsPassed++
            return $data
        } else {
            Write-Host "   ✗ FAIL - Expected $ExpectedStatus, got $($response.StatusCode)" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    catch {
        Write-Host "   ✗ FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
    }
    
    Write-Host ""
    return $null
}

# Check if server is running
Write-Host "Checking if API server is running..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri $BASE_URL -Method GET -ErrorAction Stop
    Write-Host "✓ Server is running" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "✗ Server is not running!" -ForegroundColor Red
    Write-Host "Please start the server first:" -ForegroundColor Yellow
    Write-Host "  python standalone_booking_api.py" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 1: Health Check" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "Health Check" -Method "GET" -Endpoint "/"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 2: Create Valid Appointment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$futureDate = (Get-Date).AddDays(5).ToString("yyyy-MM-ddTHH:mm:ssZ")
$futureEndDate = (Get-Date).AddDays(5).AddMinutes(30).ToString("yyyy-MM-ddTHH:mm:ssZ")

$validAppointment = @{
    userId = "user-test-123"
    startTime = $futureDate
    endTime = $futureEndDate
    mode = "video"
    notes = "Test appointment"
}

$appointmentId = Test-Endpoint `
    -Name "Create Valid Appointment" `
    -Method "POST" `
    -Endpoint "/appointments" `
    -Body $validAppointment `
    -ExpectedStatus 201

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 3: Get Appointment by ID" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($appointmentId) {
    Test-Endpoint `
        -Name "Get Appointment" `
        -Method "GET" `
        -Endpoint "/appointments/$appointmentId"
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 4: List All Appointments" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Name "List All Appointments" -Method "GET" -Endpoint "/appointments"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 5: List Appointments by User" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Test-Endpoint `
    -Name "List User's Appointments" `
    -Method "GET" `
    -Endpoint "/appointments?userId=user-test-123"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 6: Validation Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test: Empty userId
$invalidAppointment1 = @{
    userId = ""
    startTime = $futureDate
    endTime = $futureEndDate
    mode = "video"
}

Write-Host "[V1] Testing: Empty userId (should fail)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest `
        -Uri "$BASE_URL/appointments" `
        -Method POST `
        -Headers $HEADERS `
        -Body ($invalidAppointment1 | ConvertTo-Json -Compress) `
        -ErrorAction Stop
    
    Write-Host "   ✗ FAIL - Should have rejected empty userId" -ForegroundColor Red
    $script:testsFailed++
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "   ✓ PASS - Correctly rejected empty userId" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "   ✗ FAIL - Wrong status code" -ForegroundColor Red
        $script:testsFailed++
    }
}
Write-Host ""

# Test: Past time
$pastDate = (Get-Date).AddDays(-1).ToString("yyyy-MM-ddTHH:mm:ssZ")
$invalidAppointment2 = @{
    userId = "user-test-123"
    startTime = $pastDate
    endTime = $futureDate
    mode = "video"
}

Write-Host "[V2] Testing: Past startTime (should fail)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest `
        -Uri "$BASE_URL/appointments" `
        -Method POST `
        -Headers $HEADERS `
        -Body ($invalidAppointment2 | ConvertTo-Json -Compress) `
        -ErrorAction Stop
    
    Write-Host "   ✗ FAIL - Should have rejected past time" -ForegroundColor Red
    $script:testsFailed++
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "   ✓ PASS - Correctly rejected past time" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "   ✗ FAIL - Wrong status code" -ForegroundColor Red
        $script:testsFailed++
    }
}
Write-Host ""

# Test: End before start
$invalidAppointment3 = @{
    userId = "user-test-123"
    startTime = $futureEndDate
    endTime = $futureDate
    mode = "video"
}

Write-Host "[V3] Testing: endTime before startTime (should fail)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest `
        -Uri "$BASE_URL/appointments" `
        -Method POST `
        -Headers $HEADERS `
        -Body ($invalidAppointment3 | ConvertTo-Json -Compress) `
        -ErrorAction Stop
    
    Write-Host "   ✗ FAIL - Should have rejected endTime < startTime" -ForegroundColor Red
    $script:testsFailed++
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "   ✓ PASS - Correctly rejected endTime < startTime" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "   ✗ FAIL - Wrong status code" -ForegroundColor Red
        $script:testsFailed++
    }
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 7: Cancel Appointment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($appointmentId) {
    Test-Endpoint `
        -Name "Cancel Appointment" `
        -Method "POST" `
        -Endpoint "/appointments/$appointmentId/cancel"
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 8: Confirm Appointment (on cancelled - should fail)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($appointmentId) {
    Write-Host "[8] Testing: Confirm cancelled appointment (should fail)" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest `
            -Uri "$BASE_URL/appointments/$appointmentId/confirm" `
            -Method POST `
            -ErrorAction Stop
        
        Write-Host "   ✗ FAIL - Should not allow confirming cancelled appointment" -ForegroundColor Red
        $script:testsFailed++
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-Host "   ✓ PASS - Correctly prevented confirming cancelled appointment" -ForegroundColor Green
            $script:testsPassed++
        } else {
            Write-Host "   ✗ FAIL - Wrong status code" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 9: Create Another Appointment for Confirmation Test" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$appointmentId2 = Test-Endpoint `
    -Name "Create Second Appointment" `
    -Method "POST" `
    -Endpoint "/appointments" `
    -Body $validAppointment `
    -ExpectedStatus 201

if ($appointmentId2) {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  TEST 10: Confirm Appointment (should succeed)" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    Test-Endpoint `
        -Name "Confirm Appointment" `
        -Method "POST" `
        -Endpoint "/appointments/$appointmentId2/confirm"
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 11: Delete Appointment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($appointmentId) {
    Test-Endpoint `
        -Name "Delete Appointment" `
        -Method "DELETE" `
        -Endpoint "/appointments/$appointmentId"
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST 12: Get Deleted Appointment (should fail)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($appointmentId) {
    Write-Host "[12] Testing: Get deleted appointment (should fail)" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest `
            -Uri "$BASE_URL/appointments/$appointmentId" `
            -Method GET `
            -ErrorAction Stop
        
        Write-Host "   ✗ FAIL - Should not find deleted appointment" -ForegroundColor Red
        $script:testsFailed++
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "   ✓ PASS - Correctly returned 404 for deleted appointment" -ForegroundColor Green
            $script:testsPassed++
        } else {
            Write-Host "   ✗ FAIL - Wrong status code" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    Write-Host ""
}

# Test Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests: $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✓ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ✗ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    exit 1
}
