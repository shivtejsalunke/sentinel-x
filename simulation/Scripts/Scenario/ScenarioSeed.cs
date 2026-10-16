using System;

namespace SentinelX.Simulation.Scenario
{
    public static class ScenarioSeed
    {
        public static Random CreateRandom(int seed)
        {
            if (seed < 0)
                throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be non-negative.");
            return new Random(seed);
        }
    }
}
