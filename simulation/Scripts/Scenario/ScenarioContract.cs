using System;
using System.Collections.Generic;

namespace SentinelX.Simulation.Scenario
{
    [Serializable]
    public sealed class ScenarioContract
    {
        public string scenario_id;
        public string version;
        public string title;
        public string rubric_id;
        public string rubric_version;
        public string difficulty_band;
        public List<string> learning_objectives = new List<string>();
        public List<string> observation_ids = new List<string>();
    }
}
