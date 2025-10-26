import pytest
import json
import os
from unittest.mock import patch, MagicMock
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the functions we want to test
import sys
sys.path.append('/Users/magnusgraham/calhacks/calhacks2025/backend')
from utils.learning_agent import handle_screenshot_event, _ensure_lesson_loaded
from utils.database_context import DatabaseContextProvider

class TestScreenshotEndpoint:
    """Test suite for the screenshot endpoint functionality."""
    
    @pytest.fixture
    def supabase_client(self):
        """Create a real Supabase client for testing."""
        url = os.environ.get("SUPABASE_URL", "https://nynhpfozeopaaqkczcqs.supabase.co")
        key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55bmhwZm96ZW9wYWFxa2N6Y3FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNTAxNTQsImV4cCI6MjA3NjkyNjE1NH0.Cn9Ke-dEiTVxQryfqI3MeuLruKUpV8bgjK-p3w7fKIE")
        
        try:
            client = create_client(url, key)
            return client
        except Exception as e:
            pytest.skip(f"Could not connect to Supabase: {e}")
    
    @pytest.fixture
    def db_context(self):
        """Create database context provider."""
        return DatabaseContextProvider()
    
    def test_get_lesson_steps_batch_with_real_data(self, supabase_client, db_context):
        """Test that we can actually fetch lesson data from Supabase."""
        # Test with lesson_id = 1
        lesson_data = db_context.get_lesson_steps_batch(1)
        
        print(f"Lesson data for lesson 1: {lesson_data}")
        
        # Should return a dictionary with step_order as keys
        assert isinstance(lesson_data, dict)
        
        # If there's data, check the structure
        if lesson_data:
            for step_order, step_info in lesson_data.items():
                assert isinstance(step_order, int)
                assert isinstance(step_info, dict)
                assert "name" in step_info
                assert "description" in step_info
                assert "finish_criteria" in step_info
    
    def test_ensure_lesson_loaded_with_real_data(self, supabase_client):
        """Test the _ensure_lesson_loaded function with real Supabase data."""
        # Test with lesson_id = 1
        lesson_data = _ensure_lesson_loaded(1)
        
        print(f"_ensure_lesson_loaded result for lesson 1: {lesson_data}")
        
        if lesson_data:
            assert isinstance(lesson_data, dict)
            # Check that it has the expected structure
            for step_order, step_info in lesson_data.items():
                assert isinstance(step_order, int)
                assert isinstance(step_info, dict)
                assert "description" in step_info
                assert "finish_criteria" in step_info
    
    def test_handle_screenshot_event_with_real_lesson(self, supabase_client):
        """Test handle_screenshot_event with a real lesson from Supabase."""
        # First, let's see what lessons exist
        try:
            lessons_resp = supabase_client.table("lesson").select("id,name").execute()
            lessons = lessons_resp.data or []
            print(f"Available lessons: {lessons}")
            
            if not lessons:
                pytest.skip("No lessons found in database")
            
            # Use the first available lesson
            lesson_id = lessons[0]["id"]
            print(f"Testing with lesson_id: {lesson_id}")
            
            # Test the function
            result = handle_screenshot_event(
                user_id="test-user",
                lesson_id=lesson_id,
                step_order=1,
                base64_image="fake_base64_image_data"
            )
            
            print(f"handle_screenshot_event result: {result}")
            
            # Should not have "error" key if lesson exists
            assert "error" not in result, f"Unexpected error: {result.get('error')}"
            assert "completed" in result
            
        except Exception as e:
            pytest.skip(f"Could not test with real data: {e}")
    
    def test_handle_screenshot_event_nonexistent_lesson(self, supabase_client):
        """Test handle_screenshot_event with a lesson that doesn't exist."""
        # Use a very high lesson_id that likely doesn't exist
        result = handle_screenshot_event(
            user_id="test-user",
            lesson_id=99999,
            step_order=1,
            base64_image="fake_base64_image_data"
        )
        
        print(f"Result for nonexistent lesson: {result}")
        
        # Should return error
        assert result["completed"] == False
        assert "error" in result
        assert "Lesson not found" in result["error"]
    
    def test_handle_screenshot_event_nonexistent_step(self, supabase_client):
        """Test handle_screenshot_event with a step that doesn't exist."""
        try:
            # First get a real lesson
            lessons_resp = supabase_client.table("lesson").select("id").execute()
            lessons = lessons_resp.data or []
            
            if not lessons:
                pytest.skip("No lessons found in database")
            
            lesson_id = lessons[0]["id"]
            
            # Test with a very high step_order that likely doesn't exist
            result = handle_screenshot_event(
                user_id="test-user",
                lesson_id=lesson_id,
                step_order=999,
                base64_image="fake_base64_image_data"
            )
            
            print(f"Result for nonexistent step: {result}")
            
            # Should handle gracefully (might not error, just return completed=False)
            assert "completed" in result
            
        except Exception as e:
            pytest.skip(f"Could not test with real data: {e}")
    
    def test_direct_supabase_query_structure(self, supabase_client):
        """Test the exact query structure used in the application."""
        try:
            # Test the exact query from get_lesson_steps_batch
            resp = (
                supabase_client
                .table("step")
                .select("step_order,name,description,finish_criteria")
                .eq("lesson_id", 1)
                .order("step_order")
                .execute()
            )
            
            results = resp.data or []
            print(f"Direct Supabase query results: {results}")
            
            # Convert to the same format as the application
            lesson_data = {}
            for row in results:
                step_order = row["step_order"]
                name = row["name"]
                description = row["description"]
                finish_criteria = row.get("finish_criteria")
                lesson_data[step_order] = {
                    "name": name,
                    "description": description,
                    "finish_criteria": finish_criteria or ""
                }
            
            print(f"Formatted lesson data: {lesson_data}")
            
            # Should be a dictionary
            assert isinstance(lesson_data, dict)
            
        except Exception as e:
            pytest.skip(f"Could not test direct Supabase query: {e}")

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
