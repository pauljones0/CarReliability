# Car Reliability Aggregator & MCP Server

A robust, modular data collection pipeline and CLI-first MCP server for automotive reliability, maintenance costs, and safety data.

## 🚀 Model Context Protocol (MCP)
This project is an **MCP Server**. AI agents can explore the dataset using familiar Unix-style commands.

### Agent Workflow
1.  **Discover:** `reliability` (shows usage)
2.  **Explore:** `reliability ls Honda` (lists models)
3.  **Search:** `reliability grep "Accord"`
4.  **Inspect:** `reliability cat Honda_Accord`

### MCP Setup
Add this to your `mcp_config.json` (e.g., in Claude Desktop or other clients):

```json
{
  "mcpServers": {
    "car-reliability": {
      "command": "python3",
      "args": ["/path/to/CarReliability/src/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/CarReliability"
      }
    }
  }
}
```
See `mcp_config.sample.json` for a template.

---

## 🔄 Refresh Pipeline
To refresh the entire dataset (443+ models), use the following command. It features **exponential backoff** for rate limits and **automated model discovery** for NHTSA.

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 src/main.py --all --workers 5
```

### Contribution Workflow (PRs)
We prioritize community data updates! If you update the data or fix a naming mismatch:
1.  Run the refresh pipeline.
2.  Review `naming_audit.log` for any new 404s.
3.  **Commit both code and data:** `git add src/ aggregated_reliability.json`
4.  **Submit a PR:** Please make a PR to the main remote repo with your updated `aggregated_reliability.json` so the entire community benefits from the fresh stats.

---

## 🛠 Architecture & Modularity
The project is built on a "Two-Layer" Unix philosophy:
-   **Execution Layer (`UnixExecutor`):** Pure logic, piping (`|`), and sequential (`;`) execution.
-   **Presentation Layer (`LLMPresentation`):** Binary guards, auto-truncation (200 line limit), and metadata footers (`[exit:0 | 12ms]`).

### Project Structure
-   `src/sources/`: Modular data fetchers (NHTSA, RepairPal, CarEdge, etc.)
-   `src/cli_interface.py`: The `reliability` command implementation.
-   `src/mcp_server.py`: The MCP wrapper for agent interaction.
-   `src/main.py`: The primary aggregation engine.

## Data Sources
1.  **Dashboard Light:** Historical reliability (1993-2018) via OpenCV image processing.
2.  **RepairPal:** Annual repair costs and 5.0-scale ratings.
3.  **NHTSA:** Official recalls and consumer complaints (up to 2024).
4.  **CarComplaints.com:** Worst years and common mechanical failure points.
5.  **FuelEconomy.gov (EPA):** Official MPG estimates.
6.  **VMR Canada:** Wholesale/Retail pricing by trim.
7.  **CarEdge:** 10-year projected maintenance costs.
8.  **Safety Ratings:** Combined NHTSA/IIHS crash test results.

## Testing
```bash
pytest tests/
# or use the verification script
python3 scratch/verify_mcp.py
```
