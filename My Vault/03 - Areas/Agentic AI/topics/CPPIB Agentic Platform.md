1. Agentic Experience
	- Cohesive web UI, all-in-one experience (like Claude desktop) to enable user work with agents and manage agents, agent teams, automations, install skills/tools(mcp), provision sandboxes; monitor agent activities, status; validate output quality with AI-assistance
	- In-chat interface
	- Mobile integration
	- IDE integration
	- Claude Terminal integration
	- Claw-alike autonomous agent with local-first, persistsited memory
2. Agentic Automation
	- Autonomy & Multi-Step execution
	- Build the integration between events and agents, events bootstraps agent container and execute on AgentCore Runtime, the results are available from agent UI and CloudWatch;
	- HITL guard the risky actions, and send proactive confirmation via chat msgs
	- Build holistic coverage of events
		- GitHub events
		- Data Fabric events
		- AWS events (S3, CloudWatch Alarms, etc)
	- Use custom periodic jobs to automate 
3. Agentic Foundations
	- Build resilient, interoperable, replayable and cost-effective agent harness to orchestrate the agent system: Context, Memory, Tools, Skills, Session/State, Safety, Traceability, Identity/Auth
	- The agent harness is the core engine for agentic workload and supports different execution paradims (long-running, on-demand, event-driven), it needs to be self-contained, env-agnostic
	- 
	