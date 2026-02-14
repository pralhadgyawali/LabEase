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
        
        # Booking request patterns - prioritize this
        if any(word in user_message_lower for word in ['book', 'booking', 'want to book', 'can i book', 'i need to book', 'book test', 'book a test', 'schedule', 'appointment']):
            response = self._handle_booking_request(user_message)
            suggestions = self._get_booking_suggestions()
            return response, suggestions
        
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
        """Get contextual suggestions for price queries using actual tests"""
        user_lower = user_message.lower()
        suggestions = []
        all_tests = Test.objects.all()
        
        # If specific test mentioned, suggest related tests
        if 'blood' in user_lower or 'cbc' in user_lower or 'complete blood' in user_lower:
            for test in all_tests:
                if 'blood' in test.name.lower() or 'cbc' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
            if len(suggestions) < 3:
                suggestions.append("Show me all blood tests")
        
        elif 'glucose' in user_lower or 'diabetes' in user_lower or 'sugar' in user_lower:
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['glucose', 'diabetes', 'a1c']):
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'thyroid' in user_lower:
            for test in all_tests:
                if 'thyroid' in test.name.lower() or 'tsh' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'liver' in user_lower:
            for test in all_tests:
                if 'liver' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'kidney' in user_lower:
            for test in all_tests:
                if 'kidney' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        else:
            # Show actual available tests
            for test in all_tests[:3]:
                suggestions.append(f"What is the price of {test.name}?")
            if not suggestions:
                suggestions.append("What tests are available?")
        
        return suggestions[:3]
    
    def _get_symptom_suggestions(self, user_message):
        """Get contextual suggestions for symptom queries using actual tests"""
        user_lower = user_message.lower()
        suggestions = []
        
        # Get actual tests from database with keywords
        all_tests = Test.objects.all()
        
        if any(word in user_lower for word in ['diabetes', 'blood sugar', 'glucose', 'thirsty', 'urination']):
            # Find diabetes-related tests
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['glucose', 'diabetes', 'a1c', 'hemoglobin']):
                    suggestions.append(f"What is the price of {test.name}?")
                    break
            if not suggestions:
                suggestions.append("What tests do you have for diabetes?")
        
        elif any(word in user_lower for word in ['heart', 'chest', 'cardiac']):
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['cardiac', 'heart', 'ecg', 'troponin']):
                    suggestions.append(f"What is the price of {test.name}?")
                    break
            if not suggestions:
                suggestions.append("What heart tests do you offer?")
        
        elif any(word in user_lower for word in ['thyroid', 'tired', 'fatigue', 'weight']):
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['thyroid', 'tsh', 't3', 't4']):
                    suggestions.append(f"What is the price of {test.name}?")
                    break
            if not suggestions:
                suggestions.append("What thyroid tests do you have?")
        
        elif any(word in user_lower for word in ['liver', 'jaundice', 'yellow']):
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['liver', 'alt', 'ast', 'function']):
                    suggestions.append(f"What is the price of {test.name}?")
                    break
            if not suggestions:
                suggestions.append("What liver function tests do you have?")
        
        else:
            # General recommendation
            if all_tests.exists():
                first_test = all_tests.first()
                suggestions.append(f"What tests do you have?")
                suggestions.append(f"What is the price of {first_test.name}?")
                suggestions.append("Book a test")
        
        return suggestions[:3]
    
    def _get_test_suggestions(self, user_message):
        """Get contextual suggestions for test queries using actual tests"""
        user_lower = user_message.lower()
        suggestions = []
        all_tests = Test.objects.all()
        
        # Get tests based on user message
        if 'blood' in user_lower or 'cbc' in user_lower:
            for test in all_tests:
                if 'blood' in test.name.lower() or 'cbc' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
                    suggestions.append(f"Find labs offering {test.name}")
            if not suggestions:
                suggestions.append("What blood tests do you have?")
        
        elif 'glucose' in user_lower or 'diabetes' in user_lower:
            for test in all_tests:
                if any(kw in test.name.lower() for kw in ['glucose', 'diabetes', 'a1c']):
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'thyroid' in user_lower:
            for test in all_tests:
                if 'thyroid' in test.name.lower() or 'tsh' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'liver' in user_lower:
            for test in all_tests:
                if 'liver' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        elif 'kidney' in user_lower:
            for test in all_tests:
                if 'kidney' in test.name.lower():
                    suggestions.append(f"What is the price of {test.name}?")
        
        else:
            # Show available tests
            for test in all_tests[:3]:
                suggestions.append(f"What is the price of {test.name}?")
            if not suggestions:
                suggestions.append("What tests are available?")
        
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
    
    def _handle_booking_request(self, user_message):
        """Handle test booking requests - extract test name if present"""
        # Check if a test name is already mentioned in the message
        test_name = None
        all_tests = Test.objects.all().values_list('name', flat=True)
        
        # Look for test names in the message
        for test in all_tests:
            if test.lower() in user_message.lower():
                test_name = test
                break
        
        # If a specific test was mentioned, ask for just the user details
        if test_name:
            response = f"✅ **Test Selected: {test_name}**\n\n"
            response += f"Perfect! I'll book **{test_name}** for you.\n\n"
            response += f"Just provide your details:\n\n"
            response += f"**Please include:**\n"
            response += f"• Your full name\n"
            response += f"• Your email address\n"
            response += f"• Phone number (optional)\n"
            response += f"• Preferred date/time (optional)\n\n"
            response += f"**Example:**\n"
            response += f"*My name is John Smith, john@gmail.com, 9876543210, tomorrow morning*\n\n"
            response += f"Once you provide your details, I'll book {test_name} instantly! 🎯"
            return response
        
        # Otherwise, show generic booking flow
        response = "🏥 **Smart Test Booking**\n\n"
        response += "Great! I'll help you book a test in seconds. Let me understand your needs:\n\n"
        response += "**Step 1: Your Health**\n"
        response += "• What symptoms or concerns do you have?\n"
        response += "  (e.g., tired & weak, chest pain, weight gain, fever)\n\n"
        response += "**Step 2: Your Information**\n"
        response += "• Your full name\n"
        response += "• Your email\n"
        response += "• Your phone number (optional)\n\n"
        response += "**Step 3: Preferences** (optional)\n"
        response += "• Preferred date/time for test\n"
        response += "• Any special notes or allergies\n\n"
        response += "**Example Message:**\n"
        response += "*I'm feeling tired and weak with headaches. My name is John Smith, john@gmail.com, 9876543210, tomorrow morning would work best.*\n\n"
        response += "Based on your details, I'll:\n"
        response += "✓ Recommend the best tests\n"
        response += "✓ Find the nearest labs\n"
        response += "✓ Show prices\n"
        response += "✓ Book your test instantly!\n\n"
        response += "Ready? Just share your health concern! 👨‍⚕️"
        
        return response
    
    def _get_booking_suggestions(self):
        """Get suggestions for booking flow"""
        return [
            "Available blood tests",
            "Cheapest tests available",
            "Complete booking process"
        ]
    
    def _get_default_suggestions(self):
        """Get default suggestions based on actual available tests"""
        # Get random actual tests from database
        tests = Test.objects.all()[:3]
        if tests:
            test_suggestion = f"What is the price of {tests[0].name}?"
        else:
            test_suggestion = "What tests do you have?"
        
        return [
            "Book a test",
            test_suggestion,
            "Find labs near me"
        ]
    
    def _greeting_response(self):
        return """👋 **Welcome to LabEase!**

I'm your intelligent healthcare assistant. Here's how I can help you:

🔍 **Search Tests** - Ask me about any medical test
💰 **Check Prices** - Find affordable tests near you
📍 **Find Labs** - Locate labs in your area
🏥 **Get Recommendations** - Describe your symptoms and I'll suggest tests
📋 **Book Tests** - I can help you book a test instantly through chat
ℹ️ **Learn More** - Get information about any test or health concern

**What would you like to do today?** Just type your question or choose from suggestions below! 😊"""
    
    def _handle_test_query(self, user_message):
        """Handle queries about tests with professional, detailed responses"""
        # Use RAG to retrieve relevant tests
        retrieved_tests = RAGService.retrieve_tests(user_message, limit=10)
        
        if retrieved_tests.exists():
            response = f"I found {retrieved_tests.count()} test(s) matching your query. Here are the details:\n\n"
            
            for test in retrieved_tests[:6]:
                labs_offering = Lab.objects.filter(tests=test).distinct()[:3]
                response += f"**🧬 {test.name}**\n"
                
                if test.description:
                    response += f"   _{test.description}_\n"
                
                if test.price:
                    response += f"   💰 **Price:** Rs. {test.price}\n"
                else:
                    response += f"   💰 **Price:** Contact lab for rates\n"
                
                if labs_offering.exists():
                    response += f"   🏥 **Available at:** {', '.join([lab.name for lab in labs_offering])}\n"
                else:
                    response += f"   🏥 **Available at:** Contact us for labs\n"
                
                response += "\n"
            
            if retrieved_tests.count() > 6:
                response += f"\n📌 *Showing 6 of {retrieved_tests.count()} results. Search for more!*\n\n"
            
            response += "**What's Next?**\n"
            response += "✓ Interested? Say 'Book {test name}'\n"
            response += "✓ Want more info? Ask about the test\n"
            response += "✓ Need another test? Keep searching!\n"
            
            return response
        else:
            # List all available tests
            all_tests = Test.objects.filter(
                name__in=[
                    'a', 'u', 'z', 'x', 'acer', 'xray', 'ICU', 'BED', 'SSCU',
                    'AMBULANCE CHARG', 'VENTILATOR CHARGE', 'CABIN BED'
                ]
            ).values_list('id', flat=True)  # Exclude list
            
            valid_tests = Test.objects.exclude(
                id__in=all_tests
            ).order_by('-price')[:15]
            
            if valid_tests.exists():
                response = f"📋 **Medical Tests Available**\n\n"
                response += f"We have **{Test.objects.exclude(id__in=all_tests).count()} quality medical tests** available.\n\n"
                response += f"**Popular Tests:**\n\n"
                
                for test in valid_tests[:10]:
                    response += f"🧬 **{test.name}**"
                    if test.price:
                        response += f" - **Rs. {test.price}**"
                    response += "\n"
                
                response += "\n**Quick Links:**\n"
                response += "• Use search to find specific tests\n"
                response += "• Ask about test categories (blood, cardiac, hormones)\n"
                response += "• Book any test - just ask!\n"
                response += "• Need recommendations? Describe your symptoms\n"
            else:
                response = "📋 We offer a variety of medical tests!\n\n"
                response += "• **Use our search** to find specific tests\n"
                response += "• **Describe your symptoms** and I'll recommend tests\n"
                response += "• **Ask about prices** for any test\n"
                response += "• **Book instantly** through chat!\n\n"
                response += "What can I help you find?"
            
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
            response = f"💰 **Pricing for {specific_test.name}**\n\n"
            
            if specific_test.description:
                response += f"**About:** {specific_test.description}\n\n"
            
            response += f"**💵 Price:** Rs. {specific_test.price}\n\n"
            
            if labs_offering.exists():
                response += f"**🏥 Available at:**\n"
                for lab in labs_offering:
                    response += f"• **{lab.name}** - {lab.city}\n"
                    if lab.contact_phone:
                        response += f"  📞 {lab.contact_phone}\n"
                response += "\n"
            
            response += "**What Next?**\n"
            response += "✓ Book now? Say 'Book {test name}'\n"
            response += "✓ More details? Ask about the test\n"
            response += "✓ Find other tests? Keep searching!"
            
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
                    response = "🩸 **Blood Test Pricing**\n\n"
                    response += "Available blood tests in your area:\n\n"
                    for test in blood_tests:
                        response += f"**{test.name}**\n"
                        if test.description:
                            response += f"   _{test.description}_\n"
                        response += f"   **💵 Rs. {test.price}**\n\n"
                    
                    response += "**ℹ️ Note:** Prices shown are reference rates and may vary by lab.\n\n"
                    response += "**Want to book?** Say 'Book [test name]' 📋"
                    return response
            
            # General price listing
            response = "💰 **Test Pricing Guide**\n\n"
            response += "Popular tests with current pricing:\n\n"
            for test in retrieved_tests[:6]:
                response += f"**🧬 {test.name}**\n"
                if test.description:
                    response += f"   _{test.description}_\n"
                response += f"   **💵 Rs. {test.price}**\n\n"
            
            if retrieved_tests.count() > 6:
                response += f"*Showing 6 of {retrieved_tests.count()} tests. Search for more!*\n\n"
            
            response += "**Important Info:**\n"
            response += "• Prices are approximate reference rates\n"
            response += "• Actual price may vary by lab & location\n"
            response += "• Contact lab directly for exact pricing\n\n"
            response += "**Next Step?** Say 'Book [test name]' to get started! 📋"
            
            return response
        
        # Fallback: show popular tests with prices
        tests_with_prices = Test.objects.filter(price__isnull=False).order_by('price')[:5]
        if tests_with_prices.exists():
            response = "💰 **Test Pricing Info**\n\n"
            response += "Here are some commonly requested tests:\n\n"
            for test in tests_with_prices:
                response += f"🧬 **{test.name}** - Rs. {test.price}\n"
            
            response += "\n**How to Get Pricing for Specific Tests:**\n"
            response += "1. Tell me the test name\n"
            response += "2. Use the search bar on our homepage\n"
            response += "3. Say 'Book test' and I'll guide you\n\n"
            response += "**Example:** 'What's the price of thyroid test?'"
            
            return response
        
        # No tests found
        response = "💰 **Test Pricing**\n\n"
        response += "I'm here to help you with test pricing! Here's what you can do:\n\n"
        response += "✓ **Ask About Specific Tests**\n"
        response += "   Example: 'How much is Complete Blood Count?'\n\n"
        response += "✓ **Find Test Categories**\n"
        response += "   Example: 'Blood test prices' or 'Thyroid tests'\n\n"
        response += "✓ **Book tests Direct From Chat**\n"
        response += "   Example: 'Book glucose test'\n\n"
        response += "**💡 Current Pricing Varies By Lab**\n"
        response += "Contact the lab directly for exact rates."
        
        return response
    
    def _handle_symptom_query(self, user_message):
        """Handle symptom-based test recommendations with professional medical guidance"""
        # Use RAG to retrieve relevant tests based on symptoms
        retrieved_tests = RAGService.retrieve_tests_for_symptoms(user_message)
        
        if retrieved_tests.exists():
            response = "🩺 **Suggested Tests Based on Your Symptoms**\n\n"
            response += "Here are relevant tests that may help:\n\n"
            
            for test in retrieved_tests[:5]:
                labs_offering = Lab.objects.filter(tests=test).distinct()[:2]
                response += f"**🧬 {test.name}**\n"
                if test.description:
                    response += f"   _{test.description}_\n"
                if test.price:
                    response += f"   💵 **Rs. {test.price}**\n"
                if labs_offering.exists():
                    lab_names = ', '.join([lab.name for lab in labs_offering])
                    response += f"   🏥 **Available at:** {lab_names}\n"
                response += "\n"
            
            response += "**⚠️ Important Reminder:**\n"
            response += "These suggestions are general guidance only. For accurate diagnosis:\n"
            response += "✓ Consult with a doctor\n"
            response += "✓ Discuss which tests are right for you\n"
            response += "✓ Follow professional medical advice\n\n"
            response += "**Ready to Book?**\n"
            response += "Say 'Book [test name]' and I'll get you started! 📋"
            
            return response
        else:
            # Try to provide general recommendations
            common_tests = Test.objects.all()[:5]
            if common_tests.exists():
                response = "🩺 **Symptom-Based Test Recommendations**\n\n"
                response += "Thanks for sharing your symptoms! Here are some tests that may be helpful:\n\n"
                
                for test in common_tests:
                    response += f"🧬 **{test.name}**"
                    if test.price:
                        response += f" - Rs. {test.price}"
                    if test.description:
                        response += f"\n   _{test.description}_"
                    response += "\n"
                
                response += "\n**⚠️ Medical Advice:**\n"
                response += "Always consult a healthcare provider for personalized recommendations based on your symptoms and medical history.\n\n"
                response += "**What Can I Help With?**\n"
                response += "✓ More test details\n"
                response += "✓ Find nearby labs\n"
                response += "✓ Check pricing\n"
                response += "✓ Book tests now\n\n"
                response += "**Want to proceed?** Say 'Book [test name]' 📋"
            else:
                response = "🩺 **Symptom-Based Recommendations**\n\n"
                response += "Thanks for sharing! Here's how I can help:\n\n"
                response += "**🤝 For Best Results:**\n"
                response += "• Talk to a doctor about your symptoms\n"
                response += "• Describe your symptoms in detail\n"
                response += "• I'll suggest relevant tests\n\n"
                response += "**I Can Help With:**\n"
                response += "✓ Test information\n"
                response += "✓ Lab locations\n"
                response += "✓ Pricing details\n"
                response += "✓ Booking tests\n\n"
                response += "**What would you like to do?** 😊"
            
            return response
    
    def _help_response(self):
        return """ℹ️ **How I Can Help You**

I'm your personal healthcare assistant! I can help you navigate medical testing easily:

🔍 **Search & Find Tests**
• Ask about specific tests by name
• Get test descriptions & pricing
• Example: "What is Complete Blood Count?" or "Blood test price"

📍 **Find Nearby Labs**
• Locate labs in your area
• See which labs offer specific tests
• Get lab contact information
• Example: "Labs in Kathmandu" or "Where can I do thyroid test?"

💰 **Pricing & Costs**
• Compare test prices instantly
• Find affordable options
• No hidden charges
• Example: "How much does a lipid panel cost?"

🩺 **Smart Recommendations**
• Describe your symptoms → I suggest relevant tests
• Based on your health concerns
• Only quality, verified tests
• Example: "I have headaches and fatigue"

📋 **Quick Booking**
• Book tests directly through chat
• Get confirmation instantly
• Email confirmation sent to you
• Example: "Book Complete Blood Count"

❓ **Got Questions?**
• "What is diabetes screening?"
• "Which test for heart health?"
• "Do I need fasting for blood test?"
• "Labs near me"

**💡 Pro Tip:** The more details you provide, the better recommendations I can give! 😊

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
            response = "🔍 **Matching Tests Found**\n\n"
            response += "Here are tests that match your search:\n\n"
            for test in tests:
                response += f"**🧬 {test.name}**"
                if test.price:
                    response += f" - Rs. {test.price}"
                response += "\n"
                if test.description:
                    response += f"   _{test.description}_\n"
                response += "\n"
            
            response += "**What's Next?**\n"
            response += "✓ Want to book? Say 'Book [test name]'\n"
            response += "✓ Need more details? Ask about the test\n"
            response += "✓ Find labs? I can show you nearby labs\n"
            
            return response
        elif labs.exists():
            response = "🏥 **Matching Labs Found**\n\n"
            response += "Here are labs we found:\n\n"
            for lab in labs[:5]:
                response += f"**{lab.name}**\n"
                response += f"   📍 {lab.city}, {lab.state}\n"
                response += f"   🧪 {lab.tests.count()} tests available\n\n"
            
            response += "**What's Next?**\n"
            response += "✓ Want to see their tests? Ask about them\n"
            response += "✓ Looking for a specific test? Let me search\n"
            response += "✓ Ready to book? I'm here to help!\n"
            
            return response
        else:
            response = "🤔 **Didn't quite catch that**\n\n"
            response += "I'm here to help! Here's what you can do:\n\n"
            response += "**🧬 Search Tests**\n"
            response += "• Ask about any medical test\n"
            response += "• Example: \"What is Complete Blood Count?\"\n\n"
            response += "**🏥 Find Labs**\n"
            response += "• Find labs near you\n"
            response += "• Example: \"Labs in Kathmandu\"\n\n"
            response += "**💰 Check Prices**\n"
            response += "• Get test pricing instantly\n"
            response += "• Example: \"How much is diabetes test?\"\n\n"
            response += "**🩺 Get Recommendations**\n"
            response += "• Tell me your symptoms\n"
            response += "• Example: \"I have fever and cough\"\n\n"
            response += "**📋 Quick Booking**\n"
            response += "• Book tests through chat\n"
            response += "• Example: \"Book blood test\"\n\n"
            response += "**What would you like to do?** 😊"
            
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
        
        # If no specific matches, return popular/common tests
        if not unique_recommendations:
            # Return commonly used medical tests
            popular_test_names = [
                'BLOOD SUGAR F', 'CHOLESTEROL', 'LIPID PROFILE', 
                'CREATININE', 'BUN', 'ALBUMIN', 'HB A1C',
                'BILIRUBIN', 'BLOOD GAS ANALYSIS', 'LFT'
            ]
            common_tests = []
            for name in popular_test_names:
                test = Test.objects.filter(name__icontains=name).first()
                if test:
                    common_tests.append(test)
            
            if common_tests:
                unique_recommendations = common_tests[:10]
            else:
                # Last resort: get first 5 tests only if nothing else works
                fallback_tests = Test.objects.all()[:5]
                if fallback_tests.exists():
                    unique_recommendations = list(fallback_tests)
        
        # Save recommendation only if we have tests
        if unique_recommendations:
            recommendation = AIRecommendation.objects.create(
                symptoms=symptoms_text,
                user=user
            )
            recommendation.recommended_tests.set(unique_recommendations[:10])
            return recommendation
        
        return None
