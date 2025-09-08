"""
Comprehensive tests for MCP integration and natural language processing.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from src.mcp.nlp import NaturalLanguageProcessor, CommandIntent, CommandExecutor
from src.mcp.client import InternshalaAutomationClient
from src.mcp.server import TOOL_HANDLERS


class TestNaturalLanguageProcessor:
    """Test natural language command parsing."""
    
    @pytest.fixture
    def nlp_processor(self):
        """Create NLP processor for testing."""
        return NaturalLanguageProcessor(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_fallback_parsing_chat_messages(self, nlp_processor):
        """Test fallback parsing for chat message commands."""
        command = "Download chat messages from the last 5 days"
        
        intent = await nlp_processor._fallback_parse(command)
        
        assert intent.action == "extract_chat_messages"
        assert intent.parameters["since_days"] == 5
        assert intent.parameters["export_csv"] is True
        assert intent.confidence == 0.7
    
    @pytest.mark.asyncio
    async def test_fallback_parsing_stipend_filter(self, nlp_processor):
        """Test parsing messages with stipend filter."""
        command = "Find messages that mention stipend above 1000"
        
        intent = await nlp_processor._fallback_parse(command)
        
        assert intent.action == "extract_chat_messages"
        assert intent.parameters["min_stipend"] == 1000
        assert "stipend" in intent.parameters.get("keyword", "")
    
    @pytest.mark.asyncio
    async def test_fallback_parsing_internship_search(self, nlp_processor):
        """Test parsing internship search commands."""
        command = "Show opportunities posted in the last 7 days for Graphic Design"
        
        intent = await nlp_processor._fallback_parse(command)
        
        assert intent.action == "search_internships"
        assert intent.parameters["posted_within_days"] == 7
        assert intent.parameters["role"] == "Graphic Design"
    
    @pytest.mark.asyncio 
    async def test_fallback_parsing_startup_filter(self, nlp_processor):
        """Test parsing with startup filter."""
        command = "Download all internships where company is a startup and role is Marketing"
        
        intent = await nlp_processor._fallback_parse(command)
        
        assert intent.action == "search_internships"
        assert intent.parameters["startup_only"] is True
        assert intent.parameters["role"] == "Marketing"
    
    def test_entity_extraction(self, nlp_processor):
        """Test entity extraction from text."""
        text = "Find messages from last 5 days mentioning 10000 stipend"
        
        entities = nlp_processor.extract_entities(text)
        
        assert "numbers" in entities
        assert 5 in entities["numbers"]
        assert 10000 in entities["numbers"]
        assert entities.get("time_days") == 5


class TestCommandIntent:
    """Test CommandIntent model."""
    
    def test_command_intent_creation(self):
        """Test creating a CommandIntent."""
        intent = CommandIntent(
            action="extract_chat_messages",
            parameters={"since_days": 5},
            confidence=0.9,
            original_command="Download messages from last 5 days"
        )
        
        assert intent.action == "extract_chat_messages"
        assert intent.parameters["since_days"] == 5
        assert intent.confidence == 0.9
    
    def test_command_intent_validation(self):
        """Test CommandIntent validation."""
        with pytest.raises(ValueError):
            CommandIntent(
                action="",  # Empty action should fail
                parameters={},
                confidence=0.5,
                original_command="test"
            )


class TestCommandExecutor:
    """Test command execution."""
    
    @pytest.fixture
    def executor(self):
        """Create command executor for testing."""
        return CommandExecutor()
    
    @pytest.mark.asyncio
    async def test_chat_extraction_execution(self, executor):
        """Test chat extraction command execution."""
        intent = CommandIntent(
            action="extract_chat_messages",
            parameters={"since_days": 5, "export_csv": True},
            confidence=0.9,
            original_command="test"
        )
        
        result = await executor.execute_command(intent)
        
        assert result["success"] is True
        assert result["action"] == "extract_chat_messages"
        assert result["parameters"]["since_days"] == 5
    
    @pytest.mark.asyncio
    async def test_internship_search_execution(self, executor):
        """Test internship search command execution."""
        intent = CommandIntent(
            action="search_internships",
            parameters={"role": "Marketing", "startup_only": True},
            confidence=0.9,
            original_command="test"
        )
        
        result = await executor.execute_command(intent)
        
        assert result["success"] is True
        assert result["action"] == "search_internships"
        assert result["parameters"]["startup_only"] is True
    
    @pytest.mark.asyncio
    async def test_unknown_action_handling(self, executor):
        """Test handling of unknown actions."""
        intent = CommandIntent(
            action="unknown_action",
            parameters={},
            confidence=0.5,
            original_command="test"
        )
        
        result = await executor.execute_command(intent)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]


class TestInternshalaAutomationClient:
    """Test the main automation client."""
    
    @pytest.fixture
    def client(self):
        """Create client for testing."""
        return InternshalaAutomationClient(openai_api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_low_confidence_handling(self, client):
        """Test handling of low confidence parsing."""
        with patch.object(client.nlp, 'parse_command') as mock_parse:
            mock_parse.return_value = CommandIntent(
                action="unknown",
                parameters={},
                confidence=0.3,  # Low confidence
                original_command="unclear command"
            )
            
            result = await client.process_natural_language_command("unclear command")
            
            assert result["success"] is False
            assert "Could not understand" in result["error"]
            assert "suggestion" in result
    
    @pytest.mark.asyncio
    async def test_successful_command_processing(self, client):
        """Test successful command processing."""
        with patch.object(client.nlp, 'parse_command') as mock_parse, \
             patch.object(client, '_execute_mcp_tool') as mock_execute:
            
            mock_parse.return_value = CommandIntent(
                action="extract_chat_messages",
                parameters={"since_days": 5},
                confidence=0.9,
                original_command="Download messages from last 5 days"
            )
            
            mock_execute.return_value = {
                "tool_executed": "extract_chat_messages",
                "mcp_response": "Successfully extracted 10 messages"
            }
            
            result = await client.process_natural_language_command("Download messages from last 5 days")
            
            assert result["success"] is True
            assert result["original_command"] == "Download messages from last 5 days"
            assert "result" in result


class TestMCPTools:
    """Test MCP tool functions."""
    
    @pytest.mark.asyncio
    async def test_extract_chat_messages_tool(self):
        """Test the extract_chat_messages MCP tool."""
        from src.mcp.server import call_extract_chat_messages
        
        arguments = {
            "limit": 10,
            "since_days": 5,
            "export_csv": True
        }
        
        # Mock the ChatMessageExtractor
        with patch('src.mcp.server.ChatMessageExtractor') as mock_extractor:
            mock_instance = AsyncMock()
            mock_extractor.return_value.__aenter__.return_value = mock_instance
            mock_instance.extract_all_messages.return_value = []
            
            result = await call_extract_chat_messages(arguments)
            
            assert result is not None
            assert hasattr(result, 'content')
    
    @pytest.mark.asyncio
    async def test_search_internships_tool(self):
        """Test the search_internships MCP tool."""
        from src.mcp.server import call_search_internships
        
        arguments = {
            "role": "Marketing",
            "startup_only": True,
            "limit": 20
        }
        
        # Mock the InternshipScraper
        with patch('src.mcp.server.InternshipScraper') as mock_scraper:
            mock_instance = AsyncMock()
            mock_scraper.return_value.__aenter__.return_value = mock_instance
            mock_instance.search_internships.return_value = []
            
            result = await call_search_internships(arguments)
            
            assert result is not None
            assert hasattr(result, 'content')


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_chat_extraction(self):
        """Test complete pipeline for chat extraction."""
        command = "Download chat messages from the last 5 days"
        
        # Mock all the dependencies
        with patch('src.mcp.client.OpenAI') as mock_openai, \
             patch('src.mcp.server.ChatMessageExtractor') as mock_extractor:
            
            # Setup mocks
            mock_openai_instance = AsyncMock()
            mock_openai.return_value = mock_openai_instance
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '''
            {
                "action": "extract_chat_messages",
                "parameters": {"since_days": 5, "export_csv": true},
                "confidence": 0.95
            }
            '''
            mock_openai_instance.chat.completions.create.return_value = mock_response
            
            mock_extractor_instance = AsyncMock()
            mock_extractor.return_value.__aenter__.return_value = mock_extractor_instance
            mock_extractor_instance.extract_all_messages.return_value = []
            
            # Run the test
            client = InternshalaAutomationClient(openai_api_key="test-key")
            result = await client.process_natural_language_command(command)
            
            # Verify results
            assert result["success"] is True
            assert result["parsed_intent"]["action"] == "extract_chat_messages"
            assert result["parsed_intent"]["parameters"]["since_days"] == 5
    
    @pytest.mark.asyncio
    async def test_end_to_end_internship_search(self):
        """Test complete pipeline for internship search."""
        command = "Find marketing internships at startups"
        
        # This would use fallback parsing since we're not mocking OpenAI here
        client = InternshalaAutomationClient(openai_api_key="test-key")
        
        # Mock only the MCP tool execution
        with patch('src.mcp.server.InternshipScraper') as mock_scraper:
            mock_instance = AsyncMock()
            mock_scraper.return_value.__aenter__.return_value = mock_instance
            mock_instance.search_internships.return_value = []
            
            result = await client.process_natural_language_command(command)
            
            # Should work with fallback parsing
            assert result["success"] is True
            assert result["parsed_intent"]["action"] == "search_internships"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
