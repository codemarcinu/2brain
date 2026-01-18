"""
Tests for LLM Processor
"""
import pytest
from unittest.mock import Mock, patch


class TestLLMProcessor:
    """Test suite for LLMProcessor"""

    def test_parse_json_response_clean_json(self):
        """Test parsing clean JSON response"""
        from services.llm_processor import LLMProcessor

        # Create mock config
        mock_config = Mock()
        mock_config.base.ollama_host = "http://localhost:11434"
        mock_config.llm_model = "test-model"
        mock_config.prompts_path = Mock()

        with patch("services.llm_processor.ChatOllama"):
            processor = LLMProcessor(config=mock_config)

        json_str = '{"summary": "Test summary", "tags": ["tag1", "tag2"]}'
        result = processor._parse_json_response(json_str)

        assert result is not None
        assert result["summary"] == "Test summary"
        assert result["tags"] == ["tag1", "tag2"]

    def test_parse_json_response_with_markdown_blocks(self):
        """Test parsing JSON wrapped in markdown code blocks"""
        from services.llm_processor import LLMProcessor

        mock_config = Mock()
        mock_config.base.ollama_host = "http://localhost:11434"
        mock_config.llm_model = "test-model"
        mock_config.prompts_path = Mock()

        with patch("services.llm_processor.ChatOllama"):
            processor = LLMProcessor(config=mock_config)

        json_str = '```json\n{"summary": "Test", "tags": []}\n```'
        result = processor._parse_json_response(json_str)

        assert result is not None
        assert result["summary"] == "Test"

    def test_parse_json_response_invalid_json(self):
        """Test parsing invalid JSON returns None"""
        from services.llm_processor import LLMProcessor

        mock_config = Mock()
        mock_config.base.ollama_host = "http://localhost:11434"
        mock_config.llm_model = "test-model"
        mock_config.prompts_path = Mock()

        with patch("services.llm_processor.ChatOllama"):
            processor = LLMProcessor(config=mock_config)

        json_str = "This is not JSON"
        result = processor._parse_json_response(json_str)

        assert result is None
