"""
RAG (Retrieval Augmented Generation) Service for LabEase
Retrieves relevant information from the database to provide accurate answers
"""
from .models import Test, Lab, LabTestDetail
from django.db.models import Q


class RAGService:
    """Retrieval service for finding relevant tests and labs"""
    
    @staticmethod
    def retrieve_tests(query, limit=10):
        """Retrieve relevant tests based on query"""
        query_lower = query.lower()
        
        # Search in test names and descriptions
        tests = Test.objects.filter(
            Q(name__icontains=query_lower) |
            Q(description__icontains=query_lower)
        ).distinct()[:limit]
        
        # If no direct match, try fuzzy matching with keywords
        if not tests.exists():
            keywords = query_lower.split()
            for keyword in keywords:
                if len(keyword) > 3:  # Only search for meaningful keywords
                    tests = Test.objects.filter(
                        Q(name__icontains=keyword) |
                        Q(description__icontains=keyword)
                    ).distinct()[:limit]
                    if tests.exists():
                        break
        
        return tests
    
    @staticmethod
    def retrieve_tests_by_price(query):
        """Retrieve tests with price information - enhanced matching"""
        query_lower = query.lower()
        
        # Extract price-related keywords to remove
        price_keywords = ['price', 'cost', 'expensive', 'cheap', 'affordable', 'how', 'much', 'what', 'is', 'the', 'of', 'a', 'an', 'does', 'do']
        test_keywords = []
        
        # Extract meaningful test name keywords
        for word in query_lower.split():
            if word not in price_keywords and len(word) > 2:
                test_keywords.append(word)
        
        # Handle specific test patterns with better matching
        if 'blood' in query_lower:
            # Prioritize CBC and blood-related tests
            tests = Test.objects.filter(price__isnull=False).filter(
                Q(name__icontains='cbc') |
                Q(name__icontains='complete blood') |
                Q(name__icontains='blood count') |
                Q(name__icontains='blood') |
                Q(description__icontains='blood')
            ).distinct()
            if tests.exists():
                return tests[:10]
        
        # Handle other common test patterns
        test_patterns = {
            'glucose': ['glucose', 'blood sugar', 'sugar'],
            'diabetes': ['glucose', 'hba1c', 'hemoglobin a1c', 'diabetes'],
            'thyroid': ['thyroid', 'tsh', 't3', 't4'],
            'liver': ['liver', 'lft', 'alt', 'ast', 'bilirubin'],
            'kidney': ['kidney', 'creatinine', 'bun', 'renal'],
            'lipid': ['lipid', 'cholesterol'],
            'cardiac': ['cardiac', 'troponin', 'ecg', 'ekg', 'heart'],
        }
        
        for pattern, keywords in test_patterns.items():
            if pattern in query_lower:
                tests = Test.objects.filter(price__isnull=False)
                q_objects = Q()
                for keyword in keywords:
                    q_objects |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
                tests = tests.filter(q_objects).distinct()
                if tests.exists():
                    return tests[:10]
        
        # Search for tests using extracted keywords
        if test_keywords:
            tests = Test.objects.filter(price__isnull=False)
            q_objects = Q()
            for keyword in test_keywords:
                q_objects |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
            tests = tests.filter(q_objects).distinct()
            if tests.exists():
                return tests[:10]
        
        # Return popular tests with prices as fallback
        return Test.objects.filter(price__isnull=False).order_by('price')[:10]
    
    @staticmethod
    def retrieve_labs(query, limit=10):
        """Retrieve relevant labs based on query"""
        query_lower = query.lower()
        
        # Search by location
        labs = Lab.objects.filter(
            Q(name__icontains=query_lower) |
            Q(city__icontains=query_lower) |
            Q(state__icontains=query_lower) |
            Q(address__icontains=query_lower)
        ).distinct()[:limit]
        
        return labs
    
    @staticmethod
    def retrieve_tests_for_symptoms(symptoms_text):
        """Retrieve tests relevant to symptoms"""
        symptoms_lower = symptoms_text.lower()
        
        # Symptom to test keyword mapping
        symptom_mappings = {
            'diabetes': ['glucose', 'hba1c', 'hemoglobin a1c', 'blood sugar', 'diabetes'],
            'blood sugar': ['glucose', 'hba1c', 'diabetes'],
            'glucose': ['glucose', 'hba1c', 'diabetes'],
            'thirsty': ['glucose', 'diabetes'],
            'frequent urination': ['glucose', 'diabetes', 'urinalysis'],
            'heart': ['cardiac', 'troponin', 'ekg', 'ecg', 'cholesterol', 'lipid'],
            'chest pain': ['cardiac', 'troponin', 'ekg', 'ecg'],
            'cardiac': ['cardiac', 'troponin', 'ekg', 'ecg'],
            'thyroid': ['thyroid', 'tsh', 't3', 't4'],
            'tired': ['thyroid', 'tsh', 'cbc', 'vitamin d', 'vitamin b12'],
            'fatigue': ['thyroid', 'tsh', 'cbc', 'vitamin d', 'vitamin b12'],
            'weight gain': ['thyroid', 'tsh'],
            'weight loss': ['thyroid', 'tsh'],
            'liver': ['liver', 'alt', 'ast', 'bilirubin', 'lft'],
            'jaundice': ['liver', 'bilirubin', 'alt', 'ast'],
            'kidney': ['kidney', 'creatinine', 'bun', 'urinalysis'],
            'urine': ['urinalysis', 'kidney', 'creatinine'],
            'cholesterol': ['cholesterol', 'lipid'],
            'anemia': ['cbc', 'complete blood', 'hemoglobin'],
            'blood count': ['cbc', 'complete blood'],
            'cbc': ['cbc', 'complete blood'],
        }
        
        # Find matching keywords
        matching_keywords = []
        for symptom, keywords in symptom_mappings.items():
            if symptom in symptoms_lower:
                matching_keywords.extend(keywords)
        
        # If no direct match, search in symptoms text
        if not matching_keywords:
            for keyword in symptoms_lower.split():
                if len(keyword) > 3:
                    matching_keywords.append(keyword)
        
        # Retrieve tests
        tests = Test.objects.none()
        for keyword in matching_keywords[:5]:  # Limit to avoid too many queries
            keyword_tests = Test.objects.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
            tests = tests | keyword_tests
        
        return tests.distinct()[:10]
    
    @staticmethod
    def format_test_info(test):
        """Format test information for LLM context"""
        labs_offering = Lab.objects.filter(tests=test)[:3]
        info = {
            'name': test.name,
            'description': test.description or 'No description available',
            'price': str(test.price) if test.price else 'Price not available',
            'labs': [lab.name for lab in labs_offering]
        }
        return info
    
    @staticmethod
    def format_lab_info(lab):
        """Format lab information for LLM context"""
        test_count = lab.tests.count()
        info = {
            'name': lab.name,
            'address': lab.address,
            'city': lab.city,
            'state': lab.state,
            'phone': lab.contact_phone,
            'email': lab.contact_email,
            'test_count': test_count
        }
        return info
