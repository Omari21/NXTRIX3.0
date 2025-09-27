#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_function_only():
    # Extract just the function in question
    function_code = '''
def show_investor_portal():
    """Investor Portal with Secure Access and Analytics"""
    st.header("🏛️ Investor Portal")
'''
    
    try:
        compile(function_code, '<string>', 'exec')
        print("Function code compiles successfully")
        return True
    except SyntaxError as e:
        print(f"Function syntax error: {e}")
        return False

def test_preceding_code():
    # Test the code just before the function
    preceding_code = '''
    # Optimization Recommendations
    st.subheader("🎯 Portfolio Optimization Recommendations")
    if recommendations:
        for rec in recommendations:
            with st.expander(f"{rec['priority']} Priority: {rec['title']}"):
                st.write(f"**Type:** {rec['type']}")
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Potential Impact:** {rec['impact']}")
                
                if st.button(f"Implement {rec['title']}", key=f"implement_{rec['type']}"):
                    st.success("Recommendation noted! Our team will follow up with implementation details.")
    else:
        st.info("Your portfolio is well-optimized! No immediate recommendations.")
'''
    
    try:
        compile(preceding_code, '<string>', 'exec')
        print("Preceding code compiles successfully") 
        return True
    except SyntaxError as e:
        print(f"Preceding code syntax error: {e}")
        return False

if __name__ == "__main__":
    print("Testing function only:")
    test_function_only()
    print("\nTesting preceding code:")
    test_preceding_code()