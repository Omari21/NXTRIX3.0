"""Feature request system module"""

class FeatureRequestSystem:
    def __init__(self):
        self.requests = []
    
    def submit_request(self, user_id, request):
        return {"success": True, "request_id": "demo_req_123"}

feature_system = FeatureRequestSystem()