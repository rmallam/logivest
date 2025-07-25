# Real Estate Investment Analyzer - Australian Market Edition

A sophisticated MCP (Model Context Protocol) server that provides comprehensive real estate investment analysis tools for the Australian property market. This system helps investors identify profitable rental properties, calculate yields, and make informed investment decisions across major Australian cities.

## 🏠 Features

### MCP Server Tools
- **Property Analysis**: Comprehensive property valuation and investment scoring
- **Rental Yield Calculator**: Calculate gross/net yields and cash flow projections
- **Investment Opportunities**: Find properties matching budget and yield criteria
- **Market Analysis**: Local market insights and investment recommendations
- **Loan Scenarios**: Compare different financing options

### Web Interface
- **Interactive Dashboard**: User-friendly property analysis interface
- **Budget-based Search**: Filter properties by budget constraints
- **Investment Calculator**: Standalone calculator for quick calculations
- **Market Insights**: Real-time market analysis for popular locations

### Australian Market Features
- **Major Cities Coverage**: Melbourne, Sydney, Brisbane, Perth, Adelaide, Canberra
- **Local Currency**: All calculations in Australian Dollars (AUD)
- **Metric Measurements**: Property sizes in square meters
- **Australian Market Data**: Realistic property prices and rental rates for Australian cities
- **Local Market Conditions**: Vacancy rates, days on market, and growth trends specific to Australian markets

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Activate the virtual environment (already created)
source .venv/bin/activate

# Install dependencies (already installed)
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template (optional - uses sample data by default)
cp .env.example .env

# Edit .env with your API keys (optional)
# ZILLOW_API_KEY=your_key_here
# RENTSPYDER_API_KEY=your_key_here
```

### 3. Run MCP Server
```bash
# Start the MCP server for Claude Desktop integration
python -m mcp_server.server
```

### 4. Run Web Interface
```bash
# Start the web application (in a separate terminal)
python web_interface/app.py
```

### 5. Access the Application
- **Web Interface**: http://localhost:5001 (port 5001 to avoid conflicts)
- **MCP Server**: Configured for Claude Desktop integration

## 📊 Usage Examples

### Property Analysis
```python
# Analyze a specific property
get_property_analysis(
    address="123 Collins St, Melbourne VIC", 
    budget=500000
)
```

### Find Investment Opportunities
```python
# Search for properties in a location
find_investment_opportunities(
    location="Melbourne, VIC",
    max_budget=600000,
    min_yield=8.0,
    property_type="house"
)
```

### Calculate Returns
```python
# Calculate rental yields and returns
calculate_rental_yield(
    property_price=400000,
    monthly_rent=2500,
    annual_expenses=5000,
    down_payment_percent=20
)
```

## 🔧 MCP Server Integration

### Configure Claude Desktop
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "real-estate-analyzer": {
      "type": "stdio",
      "command": "/Users/rakeshkumarmallam/logivest/.venv/bin/python",
      "args": ["-m", "mcp_server.server"]
    }
  }
}
```

### Available Tools
1. `get_property_analysis` - Analyze specific properties
2. `calculate_rental_yield` - Calculate investment returns
3. `find_investment_opportunities` - Search for properties
4. `get_market_analysis` - Market insights
5. `compare_loan_scenarios` - Compare financing options

## 🏗️ Project Structure

```
logivest/
├── mcp_server/                 # MCP Server implementation
│   ├── server.py              # Main MCP server
│   ├── tools/                 # Analysis tools
│   │   ├── property_analysis.py
│   │   ├── financial_calc.py
│   │   └── market_research.py
│   └── data/                  # Data clients and samples
│       └── api_clients.py
├── web_interface/             # Flask web application
│   ├── app.py                # Main web server
│   └── templates/            # HTML templates
├── .vscode/                  # VS Code configuration
│   └── mcp.json             # MCP server config
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── CONTEXT.md              # Detailed project context
└── README.md               # This file
```

## 📈 Investment Metrics Calculated

### Yield Calculations
- **Gross Rental Yield**: Annual rent ÷ Property price × 100
- **Net Rental Yield**: (Annual rent - Expenses) ÷ Property price × 100
- **Cap Rate**: Net Operating Income ÷ Property Value × 100

### Cash Flow Analysis
- **Monthly Cash Flow**: Monthly rent - Monthly expenses - Mortgage payment
- **Cash-on-Cash Return**: Annual cash flow ÷ Total cash invested × 100
- **Break-even Analysis**: Time to recover initial investment

### Risk Assessment
- **Investment Scoring**: 1-10 scale based on multiple factors
- **Market Analysis**: Local market conditions and trends
- **Recommendation Engine**: AI-powered investment suggestions

## 🔗 Data Sources

### Current Implementation
- **Sample Data**: Realistic property and market data for demonstration
- **Market Research**: Built-in market analysis for major cities
- **Calculation Engine**: Comprehensive financial modeling

### Future API Integrations
- **Zillow API**: Property values and rental estimates
- **RentSpyder API**: Rental market data
- **Census API**: Demographic and economic data
- **Walk Score API**: Neighborhood amenities

## 🌐 Web Interface Features

### Property Analysis Page
- Input property address and budget
- Comprehensive analysis results
- Visual metrics and scoring
- Investment recommendations

### Investment Search
- Location-based property search
- Budget and yield filtering
- Comparative analysis
- Market insights

### Calculator Tools
- Standalone rental yield calculator
- Loan scenario comparisons
- Quick calculation scenarios
- Export and print functionality

## 🧪 Development

### Running Tests
```bash
# Run MCP server tests
python -m pytest tests/ -v

# Test web interface
python -m pytest web_interface/tests/ -v
```

### Adding New Features
1. **MCP Tools**: Add new analysis functions to `mcp_server/tools/`
2. **Web Pages**: Create new templates in `web_interface/templates/`
3. **Data Sources**: Extend `api_clients.py` with new data providers

## 🔒 Disclaimer

This tool provides estimates and analysis based on available data sources. All calculations are for informational purposes only and should not be considered as financial advice. 

**Important**: Always consult with qualified real estate and financial professionals before making investment decisions. The accuracy of estimates depends on data quality and market conditions.

## 📄 License

This project is for educational and demonstration purposes. Real estate investment involves significant financial risk and professional guidance is recommended.

## 🤝 Contributing

This project serves as a foundation for real estate investment analysis tools. The modular architecture allows for easy extension with additional data sources, analysis methods, and user interface enhancements.

---

**Built with Model Context Protocol (MCP) Technology**  
*Enabling seamless integration between AI assistants and real estate analysis tools*
