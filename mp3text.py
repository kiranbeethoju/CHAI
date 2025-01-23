Install-Package Microsoft.CognitiveServices.Speech

using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    // Configuration
    private static readonly string SubscriptionKey = "233lj2lkj1lkj2ghlj";
    private static readonly string Region = "eastus";
    private static readonly string AudioFile = "test.mp3";
    private static readonly string OutputFile = "transcription.txt";

    static async Task Main(string[] args)
    {
        try
        {
            // Create speech configuration
            var speechConfig = SpeechConfig.FromSubscription(SubscriptionKey, Region);
            
            // Set speech recognition language (you can change this as needed)
            speechConfig.SpeechRecognitionLanguage = "en-US";

            // Create audio configuration
            using var audioConfig = AudioConfig.FromWavFileInput(AudioFile);
            
            // Create speech recognizer
            using var speechRecognizer = new SpeechRecognizer(speechConfig, audioConfig);

            Console.WriteLine("Starting transcription...");

            // Initialize result string
            string transcriptionText = "";

            // Handle recognition events
            speechRecognizer.Recognized += (sender, e) =>
            {
                if (e.Result.Reason == ResultReason.RecognizedSpeech)
                {
                    transcriptionText += e.Result.Text + Environment.NewLine;
                    Console.WriteLine($"Recognized: {e.Result.Text}");
                }
            };

            // Start continuous recognition
            await speechRecognizer.StartContinuousRecognitionAsync();

            // Keep the program running while recognition is in progress
            Console.WriteLine("Press Enter to stop recognition...");
            Console.ReadLine();

            // Stop recognition
            await speechRecognizer.StopContinuousRecognitionAsync();

            // Save transcription to file
            await File.WriteAllTextAsync(OutputFile, transcriptionText);
            Console.WriteLine($"Transcription saved to {OutputFile}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error occurred: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
        }
    }
}
