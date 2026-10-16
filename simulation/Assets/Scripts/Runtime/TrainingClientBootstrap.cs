using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace SentinelX.Client
{
    public sealed class TrainingClientBootstrap : MonoBehaviour
    {
        private readonly AssessmentApiClient api = new AssessmentApiClient();
        private readonly List<CreateEventRequest> pendingEvents = new List<CreateEventRequest>();
        private InputField baseUrlInput;
        private InputField traineeInput;
        private Text statusText;
        private Text promptText;
        private Text scenarioText;
        private Button startButton;
        private Button submitButton;
        private Button completeButton;
        private string selectedCategory = "category_a";
        private readonly List<Button> categoryButtons = new List<Button>();
        private ScenarioObservationResponse scenario;
        private SessionResponse session;
        private int observationIndex;
        private int seed;
        private float startedAt;
        private bool busy;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateRuntimeClient()
        {
            if (FindObjectOfType<TrainingClientBootstrap>() != null) return;
            var root = new GameObject("SENTINEL-X Training Client");
            root.AddComponent<TrainingClientBootstrap>();
            DontDestroyOnLoad(root);
        }

        private void Start()
        {
            BuildUi();
            SetStatus("Connect to the local assessment API, then start a synthetic scenario.");
        }

        private void BuildUi()
        {
            var canvasObject = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasObject.transform.SetParent(transform, false);
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            eventSystem.transform.SetParent(transform, false);
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 800);

            var panel = MakePanel(canvasObject.transform, "Panel", new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(900, 650));
            var layout = panel.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(24, 24, 20, 20);
            layout.spacing = 12;
            layout.childControlHeight = true;
            layout.childForceExpandHeight = false;
            layout.childControlWidth = true;
            AddText(panel.transform, "SENTINEL-X | TRAINING CLIENT", 26, 44);
            baseUrlInput = AddInput(panel.transform, "API base URL", "http://127.0.0.1:8000");
            traineeInput = AddInput(panel.transform, "Synthetic trainee ID", "trainee-demo");
            scenarioText = AddText(panel.transform, "Scenario: OBS-001 — Synthetic baseline", 18, 32);
            promptText = AddText(panel.transform, "Select Start Scenario to load the trainee-facing prompts.", 20, 110);
            AddText(panel.transform, "Response category", 14, 24);
            var categoryRow = new GameObject("Response Categories", typeof(RectTransform), typeof(HorizontalLayoutGroup));
            categoryRow.transform.SetParent(panel.transform, false);
            var categoryLayout = categoryRow.GetComponent<HorizontalLayoutGroup>();
            categoryLayout.spacing = 8;
            categoryLayout.childForceExpandWidth = true;
            categoryLayout.childControlHeight = true;
            categoryButtons.Add(AddButton(categoryRow.transform, "Category A", () => SelectCategory("category_a")));
            categoryButtons.Add(AddButton(categoryRow.transform, "Category B", () => SelectCategory("category_b")));
            categoryButtons.Add(AddButton(categoryRow.transform, "Category C", () => SelectCategory("category_c")));
            categoryButtons.Add(AddButton(categoryRow.transform, "No observation", () => SelectCategory("no_observation")));
            SelectCategory(selectedCategory);
            var buttons = new GameObject("Actions", typeof(RectTransform), typeof(HorizontalLayoutGroup));
            buttons.transform.SetParent(panel.transform, false);
            var row = buttons.GetComponent<HorizontalLayoutGroup>();
            row.spacing = 10;
            row.childForceExpandWidth = true;
            row.childControlHeight = true;
            startButton = AddButton(buttons.transform, "Start Scenario", StartScenario);
            submitButton = AddButton(buttons.transform, "Submit Response", SubmitResponse);
            completeButton = AddButton(buttons.transform, "Complete Session", CompleteSession);
            statusText = AddText(panel.transform, "Ready", 16, 90);
            submitButton.interactable = false;
            completeButton.interactable = false;
        }

        private void StartScenario()
        {
            if (busy) return;
            api.BaseUrl = baseUrlInput.text.Trim();
            var trainee = traineeInput.text.Trim();
            if (string.IsNullOrEmpty(trainee)) { SetStatus("Enter a synthetic trainee ID."); return; }
            seed = Math.Abs(Environment.TickCount);
            pendingEvents.Clear();
            observationIndex = 0;
            session = null;
            scenario = null;
            busy = true;
            startButton.interactable = false;
            StartCoroutine(api.GetObservations("OBS-001", loaded =>
            {
                scenario = loaded;
                StartCoroutine(api.CreateSession(trainee, "OBS-001", seed, created =>
                {
                    session = created;
                    startedAt = Time.realtimeSinceStartup;
                    busy = false;
                    startButton.interactable = true;
                    submitButton.interactable = true;
                    completeButton.interactable = true;
                    selectedCategory = scenario.allowed_response_categories.Length > 0
                        ? scenario.allowed_response_categories[0] : "category_a";
                    SelectCategory(selectedCategory);
                    ShowCurrentObservation();
                    SetStatus("Session " + session.session_id + " started. Seed: " + seed);
                }, Failed));
            }, Failed));
        }

        private void SubmitResponse()
        {
            if (busy || session == null || scenario == null || observationIndex >= scenario.observations.Length) return;
            var prompt = scenario.observations[observationIndex];
            var item = new CreateEventRequest
            {
                sequence_number = pendingEvents.Count + 1,
                scenario_time_ms = (long)((Time.realtimeSinceStartup - startedAt) * 1000f),
                event_type = "classification_submitted",
                payload = new EventPayload
                {
                    observation_id = prompt.observation_id,
                    response_category = selectedCategory,
                    confidence = 0.8f
                }
            };
            busy = true;
            submitButton.interactable = false;
            StartCoroutine(api.SubmitEvent(session.session_id, item, () =>
            {
                pendingEvents.Add(item);
                observationIndex++;
                busy = false;
                submitButton.interactable = observationIndex < scenario.observations.Length;
                ShowCurrentObservation();
                SetStatus("Recorded response " + pendingEvents.Count + " of " + scenario.observations.Length + ".");
            }, Failed));
        }

        private void CompleteSession()
        {
            if (busy || session == null || pendingEvents.Count == 0) { SetStatus("Record at least one response before completing."); return; }
            busy = true;
            completeButton.interactable = false;
            StartCoroutine(api.CompleteSession(session.session_id, result =>
            {
                busy = false;
                submitButton.interactable = false;
                completeButton.interactable = false;
                promptText.text = "Assessment complete. Overall score: " + result.overall_score.ToString("F1") + "/100";
                SetStatus("Assessment " + result.assessment_id + " saved. Results are provisional training feedback.");
            }, Failed));
        }

        private void ShowCurrentObservation()
        {
            if (scenario == null) return;
            if (observationIndex >= scenario.observations.Length)
            {
                promptText.text = "All prompts answered. Complete the session to calculate the assessment.";
                submitButton.interactable = false;
                return;
            }
            var current = scenario.observations[observationIndex];
            promptText.text = "Observation " + (observationIndex + 1) + " of " + scenario.observations.Length + "\n\n" + current.display_prompt;
        }

        private void Failed(string error)
        {
            busy = false;
            if (startButton != null) startButton.interactable = true;
            if (submitButton != null) submitButton.interactable = session != null;
            if (completeButton != null) completeButton.interactable = session != null;
            SetStatus("API error: " + error);
        }

        private void SetStatus(string message) { if (statusText != null) statusText.text = message; }

        private static GameObject MakePanel(Transform parent, string name, Vector2 anchorMin, Vector2 anchorMax, Vector2 size)
        {
            var item = new GameObject(name, typeof(RectTransform), typeof(Image));
            item.transform.SetParent(parent, false);
            var rect = item.GetComponent<RectTransform>();
            rect.anchorMin = anchorMin; rect.anchorMax = anchorMax; rect.sizeDelta = size;
            item.GetComponent<Image>().color = new Color(0.08f, 0.10f, 0.14f, 0.96f);
            return item;
        }

        private static Text AddText(Transform parent, string value, int size, float height)
        {
            var item = new GameObject("Text", typeof(RectTransform), typeof(Text), typeof(LayoutElement));
            item.transform.SetParent(parent, false);
            var text = item.GetComponent<Text>();
            text.text = value; text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = size; text.color = Color.white; text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            item.GetComponent<LayoutElement>().preferredHeight = height;
            return text;
        }

        private static InputField AddInput(Transform parent, string label, string value)
        {
            AddText(parent, label, 14, 24);
            var item = new GameObject("Input", typeof(RectTransform), typeof(Image), typeof(InputField), typeof(LayoutElement));
            item.transform.SetParent(parent, false);
            item.GetComponent<Image>().color = new Color(0.16f, 0.18f, 0.23f);
            item.GetComponent<LayoutElement>().preferredHeight = 34;
            var text = AddText(item.transform, value, 16, 28);
            var input = item.GetComponent<InputField>();
            input.textComponent = text; input.text = value;
            return input;
        }

        private void SelectCategory(string category)
        {
            selectedCategory = category;
            var names = new[] { "category_a", "category_b", "category_c", "no_observation" };
            for (var i = 0; i < categoryButtons.Count; i++)
            {
                var button = categoryButtons[i];
                if (button == null) continue;
                var image = button.GetComponent<Image>();
                image.color = names[i] == selectedCategory
                    ? new Color(0.12f, 0.48f, 0.32f)
                    : new Color(0.16f, 0.18f, 0.23f);
            }
        }

        private static Button AddButton(Transform parent, string label, Action action)
        {
            var item = new GameObject(label, typeof(RectTransform), typeof(Image), typeof(Button), typeof(LayoutElement));
            item.transform.SetParent(parent, false);
            item.GetComponent<Image>().color = new Color(0.13f, 0.34f, 0.54f);
            item.GetComponent<LayoutElement>().preferredHeight = 42;
            var button = item.GetComponent<Button>();
            var text = AddText(item.transform, label, 15, 36);
            text.alignment = TextAnchor.MiddleCenter;
            button.onClick.AddListener(() => action());
            return button;
        }
    }
}
