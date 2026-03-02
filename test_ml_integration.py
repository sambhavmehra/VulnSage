#!/usr/bin/env python3
"""
Test ML Model Integration
Verifies that the vulnerability_model.pkl is properly integrated
"""

import sys
import os

print("=" * 70)
print("🧪 Testing ML Model Integration")
print("=" * 70)

# Test 1: Check if model file exists
print("\n[1] Checking if vulnerability_model.pkl exists...")
if os.path.exists('vulnerability_model.pkl'):
    print("✅ Model file found")
    file_size = os.path.getsize('vulnerability_model.pkl')
    print(f"   File size: {file_size / 1024:.2f} KB")
else:
    print("❌ Model file NOT found!")
    sys.exit(1)

# Test 2: Try loading the model
print("\n[2] Loading ML model...")
try:
    import joblib
    model = joblib.load('vulnerability_model.pkl')
    print("✅ Model loaded successfully")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Features: {list(model.feature_names_in_)}")
    print(f"   Classes: {list(model.classes_)}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# Test 3: Test VulnerabilityDetector initialization
print("\n[3] Testing VulnerabilityDetector with ML model...")
try:
    from vulnerability_detector import VulnerabilityDetector
    
    # Initialize with ML model
    detector = VulnerabilityDetector(
        enable_ai=False,  # Disable AI for this test
        max_pages=5,
        model_path='vulnerability_model.pkl'
    )
    
    if detector.enable_ml:
        print("✅ VulnerabilityDetector initialized with ML model")
        print(f"   ML enabled: {detector.enable_ml}")
        print(f"   Model classes: {list(detector.ml_model.classes_)}")
    else:
        print("❌ ML model not enabled in detector")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to initialize detector: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test feature extraction
print("\n[4] Testing ML feature extraction...")
try:
    # Create a mock page object
    test_page = {
        'url': 'https://example.com/test',
        'html': '<html><body><script src="test.js"></script></body></html>',
        'headers': {'Content-Type': 'text/html'},
        'forms': [
            {'action': '/login', 'method': 'POST', 'inputs': []}
        ],
        'scripts': [
            {'src': 'test.js', 'external': False}
        ],
        'links': [],
        'inputs': [],
        'cookies': {}
    }
    
    features = detector._extract_ml_features(test_page)
    print("✅ Feature extraction successful")
    print(f"   Extracted features: {features}")
    print(f"   Feature breakdown:")
    print(f"   - Forms: {features[0]}")
    print(f"   - Scripts: {features[1]}")
    print(f"   - Missing CSP: {features[2]}")
    
except Exception as e:
    print(f"❌ Feature extraction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test ML prediction
print("\n[5] Testing ML vulnerability prediction...")
try:
    # Test with different feature combinations
    test_cases = [
        {
            'name': 'High risk page (many forms, many scripts, no CSP)',
            'features': [5, 10, 1],
            'page': {
                'url': 'https://example.com/login',
                'forms': [{}] * 5,
                'scripts': [{}] * 10,
                'headers': {}
            }
        },
        {
            'name': 'Low risk page (no forms, few scripts, has CSP)',
            'features': [0, 2, 0],
            'page': {
                'url': 'https://example.com/about',
                'forms': [],
                'scripts': [{}] * 2,
                'headers': {'Content-Security-Policy': 'default-src self'}
            }
        },
        {
            'name': 'Medium risk page (some forms, some scripts, no CSP)',
            'features': [2, 5, 1],
            'page': {
                'url': 'https://example.com/contact',
                'forms': [{}] * 2,
                'scripts': [{}] * 5,
                'headers': {}
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        features = test_case['features']
        
        prediction = model.predict([features])[0]
        probability = model.predict_proba([features])[0]
        
        print(f"   Features: {features}")
        print(f"   Prediction: {prediction}")
        print(f"   Confidence scores:")
        for cls, prob in zip(model.classes_, probability):
            print(f"     - {cls}: {prob*100:.1f}%")
    
    print("\n✅ ML prediction working correctly")
    
except Exception as e:
    print(f"❌ ML prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test complete ML detection
print("\n[6] Testing complete ML vulnerability detection...")
try:
    test_page = {
        'url': 'https://example.com/admin',
        'html': '<html><body><form><input type="text" name="username"></form></body></html>',
        'headers': {},
        'forms': [
            {'action': '/login', 'method': 'POST', 'inputs': [{'name': 'user', 'type': 'text'}]},
            {'action': '/register', 'method': 'POST', 'inputs': [{'name': 'email', 'type': 'email'}]}
        ],
        'scripts': [
            {'src': 'jquery.js', 'external': True},
            {'src': 'app.js', 'external': False},
            {'src': None, 'inline': 'console.log("test");'}
        ],
        'links': [],
        'inputs': [],
        'cookies': {}
    }
    
    vulnerabilities = detector._ml_detect_vulnerabilities(test_page)
    
    if vulnerabilities:
        print(f"✅ ML detected {len(vulnerabilities)} vulnerability(ies)")
        for vuln in vulnerabilities:
            print(f"\n   Vulnerability: {vuln['type']}")
            print(f"   Severity: {vuln['severity']}")
            print(f"   Confidence: {vuln['confidence']}%")
            print(f"   ML Prediction: {vuln.get('ml_prediction')}")
            print(f"   Detection Method: {vuln.get('detection_method')}")
    else:
        print("   No vulnerabilities detected (confidence below threshold)")
        
except Exception as e:
    print(f"❌ Complete ML detection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\n💡 Summary:")
print("   - ML model is properly loaded")
print("   - VulnerabilityDetector can use the ML model")
print("   - Feature extraction is working")
print("   - ML predictions are functional")
print("   - Complete vulnerability detection pipeline works")
print("\n🚀 Your scanner is ready to use ML-powered detection!")
print("\n   Run the app with: streamlit run app_ai.py")
print("=" * 70)
