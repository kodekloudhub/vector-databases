"""
Test script for Amazon Bedrock connectivity and functionality
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bedrock_client import BedrockClient
from config import validate_config

def test_configuration():
    """Test configuration and environment variables"""
    print("🔧 Testing Configuration...")
    
    if validate_config():
        print("✅ Configuration valid")
        return True
    else:
        print("❌ Configuration invalid - check environment variables")
        return False

def test_bedrock_connection():
    """Test basic Bedrock connection"""
    print("\n🔗 Testing Bedrock Connection...")
    
    try:
        client = BedrockClient()
        print("✅ Bedrock client initialized")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize Bedrock client: {str(e)}")
        return None

def test_embedding_generation(client: BedrockClient):
    """Test embedding generation"""
    print("\n🧠 Testing Embedding Generation...")
    
    test_texts = [
        "A young professional interested in electronics and technology",
        "iPhone 15 Pro Max with advanced camera system and titanium design",
        "Comfortable running shoes for daily exercise and fitness"
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            embedding = client.generate_embedding(text)
            if embedding and len(embedding) > 0:
                print(f"✅ Test {i}: Generated embedding with {len(embedding)} dimensions")
            else:
                print(f"❌ Test {i}: Failed to generate embedding")
                return False
        except Exception as e:
            print(f"❌ Test {i}: Error - {str(e)}")
            return False
    
    return True

def test_customer_embedding(client: BedrockClient):
    """Test customer profile embedding"""
    print("\n👤 Testing Customer Profile Embedding...")
    
    customer_profile = {
        'name': 'Test Customer',
        'age': 30,
        'gender': 'M',
        'location': 'Dubai',
        'preferences': ['Electronics', 'Clothing'],
        'price_sensitivity': 0.5,
        'lifestyle': 'Young Professional',
        'occupation': 'Software Engineer'
    }
    
    try:
        embedding = client.generate_customer_embedding(customer_profile)
        if embedding and len(embedding) > 0:
            print(f"✅ Customer embedding generated with {len(embedding)} dimensions")
            return True
        else:
            print("❌ Failed to generate customer embedding")
            return False
    except Exception as e:
        print(f"❌ Error generating customer embedding: {str(e)}")
        return False

def test_product_embedding(client: BedrockClient):
    """Test product embedding"""
    print("\n🛍️ Testing Product Embedding...")
    
    product_data = {
        'product_name': 'iPhone 15 Pro Max',
        'category': 'Electronics',
        'subcategory': 'Mobile',
        'price': 1199.99,
        'brand': 'Apple',
        'description': 'Latest iPhone with titanium design and advanced camera system',
        'features': ['A17 Pro chip', '48MP camera', 'Titanium build', '5G connectivity']
    }
    
    try:
        embedding = client.generate_product_embedding(product_data)
        if embedding and len(embedding) > 0:
            print(f"✅ Product embedding generated with {len(embedding)} dimensions")
            return True
        else:
            print("❌ Failed to generate product embedding")
            return False
    except Exception as e:
        print(f"❌ Error generating product embedding: {str(e)}")
        return False

def test_explanation_generation(client: BedrockClient):
    """Test explanation generation with Claude"""
    print("\n💬 Testing Explanation Generation...")
    
    customer_profile = {
        'name': 'Ahmed Al Mansouri',
        'age': 32,
        'gender': 'M',
        'location': 'Dubai',
        'preferences': ['Electronics', 'Home & Garden'],
        'lifestyle': 'Tech Executive'
    }
    
    recommendations = [
        {
            'product_name': 'iPhone 15 Pro Max',
            'similarity_score': 0.95,
            'category': 'Electronics'
        },
        {
            'product_name': 'MacBook Pro 14-inch',
            'similarity_score': 0.89,
            'category': 'Electronics'
        }
    ]
    
    try:
        explanation = client.generate_explanation(customer_profile, recommendations)
        if explanation and len(explanation.strip()) > 0:
            print("✅ Explanation generated successfully")
            print(f"📝 Sample explanation: {explanation[:100]}...")
            return True
        else:
            print("❌ Failed to generate explanation")
            return False
    except Exception as e:
        print(f"❌ Error generating explanation: {str(e)}")
        return False

def test_similarity_calculation():
    """Test cosine similarity calculation"""
    print("\n📐 Testing Similarity Calculation...")
    
    from bedrock_client import cosine_similarity
    
    # Test vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]  # Identical
    vec3 = [0.0, 1.0, 0.0]  # Orthogonal
    vec4 = [0.5, 0.5, 0.0]  # Similar
    
    try:
        # Test identical vectors
        sim1 = cosine_similarity(vec1, vec2)
        if abs(sim1 - 1.0) < 0.001:
            print("✅ Identical vectors similarity: 1.0")
        else:
            print(f"❌ Identical vectors similarity: {sim1} (expected 1.0)")
            return False
        
        # Test orthogonal vectors
        sim2 = cosine_similarity(vec1, vec3)
        if abs(sim2 - 0.0) < 0.001:
            print("✅ Orthogonal vectors similarity: 0.0")
        else:
            print(f"❌ Orthogonal vectors similarity: {sim2} (expected 0.0)")
            return False
        
        # Test similar vectors
        sim3 = cosine_similarity(vec1, vec4)
        expected = 0.707  # cos(45°)
        if abs(sim3 - expected) < 0.01:
            print(f"✅ Similar vectors similarity: {sim3:.3f}")
        else:
            print(f"❌ Similar vectors similarity: {sim3} (expected ~{expected})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in similarity calculation: {str(e)}")
        return False

def test_error_handling(client: BedrockClient):
    """Test error handling scenarios"""
    print("\n🛡️ Testing Error Handling...")
    
    # Test with empty text
    try:
        embedding = client.generate_embedding("")
        if embedding is None:
            print("✅ Empty text handled gracefully")
        else:
            print("⚠️ Empty text returned embedding (unexpected)")
    except Exception as e:
        print(f"✅ Empty text raised exception (handled): {str(e)[:50]}...")
    
    # Test with very long text
    try:
        long_text = "This is a test. " * 1000  # Very long text
        embedding = client.generate_embedding(long_text)
        if embedding:
            print("✅ Long text handled successfully")
        else:
            print("⚠️ Long text failed (may be expected)")
    except Exception as e:
        print(f"✅ Long text raised exception (handled): {str(e)[:50]}...")
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Bedrock Test Suite")
    print("=" * 50)
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please check your AWS credentials.")
        return False
    
    # Test Bedrock connection
    client = test_bedrock_connection()
    if not client:
        print("\n❌ Bedrock connection test failed. Cannot proceed with other tests.")
        return False
    
    # Test basic functionality
    tests = [
        ("Embedding Generation", lambda: test_embedding_generation(client)),
        ("Customer Embedding", lambda: test_customer_embedding(client)),
        ("Product Embedding", lambda: test_product_embedding(client)),
        ("Explanation Generation", lambda: test_explanation_generation(client)),
        ("Similarity Calculation", test_similarity_calculation),
        ("Error Handling", lambda: test_error_handling(client))
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your Bedrock setup is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Bedrock connectivity and functionality')
    parser.add_argument('--quick', action='store_true', help='Run quick connection test only')
    parser.add_argument('--embedding-only', action='store_true', help='Test embedding generation only')
    parser.add_argument('--explanation-only', action='store_true', help='Test explanation generation only')
    
    args = parser.parse_args()
    
    if args.quick:
        # Quick test
        print("🚀 Running Quick Connection Test")
        if test_configuration() and test_bedrock_connection():
            print("✅ Quick test passed!")
        else:
            print("❌ Quick test failed!")
    
    elif args.embedding_only:
        # Embedding test only
        print("🚀 Testing Embedding Generation Only")
        client = test_bedrock_connection()
        if client and test_embedding_generation(client):
            print("✅ Embedding test passed!")
        else:
            print("❌ Embedding test failed!")
    
    elif args.explanation_only:
        # Explanation test only
        print("🚀 Testing Explanation Generation Only")
        client = test_bedrock_connection()
        if client and test_explanation_generation(client):
            print("✅ Explanation test passed!")
        else:
            print("❌ Explanation test failed!")
    
    else:
        # Comprehensive test
        success = run_comprehensive_test()
        exit(0 if success else 1)

if __name__ == "__main__":
    main()