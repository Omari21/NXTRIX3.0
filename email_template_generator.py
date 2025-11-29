"""Email template generator module"""

class EmailTemplateGenerator:
    def __init__(self):
        self.templates = []
    
    def generate_template(self, template_type, context):
        return {"subject": "Demo Subject", "body": "Demo email body"}

email_generator = EmailTemplateGenerator()