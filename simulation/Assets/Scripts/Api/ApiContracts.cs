using System;
using System.Collections.Generic;

namespace SentinelX.Client
{
    [Serializable] public sealed class ScenarioObservationResponse
    {
        public string scenario_id;
        public string version;
        public string[] allowed_response_categories;
        public ObservationPrompt[] observations;
    }

    [Serializable] public sealed class ObservationPrompt
    {
        public string observation_id;
        public string display_prompt;
    }

    [Serializable] public sealed class CreateSessionRequest
    {
        public string trainee_id;
        public string scenario_id;
        public int seed;
    }

    [Serializable] public sealed class SessionResponse
    {
        public string session_id;
        public string status;
    }

    [Serializable] public sealed class EventPayload
    {
        public string observation_id;
        public string response_category;
        public float confidence;
    }

    [Serializable] public sealed class CreateEventRequest
    {
        public int sequence_number;
        public long scenario_time_ms;
        public string event_type;
        public EventPayload payload;
    }

    [Serializable] public sealed class AssessmentResponse
    {
        public string assessment_id;
        public string scenario_id;
        public float overall_score;
        public Dictionary<string, float> component_scores;
    }

    [Serializable] public sealed class AssessmentWireResponse
    {
        public string assessment_id;
        public string session_id;
        public string scenario_id;
        public float overall_score;
        public string rubric_id;
        public string rubric_version;
    }
}
