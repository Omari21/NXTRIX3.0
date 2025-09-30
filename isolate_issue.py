#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def isolate_problem_area(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Start from the problematic function and work backwards
        start_line = 2730  # A few lines before the problematic function
        
        # Try different end points to find where it breaks
        for end_line in range(start_line + 10, len(lines) + 1, 50):
            test_content = ''.join(lines[start_line:end_line])
            
            try:
                compile(test_content, f'<lines {start_line}-{end_line}>', 'exec')
                print(f"Lines {start_line}-{end_line}: OK")
            except SyntaxError as e:
                print(f"Lines {start_line}-{end_line}: Syntax Error at line {e.lineno + start_line}: {e.msg}")
                # If we found an error, narrow it down
                return start_line + e.lineno - 1
            except Exception as e:
                print(f"Lines {start_line}-{end_line}: Other error: {e}")
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    problem_line = isolate_problem_area("streamlit_app.py")
    if problem_line:
        print(f"\nProblem is around line {problem_line}")
    else:
        print("\nCould not isolate the problem")