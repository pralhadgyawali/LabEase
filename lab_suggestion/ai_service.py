"""
AI Service module for LabEase
Provides AI-powered chatbot and recommendation functionality with RAG
"""
import re
from django.db.models import Q
from .models import Test, Lab, ChatMessage, AIRecommendation
from .rag_service import RAGService

class AIChatbotService:
    """AI Chatbot service for answering questions about labs and tests"""
    
    def __init__(self):
        self.context = self._load_context()
    
    def _load_context(self):
        """Load context about available labs and tests"""
        tests = Test.objects.all()
        labs = Lab.objects.all()
        
        test_info = "\n".join([f"- {test.name}: {test.description or 'No description'}" for test in tests[:20]])
        lab_info = "\n".join([f"- {lab.name} (Location: {lab.city}, {lab.state})" for lab in labs[:20]])
        
        return {
            'tests': test_info,
            'labs': lab_info,
            'total_tests': tests.count(),
            'total_labs': labs.count()
        }
    
    def generate_response(self, user_message, session_id=None):
        """Generate AI response based on user message using RAG"""
        user_message_lower = user_message.lower()
        
        # Greeting patterns
        if any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            response = self._greeting_response()
            suggestions = self._get_default_suggestions()
            return response, suggestions
        
        # Price queries - prioritize this as it's a common question
        if any(word in user_message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'affordable', 'how much']):
            response = self._handle_price_query(user_message)
            suggestions = self._get_price_suggestions(user_message)
            return response, suggestions
        
        # Symptom-based recommendations
        if any(word in user_message_lower for word in ['symptom', 'symptoms', 'feel', 'feeling', 'pain', 'recommend', 'suggest', 'should i take', 'what test']):
            response = self._handle_symptom_query(user_message)
            suggestions = self._get_symptom_suggestions(user_message)
            return response, suggestions
        
        # Search for tests
        if any(word in user_message_lower for word in ['test', 'tests', 'lab test', 'what test', 'which test', 'do you have']):
            response = self._handle_test_query(user_message)
            suggestions = self._get_test_suggestions(user_message)
            return response, suggestions
        
        # Search for labs
        if any(word in user_message_lower for word in ['lab', 'labs', 'laboratory', 'where', 'location', 'find lab', 'near me']):
            response = self._handle_lab_query(user_message)
            suggestions = self._get_lab_suggestions(user_message)
            return response, suggestions
        
        # General help
        if any(word in user_message_lower for word in ['help', 'how', 'what can', 'what do', 'guide']):
            response = self._help_response()
            suggestions = self._get_default_suggestions()
            return response, suggestions
        
        # Default response with RAG
        response = self._default_response_with_rag(user_message)
        suggestions = self._get_default_suggestions()
        return response, suggestions
    
    def _get_default_suggestions(self):
        """Get default suggestions for general queries"""
        return [
            "What tests do you have?",
            "Find labs near me",
            "What is the price of blood test?"
        ]
    
    def _get_price_suggestions(self, user_message):
        """Get contextual suggestions for price queries"""
        user_lower = user_message.lower()
        suggestions = []
        
        # If specific test mentioned, suggest related tests
        if 'blood' in user_lower or 'cbc' in user_lower or 'complete blood' in user_lower:
            suggestions = [
                "What is the price of glucose test?",
                "What is the price of lipid panel?",
                "Show me all test prices"
            ]
        elif 'glucose' in user_lower or 'diabetes' in user_lower or 'sugar' in user_lower:
            suggestions = [
                "What is the price of Hemoglobin A1C?",
                "What is the price of complete blood count?",
                "Find labs offering diabetes tests"
            ]
        elif 'thyroid' in user_lower:
            suggestions = [
                "What is the price of T3 and T4 test?",
                "Find labs offering thyroid tests",
                "What other hormone tests do you have?"
            ]
        elif 'liver' in user_lower:
            suggestions = [
                "What is the price of ALT and AST test?",
                "Find labs offering liver tests",
                "What is liver function test?"
            ]
        elif 'kidney' in user_lower:
            suggestions = [
                "What is the price of kidney function test?",
                "What is the price of creatinine test?",
                "Find labs offering kidney tests"
            ]
        else:
            suggestions = [
                "What is the price of complete blood count?",
                "What is the price of glucose test?",
                "Show me cheapest tests"
            ]
        
        return suggestions[:3]
    
    def _get_symptom_suggestions(self, user_message):
        """Get contextual suggestions for symptom queries"""
        user_lower = user_message.lower()
        suggestions = []
        
        if any(word in user_lower for word in ['diabetes', 'blood sugar', 'glucose', 'thirsty', 'urination']):
            suggestions = [
                "What is the price of glucose test?",
                "Find labs offering diabetes tests",
                "Tell me more about Hemoglobin A1C test"
            ]
        elif any(word in user_lower for word in ['heart', 'chest', 'cardiac']):
            suggestions = [
                "What is the price of cardiac tests?",
                "Find labs offering heart tests",
                "What is ECG test?"
            ]
        elif any(word in user_lower for word in ['thyroid', 'tired', 'fatigue', 'weight']):
            suggestions = [
                "What is the price of thyroid test?",
                "Find labs offering thyroid tests",
                "What is TSH test?"
            ]
        elif any(word in user_lower for word in ['liver', 'jaundice', 'yellow']):
            suggestions = [
                "What is the price of liver function test?",
                "Find labs offering liver tests",
                "What is ALT and AST test?"
            ]
        else:
            suggestions = [
                "What tests do you recommend for my symptoms?",
                "Find labs near me",
                "What is the price of complete blood count?"
            ]
        
        return suggestions[:3]
    
    def _get_test_suggestions(self, user_message):
        """Get contextual suggestions for test queries"""
        user_lower = user_message.lower()
        suggestions = []
        
        # Get some actual test names from database
        tests = Test.objects.all()[:10]
        test_names = [test.name.lower() for test in tests]
        
        if 'blood' in user_lower or 'cbc' in user_lower or 'complete blood' in user_lower:
            suggestions = [
                "What is the price of complete blood count?",
                "Find labs offering blood tests",
                "What other blood tests do you have?"
            ]
        elif 'glucose' in user_lower or 'diabetes' in user_lower or 'sugar' in user_lower:
            suggestions = [
                "What is the price of glucose test?",
                "What is Hemoglobin A1C test?",
                "Find labs offering diabetes tests"
            ]
        elif 'thyroid' in user_lower:
            suggestions = [
                "What is the price of thyroid test?",
                "What is TSH test?",
                "Find labs offering thyroid tests"
            ]
        elif 'liver' in user_lower:
            suggestions = [
                "What is the price of liver function test?",
                "What is ALT and AST test?",
                "Find labs offering liver tests"
            ]
        elif any(test_name in user_lower for test_name in test_names):
            # If specific test mentioned, suggest related
            suggestions = [
                "What is the price of this test?",
                "Find labs offering this test",
                "Tell me more about this test"
            ]
        else:
            suggestions = [
                "What is the price of complete blood count?",
                "What is the price of glucose test?",
                "Find labs near me"
            ]
        
        return suggestions[:3]
    
    def _get_lab_suggestions(self, user_message):
        """Get contextual suggestions for lab queries"""
        user_lower = user_message.lower()
        suggestions = []
        
        if 'kathmandu' in user_lower:
            suggestions = [
                "Find labs in Lalitpur",
                "Find labs in Bhaktapur",
                "What tests are available in Kathmandu?"
            ]
        elif 'lalitpur' in user_lower or 'patan' in user_lower:
            suggestions = [
                "Find labs in Kathmandu",
                "Find labs in Bhaktapur",
                "What tests are available in Lalitpur?"
            ]
        elif 'near me' in user_lower or 'location' in user_lower:
            suggestions = [
                "Find labs in Kathmandu",
                "Find labs in Lalitpur",
                "What tests do you have?"
            ]
        else:
            suggestions = [
                "Find labs in Kathmandu",
                "Find labs in Lalitpur",
                "What tests do these labs offer?"
            ]
        
        return suggestions[:3]
    
    def _greeting_response(self):
        return "Hello! I'm LabEase AI Assistant, your trusted healthcare companion. I'm here to help you find medical laboratories, search for tests, get accurate pricing information, and provide test recommendations based on symptoms. How may I assist you today?"
    
    def _handle_test_query(self, user_message):
        """Handle queries about tests with professional, detailed responses"""
        # Use RAG to retrieve relevant tests
        retrieved_tests = RAGService.retrieve_tests(user_message, limit=10)
        
        if retrieved_tests.exists():
            response = f"I found {retrieved_tests.count()} test(s) matching your query. Here are the details:\n\n"
            
            for test in retrieved_tests[:6]:
                labs_offering = Lab.objects.filter(tests=test).distinct()[:3]
                response += f"**{test.name}**\n"
                
                if test.description:
                    response += f"   *{test.description}*\n"
                
                if test.price:
                    response += f"   **Price:** Rs. {test.price}\n"
                else:
                    response += f"   **Price:** Contact lab for pricing\n"
                
                if labs_offering.exists():
                    response += f"   **Available at:** {', '.join([lab.name for lab in labs_offering])}\n"
                
                response += "\n"
            
            if retrieved_tests.count() > 6:
                response += f"\n*Showing 6 of {retrieved_tests.count()} matching tests. Use our search feature to see all results and find labs near you.*\n\n"
            
            response += "💡 **Next Steps:**\n"
            response += "• Use our search feature to find labs offering these tests\n"
            response += "• Click 'Book Test' to send a booking request to your preferred lab\n"
            response += "• Contact labs directly for appointment scheduling\n"
            
            return response
        else:
            # List all available tests
            all_tests = Test.objects.all()[:10]
            if all_tests.exists():
                response = f"Thank you for your interest! We currently have **{self.context['total_tests']} different medical tests** available through our partner laboratories. Here are some popular options:\n\n"
                
                for test in all_tests:
                    response += f"• **{test.name}**"
                    if test.price:
                        response += f" - Rs. {test.price}"
                    if test.description:
                        response += f"\n  _{test.description}_"
                    response += "\n"
                
                response += "\n💡 **How to find more:**\n"
                response += "• Use our search bar on the homepage to search for specific tests\n"
                response += "• Ask me about specific test names (e.g., 'Tell me about Complete Blood Count')\n"
                response += "• Describe what you're looking for and I'll help you find the right test\n"
            else:
                response = "I'd be happy to help you find medical tests! Here's how you can search:\n\n"
                response += "• **Use our search feature** on the homepage to find specific tests\n"
                response += "• **Ask me directly** about test names (e.g., 'What is Complete Blood Count?')\n"
                response += "• **Describe your needs** and I'll recommend appropriate tests\n\n"
                response += "What type of test are you looking for?"
            
            return response
    
    def _handle_lab_query(self, user_message):
        """Handle queries about labs with detailed, helpful information"""
        user_lower = user_message.lower()
        labs = Lab.objects.all()
        
        # Try to find location in message
        found_labs = []
        location_keywords = ['kathmandu', 'lalitpur', 'bhaktapur', 'patan']
        
        for keyword in location_keywords:
            if keyword in user_lower:
                found_labs = list(labs.filter(city__icontains=keyword))
                break
        
        # If no specific location, check for general location queries
        if not found_labs and any(word in user_lower for word in ['near me', 'close', 'nearby', 'location']):
            found_labs = list(labs[:5])  # Show some labs
        
        if found_labs:
            response = f"I found **{len(found_labs)} laboratory/laboratories** matching your search:\n\n"
            
            for lab in found_labs[:5]:
                response += f"**{lab.name}**\n"
                response += f"   📍 **Location:** {lab.address}, {lab.city}, {lab.state}\n"
                
                if lab.contact_phone:
                    response += f"   📞 **Phone:** {lab.contact_phone}\n"
                if lab.contact_email:
                    response += f"   ✉️ **Email:** {lab.contact_email}\n"
                
                test_count = lab.tests.count()
                response += f"   🧪 **Tests Offered:** {test_count} test{'s' if test_count != 1 else ''}\n"
                response += "\n"
            
            if len(found_labs) > 5:
                response += f"\n*Showing 5 of {len(found_labs)} labs. Use our search feature to see all labs and filter by test type.*\n\n"
            
            response += "💡 **To book a test:**\n"
            response += "• Use our search feature to find specific tests\n"
            response += "• Click 'Book Test' on any test result to send a booking request\n"
            response += "• Contact the lab directly using the provided phone or email\n"
            
            return response
        else:
            response = f"We currently have **{self.context['total_labs']} partner laboratories** in our network, primarily located in:\n\n"
            response += "• **Kathmandu**\n"
            response += "• **Lalitpur**\n"
            response += "• **Bhaktapur**\n\n"
            response += "💡 **How to find labs:**\n"
            response += "• Search for a specific test on our homepage - results will show labs offering that test\n"
            response += "• Ask me about labs in a specific area (e.g., 'Find labs in Kathmandu')\n"
            response += "• Use our search feature to filter by location and test type\n\n"
            response += "What location or test are you looking for?"
            
            return response
    
    def _handle_price_query(self, user_message):
        """Handle price-related queries with precise, professional responses"""
        user_lower = user_message.lower()
        
        # Use RAG to find specific tests mentioned in the query
        retrieved_tests = RAGService.retrieve_tests_by_price(user_message)
        
        # Try to identify specific test mentioned
        specific_test = None
        test_keywords_map = {
            'blood': ['cbc', 'complete blood count', 'blood'],
            'cbc': ['cbc', 'complete blood count'],
            'glucose': ['glucose', 'blood sugar'],
            'diabetes': ['glucose', 'hba1c', 'hemoglobin a1c'],
            'thyroid': ['tsh', 'thyroid', 't3', 't4'],
            'liver': ['liver', 'lft', 'alt', 'ast'],
            'kidney': ['kidney', 'creatinine', 'bun'],
            'lipid': ['lipid', 'cholesterol'],
            'cardiac': ['cardiac', 'troponin', 'ecg', 'ekg'],
        }
        
        # Check for specific test mentions
        for keyword, test_names in test_keywords_map.items():
            if keyword in user_lower:
                for test_name in test_names:
                    test = Test.objects.filter(
                        name__icontains=test_name
                    ).filter(price__isnull=False).first()
                    if test:
                        specific_test = test
                        break
                if specific_test:
                    break
        
        # If specific test found, provide detailed information
        if specific_test:
            labs_offering = Lab.objects.filter(tests=specific_test).distinct()[:3]
            response = f"I have the pricing information for **{specific_test.name}**:\n\n"
            
            if specific_test.description:
                response += f"**Test Description:** {specific_test.description}\n\n"
            
            response += f"**Price:** Rs. {specific_test.price}\n\n"
            
            if labs_offering.exists():
                response += f"**Available at the following labs:**\n"
                for lab in labs_offering:
                    response += f"• {lab.name} - {lab.city}\n"
                    if lab.contact_phone:
                        response += f"  Contact: {lab.contact_phone}\n"
                response += "\n"
            
            response += "💡 **Tip:** Prices may vary slightly between labs. I recommend contacting the lab directly to confirm the exact price and schedule an appointment. You can use the 'Book Test' button on our search results page to send a booking request."
            
            return response
        
        # If multiple tests found, provide comprehensive list
        if retrieved_tests.exists():
            # Check if asking for blood test specifically
            if 'blood' in user_lower and 'test' in user_lower:
                blood_tests = retrieved_tests.filter(
                    Q(name__icontains='blood') | 
                    Q(name__icontains='cbc') |
                    Q(description__icontains='blood')
                )[:5]
                
                if blood_tests.exists():
                    response = "Here are the prices for blood tests available in our system:\n\n"
                    for test in blood_tests:
                        response += f"**{test.name}**\n"
                        if test.description:
                            response += f"   {test.description}\n"
                        response += f"   **Price:** Rs. {test.price}\n\n"
                    
                    response += "💡 **Note:** These are standard prices. Actual prices may vary by lab and location. For the most accurate pricing and to book an appointment, please contact the lab directly or use our search feature to find labs near you."
                    return response
            
            # General price listing
            response = "Here are the current prices for tests in our system:\n\n"
            for test in retrieved_tests[:6]:
                response += f"**{test.name}**\n"
                if test.description:
                    response += f"   {test.description}\n"
                response += f"   **Price:** Rs. {test.price}\n\n"
            
            if retrieved_tests.count() > 6:
                response += f"\n*Showing 6 of {retrieved_tests.count()} available tests. Use our search feature to find more specific tests and their prices.*\n\n"
            
            response += "💡 **Helpful Information:**\n"
            response += "• Prices are approximate and may vary by lab location\n"
            response += "• Contact labs directly for exact pricing and appointment scheduling\n"
            response += "• Use our search feature to find labs offering specific tests in your area\n"
            
            return response
        
        # Fallback: show popular tests with prices
        tests_with_prices = Test.objects.filter(price__isnull=False).order_by('price')[:5]
        if tests_with_prices.exists():
            response = "I'd be happy to help you with test pricing information. Here are some commonly requested tests and their prices:\n\n"
            for test in tests_with_prices:
                response += f"**{test.name}** - Rs. {test.price}\n"
            
            response += "\n💡 **To get specific pricing:**\n"
            response += "• Use our search feature on the homepage to find specific tests\n"
            response += "• Search results will show prices from multiple labs\n"
            response += "• You can contact labs directly through the 'Book Test' feature\n"
            
            return response
        
        # No tests found
        response = "I understand you're looking for test pricing information. To help you better:\n\n"
        response += "1. **Use our search feature** on the homepage to find specific tests\n"
        response += "2. **Search results** will display prices from multiple labs in your area\n"
        response += "3. **Contact labs directly** for exact pricing and to schedule appointments\n\n"
        response += "You can also ask me about specific tests like 'What is the price of Complete Blood Count?' or 'How much does a glucose test cost?'"
        
        return response
    
    def _handle_symptom_query(self, user_message):
        """Handle symptom-based test recommendations with professional medical guidance"""
        # Use RAG to retrieve relevant tests based on symptoms
        retrieved_tests = RAGService.retrieve_tests_for_symptoms(user_message)
        
        if retrieved_tests.exists():
            response = "Based on the symptoms you've described, I can suggest the following tests that may be relevant:\n\n"
            
            for test in retrieved_tests[:5]:
                labs_offering = Lab.objects.filter(tests=test).distinct()[:2]
                response += f"**{test.name}**\n"
                if test.description:
                    response += f"   *{test.description}*\n"
                if test.price:
                    response += f"   **Price:** Rs. {test.price}\n"
                if labs_offering.exists():
                    lab_names = ', '.join([lab.name for lab in labs_offering])
                    response += f"   **Available at:** {lab_names}\n"
                response += "\n"
            
            response += "\n⚠️ **Important Medical Disclaimer:**\n"
            response += "These are general test suggestions based on common symptoms. **I strongly recommend:**\n"
            response += "• Consulting with a qualified healthcare provider for proper diagnosis\n"
            response += "• Discussing your symptoms with a doctor before taking any tests\n"
            response += "• Following professional medical advice for your specific situation\n\n"
            response += "💡 **Next Steps:**\n"
            response += "• Consult with a healthcare provider to determine which tests are appropriate for you\n"
            response += "• Use our search feature to find labs offering these tests\n"
            response += "• Book appointments through our platform or contact labs directly\n"
            
            return response
        else:
            # Try to provide general recommendations
            common_tests = Test.objects.all()[:5]
            if common_tests.exists():
                response = "Thank you for sharing your symptoms. While I can provide general guidance, here are some commonly recommended screening tests:\n\n"
                
                for test in common_tests:
                    response += f"• **{test.name}**"
                    if test.price:
                        response += f" - Rs. {test.price}"
                    if test.description:
                        response += f"\n  _{test.description}_"
                    response += "\n"
                
                response += "\n⚠️ **Medical Advice:**\n"
                response += "Please consult with a healthcare provider to determine which tests are most appropriate for your specific symptoms and medical history. A doctor can provide personalized recommendations based on a thorough evaluation.\n\n"
                response += "💡 **How I can help:**\n"
                response += "• Provide information about specific tests\n"
                response += "• Help you find labs offering these tests\n"
                response += "• Share pricing information\n\n"
                response += "Would you like more details about any specific test, or would you prefer to search for tests by name?"
            else:
                response = "I understand you're seeking test recommendations based on your symptoms. Here's how I can help:\n\n"
                response += "**For accurate recommendations:**\n"
                response += "• Consult with a qualified healthcare provider who can evaluate your symptoms properly\n"
                response += "• Describe your symptoms in more detail, and I can suggest relevant tests\n"
                response += "• Use our search feature to explore available tests\n\n"
                response += "**I can assist you with:**\n"
                response += "• Finding information about specific tests\n"
                response += "• Locating labs in your area\n"
                response += "• Providing pricing information\n\n"
                response += "What specific symptoms or tests would you like to know more about?"
            
            return response
    
    def _help_response(self):
        return """I'm here to assist you with all your medical testing needs. Here's what I can help you with:

**🔍 Finding Tests**
Ask me about specific tests by name, or describe what you're looking for. I'll provide detailed information including descriptions and pricing.

**📍 Finding Labs**
I can help you locate laboratories in Kathmandu, Lalitpur, and Bhaktapur. Just ask about labs in a specific area or search for tests to see which labs offer them.

**💰 Price Information**
Get accurate pricing for any test in our system. Ask me about specific tests like "What is the price of Complete Blood Count?" and I'll provide detailed pricing information.

**💡 Test Recommendations**
Describe your symptoms and I'll suggest relevant tests. However, please remember to consult with a healthcare provider for proper diagnosis.

**📋 General Information**
Ask me anything about our services, how to book tests, or how to use our platform.

**Example Questions:**
• "What tests do you have?"
• "Find labs in Kathmandu"
• "What is the price of blood test?"
• "I have diabetes symptoms, what tests should I take?"
• "Tell me about Complete Blood Count test"

How may I assist you today?"""
    
    def _get_contextual_suggestions(self, user_message, response_text):
        """Generate contextual suggestions based on user message and response"""
        user_lower = user_message.lower()
        response_lower = response_text.lower()
        
        # Analyze context from both user message and AI response
        suggestions = []
        
        # If response mentions specific tests
        if 'test' in response_lower and any(word in response_lower for word in ['found', 'available', 'following']):
            suggestions.append("What is the price of this test?")
            suggestions.append("Find labs offering this test")
            suggestions.append("Tell me more about this test")
        
        # If response mentions labs
        elif 'lab' in response_lower:
            suggestions.append("What tests does this lab offer?")
            suggestions.append("What is the contact information?")
            suggestions.append("Find more labs in this area")
        
        # If response mentions prices
        elif 'price' in response_lower or 'rs.' in response_lower:
            suggestions.append("Find labs offering this test")
            suggestions.append("What is the price of other tests?")
            suggestions.append("Show me cheapest tests")
        
        # If response mentions symptoms/recommendations
        elif any(word in response_lower for word in ['symptom', 'recommend', 'suggest']):
            suggestions.append("What is the price of these tests?")
            suggestions.append("Find labs offering these tests")
            suggestions.append("Tell me more about these tests")
        
        # Default suggestions if no specific context
        if len(suggestions) < 3:
            default = self._get_default_suggestions()
            suggestions.extend(default)
        
        return suggestions[:3]
    
    def _default_response_with_rag(self, user_message):
        """Default response with RAG fallback - professional and helpful"""
        # Try to find any relevant information
        tests = RAGService.retrieve_tests(user_message, limit=3)
        labs = RAGService.retrieve_labs(user_message, limit=3)
        
        if tests.exists():
            response = "I found some tests that might be relevant to your query:\n\n"
            for test in tests:
                response += f"**{test.name}**"
                if test.price:
                    response += f" - Rs. {test.price}"
                if test.description:
                    response += f"\n   _{test.description}_"
                response += "\n\n"
            
            response += "💡 **Would you like to:**\n"
            response += "• Get more details about any of these tests?\n"
            response += "• Find labs offering these tests?\n"
            response += "• Get pricing information?\n"
            
            return response
        elif labs.exists():
            response = "I found some laboratories that match your query:\n\n"
            for lab in labs:
                response += f"**{lab.name}**\n"
                response += f"   📍 {lab.city}, {lab.state}\n"
                response += f"   🧪 {lab.tests.count()} test{'s' if lab.tests.count() != 1 else ''} available\n\n"
            
            response += "💡 **Would you like to:**\n"
            response += "• Get contact information for these labs?\n"
            response += "• See what tests they offer?\n"
            response += "• Find labs in a specific location?\n"
            
            return response
        else:
            response = "I'm here to help you with all your medical testing needs. I can assist you with:\n\n"
            response += "**🔍 Finding Information:**\n"
            response += "• Search for specific tests by name\n"
            response += "• Find laboratories in your area\n"
            response += "• Get pricing information\n\n"
            response += "**💡 How to get the best results:**\n"
            response += "• Be specific about what you're looking for (e.g., 'Complete Blood Count test')\n"
            response += "• Mention locations if looking for labs (e.g., 'labs in Kathmandu')\n"
            response += "• Ask about prices for specific tests\n\n"
            response += "**Example questions:**\n"
            response += "• \"What is the price of blood test?\"\n"
            response += "• \"Find labs in Kathmandu\"\n"
            response += "• \"Tell me about Complete Blood Count\"\n\n"
            response += "What would you like to know more about?"
            
            return response


class AIRecommendationService:
    """AI service for generating test recommendations based on symptoms"""
    
    @staticmethod
    def recommend_tests(symptoms_text, user=None):
        """Generate test recommendations based on symptoms"""
        symptoms_lower = symptoms_text.lower()
        
        # Symptom to test mapping
        recommendations = []
        
        # Diabetes related
        if any(word in symptoms_lower for word in ['diabetes', 'blood sugar', 'glucose', 'thirsty', 'frequent urination']):
            tests = Test.objects.filter(name__icontains='glucose') | Test.objects.filter(name__icontains='diabetes') | Test.objects.filter(name__icontains='hba1c')
            recommendations.extend(list(tests))
        
        # Heart related
        if any(word in symptoms_lower for word in ['chest pain', 'heart', 'cardiac', 'shortness of breath']):
            tests = Test.objects.filter(name__icontains='cardiac') | Test.objects.filter(name__icontains='troponin') | Test.objects.filter(name__icontains='ekg')
            recommendations.extend(list(tests))
        
        # Thyroid related
        if any(word in symptoms_lower for word in ['thyroid', 'tired', 'fatigue', 'weight gain', 'weight loss']):
            tests = Test.objects.filter(name__icontains='thyroid') | Test.objects.filter(name__icontains='tsh') | Test.objects.filter(name__icontains='t3') | Test.objects.filter(name__icontains='t4')
            recommendations.extend(list(tests))
        
        # Liver related
        if any(word in symptoms_lower for word in ['liver', 'jaundice', 'yellow', 'abdominal pain']):
            tests = Test.objects.filter(name__icontains='liver') | Test.objects.filter(name__icontains='alt') | Test.objects.filter(name__icontains='ast') | Test.objects.filter(name__icontains='bilirubin')
            recommendations.extend(list(tests))
        
        # Kidney related
        if any(word in symptoms_lower for word in ['kidney', 'urine', 'kidney pain', 'back pain']):
            tests = Test.objects.filter(name__icontains='kidney') | Test.objects.filter(name__icontains='creatinine') | Test.objects.filter(name__icontains='bun')
            recommendations.extend(list(tests))
        
        # Cholesterol
        if any(word in symptoms_lower for word in ['cholesterol', 'heart disease', 'high blood pressure']):
            tests = Test.objects.filter(name__icontains='cholesterol') | Test.objects.filter(name__icontains='lipid')
            recommendations.extend(list(tests))
        
        # Complete Blood Count
        if any(word in symptoms_lower for word in ['anemia', 'weakness', 'pale', 'blood count']):
            tests = Test.objects.filter(name__icontains='cbc') | Test.objects.filter(name__icontains='complete blood') | Test.objects.filter(name__icontains='hemoglobin')
            recommendations.extend(list(tests))
        
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for test in recommendations:
            if test.id not in seen:
                seen.add(test.id)
                unique_recommendations.append(test)
        
        # If no specific matches, return common tests
        if not unique_recommendations:
            common_tests = Test.objects.all()[:5]
            if common_tests.exists():
                unique_recommendations = list(common_tests)
        
        # Save recommendation only if we have tests
        if unique_recommendations:
            recommendation = AIRecommendation.objects.create(
                symptoms=symptoms_text,
                user=user
            )
            recommendation.recommended_tests.set(unique_recommendations[:10])
            return recommendation
        
        return None
