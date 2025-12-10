# Integration Test for Symptom Recommendations API
# Tests the /api/symptom-recommendations endpoint

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  INTEGRATION TEST: Symptom Recommendations API" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"
$endpoint = "$baseUrl/api/symptom-recommendations"
$passCount = 0
$failCount = 0

function Test-Endpoint {
    param(
        [string]$TestName,
        [hashtable]$Body,
        [bool]$ShouldSucceed = $true,
        [string[]]$ExpectedSpecialties = @()
    )
    
    Write-Host "TEST: $TestName" -ForegroundColor Yellow
    
    try {
        $jsonBody = $Body | ConvertTo-Json -Depth 10
        $response = Invoke-RestMethod -Uri $endpoint -Method Post -Body $jsonBody -ContentType "application/json" -ErrorAction Stop
        
        if ($ShouldSucceed) {
            if ($response.ok -eq $true) {
                Write-Host "  ✓ Response OK" -ForegroundColor Green
                
                # Check specialties
                if ($ExpectedSpecialties.Count -gt 0) {
                    $found = $false
                    foreach ($expected in $ExpectedSpecialties) {
                        if ($response.specialties -contains $expected) {
                            $found = $true
                            Write-Host "  ✓ Found expected specialty: $expected" -ForegroundColor Green
                        }
                    }
                    if (-not $found) {
                        Write-Host "  ✗ Expected specialties not found. Got: $($response.specialties -join ', ')" -ForegroundColor Red
                        $script:failCount++
                        return
                    }
                }
                
                # Check recommendations structure
                if ($response.recommendations -and $response.recommendations.Count -gt 0) {
                    Write-Host "  ✓ Got $($response.recommendations.Count) specialty recommendation(s)" -ForegroundColor Green
                    
                    foreach ($rec in $response.recommendations) {
                        if ($rec.doctors -and $rec.doctors.Count -gt 0) {
                            $doctor = $rec.doctors[0]
                            Write-Host "    - $($rec.specialty): $($doctor.name) at $($doctor.address)" -ForegroundColor Cyan
                            
                            # Verify required fields
                            if ($doctor.name -and $doctor.phone -and $doctor.address -and $doctor.lat -and $doctor.lng) {
                                Write-Host "      ✓ All required fields present" -ForegroundColor Green
                            } else {
                                Write-Host "      ✗ Missing required fields" -ForegroundColor Red
                                $script:failCount++
                                return
                            }
                        }
                    }
                    
                    $script:passCount++
                } else {
                    Write-Host "  ✗ No recommendations returned" -ForegroundColor Red
                    $script:failCount++
                }
            } else {
                Write-Host "  ✗ Response not OK" -ForegroundColor Red
                $script:failCount++
            }
        } else {
            Write-Host "  ✗ Should have failed but succeeded" -ForegroundColor Red
            $script:failCount++
        }
    }
    catch {
        if (-not $ShouldSucceed) {
            Write-Host "  ✓ Failed as expected: $($_.Exception.Message)" -ForegroundColor Green
            $script:passCount++
        } else {
            Write-Host "  ✗ Request failed: $($_.Exception.Message)" -ForegroundColor Red
            $script:failCount++
        }
    }
    
    Write-Host ""
}

# Test 1: ENT symptoms (head/throat + hearing issues)
Test-Endpoint -TestName "ENT Symptoms" -Body @{
    patientLocation = @{ lat = 22.5726; lng = 88.3639 }
    answers = @{
        q1 = "a"  # Head/throat
        q2 = "a"  # Sharp pain
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "a"  # Hearing loss/ear pain
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("ENT")

# Test 2: Cardiology symptoms (chest pain + breathlessness)
Test-Endpoint -TestName "Cardiology Symptoms" -Body @{
    patientLocation = @{ lat = 19.0760; lng = 72.8777 }  # Mumbai
    answers = @{
        q1 = "b"  # Chest/breathing/heart
        q2 = "a"  # Sharp pain
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "a"  # Severe breathlessness
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Cardiology")

# Test 3: Orthopedics symptoms (limb + injury)
Test-Endpoint -TestName "Orthopedics Symptoms" -Body @{
    patientLocation = @{ lat = 28.6139; lng = 77.2090 }  # Delhi
    answers = @{
        q1 = "c"  # Arms/legs/joints/back
        q2 = "a"  # Sharp pain
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "a"  # Major injury/fracture
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Orthopedics")

# Test 4: Dermatology symptoms (skin rash)
Test-Endpoint -TestName "Dermatology Symptoms" -Body @{
    answers = @{
        q1 = "a"  # Head
        q2 = "c"  # Burning/tingling
        q3 = "c"  # No fever
        q4 = "a"  # Rash/lesion
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Dermatology")

# Test 5: Psychiatry symptoms (mental health)
Test-Endpoint -TestName "Psychiatry Symptoms" -Body @{
    answers = @{
        q1 = "a"  # Head
        q2 = "b"  # Dull aching
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "a"  # Severe mental changes
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Psychiatry")

# Test 6: OB/GYN symptoms (pregnancy)
Test-Endpoint -TestName "OB/GYN Symptoms" -Body @{
    answers = @{
        q1 = "b"  # Chest
        q2 = "b"  # Dull aching
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "b"  # Mild nausea
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "a" # Pregnant/unsure
    }
} -ExpectedSpecialties @("Obstetrics/Gynecology")

# Test 7: Gastroenterology symptoms (digestive)
Test-Endpoint -TestName "Gastroenterology Symptoms" -Body @{
    answers = @{
        q1 = "b"  # Chest/abdomen
        q2 = "b"  # Dull aching
        q3 = "b"  # Mild fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "a"  # Severe abdominal pain
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Gastroenterology")

# Test 8: Neurology symptoms (neurological)
Test-Endpoint -TestName "Neurology Symptoms" -Body @{
    answers = @{
        q1 = "a"  # Head
        q2 = "c"  # Burning/tingling/numbness
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Neurology")

# Test 9: Multiple specialties (complex case)
Test-Endpoint -TestName "Multiple Specialties" -Body @{
    patientLocation = @{ lat = 22.5726; lng = 88.3639 }
    answers = @{
        q1 = "a"  # Head (ENT +2, Neurology +1)
        q2 = "c"  # Burning/tingling (Neurology +2)
        q3 = "a"  # High fever (Infectious +2, GP +1)
        q4 = "c"  # No skin
        q5 = "a"  # Hearing loss (ENT +2)
        q6 = "c"  # No breathing
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
}

# Test 10: Without location (should still work)
Test-Endpoint -TestName "Without Patient Location" -Body @{
    answers = @{
        q1 = "b"  # Chest
        q2 = "a"  # Sharp
        q3 = "c"  # No fever
        q4 = "c"  # No skin
        q5 = "c"  # No hearing
        q6 = "a"  # Severe breathlessness
        q7 = "c"  # No digestive
        q8 = "c"  # No injury
        q9 = "c"  # No mental
        q10 = "c" # Not pregnant
    }
} -ExpectedSpecialties @("Cardiology")

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  PASSED: $passCount" -ForegroundColor Green
Write-Host "  FAILED: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "  ✓ ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "  ✗ SOME TESTS FAILED" -ForegroundColor Red
    exit 1
}
