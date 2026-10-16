namespace SentinelX.Simulation.UI
{
    public sealed class SimulationStatus
    {
        public string ScenarioId { get; private set; } = string.Empty;
        public string SessionId { get; private set; } = string.Empty;
        public string State { get; private set; } = "READY";

        public void SetSession(string scenarioId, string sessionId)
        {
            ScenarioId = scenarioId ?? string.Empty;
            SessionId = sessionId ?? string.Empty;
            State = "RUNNING";
        }

        public void Complete()
        {
            State = "COMPLETED";
        }
    }
}
