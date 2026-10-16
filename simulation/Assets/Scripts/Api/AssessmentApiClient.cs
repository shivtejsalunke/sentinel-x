using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace SentinelX.Client
{
    public sealed class AssessmentApiClient
    {
        public string BaseUrl { get; set; } = "http://127.0.0.1:8000";

        public IEnumerator GetObservations(string scenarioId, Action<ScenarioObservationResponse> success, Action<string> failure)
        {
            using (var request = UnityWebRequest.Get(Url("/api/v1/scenarios/" + UnityWebRequest.EscapeURL(scenarioId) + "/observations")))
            {
                yield return request.SendWebRequest();
                if (request.result != UnityWebRequest.Result.Success) { failure?.Invoke(Error(request)); yield break; }
                var response = JsonUtility.FromJson<ScenarioObservationResponse>(request.downloadHandler.text);
                if (response == null || response.observations == null) { failure?.Invoke("Invalid scenario response."); yield break; }
                success?.Invoke(response);
            }
        }

        public IEnumerator CreateSession(string traineeId, string scenarioId, int seed, Action<SessionResponse> success, Action<string> failure)
        {
            var body = JsonUtility.ToJson(new CreateSessionRequest { trainee_id = traineeId, scenario_id = scenarioId, seed = seed });
            using (var request = JsonRequest(Url("/api/v1/sessions"), body))
            {
                yield return request.SendWebRequest();
                if (request.result != UnityWebRequest.Result.Success) { failure?.Invoke(Error(request)); yield break; }
                var response = JsonUtility.FromJson<SessionResponse>(request.downloadHandler.text);
                if (response == null || string.IsNullOrEmpty(response.session_id)) { failure?.Invoke("Invalid session response."); yield break; }
                success?.Invoke(response);
            }
        }

        public IEnumerator SubmitEvent(string sessionId, CreateEventRequest item, Action success, Action<string> failure)
        {
            var body = JsonUtility.ToJson(item);
            using (var request = JsonRequest(Url("/api/v1/sessions/" + UnityWebRequest.EscapeURL(sessionId) + "/events"), body))
            {
                yield return request.SendWebRequest();
                if (request.result != UnityWebRequest.Result.Success) { failure?.Invoke(Error(request)); yield break; }
                success?.Invoke();
            }
        }

        public IEnumerator CompleteSession(string sessionId, Action<AssessmentWireResponse> success, Action<string> failure)
        {
            using (var request = JsonRequest(Url("/api/v1/sessions/" + UnityWebRequest.EscapeURL(sessionId) + "/complete"), "{}"))
            {
                yield return request.SendWebRequest();
                if (request.result != UnityWebRequest.Result.Success) { failure?.Invoke(Error(request)); yield break; }
                var response = JsonUtility.FromJson<AssessmentWireResponse>(request.downloadHandler.text);
                if (response == null || string.IsNullOrEmpty(response.assessment_id)) { failure?.Invoke("Invalid assessment response."); yield break; }
                success?.Invoke(response);
            }
        }

        private UnityWebRequest JsonRequest(string url, string body)
        {
            var request = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST);
            request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = 10;
            return request;
        }

        private string Url(string path) => BaseUrl.TrimEnd('/') + path;
        private static string Error(UnityWebRequest request) =>
            string.IsNullOrEmpty(request.downloadHandler?.text) ? request.error : request.downloadHandler.text;
    }
}
