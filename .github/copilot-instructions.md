<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Real Estate Investment Analyzer - Copilot Instructions

## Project Overview
This is a Model Context Protocol (MCP) server project for comprehensive real estate investment analysis. The system provides tools for property valuation, rental yield calculation, and investment recommendations through both MCP integration and web interface.

## Architecture Guidelines

### MCP Server Development
- All MCP tools should follow the FastMCP framework patterns
- Use proper async/await patterns for all data fetching operations
- Implement comprehensive error handling and logging
- Return formatted strings with emoji indicators for better readability
- Tools should be self-contained and not depend on external state

### Code Style and Patterns
- Follow Python PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Implement proper logging to stderr (never stdout for MCP servers)
- Use descriptive variable names and comprehensive docstrings
- Structure code with clear separation of concerns

### Financial Calculations
- All financial calculations should use standard real estate formulas
- Implement proper validation for input parameters
- Consider edge cases (zero values, negative numbers)
- Provide clear explanations of calculation methodologies
- Use industry-standard metrics and terminology

### Data Handling
- Provide sample data for demonstration when APIs are unavailable
- Implement graceful fallbacks for API failures
- Use realistic data ranges and market conditions
- Structure data models consistently across the application
- Implement proper data validation and sanitization

### Web Interface Development
- Use Bootstrap 5 for consistent UI components
- Implement responsive design for mobile compatibility
- Provide clear user feedback for all operations
- Use semantic HTML and accessibility best practices
- Implement proper form validation and error handling

### Error Handling and Logging
- Log all errors to stderr using the logging module
- Provide user-friendly error messages
- Implement proper exception handling in all async operations
- Never write to stdout in MCP server code
- Use appropriate log levels (INFO, WARNING, ERROR)

## Development References

### MCP Server Resources
- Official MCP Documentation: https://modelcontextprotocol.io/
- Python SDK Reference: https://github.com/modelcontextprotocol/create-python-server
- FastMCP Framework: Use for rapid MCP server development

### Real Estate Calculations
- Rental Yield = (Annual Rental Income / Property Price) × 100
- Cap Rate = (Net Operating Income / Property Value) × 100
- Cash-on-Cash Return = (Annual Cash Flow / Total Cash Invested) × 100
- Loan-to-Value Ratio = (Loan Amount / Property Value) × 100

### Technology Stack
- **Backend**: Python 3.13+ with FastMCP, Flask
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Data**: Pandas, NumPy for calculations
- **APIs**: HTTPX for async HTTP requests
- **Environment**: Python virtual environment with pip

## File Organization

### MCP Server (`mcp_server/`)
- `server.py`: Main MCP server with tool definitions
- `tools/`: Individual analysis modules (property, financial, market)
- `data/`: API clients and sample data providers

### Web Interface (`web_interface/`)
- `app.py`: Flask application with routes and API endpoints
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JavaScript, and image assets

### Configuration
- `requirements.txt`: Python package dependencies
- `.env.example`: Environment variable template
- `README.md`: Comprehensive project documentation

## Development Workflows

### Adding New MCP Tools
1. Define the tool function with proper type hints
2. Use `@mcp.tool()` decorator with descriptive docstring
3. Implement async data fetching and calculation logic
4. Return formatted string results with emoji indicators
5. Add comprehensive error handling and logging

### Extending Web Interface
1. Create new route in `app.py` with proper error handling
2. Implement corresponding HTML template
3. Add navigation links and form validation
4. Test responsive design across device sizes
5. Implement proper accessibility features

### Adding New Data Sources
1. Extend `api_clients.py` with new API integration
2. Implement proper authentication and rate limiting
3. Provide realistic sample data fallbacks
4. Add appropriate error handling and retries
5. Update documentation with new data source information

## Testing and Quality Assurance

### Code Quality
- Use proper type hints throughout the codebase
- Implement comprehensive docstrings for all functions
- Follow consistent naming conventions
- Use proper async/await patterns for I/O operations
- Implement proper error handling and logging

### Testing Considerations
- Test all MCP tools with various input scenarios
- Verify web interface functionality across browsers
- Test API integration with both real and sample data
- Validate financial calculations against known formulas
- Test error handling and edge case scenarios

## Deployment Considerations

### MCP Server Deployment
- Ensure proper Python virtual environment setup
- Configure Claude Desktop integration properly
- Test MCP server communication and tool execution
- Verify logging configuration (stderr only)
- Document installation and configuration steps

### Web Interface Deployment
- Configure proper Flask production settings
- Implement proper security headers and CSRF protection
- Set up proper static file serving
- Configure appropriate logging and monitoring
- Document deployment requirements and procedures

## Best Practices

### Performance
- Use async/await for all I/O operations
- Implement proper caching for frequently accessed data
- Optimize database queries and API calls
- Use appropriate data structures for calculations
- Monitor memory usage and optimize where necessary

### Security
- Validate all user input properly
- Implement proper authentication for production use
- Use environment variables for sensitive configuration
- Sanitize data before display to prevent XSS
- Implement proper CSRF protection for forms

### Maintainability
- Keep functions focused and single-purpose
- Use consistent code organization and naming
- Implement proper configuration management
- Document all complex business logic
- Use version control best practices

This project demonstrates modern MCP server development with comprehensive real estate analysis capabilities.
