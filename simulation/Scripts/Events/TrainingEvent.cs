using System;

namespace SentinelX.Simulation.Events
{
    [Serializable]
    public sealed class TrainingEvent
    {
        public int sequence_number;
        public long scenario_time_ms;
        public string event_type;
        public string observation_id;
        public string response_category;
        public float confidence;
    }
}
